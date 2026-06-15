"""
Carga / actualiza productos desde data/productos.csv a la base de datos.
Idempotente: si un producto con el mismo slug ya existe, lo actualiza.
Uso:  python load_productos.py
      python load_productos.py --csv data/mis_productos.csv
"""
import csv
import json
import os
import re
import sys
import unicodedata
import sqlite3
import argparse
from database import DB_PATH


CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "productos.csv")
USD_RATE = 1260.0  # actualizar si cambia el tipo de cambio


# ── helpers ──────────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore").decode()
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:120]


def get_db() -> sqlite3.Connection:
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── main ─────────────────────────────────────────────────────────────────────

def load(csv_path: str) -> None:
    if not os.path.exists(csv_path):
        sys.exit(f"ERROR: no se encontró el CSV en {csv_path}")

    conn = get_db()

    # índice de emails → user id
    users = {r["email"]: r["id"] for r in conn.execute("SELECT id, email FROM users")}

    # índice de slugs de categoría → category id
    cats  = {r["slug"]: r["id"] for r in conn.execute("SELECT id, slug FROM categories")}

    inserted = updated = skipped = errors = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for lineno, row in enumerate(reader, start=2):
            try:
                email   = row["seller_email"].strip()
                cat_sl  = row["category_slug"].strip()
                title   = row["title"].strip()

                # validaciones básicas
                if not title or not email:
                    print(f"  línea {lineno}: título o email vacío — saltando")
                    skipped += 1
                    continue

                seller_id = users.get(email)
                if seller_id is None:
                    print(f"  línea {lineno}: vendedor '{email}' no existe — saltando")
                    skipped += 1
                    continue

                cat_id = cats.get(cat_sl)
                if cat_id is None:
                    print(f"  línea {lineno}: categoría '{cat_sl}' no existe — saltando")
                    skipped += 1
                    continue

                slug    = slugify(title)
                brand   = row.get("brand", "").strip() or None
                model   = row.get("model", "").strip() or None
                compat  = [c.strip() for c in row.get("compatible_models", "").split(";") if c.strip()]
                cond    = row.get("condition", "NUEVO").strip().upper()
                price   = float(row.get("price", 0) or 0)
                feat    = int(row.get("featured", 0) or 0)
                short   = row.get("short_desc", "").strip()
                desc    = row.get("description", "").strip()

                # imagen: si empieza con http → URL externa; si no → ruta local en static/
                raw_img = row.get("image", "").strip()
                if raw_img:
                    if raw_img.startswith("http"):
                        image_url = raw_img
                    else:
                        # ruta local: asegurarse de que empiece con /static/
                        if not raw_img.startswith("/"):
                            raw_img = "/static/" + raw_img.lstrip("/")
                        image_url = raw_img
                        # avisar si el archivo físico no existe todavía
                        local_path = os.path.join(os.path.dirname(__file__), raw_img.lstrip("/").replace("/", os.sep))
                        if not os.path.exists(local_path):
                            print(f"  AVISO línea {lineno}: imagen '{image_url}' no encontrada en disco (la fila se carga igual)")
                else:
                    image_url = None

                images_json = json.dumps([image_url]) if image_url else json.dumps([])
                compat_json = json.dumps(compat)
                tags_json   = json.dumps([brand or "", model or "", cat_sl])
                price_usd   = round(price / USD_RATE, 2)

                existing = conn.execute("SELECT id FROM products WHERE slug=?", (slug,)).fetchone()

                if existing:
                    conn.execute("""
                        UPDATE products SET
                            seller_id=?, category_id=?, title=?, short_desc=?, description=?,
                            price=?, price_usd=?, condition=?, brand=?, model=?,
                            compatible_models=?, featured=?, tags=?,
                            image_url=COALESCE(NULLIF(?,''),(SELECT image_url FROM products WHERE slug=?)),
                            images=CASE WHEN ?!='' THEN ? ELSE images END
                        WHERE slug=?
                    """, (
                        seller_id, cat_id, title, short, desc,
                        price, price_usd, cond, brand, model,
                        compat_json, feat, tags_json,
                        image_url or "", slug,
                        image_url or "", images_json,
                        slug,
                    ))
                    updated += 1
                else:
                    conn.execute("""
                        INSERT INTO products(
                            seller_id, category_id, title, slug, short_desc, description,
                            price, price_usd, condition, brand, model, compatible_models,
                            stock, status, province, city, views, leads_count,
                            featured, part_number, image_url, images, tags
                        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """, (
                        seller_id, cat_id, title, slug, short, desc,
                        price, price_usd, cond, brand, model, compat_json,
                        1, "ACTIVO", "Buenos Aires", "Mar del Plata", 0, 0,
                        feat, None, image_url, images_json, tags_json,
                    ))
                    inserted += 1

            except Exception as exc:
                print(f"  ERROR línea {lineno}: {exc}")
                errors += 1

    conn.commit()
    conn.close()

    print(f"\nListo — insertados: {inserted}  actualizados: {updated}  saltados: {skipped}  errores: {errors}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default=CSV_PATH, help="Ruta al CSV de productos")
    args = parser.parse_args()
    print(f"Cargando desde: {args.csv}")
    load(args.csv)
