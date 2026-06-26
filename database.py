import sqlite3, os, json, random, bcrypt, re
from datetime import datetime, timedelta

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'repuestos.db')
DB_PATH = os.environ.get('DB_PATH', DEFAULT_DB_PATH)
USD_RATE = 1250

# ─── MARCAS Y MODELOS DE MOTOS ────────────────────────────────────────────────
MARCAS_MOTO = [
    'Honda','Yamaha','Zanella','Motomel','Corven','Gilera','Beta',
    'Kawasaki','Suzuki','Bajaj','TVS','Kymco','Mondial','Yumbo','Guerrero'
]

MODELOS_POR_MARCA = {
    'Honda':    ['Wave 110','Biz 125','CB 190R','CB 250F','XR 150L','PCX 150','CG 150','Titan 150'],
    'Yamaha':   ['YBR 125','FZ 25','XTZ 125','MT-03','FZ-S','R3','Crypton 110','SZ-RR'],
    'Zanella':  ['ZB 110','ZTT 200','Patagonia 250','RX 150 Z','Due 150','RZ3 150','ZB 50'],
    'Motomel':  ['CG 150 S2','Skua 150','Blitz 110','Xpro 250','Vx 150','CG 200'],
    'Corven':   ['Energy 110','Triax 150','TXR 250L','Mirage 110','Expert 200'],
    'Gilera':   ['SMX 200','VC 150','Sahara 200','Smash 110','GT1 200'],
    'Beta':     ['RR 200','Tempo 125','Urban 200','BS 150','Arrow 200'],
    'Kawasaki': ['Z400','Ninja 400','Versys 300','W175','KLX 150'],
    'Suzuki':   ['GSX-S750','Hayabusa','GN 125','Boulevard M800','V-Strom 650'],
    'Bajaj':    ['Rouser 200','Pulsar NS 200','Rouser 135','Boxer CT100'],
    'TVS':      ['Apache RR 310','RTR 200 4V','Sport 110'],
    'Kymco':    ['Like 200','AK 550','Agility 125'],
    'Mondial':  ['HD 254','TD 250','RX 250'],
    'Yumbo':    ['Sport 200','GTS 150','Dakar 200'],
    'Guerrero': ['GR 200','Trip 150','GMX 110'],
}

# ─── TIENDAS DE MAR DEL PLATA (datos reales de búsqueda) ─────────────────────
STORES_MDQ = [
    {
        'name': 'MDR Motos',
        'address': 'Av. Independencia 3527',
        'phone': '0223 456-7890',
        'whatsapp': '2234567890',
        'lat': -38.0057, 'lng': -57.5426,
        'brands': ['Honda','Yamaha','Zanella','Motomel'],
        'hours': 'Lun-Vie 9-18h · Sáb 9-13h',
        'description': 'Referente en repuestos de motos en Mar del Plata. Más de 15 años en el rubro.',
        'verified': 1,
    },
    {
        'name': 'Emiliozzi Motos',
        'address': 'Jacinto Peralta Ramos 1598',
        'phone': '0223 451-2233',
        'whatsapp': '2234512233',
        'lat': -37.9999, 'lng': -57.5627,
        'brands': ['Honda','Yamaha','Kawasaki','Suzuki'],
        'hours': 'Lun-Vie 8:30-18h · Sáb 9-13h',
        'description': 'Motor, suspensión, lubricantes y más. Especialistas en marcas japonesas.',
        'verified': 1,
    },
    {
        'name': 'LC Motoparts',
        'address': 'Av. Colon 2598',
        'phone': '0223 495-1100',
        'whatsapp': '2234951100',
        'lat': -37.9980, 'lng': -57.5698,
        'brands': ['Honda','Kawasaki','Yamaha','Suzuki','KTM'],
        'hours': 'Lun-Vie 9-18h · Sáb 9-14h',
        'description': 'Dealer oficial Honda, Kawasaki, Yamaha y Suzuki. Repuestos originales y accesorios.',
        'verified': 1,
    },
    {
        'name': 'Motos Marcos',
        'address': 'Av. Libertad 4156',
        'phone': '0223 473-8844',
        'whatsapp': '2234738844',
        'lat': -37.9823, 'lng': -57.5555,
        'brands': ['Zanella','Motomel','Corven','Gilera'],
        'hours': 'Lun-Sáb 9-18h',
        'description': 'Más de 130 reseñas positivas. Todo tipo de repuestos para motos nacionales.',
        'verified': 1,
    },
    {
        'name': 'Motos Pedro',
        'address': 'Av. Juan B. Justo 2196',
        'phone': '0223 474-5500',
        'whatsapp': '2234745500',
        'lat': -38.0023, 'lng': -57.5783,
        'brands': ['Honda','Zanella','Yamaha','TVS'],
        'hours': 'Lun-Vie 9-17:30h · Sáb 9-12:30h',
        'description': 'Atención personalizada. Especialistas en Honda Wave y Yamaha YBR.',
        'verified': 0,
    },
    {
        'name': 'Masxmoto',
        'address': 'Jujuy 3101',
        'phone': '0223 488-2200',
        'whatsapp': '2234882200',
        'lat': -38.0035, 'lng': -57.5530,
        'brands': ['Yamaha','Kawasaki','Suzuki','Beta'],
        'hours': 'Lun-Vie 9-18h · Sáb 9-13h',
        'description': 'Gran variedad en accesorios e indumentaria. Envíos a todo el país.',
        'verified': 0,
    },
    {
        'name': 'Motos Jonte',
        'address': 'Av. Constitucion 4550',
        'phone': '0223 476-6600',
        'whatsapp': '2234766600',
        'lat': -37.9756, 'lng': -57.5580,
        'brands': ['Honda','Yamaha','Corven','Bajaj'],
        'hours': 'Lun-Vie 9-18h · Sáb 9-13h',
        'description': 'MercadoLíder Platinum. Repuestos, cascos y accesorios. Envíos a todo el país.',
        'verified': 1,
    },
    {
        'name': 'Repuestos El Zorro',
        'address': 'Av. Independencia 2134',
        'phone': '0223 453-9900',
        'whatsapp': '2234539900',
        'lat': -38.0022, 'lng': -57.5437,
        'brands': ['Honda','Zanella','Motomel','Guerrero'],
        'hours': 'Lun-Sáb 8:30-18h',
        'description': 'Más de 20 años en el mercado. Precios competitivos y atención rápida.',
        'verified': 0,
    },
    {
        'name': 'Fraser Motos',
        'address': 'Av. Mario Bravo 3820',
        'phone': '0223 474-1122',
        'whatsapp': '2234741122',
        'lat': -38.0089, 'lng': -57.5590,
        'brands': ['Kawasaki','Suzuki','Yamaha','Beta'],
        'hours': 'Lun-Vie 9-18h · Sáb 9-13h',
        'description': 'Especialistas en motos deportivas y off-road. Kits de transmision y suspension.',
        'verified': 0,
    },
    {
        'name': 'Moto Norte MDP',
        'address': 'Av. Champagnat 3100',
        'phone': '0223 465-3344',
        'whatsapp': '2234653344',
        'lat': -37.9678, 'lng': -57.5672,
        'brands': ['Honda','TVS','Bajaj','Mondial'],
        'hours': 'Lun-Vie 9-17h · Sáb 9-12h',
        'description': 'Zona norte de Mar del Plata. Repuestos y accesorios para motos de trabajo.',
        'verified': 0,
    },
]

MDP_CENTER = (-38.0023, -57.5575)
MDP_BARRIOS = ['Centro', 'Puerto', 'La Perla', 'Los Troncos', 'Constitución', 'San Carlos', 'Camet']

def jitter_mdp_coords():
    """Coordenada aleatoria cerca del centro de Mar del Plata (~6km de radio)."""
    lat = MDP_CENTER[0] + random.uniform(-0.05, 0.05)
    lng = MDP_CENTER[1] + random.uniform(-0.05, 0.05)
    return round(lat, 5), round(lng, 5), random.choice(MDP_BARRIOS)


def slugify(t):
    t = str(t).lower()
    for a, b in [('á','a'),('é','e'),('í','i'),('ó','o'),('ú','u'),('ñ','n'),('ü','u')]:
        t = t.replace(a, b)
    t = re.sub(r'[^a-z0-9\s-]', '', t)
    return re.sub(r'\s+', '-', t.strip())

_used_slugs = set()
def make_slug(title):
    s = slugify(title)
    orig = s
    i = 2
    while s in _used_slugs:
        s = f'{orig}-{i}'
        i += 1
    _used_slugs.add(s)
    return s

# get_connection vive en db.py (dual-driver SQLite/Postgres). Se re-exporta acá
# para no romper los imports existentes (`from database import get_connection`).
from db import get_connection, IS_POSTGRES  # noqa: E402

# ─── SCHEMA ──────────────────────────────────────────────────────────────────
SCHEMA = """
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    icon TEXT DEFAULT '🔧',
    parent_id INTEGER REFERENCES categories(id),
    position INTEGER DEFAULT 0,
    description TEXT,
    image_url TEXT
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'COMPRADOR',
    phone TEXT,
    province TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS seller_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE REFERENCES users(id),
    company_name TEXT NOT NULL,
    description TEXT,
    phone TEXT,
    whatsapp TEXT,
    province TEXT DEFAULT 'Buenos Aires',
    city TEXT DEFAULT 'Mar del Plata',
    address TEXT,
    lat REAL,
    lng REAL,
    cuit TEXT,
    website TEXT,
    verified INTEGER DEFAULT 0,
    rating REAL DEFAULT 4.5,
    total_reviews INTEGER DEFAULT 8,
    total_leads INTEGER DEFAULT 0,
    response_rate INTEGER DEFAULT 95,
    response_time TEXT DEFAULT 'Menos de 2 hs',
    member_since TEXT DEFAULT (date('now')),
    store_hours TEXT,
    brands_json TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seller_id INTEGER REFERENCES users(id),
    category_id INTEGER REFERENCES categories(id),
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    short_desc TEXT,
    description TEXT,
    price REAL,
    price_usd REAL,
    condition TEXT DEFAULT 'NUEVO',
    brand TEXT,
    model TEXT,
    compatible_models TEXT,
    stock INTEGER DEFAULT 10,
    unit TEXT DEFAULT 'unidad',
    min_order INTEGER DEFAULT 1,
    status TEXT DEFAULT 'ACTIVO',
    province TEXT DEFAULT 'Buenos Aires',
    city TEXT DEFAULT 'Mar del Plata',
    views INTEGER DEFAULT 0,
    leads_count INTEGER DEFAULT 0,
    featured INTEGER DEFAULT 0,
    part_number TEXT,
    weight TEXT,
    image_url TEXT,
    images TEXT,
    tags TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER REFERENCES products(id),
    seller_id INTEGER REFERENCES users(id),
    buyer_name TEXT,
    buyer_email TEXT,
    buyer_phone TEXT,
    province TEXT,
    message TEXT,
    status TEXT DEFAULT 'NUEVO',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seller_id INTEGER REFERENCES users(id),
    buyer_name TEXT,
    rating INTEGER DEFAULT 5,
    comment TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS market_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price_ars REAL,
    change_pct REAL DEFAULT 0,
    category TEXT
);

CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    product_id INTEGER REFERENCES products(id),
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(user_id, product_id)
);

CREATE TABLE IF NOT EXISTS view_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    product_id INTEGER REFERENCES products(id),
    viewed_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS visited_places (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    seller_id INTEGER REFERENCES users(id),
    lat REAL, lng REAL, label TEXT,
    visited_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seller_id INTEGER REFERENCES users(id),
    name TEXT, rubro TEXT,
    description TEXT, phone TEXT, whatsapp TEXT,
    lat REAL, lng REAL, location_label TEXT, address TEXT,
    store_hours TEXT, verified INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_favorites_user ON favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_view_history_user ON view_history(user_id);
CREATE INDEX IF NOT EXISTS idx_visited_places_user ON visited_places(user_id);
"""

# ─── MIGRACIÓN IDEMPOTENTE (columnas nuevas sobre esquema existente) ──────────
def migrate_schema(conn):
    from db import add_column_if_missing, IS_POSTGRES as _is_pg
    add_column_if_missing(conn, 'users', 'google_id', 'TEXT')
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id) WHERE google_id IS NOT NULL")
    add_column_if_missing(conn, 'users', 'avatar_url', 'TEXT')
    add_column_if_missing(conn, 'users', 'auth_provider', "TEXT DEFAULT 'LOCAL'")
    add_column_if_missing(conn, 'users', 'lat', 'REAL')
    add_column_if_missing(conn, 'users', 'lng', 'REAL')
    add_column_if_missing(conn, 'users', 'location_label', 'TEXT')
    if _is_pg:
        # Postgres soporta relajar NOT NULL; SQLite no sin reconstruir la tabla,
        # asi que en SQLite los usuarios de Google reciben un hash inutilizable.
        conn.execute("ALTER TABLE users ALTER COLUMN password DROP NOT NULL")

    add_column_if_missing(conn, 'products', 'lat', 'REAL')
    add_column_if_missing(conn, 'products', 'lng', 'REAL')
    add_column_if_missing(conn, 'products', 'location_label', 'TEXT')
    add_column_if_missing(conn, 'products', 'listing_type', "TEXT DEFAULT 'PRODUCTO'")
    add_column_if_missing(conn, 'products', 'seller_kind', 'TEXT')
    add_column_if_missing(conn, 'products', 'moto_year', 'INTEGER')
    add_column_if_missing(conn, 'products', 'moto_cc', 'INTEGER')
    add_column_if_missing(conn, 'products', 'moto_km', 'INTEGER')
    add_column_if_missing(conn, 'products', 'papers_ok', 'INTEGER')

    add_column_if_missing(conn, 'categories', 'vertical', "TEXT DEFAULT 'REPUESTOS'")
    conn.commit()


# ─── VERTICALES: ACCESORIOS / MOTOS / AVISOS ──────────────────────────────────
ACCESORIOS_CATS = [
    ('GPS y Navegación', 'gps-navegacion', '🧭', 'Soportes celular, GPS y porta-documentos'),
    ('Audio y Multimedia', 'audio-multimedia', '🔊', 'Parlantes, alarmas y sistemas de sonido'),
    ('Cobertores y Fundas', 'cobertores-fundas', '🛡️', 'Cobertores impermeables y fundas de asiento'),
    ('Herramientas y Mantenimiento', 'herramientas-mantenimiento', '🧰', 'Kits de herramientas y limpieza'),
]

ACCESORIOS_PRODUCTS = [
    ('Soporte de celular para manubrio universal', 'gps-navegacion', None, None, ['Universal'], 4200,
     'Soporte antivibración para celular, ajustable a cualquier manubrio.', 'NUEVO'),
    ('GPS Garmin Zumo 396 para moto', 'gps-navegacion', 'Garmin', 'Zumo 396', ['Universal'], 185000,
     'GPS resistente al agua, pantalla táctil, mapas de Argentina precargados.', 'NUEVO'),
    ('Parlantes Bluetooth para moto 2x4 pulgadas', 'audio-multimedia', None, None, ['Universal'], 32000,
     'Sistema de audio Bluetooth resistente al agua para manubrio.', 'NUEVO'),
    ('Alarma con control remoto para moto', 'audio-multimedia', None, None, ['Universal'], 18500,
     'Alarma con sensor de movimiento y sirena 120dB.', 'NUEVO'),
    ('Cobertor de moto impermeable talle L', 'cobertores-fundas', None, None, ['Universal'], 12800,
     'Cobertor con costuras selladas, protege del sol y la lluvia.', 'NUEVO'),
    ('Funda de asiento de gel antideslizante', 'cobertores-fundas', None, None, ['Universal'], 9600,
     'Funda de gel para mayor confort en viajes largos.', 'NUEVO'),
    ('Kit de herramientas básico para moto (12 piezas)', 'herramientas-mantenimiento', None, None, ['Universal'], 7400,
     'Llaves, destornilladores y pinzas en estuche compacto.', 'NUEVO'),
    ('Kit de limpieza y abrillantado para moto', 'herramientas-mantenimiento', None, None, ['Universal'], 6200,
     'Shampoo, cera y paños de microfibra para el cuidado de la moto.', 'NUEVO'),
]


def _seed_verticals_if_missing(conn):
    """Idempotente: agrega ramas Accesorios/Motos/Avisos si todavia no existen."""
    # Indumentaria (cascos, guantes, etc.) pertenece a Accesorios, no Repuestos.
    conn.execute("""UPDATE categories SET vertical='ACCESORIOS'
        WHERE slug IN ('indumentaria','cascos','guantes','camperas-pantalones','botas','accesorios-seguridad')""")
    conn.commit()

    max_pos_row = conn.execute("SELECT COALESCE(MAX(position),0) FROM categories WHERE parent_id IS NULL").fetchone()
    pos = (max_pos_row[0] or 0) + 1

    cat_map = {}
    for name, slug, icon, desc in ACCESORIOS_CATS:
        existing = conn.execute("SELECT id FROM categories WHERE slug=?", (slug,)).fetchone()
        if existing:
            cat_map[slug] = existing[0]
            continue
        conn.execute(
            "INSERT INTO categories(name,slug,icon,description,position,image_url,vertical) "
            "VALUES(?,?,?,?,?,?,'ACCESORIOS')",
            (name, slug, icon, desc, pos, img(slug)))
        cat_map[slug] = conn.execute("SELECT id FROM categories WHERE slug=?", (slug,)).fetchone()[0]
        pos += 1
    conn.commit()

    for slug, vertical, name, icon, desc in [
        ('motos-en-venta', 'MOTOS', 'Motos en venta', '🏍️', 'Motos publicadas por particulares y concesionarias'),
        ('avisos-varios', 'AVISOS', 'Avisos', '📋', 'Avisos clasificados varios'),
    ]:
        row = conn.execute("SELECT id FROM categories WHERE slug=?", (slug,)).fetchone()
        if not row:
            conn.execute(
                "INSERT INTO categories(name,slug,icon,description,position,vertical) "
                "VALUES(?,?,?,?,?,?)", (name, slug, icon, desc, pos, vertical))
            pos += 1
        cat_map[slug] = conn.execute("SELECT id FROM categories WHERE slug=?", (slug,)).fetchone()[0]
    conn.commit()

    # Productos demo de Accesorios (solo si la vertical esta vacia)
    accesorios_count = conn.execute(
        "SELECT COUNT(*) FROM products WHERE category_id IN (%s)" %
        ','.join(str(cat_map[s]) for _, s, *_ in ACCESORIOS_CATS)).fetchone()[0]
    if accesorios_count == 0:
        seller_ids = [r[0] for r in conn.execute("SELECT id FROM users WHERE role='VENDEDOR'").fetchall()]
        if seller_ids:
            for title, cat_slug, brand, model, compat, price, desc, condition in ACCESORIOS_PRODUCTS:
                seller_id = random.choice(seller_ids)
                cat_id = cat_map[cat_slug]
                slug = make_slug(title)
                price_usd = round(price / USD_RATE, 2)
                img_url = cat_img(cat_slug, random.randint(1, 999))
                conn.execute("""
                    INSERT INTO products(seller_id,category_id,title,slug,short_desc,description,
                        price,price_usd,condition,brand,model,compatible_models,stock,
                        status,province,city,views,leads_count,featured,part_number,
                        image_url,images,tags,listing_type)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'PRODUCTO')""",
                    (seller_id, cat_id, title, slug,
                     desc[:100], desc, price, price_usd, condition, brand, model,
                     json.dumps(compat), random.randint(3, 40), 'ACTIVO',
                     'Buenos Aires', 'Mar del Plata', random.randint(20, 800),
                     random.randint(1, 30), 0, f"AC-{random.randint(10000,99999)}",
                     img_url, json.dumps([img_url]), json.dumps([brand or '', cat_slug])))
            conn.commit()

    # Motos demo (particulares y concesionarias)
    motos_count = conn.execute(
        "SELECT COUNT(*) FROM products WHERE listing_type='MOTO'").fetchone()[0]
    if motos_count == 0:
        seller_ids = [r[0] for r in conn.execute("SELECT id FROM users WHERE role='VENDEDOR'").fetchall()]
        if seller_ids:
            motos_cat_id = cat_map['motos-en-venta']
            demo_motos = [
                ('Honda Wave 110 2021', 'Honda', 'Wave 110', 2021, 110, 12500, 980000, 'CONCESIONARIA', 1),
                ('Yamaha YBR 125 2019', 'Yamaha', 'YBR 125', 2019, 125, 28400, 1450000, 'PARTICULAR', 1),
                ('Zanella ZB 110 2022', 'Zanella', 'ZB 110', 2022, 110, 6200, 870000, 'CONCESIONARIA', 0),
                ('Kawasaki Ninja 400 2020', 'Kawasaki', 'Ninja 400', 2020, 400, 15800, 6800000, 'PARTICULAR', 1),
                ('Motomel Skua 150 2018', 'Motomel', 'Skua 150', 2018, 150, 34200, 1190000, 'PARTICULAR', 0),
                ('Bajaj Rouser 200 2023', 'Bajaj', 'Rouser NS 200', 2023, 200, 3100, 3450000, 'CONCESIONARIA', 1),
            ]
            for title, brand, model, year, cc, km, price, seller_kind, papers_ok in demo_motos:
                seller_id = random.choice(seller_ids)
                slug = make_slug(title)
                price_usd = round(price / USD_RATE, 2)
                img_url = cat_img('motos-en-venta', random.randint(1, 999))
                lat, lng, barrio = jitter_mdp_coords()
                desc = f"{brand} {model} año {year}, {km:,} km. Service al dia, papeles {'al dia' if papers_ok else 'en tramite'}.".replace(',', '.')
                conn.execute("""
                    INSERT INTO products(seller_id,category_id,title,slug,short_desc,description,
                        price,price_usd,condition,brand,model,compatible_models,stock,
                        status,province,city,views,leads_count,featured,part_number,
                        image_url,images,tags,listing_type,seller_kind,moto_year,moto_cc,moto_km,papers_ok,
                        lat,lng,location_label)
                    VALUES(?,?,?,?,?,?,?,?,'USADO',?,?,?,1,'ACTIVO',?,?,?,?,0,?,?,?,?,'MOTO',?,?,?,?,?,?,?,?)""",
                    (seller_id, motos_cat_id, title, slug, desc[:100], desc,
                     price, price_usd, brand, model, json.dumps([f'{brand} {model}']),
                     'Buenos Aires', 'Mar del Plata', random.randint(50, 900),
                     random.randint(1, 25), f"MT-{random.randint(10000,99999)}",
                     img_url, json.dumps([img_url]), json.dumps([brand, model]),
                     seller_kind, year, cc, km, papers_ok, lat, lng, barrio))
            conn.commit()

    # Avisos demo (publicaciones livianas, sin verificacion de vendedor)
    avisos_count = conn.execute(
        "SELECT COUNT(*) FROM products WHERE listing_type='AVISO'").fetchone()[0]
    if avisos_count == 0:
        seller_ids = [r[0] for r in conn.execute("SELECT id FROM users").fetchall()]
        if seller_ids:
            avisos_cat_id = cat_map['avisos-varios']
            demo_avisos = [
                ('Busco mecánico a domicilio zona Centro', 'Necesito alguien de confianza para arreglo de embrague.', 0),
                ('Vendo cascos usados varios talles', 'Tres cascos en buen estado, $8000 cada uno.', 8000),
                ('Compro moto chocada para repuestos', 'Pago en efectivo, retiro yo mismo.', 0),
                ('Se ofrece servicio de fletes con moto', 'Envíos rápidos zona Mar del Plata.', 0),
            ]
            for title, desc, price in demo_avisos:
                seller_id = random.choice(seller_ids)
                slug = make_slug(title)
                img_url = cat_img('avisos-varios', random.randint(1, 999))
                conn.execute("""
                    INSERT INTO products(seller_id,category_id,title,slug,short_desc,description,
                        price,price_usd,condition,stock,status,province,city,views,leads_count,
                        featured,part_number,image_url,images,tags,listing_type)
                    VALUES(?,?,?,?,?,?,?,?,'USADO',1,'ACTIVO',?,?,?,?,0,?,?,?,?,'AVISO')""",
                    (seller_id, avisos_cat_id, title, slug, desc[:100], desc,
                     price or None, round((price or 0) / USD_RATE, 2),
                     'Buenos Aires', 'Mar del Plata', random.randint(10, 300),
                     random.randint(0, 10), f"AV-{random.randint(10000,99999)}",
                     img_url, json.dumps([img_url]), json.dumps(['aviso'])))
            conn.commit()

    # Servicios demo (talleres, gomerias, etc. - tabla propia, no products)
    servicios_count = conn.execute("SELECT COUNT(*) FROM services").fetchone()[0]
    if servicios_count == 0:
        seller_ids = [r[0] for r in conn.execute("SELECT id FROM users WHERE role='VENDEDOR'").fetchall()]
        if seller_ids:
            demo_servicios = [
                ('Taller Mecánico El Rayo', 'TALLER', 'Reparación general, service y diagnóstico de motos.',
                 '0223 455-1010', '2234551010', -38.0011, -57.5481, 'Centro, Mar del Plata'),
                ('Gomería Don Pedro', 'GOMERIA', 'Reparación de cubiertas y balanceo de ruedas.',
                 '0223 466-2020', '2234662020', -37.9988, -57.5601, 'Zona Sur, Mar del Plata'),
                ('Electricidad MotoSpark', 'ELECTRICA', 'Diagnóstico eléctrico, CDI, bobinas y cableado.',
                 '0223 477-3030', '2234773030', -38.0102, -57.5512, 'Zona Norte, Mar del Plata'),
                ('Grabado de Autopartes MDP', 'GRABADO', 'Grabado antirrobo de motor y chasis.',
                 '0223 488-4040', '2234884040', -37.9956, -57.5701, 'Centro, Mar del Plata'),
                ('Seguros Moto Total', 'SEGURO', 'Seguros de moto a terceros y todo riesgo.',
                 '0223 499-5050', '2234995050', -38.0033, -57.5450, 'Centro, Mar del Plata'),
            ]
            for name, rubro, desc, phone, wa, lat, lng, label in demo_servicios:
                seller_id = random.choice(seller_ids)
                conn.execute("""
                    INSERT INTO services(seller_id,name,rubro,description,phone,whatsapp,
                        lat,lng,location_label,address,store_hours,verified)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,1)""",
                    (seller_id, name, rubro, desc, phone, wa, lat, lng, label, label, 'Lun-Vie 9-18h'))
            conn.commit()

# ─── DATOS DE REFERENCIA (ticker) ────────────────────────────────────────────
MARKET_PRICES_DATA = [
    ('USD Oficial', 1250, 0.8, 'divisa'),
    ('USD Blue', 1295, 1.2, 'divisa'),
    ('Kit transmision Honda Wave', 4500, -2.1, 'repuesto'),
    ('Bateria 12V 5Ah', 8900, 3.5, 'repuesto'),
    ('Neumatico 80/100-14', 18500, 1.8, 'neumatico'),
    ('Casco integral AGV', 45000, 0.5, 'indumentaria'),
    ('Aceite 4T 10W40 1L', 2800, 2.2, 'lubricante'),
    ('Pastillas freno delantero', 2200, 0.0, 'repuesto'),
]

# ─── CATEGORÍAS PRINCIPALES ───────────────────────────────────────────────────
CATEGORIES = [
    # (name, slug, icon, description, subcategories)
    ('Motor', 'motor', '⚙️',
     'Pistones, cilindros, juntas, valvulas y todo para el motor',
     [('Pistones y Cilindros','pistones-cilindros'),
      ('Valvulas y Resortes','valvulas-resortes'),
      ('Juntas de Motor','juntas-motor'),
      ('Filtros de Aceite','filtros-aceite'),
      ('Ciguenal y Biela','ciguenal-biela'),
      ('Tapas y Carter','tapas-carter')]),

    ('Transmision', 'transmision', '⛓️',
     'Cadenas, pinones, coronas, embrague y caja de cambios',
     [('Cadenas y Kits','cadenas-kits'),
      ('Pinones y Coronas','pinones-coronas'),
      ('Embrague','embrague'),
      ('Caja de Cambios','caja-cambios')]),

    ('Frenos', 'frenos', '🛑',
     'Pastillas, zapatas, discos, cables y bombas de freno',
     [('Pastillas de Freno','pastillas-freno'),
      ('Zapatas de Freno','zapatas-freno'),
      ('Discos de Freno','discos-freno'),
      ('Cables de Freno','cables-freno'),
      ('Bombas de Freno','bombas-freno')]),

    ('Suspension', 'suspension', '🔩',
     'Amortiguadores, horquillas, bujes y resortes',
     [('Amortiguadores','amortiguadores'),
      ('Horquillas','horquillas'),
      ('Bujes y Rodamientos','bujes-rodamientos'),
      ('Resortes','resortes')]),

    ('Electrico', 'electrico', '⚡',
     'Baterias, CDI, reguladores, luces e instrumentos',
     [('Baterias','baterias'),
      ('CDI y Reguladores','cdi-reguladores'),
      ('Bobinas e Ignicion','bobinas-ignicion'),
      ('Luces y Faros','luces-faros'),
      ('Instrumentos','instrumentos')]),

    ('Carburacion', 'carburacion', '🔧',
     'Carburadores, filtros de aire, bujias y cables',
     [('Carburadores','carburadores'),
      ('Filtros de Aire','filtros-aire'),
      ('Bujias','bujias'),
      ('Cables de Acelerador','cables-acelerador')]),

    ('Carroceria y Chasis', 'carroceria', '🏍️',
     'Guardabarros, tanques, asientos, manubrios y espejos',
     [('Guardabarros','guardabarros'),
      ('Tanques de Combustible','tanques'),
      ('Asientos','asientos'),
      ('Manubrios y Puños','manubrios'),
      ('Espejos Retrovisores','espejos'),
      ('Carenados','carenados')]),

    ('Escape', 'escape', '💨',
     'Tubos de escape, silenciadores y colectores',
     [('Tubos de Escape','tubos-escape'),
      ('Silenciadores','silenciadores'),
      ('Colectores','colectores')]),

    ('Neumaticos', 'neumaticos', '⭕',
     'Cubiertas, camaras y llantas para todo tipo de moto',
     [('Cubiertas','cubiertas'),
      ('Camaras','camaras'),
      ('Llantas','llantas')]),

    ('Indumentaria', 'indumentaria', '🪖',
     'Cascos, guantes, camperas y todo para tu seguridad',
     [('Cascos','cascos'),
      ('Guantes','guantes'),
      ('Camperas y Pantalones','camperas-pantalones'),
      ('Botas','botas'),
      ('Accesorios de Seguridad','accesorios-seguridad')]),
]

# ─── PRODUCTOS DEMO (MercadoLibre-style) ─────────────────────────────────────
PRODUCTS_DATA = [
    # --- MOTOR ---
    ('Kit de piston Honda Wave 110 STD', 'pistones-cilindros', 'Honda', 'Wave 110',
     ['Honda Wave 110','Honda Biz 110'],
     8500, 'Kit completo piston + aro + pasador para Honda Wave 110. Medida estandar (STD). Incluye seguro de pasador.',
     'NUEVO', 'https://picsum.photos/seed/piston-wave/800/600', 1),

    ('Kit de piston Yamaha YBR 125 +0.25', 'pistones-cilindros', 'Yamaha', 'YBR 125',
     ['Yamaha YBR 125','Yamaha Crypton 110'],
     11200, 'Piston oversize +0.25mm para Yamaha YBR 125. Alta calidad, fabricacion nacional.',
     'NUEVO', 'https://picsum.photos/seed/piston-ybr/800/600', 0),

    ('Filtro de aceite Honda CB 190R original', 'filtros-aceite', 'Honda', 'CB 190R',
     ['Honda CB 190R','Honda CG 150'],
     1850, 'Filtro de aceite original Honda para CB 190R y CG 150. Garantia de calidad OEM.',
     'NUEVO', 'https://picsum.photos/seed/filtro-aceite/800/600', 0),

    ('Junta tapa valvulas Zanella ZB 110', 'juntas-motor', 'Zanella', 'ZB 110',
     ['Zanella ZB 110','Zanella Due 150'],
     950, 'Junta de tapa de valvulas para Zanella ZB 110. Material: goma de alta temperatura.',
     'NUEVO', 'https://picsum.photos/seed/junta-zanella/800/600', 0),

    ('Kit de juntas motor completo Honda CG 150', 'juntas-motor', 'Honda', 'CG 150',
     ['Honda CG 150','Honda Titan 150'],
     6800, 'Kit completo de juntas para motor Honda CG 150. Incluye juntas de culata, base y tapa.',
     'NUEVO', 'https://picsum.photos/seed/juntas-cg/800/600', 1),

    ('Valvulas de admision y escape Yamaha FZ 25', 'valvulas-resortes', 'Yamaha', 'FZ 25',
     ['Yamaha FZ 25','Yamaha FZ-S'],
     4200, 'Par de valvulas (admision + escape) para Yamaha FZ 25. Fabricacion italiana.',
     'NUEVO', 'https://picsum.photos/seed/valvulas-fz/800/600', 0),

    ('Ciguenal completo Honda Wave 110', 'ciguenal-biela', 'Honda', 'Wave 110',
     ['Honda Wave 110','Honda Biz 125'],
     18500, 'Ciguenal completo con biela para Honda Wave 110. Balanceado de fabrica.',
     'NUEVO', 'https://picsum.photos/seed/ciguenal-wave/800/600', 1),

    ('Bobina de encendido Motomel CG 150', 'bobinas-ignicion', 'Motomel', 'CG 150',
     ['Motomel CG 150','Motomel Vx 150'],
     3200, 'Bobina de encendido de alta potencia para Motomel CG 150. Compatible con CG 200.',
     'NUEVO', 'https://picsum.photos/seed/bobina-motomel/800/600', 0),

    # --- TRANSMISION ---
    ('Kit de transmision Honda Wave 110 (cadena+pinon+corona)', 'cadenas-kits', 'Honda', 'Wave 110',
     ['Honda Wave 110','Honda Biz 125'],
     4500, 'Kit de transmision completo para Honda Wave 110. Cadena 420x98, pinon 14T, corona 36T. Duracion prolongada.',
     'NUEVO', 'https://picsum.photos/seed/kit-trans-wave/800/600', 1),

    ('Cadena 428H x 120 eslabones reforzada', 'cadenas-kits', None, None,
     ['Universal 428H'],
     2800, 'Cadena 428H de 120 eslabones con eslabones reforzados. Compatible con modelos que usen cadena 428.',
     'NUEVO', 'https://picsum.photos/seed/cadena-428/800/600', 0),

    ('Pinon 14T Honda Titan 150', 'pinones-coronas', 'Honda', 'Titan 150',
     ['Honda Titan 150','Honda CG 150'],
     1200, 'Pinon delantero 14 dientes para Honda Titan 150. Acero templado, alta duracion.',
     'NUEVO', 'https://picsum.photos/seed/pinon-titan/800/600', 0),

    ('Corona 41T Yamaha YBR 125', 'pinones-coronas', 'Yamaha', 'YBR 125',
     ['Yamaha YBR 125','Yamaha XTZ 125'],
     2100, 'Corona trasera 41 dientes para Yamaha YBR 125 y XTZ 125. Fabricacion nacional.',
     'NUEVO', 'https://picsum.photos/seed/corona-ybr/800/600', 0),

    ('Kit de embrague completo Zanella ZB 110', 'embrague', 'Zanella', 'ZB 110',
     ['Zanella ZB 110','Zanella Due 150'],
     3800, 'Kit de embrague con platos y discos para Zanella ZB 110. Incluye resortes de embrague.',
     'NUEVO', 'https://picsum.photos/seed/embrague-zanella/800/600', 0),

    ('Disco de embrague Honda CB 190R', 'embrague', 'Honda', 'CB 190R',
     ['Honda CB 190R','Honda CB 250F'],
     2400, 'Disco de embrague para Honda CB 190R. Friccion optima para conduccion urbana y ruta.',
     'NUEVO', 'https://picsum.photos/seed/disco-embrague/800/600', 0),

    # --- FRENOS ---
    ('Pastillas de freno delantero Honda CB 190R', 'pastillas-freno', 'Honda', 'CB 190R',
     ['Honda CB 190R','Honda CB 250F'],
     2200, 'Pastillas de freno delantero semi-metalicas para Honda CB 190R. Alta temperatura de trabajo.',
     'NUEVO', 'https://picsum.photos/seed/pastillas-cb190/800/600', 1),

    ('Zapatas de freno trasero Motomel S2', 'zapatas-freno', 'Motomel', 'CG 150 S2',
     ['Motomel CG 150 S2','Motomel Vx 150'],
     850, 'Zapatas de freno trasero para Motomel S2. Material de alta friccion y durabilidad.',
     'NUEVO', 'https://picsum.photos/seed/zapatas-motomel/800/600', 0),

    ('Disco de freno 220mm Honda Wave 110', 'discos-freno', 'Honda', 'Wave 110',
     ['Honda Wave 110','Honda Biz 125'],
     3600, 'Disco de freno delantero 220mm para Honda Wave 110. Acero inoxidable, resistente a la corrosion.',
     'NUEVO', 'https://picsum.photos/seed/disco-freno-wave/800/600', 0),

    ('Cable de freno trasero Yamaha YBR 125', 'cables-freno', 'Yamaha', 'YBR 125',
     ['Yamaha YBR 125','Yamaha Crypton 110'],
     650, 'Cable de freno trasero para Yamaha YBR 125. Longitud 135cm. Funda de alta durabilidad.',
     'NUEVO', 'https://picsum.photos/seed/cable-freno/800/600', 0),

    ('Bomba de freno delantera Kawasaki Ninja 400', 'bombas-freno', 'Kawasaki', 'Ninja 400',
     ['Kawasaki Ninja 400','Kawasaki Z400'],
     4200, 'Bomba de freno delantera original para Kawasaki Ninja 400. Con deposito integrado.',
     'NUEVO', 'https://picsum.photos/seed/bomba-ninja/800/600', 0),

    # --- SUSPENSION ---
    ('Amortiguadores traseros Yamaha YBR 125 (par)', 'amortiguadores', 'Yamaha', 'YBR 125',
     ['Yamaha YBR 125','Yamaha Crypton 110'],
     7200, 'Par de amortiguadores traseros para Yamaha YBR 125. Regulables en precarga. Alta absorcion.',
     'NUEVO', 'https://picsum.photos/seed/amortiguadores-ybr/800/600', 1),

    ('Horquilla delantera completa Honda Titan 150', 'horquillas', 'Honda', 'Titan 150',
     ['Honda Titan 150','Honda CG 150'],
     9500, 'Horquilla delantera completa con tubos y buje para Honda Titan 150. Lista para instalar.',
     'NUEVO', 'https://picsum.photos/seed/horquilla-titan/800/600', 0),

    ('Buje trasero Honda Wave 110', 'bujes-rodamientos', 'Honda', 'Wave 110',
     ['Honda Wave 110'],
     1800, 'Buje trasero completo con rodamientos para Honda Wave 110. Incluye sello de aceite.',
     'NUEVO', 'https://picsum.photos/seed/buje-wave/800/600', 0),

    ('Resortes amortiguador Honda CG (par)', 'resortes', 'Honda', 'CG 150',
     ['Honda CG 150','Honda Titan 150'],
     1200, 'Par de resortes para amortiguadores Honda CG. Dureza media-alta para carga con pasajero.',
     'NUEVO', 'https://picsum.photos/seed/resortes-cg/800/600', 0),

    # --- ELECTRICO ---
    ('Bateria 12V 5Ah sellada (todas las marcas)', 'baterias', None, None,
     ['Universal 12V'],
     8900, 'Bateria sellada libre de mantenimiento 12V 5Ah. Compatible con la mayoria de motos 125-200cc.',
     'NUEVO', 'https://picsum.photos/seed/bateria-moto/800/600', 1),

    ('CDI Honda Wave 110 original', 'cdi-reguladores', 'Honda', 'Wave 110',
     ['Honda Wave 110','Honda Biz 125'],
     2800, 'Modulo CDI original para Honda Wave 110. Ignicion digital. Compatible con Biz 125.',
     'NUEVO', 'https://picsum.photos/seed/cdi-wave/800/600', 0),

    ('Regulador rectificador Yamaha YBR 125', 'cdi-reguladores', 'Yamaha', 'YBR 125',
     ['Yamaha YBR 125','Yamaha XTZ 125'],
     1950, 'Regulador-rectificador para Yamaha YBR 125 y XTZ 125. Control de carga de bateria.',
     'NUEVO', 'https://picsum.photos/seed/regulador-ybr/800/600', 0),

    ('Faro LED delantero H4 35W universal', 'luces-faros', None, None,
     ['Universal H4'],
     3400, 'Faro LED H4 35W de alta potencia. Luz blanca 6000K. Instalacion plug-and-play.',
     'NUEVO', 'https://picsum.photos/seed/faro-led/800/600', 1),

    ('Velocimetro digital LCD universal 12V', 'instrumentos', None, None,
     ['Universal'],
     4800, 'Velocimetro digital LCD con odometro, cuentakilometros parcial y reloj. Impermeable.',
     'NUEVO', 'https://picsum.photos/seed/velocimetro/800/600', 0),

    ('Bobina de alto voltaje Honda Biz 125', 'bobinas-ignicion', 'Honda', 'Biz 125',
     ['Honda Biz 125','Honda Wave 110'],
     2100, 'Bobina de alto voltaje para Honda Biz 125. Chispa potente para mejor arranque.',
     'NUEVO', 'https://picsum.photos/seed/bobina-biz/800/600', 0),

    ('Luz de giro LED Zanella ZB (par)', 'luces-faros', 'Zanella', 'ZB 110',
     ['Zanella ZB 110','Zanella ZB 50'],
     380, 'Par de luces de giro LED de repuesto para Zanella ZB. Facil instalacion.',
     'NUEVO', 'https://picsum.photos/seed/luces-zanella/800/600', 0),

    # --- CARBURACION ---
    ('Carburador completo Honda Wave 110', 'carburadores', 'Honda', 'Wave 110',
     ['Honda Wave 110','Honda Biz 110'],
     5800, 'Carburador completo para Honda Wave 110. Con valvula de mariposa y surtidor de chorro.',
     'NUEVO', 'https://picsum.photos/seed/carb-wave/800/600', 1),

    ('Carburador Yamaha YBR 125 con regulacion', 'carburadores', 'Yamaha', 'YBR 125',
     ['Yamaha YBR 125'],
     6200, 'Carburador para Yamaha YBR 125 con regulacion de mezcla. Mayor eficiencia de combustible.',
     'NUEVO', 'https://picsum.photos/seed/carb-ybr/800/600', 0),

    ('Filtro de aire Honda CB 190R original', 'filtros-aire', 'Honda', 'CB 190R',
     ['Honda CB 190R'],
     1200, 'Filtro de aire original OEM para Honda CB 190R. Cambio cada 4000km recomendado.',
     'NUEVO', 'https://picsum.photos/seed/filtro-aire-cb/800/600', 0),

    ('Bujias NGK CR7HSA pack x4', 'bujias', None, 'CR7HSA',
     ['Honda Wave','Honda Biz','Zanella ZB','Motomel CG'],
     2800, 'Pack x4 bujias NGK CR7HSA. La bujia mas usada en motos 110-150cc. Arranque facil.',
     'NUEVO', 'https://picsum.photos/seed/bujias-ngk/800/600', 1),

    ('Cable de acelerador Motomel CG 150', 'cables-acelerador', 'Motomel', 'CG 150',
     ['Motomel CG 150','Motomel CG 200'],
     480, 'Cable de acelerador para Motomel CG 150. Longitud 120cm. Funda de proteccion incluida.',
     'NUEVO', 'https://picsum.photos/seed/cable-acelerador/800/600', 0),

    # --- CARROCERIA ---
    ('Guardabarro delantero Yamaha FZ 25', 'guardabarros', 'Yamaha', 'FZ 25',
     ['Yamaha FZ 25'],
     2100, 'Guardabarro delantero de ABS para Yamaha FZ 25. Color negro. Listo para pintar.',
     'NUEVO', 'https://picsum.photos/seed/guardabarro-fz/800/600', 0),

    ('Tanque de combustible Honda Wave (replica)', 'tanques', 'Honda', 'Wave 110',
     ['Honda Wave 110'],
     12000, 'Tanque de combustible replica para Honda Wave 110. Capacidad 3.7L. Sin grifo incluido.',
     'NUEVO', 'https://picsum.photos/seed/tanque-wave/800/600', 0),

    ('Asiento tapizado Honda Titan 150', 'asientos', 'Honda', 'Titan 150',
     ['Honda Titan 150','Honda CG 150'],
     3800, 'Asiento completo con tapizado de alta resistencia para Honda Titan 150. Impermeable.',
     'NUEVO', 'https://picsum.photos/seed/asiento-titan/800/600', 0),

    ('Manubrio racing aluminio CNC universal', 'manubrios', None, None,
     ['Universal 22mm'],
     1600, 'Manubrio deportivo de aluminio CNC 22mm. Diametro universal. Varios colores disponibles.',
     'NUEVO', 'https://picsum.photos/seed/manubrio-racing/800/600', 1),

    ('Espejo retrovisor izquierdo Zanella ZB', 'espejos', 'Zanella', 'ZB 110',
     ['Zanella ZB 110','Zanella ZTT 200'],
     420, 'Espejo retrovisor izquierdo para Zanella ZB. Cristal convexo, visibilidad amplia.',
     'NUEVO', 'https://picsum.photos/seed/espejo-zanella/800/600', 0),

    ('Carenado lateral Honda PCX 150', 'carenados', 'Honda', 'PCX 150',
     ['Honda PCX 150'],
     5200, 'Carenado lateral derecho para Honda PCX 150. ABS, negro. Compatible con 2019-2023.',
     'NUEVO', 'https://picsum.photos/seed/carenado-pcx/800/600', 0),

    # --- ESCAPE ---
    ('Escape sport Yamaha YBR 125 (replica Akrapovic)', 'tubos-escape', 'Yamaha', 'YBR 125',
     ['Yamaha YBR 125','Yamaha Crypton 110'],
     8900, 'Escape deportivo estilo Akrapovic para Yamaha YBR 125. Acero inoxidable, sonido deportivo.',
     'NUEVO', 'https://picsum.photos/seed/escape-ybr/800/600', 1),

    ('Silenciador racing aluminio universal', 'silenciadores', None, None,
     ['Universal'],
     6400, 'Silenciador deportivo de aluminio. Conector 38mm universal. Diseño racing con protector.',
     'NUEVO', 'https://picsum.photos/seed/silenciador-racing/800/600', 0),

    ('Colector de escape Honda CB 190R', 'colectores', 'Honda', 'CB 190R',
     ['Honda CB 190R','Honda CB 250F'],
     4200, 'Colector de escape en acero inoxidable para Honda CB 190R. Mejor flujo de gases.',
     'NUEVO', 'https://picsum.photos/seed/colector-cb190/800/600', 0),

    # --- NEUMATICOS ---
    ('Cubierta 80/100-14 Pirelli Sport Demon', 'cubiertas', 'Pirelli', 'Sport Demon',
     ['Universal 80/100-14'],
     18500, 'Cubierta Pirelli Sport Demon 80/100-14 para uso en asfalto. Alta adherencia. Trasero.',
     'NUEVO', 'https://picsum.photos/seed/cubierta-pirelli/800/600', 1),

    ('Cubierta 110/70-17 Michelin Pilot Street', 'cubiertas', 'Michelin', 'Pilot Street',
     ['Universal 110/70-17'],
     22000, 'Cubierta Michelin Pilot Street 110/70-17. Excelente performance en mojado y seco.',
     'NUEVO', 'https://picsum.photos/seed/cubierta-michelin/800/600', 1),

    ('Camara de aire 90/90-18 reforzada', 'camaras', None, None,
     ['Universal 90/90-18'],
     1800, 'Camara de aire reforzada 90/90-18 con valvula TR4 metalica. Alta resistencia a pinchazos.',
     'NUEVO', 'https://picsum.photos/seed/camara-aire/800/600', 0),

    ('Llanta delantera 17" aluminio Honda CB 190R', 'llantas', 'Honda', 'CB 190R',
     ['Honda CB 190R'],
     5600, 'Llanta delantera 17 pulgadas de aluminio para Honda CB 190R. Peso reducido, alta resistencia.',
     'NUEVO', 'https://picsum.photos/seed/llanta-cb190/800/600', 0),

    # --- INDUMENTARIA ---
    ('Casco integral AGV K1 talle M', 'cascos', 'AGV', 'K1',
     ['Universal'],
     45000, 'Casco integral AGV K1. Certificacion ECE 22.06. Ventilacion activa. Talle M (57-58cm).',
     'NUEVO', 'https://picsum.photos/seed/casco-agv/800/600', 1),

    ('Casco jet LS2 Copter Negro Brillante', 'cascos', 'LS2', 'Copter',
     ['Universal'],
     28000, 'Casco jet LS2 Copter con visor solar integrado. Certificacion DOT. Varios talles.',
     'NUEVO', 'https://picsum.photos/seed/casco-ls2/800/600', 1),

    ('Guantes de cuero moto talle L', 'guantes', None, None,
     ['Universal'],
     8500, 'Guantes de cuero vacuno para moto. Proteccion en nudillos y palma. Talle L.',
     'NUEVO', 'https://picsum.photos/seed/guantes-moto/800/600', 0),

    ('Campera moto impermeabilizada con protecciones', 'camperas-pantalones', None, None,
     ['Universal'],
     32000, 'Campera moto impermeable con protecciones en hombros, codos y espalda. Talle XL.',
     'NUEVO', 'https://picsum.photos/seed/campera-moto/800/600', 0),

    ('Botas moto cortas cuero talle 43', 'botas', None, None,
     ['Universal'],
     18000, 'Botas cortas de cuero para moto. Proteccion lateral y tobillo. Suela antideslizante. Talle 43.',
     'NUEVO', 'https://picsum.photos/seed/botas-moto/800/600', 0),

    # Extra products for variety
    ('Aceite de motor 4T 10W40 mineral 1L', 'filtros-aceite', None, None,
     ['Universal 4T'],
     2800, 'Aceite mineral 4 tiempos 10W40 para motos. 1 litro. Apto para motores Honda, Yamaha, Zanella.',
     'NUEVO', 'https://picsum.photos/seed/aceite-4t/800/600', 0),

    ('Kit tensor de cadena Honda Wave 110', 'cadenas-kits', 'Honda', 'Wave 110',
     ['Honda Wave 110','Honda Biz 125'],
     680, 'Tensor automatico de cadena para Honda Wave 110. Incluye tornillo y tuerca de ajuste.',
     'NUEVO', 'https://picsum.photos/seed/tensor-wave/800/600', 0),

    ('Freno de mano universal cromo moto', 'cables-freno', None, None,
     ['Universal 22mm'],
     1200, 'Palanca de freno de mano en cromo para manubrio 22mm. Universal para motos tipo trabajo.',
     'NUEVO', 'https://picsum.photos/seed/freno-mano/800/600', 0),

    ('Llave de combustible Honda CG 150', 'tanques', 'Honda', 'CG 150',
     ['Honda CG 150','Honda Titan 150'],
     950, 'Grifo de combustible con reserva para Honda CG 150. Incluye filtro y junta.',
     'NUEVO', 'https://picsum.photos/seed/llave-combustible/800/600', 0),

    ('Kit de bujes delanteros Yamaha YBR 125', 'bujes-rodamientos', 'Yamaha', 'YBR 125',
     ['Yamaha YBR 125'],
     1600, 'Kit de rodamientos delanteros para Yamaha YBR 125. Incluye 2 rodamientos + sello.',
     'NUEVO', 'https://picsum.photos/seed/bujes-ybr/800/600', 0),

    ('Manoplas de goma antideslizante universal par', 'manubrios', None, None,
     ['Universal 22mm'],
     480, 'Par de manoplas de goma para manubrio 22mm. Textura antideslizante. Varios colores.',
     'NUEVO', 'https://picsum.photos/seed/manoplas/800/600', 0),
]

REVIEW_COMMENTS = [
    'Excelente producto, llego en tiempo y forma. Muy buena calidad.',
    'Lo instale sin problemas, funciona perfecto. Recomendado 100%.',
    'Buen repuesto, precio justo. El vendedor muy atento.',
    'Calidad original a buen precio. Volveria a comprar.',
    'Rapido envio y bien embalado. El producto es tal cual la descripcion.',
    'Me salvo la moto! Muy buen repuesto, dura mas que el original.',
    'Muy buena atencion del vendedor. El repuesto es de primera calidad.',
    'Llegó antes de lo esperado. Funciona perfecto en mi moto.',
]

def img(seed): return f"https://loremflickr.com/800/600/motorcycle,parts?lock={abs(hash(seed)) % 900 + 1}"

# Category → loremflickr keywords for relevant images
CAT_KEYWORDS = {
    'pistones-cilindros': 'piston,engine,cylinder',
    'valvulas-resortes':  'engine,valve,motor',
    'juntas-motor':       'gasket,engine,seal',
    'filtros-aceite':     'oil,filter,engine',
    'ciguenal-biela':     'crankshaft,engine,motor',
    'tapas-carter':       'engine,oil,carter',
    'cadenas-kits':       'motorcycle,chain,sprocket',
    'pinones-coronas':    'sprocket,chain,drive',
    'embrague':           'clutch,disc,motorcycle',
    'caja-cambios':       'gearbox,transmission,gear',
    'pastillas-freno':    'brake,pad,disc',
    'zapatas-freno':      'brake,drum,shoe',
    'discos-freno':       'brake,disc,rotor',
    'cables-freno':       'brake,cable,wire',
    'bombas-freno':       'brake,caliper,hydraulic',
    'amortiguadores':     'shock,absorber,suspension',
    'horquillas':         'fork,suspension,motorcycle',
    'bujes-rodamientos':  'bearing,wheel,hub',
    'resortes':           'spring,suspension,coil',
    'baterias':           'battery,motorcycle,12v',
    'cdi-reguladores':    'ignition,electrical,motorcycle',
    'bobinas-ignicion':   'ignition,coil,spark',
    'luces-faros':        'led,light,headlight',
    'instrumentos':       'speedometer,gauge,dashboard',
    'carburadores':       'carburetor,motorcycle,fuel',
    'filtros-aire':       'air,filter,intake',
    'bujias':             'spark,plug,ignition',
    'cables-acelerador':  'throttle,cable,motorcycle',
    'guardabarros':       'fender,mudguard,plastic',
    'tanques':            'fuel,tank,motorcycle',
    'asientos':           'seat,saddle,motorcycle',
    'manubrios':          'handlebar,grip,motorcycle',
    'espejos':            'mirror,motorcycle,rearview',
    'carenados':          'fairing,bodywork,motorcycle',
    'tubos-escape':       'exhaust,pipe,motorcycle',
    'silenciadores':      'muffler,silencer,exhaust',
    'colectores':         'exhaust,manifold,header',
    'cubiertas':          'tire,tyre,motorcycle',
    'camaras':            'tire,tube,rubber',
    'llantas':            'wheel,rim,alloy',
    'cascos':             'helmet,motorcycle,safety',
    'guantes':            'gloves,motorcycle,leather',
    'camperas-pantalones':'jacket,motorcycle,riding',
    'botas':              'boots,motorcycle,leather',
    'accesorios-seguridad':'motorcycle,safety,protection',
    # parent slugs fallback
    'motor':      'engine,motorcycle,motor',
    'transmision':'motorcycle,chain,transmission',
    'frenos':     'brake,disc,motorcycle',
    'suspension': 'suspension,shock,motorcycle',
    'electrico':  'electrical,ignition,motorcycle',
    'carburacion':'carburetor,fuel,motorcycle',
    'carroceria': 'motorcycle,bodywork,plastic',
    'escape':     'exhaust,pipe,motorcycle',
    'neumaticos': 'tire,tyre,motorcycle',
    'indumentaria':'helmet,motorcycle,gear',
}

def cat_img(cat_slug, idx):
    kw = CAT_KEYWORDS.get(cat_slug, 'motorcycle,parts,repair')
    return f"https://loremflickr.com/800/600/{kw}?lock={idx + 1}"


# ─── PRODUCTOS REALES DE TIENDAS MDP ─────────────────────────────────────────
# Formato: (store_idx, cat_slug, title, brand, model, compat_list, price, desc, condition, featured)
REAL_STORE_PRODUCTS = [
    # ── MDR Motos (store_idx=0) — datos reales del sitio repuestosmdrmotos.com.ar ──
    (0, 'cubiertas',
     'Juego Cubiertas Tacos Camel Bridge Honda XR 190/150/125',
     'Camel Bridge', 'XR 190',
     ['Honda XR 190', 'Honda XR 150', 'Honda XR 125'],
     135000,
     'Juego de cubiertas Tacos Camel Bridge para Honda XR 190/150/125. Par delantero y trasero. Excelente traccion en campo y ruta. Stock permanente.',
     'NUEVO', 1),

    (0, 'cubiertas',
     'Juego Cubiertas Camel Bridge Honda Tornado 250 / XRE 300 / XTZ 250',
     'Camel Bridge', 'Tornado 250',
     ['Honda Tornado 250', 'Honda XRE 300', 'Yamaha XTZ 250'],
     135000,
     'Juego cubiertas Tacos Camel Bridge para Tornado 250, XRE 300 y XTZ 250. Alto rendimiento off-road. Envios a todo el pais desde MDR Motos MDP.',
     'NUEVO', 1),

    (0, 'cubiertas',
     'Cubierta Trasera 2.75-14 Motos 110cc Universal',
     'Varios', None,
     ['Honda Wave 110', 'Zanella ZB 110', 'Motomel CG 110', 'Corven Energy 110'],
     27000,
     'Cubierta trasera medida 2.75-14. Compatible con gran variedad de motos 110cc. Excelente agarre, larga duracion.',
     'NUEVO', 0),

    (0, 'pinones-coronas',
     'Cubre Pinon Honda XR 300L Original',
     'Honda', 'XR 300L',
     ['Honda XR 300L'],
     16000,
     'Cubre pinon original para Honda XR 300L. Protege el pinon delantero del barro, cadena y piedras en terreno off-road.',
     'NUEVO', 0),

    (0, 'carroceria',
     'Kit de Proteccion Honda XR190 — Guardabarro y Laterales',
     'Honda', 'XR 190',
     ['Honda XR 190'],
     114000,
     'Kit de proteccion completo para Honda XR 190. Incluye guardabarro delantero, trasero y protectores laterales del motor. Solo en MDR Motos.',
     'NUEVO', 1),

    (0, 'tapas-carter',
     'Set Tapas Motor Honda XR 300L',
     'Honda', 'XR 300L',
     ['Honda XR 300L'],
     24500,
     'Set de tapas del motor para Honda XR 300L. Material de alta resistencia. Incluye juntas. Stock disponible en MDR Motos MDP.',
     'NUEVO', 0),

    # ── Emiliozzi Motos (store_idx=1) — desde 2002, 20% descuento web ──────────
    (1, 'filtros-aceite',
     'Filtro de Aceite Honda XR 150L OEM — 20% Descuento Web',
     'Honda', 'XR 150L',
     ['Honda XR 150L', 'Honda CB 150R', 'Honda CG 150'],
     2400,
     'Filtro de aceite original OEM para Honda XR 150L. Cambio recomendado cada 3000km. 20% descuento comprando online en Emiliozzi.',
     'NUEVO', 0),

    (1, 'pastillas-freno',
     'Pastillas Freno EBC Delantera Honda CB 190R',
     'EBC', 'CB 190R',
     ['Honda CB 190R', 'Honda CB 250F'],
     4800,
     'Pastillas de freno EBC para Honda CB 190R delantera. Organicas, alta friccion para uso urbano y ruta. Emiliozzi distribuidor EBC desde 2002.',
     'NUEVO', 1),

    (1, 'amortiguadores',
     'Par Amortiguadores Yamaha XTZ 125 Traseros',
     'Yamaha', 'XTZ 125',
     ['Yamaha XTZ 125', 'Yamaha YBR 125'],
     12000,
     'Par de amortiguadores traseros de alta calidad para Yamaha XTZ 125. Regulables en precarga. Precio con 20% descuento web en Emiliozzi.',
     'NUEVO', 0),

    (1, 'filtros-aceite',
     'Aceite Motor Motul 3000 4T 10W40 — 1 Litro',
     'Motul', None,
     ['Universal 4T'],
     3200,
     'Aceite motor 4 tiempos Motul 3000 10W40 mineral. 1 litro. Valido para Honda, Yamaha, Zanella y todas las marcas. Distribuidor oficial Emiliozzi MDP.',
     'NUEVO', 0),

    (1, 'filtros-aire',
     'Filtro Aire Original Honda CG 150 / Titan 150',
     'Honda', 'CG 150',
     ['Honda CG 150', 'Honda Titan 150', 'Honda Biz 125'],
     1440,
     'Filtro de aire original Honda para CG 150, Titan 150 y Biz 125. Papel de alta filtracion. Precio incluye 20% descuento web de Emiliozzi.',
     'NUEVO', 0),

    (1, 'cubiertas',
     'Cubierta Pirelli MT 75 140/70-17 — Distribuidor Oficial',
     'Pirelli', 'MT 75',
     ['Universal 140/70-17'],
     24000,
     'Cubierta Pirelli MT 75 140/70-17 para uso mixto asfalto/tierra. Emiliozzi es distribuidor autorizado Pirelli en Mar del Plata.',
     'NUEVO', 1),

    (1, 'baterias',
     'Bateria YTZ7S Sellada Honda CB 190R / CG 150',
     'Honda', 'CB 190R',
     ['Honda CB 190R', 'Honda CG 150', 'Honda Titan 150'],
     13600,
     'Bateria YTZ7S sellada libre de mantenimiento. Compatible Honda CB 190R, CG 150, Titan 150. 20% off comprando online en Emiliozzi Motos.',
     'NUEVO', 0),

    (1, 'embrague',
     'Kit Embrague Completo Yamaha YBR 125',
     'Yamaha', 'YBR 125',
     ['Yamaha YBR 125', 'Yamaha XTZ 125', 'Yamaha Crypton 110'],
     9600,
     'Kit completo de embrague para Yamaha YBR 125. Platos, discos y resortes de repuesto. 20% descuento web exclusivo de Emiliozzi Motos.',
     'NUEVO', 0),

    # ── LC Motoparts (store_idx=2) — dealer oficial Honda/Kawasaki/Yamaha/KTM ──
    (2, 'juntas-motor',
     'Kit Juntas Motor Honda CB 250F Original OEM',
     'Honda', 'CB 250F',
     ['Honda CB 250F', 'Honda CB 190R'],
     18500,
     'Kit completo de juntas de motor original Honda para CB 250F. Pieza OEM genuina. Solo disponible en dealers oficiales como LC Motoparts MDP.',
     'NUEVO', 1),

    (2, 'cdi-reguladores',
     'CDI Original Honda XR 150L — Ignicion Digital',
     'Honda', 'XR 150L',
     ['Honda XR 150L', 'Honda CB 150R'],
     8200,
     'Modulo CDI original Honda para XR 150L. Ignicion digital. Garantia de fabrica. Exclusivo en dealers oficiales Honda, solo en LC Motoparts.',
     'NUEVO', 0),

    (2, 'cadenas-kits',
     'Cadena DID 428 x 110 Honda CB 190R Original',
     'DID', 'CB 190R',
     ['Honda CB 190R', 'Honda CB 150R', 'Honda CG 150'],
     6400,
     'Cadena original DID 428 x 110 para Honda CB 190R. Alta resistencia y larga vida util. LC Motoparts dealer oficial Honda Mar del Plata.',
     'NUEVO', 0),

    (2, 'baterias',
     'Bateria Original Honda Wave 110 — 12V 3Ah',
     'Honda', 'Wave 110',
     ['Honda Wave 110', 'Honda Biz 125'],
     9800,
     'Bateria original de fabrica Honda Wave 110. 12V 3Ah. Garantia 6 meses. Pieza genuina disponible en LC Motoparts, dealer oficial MDP.',
     'NUEVO', 0),

    (2, 'amortiguadores',
     'Amortiguador Trasero Original Kawasaki Z400 / Ninja 400',
     'Kawasaki', 'Z400',
     ['Kawasaki Z400', 'Kawasaki Ninja 400'],
     28000,
     'Amortiguador trasero original Kawasaki para Z400 y Ninja 400. Pieza OEM con garantia. LC Motoparts dealer oficial Kawasaki en Mar del Plata.',
     'NUEVO', 1),

    (2, 'pastillas-freno',
     'Pastillas Freno Originales Honda CB 150R / CG 150',
     'Honda', 'CB 150R',
     ['Honda CB 150R', 'Honda CG 150', 'Honda Titan 150'],
     3600,
     'Pastillas de freno originales Honda para CB 150R y CG 150. Calidad OEM. Stock permanente garantizado en LC Motoparts MDP.',
     'NUEVO', 0),

    (2, 'electrico',
     'Llave de Contacto Completa Honda CG 150 Original',
     'Honda', 'CG 150',
     ['Honda CG 150', 'Honda Titan 150', 'Honda Biz 125'],
     4200,
     'Llave de contacto completa original Honda para CG 150, Titan 150 y Biz 125. Incluye 2 llaves. Pieza genuina Honda, solo en dealers oficiales.',
     'NUEVO', 0),
]


def init_db():
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.commit()
    migrate_schema(conn)

    if conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0] > 0:
        _seed_verticals_if_missing(conn)
        conn.close()
        return

    # ── CATEGORIAS ────────────────────────────────────────────────────────────
    cat_map = {}
    for pos, (name, slug, icon, desc, subs) in enumerate(CATEGORIES):
        conn.execute(
            "INSERT INTO categories(name,slug,icon,description,position,image_url) VALUES(?,?,?,?,?,?)",
            (name, slug, icon, desc, pos, img(slug)))
        parent_id = conn.execute("SELECT id FROM categories WHERE slug=?", (slug,)).fetchone()[0]
        cat_map[slug] = parent_id
        for sub_name, sub_slug in subs:
            conn.execute(
                "INSERT INTO categories(name,slug,icon,parent_id,position) VALUES(?,?,?,?,0)",
                (sub_name, sub_slug, icon, parent_id))
            cat_map[sub_slug] = conn.execute("SELECT id FROM categories WHERE slug=?", (sub_slug,)).fetchone()[0]
    conn.commit()

    # ── MARKET PRICES (ticker) ─────────────────────────────────────────────────
    for name, price_ars, change_pct, cat in MARKET_PRICES_DATA:
        conn.execute("INSERT INTO market_prices(name,price_ars,change_pct,category) VALUES(?,?,?,?)",
                     (name, price_ars, change_pct, cat))
    conn.commit()

    # ── VENDEDORES (tiendas de MDP) ───────────────────────────────────────────
    pw = bcrypt.hashpw(b'Demo1234!', bcrypt.gensalt()).decode()
    seller_ids = []

    for i, store in enumerate(STORES_MDQ):
        email = f"tienda{i+1}@repuestos.com.ar"
        conn.execute(
            "INSERT INTO users(name,email,password,role,phone,province) VALUES(?,?,?,?,?,?)",
            (store['name'], email, pw, 'VENDEDOR', store['phone'], 'Buenos Aires'))
        uid = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()[0]

        rating = round(random.uniform(4.1, 5.0), 1)
        reviews = random.randint(20, 180)
        since = (datetime.now() - timedelta(days=random.randint(365, 2000))).strftime('%Y-%m-%d')

        conn.execute("""
            INSERT INTO seller_profiles(user_id,company_name,description,phone,whatsapp,
                province,city,address,lat,lng,verified,rating,total_reviews,
                response_rate,response_time,member_since,store_hours,brands_json)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (uid, store['name'], store['description'], store['phone'], store['whatsapp'],
             'Buenos Aires', 'Mar del Plata', store['address'],
             store['lat'], store['lng'], store['verified'],
             rating, reviews,
             random.randint(88, 100), 'Menos de 2 hs', since,
             store['hours'], json.dumps(store['brands'])))
        seller_ids.append(uid)

    # Demo buyer
    conn.execute("INSERT INTO users(name,email,password,role,province) VALUES(?,?,?,?,?)",
                 ('Comprador Demo', 'comprador@repuestos.com.ar', pw, 'COMPRADOR', 'Buenos Aires'))
    conn.commit()

    # ── PRODUCTOS ─────────────────────────────────────────────────────────────
    for i, (title, cat_slug, brand, model, compat, price, desc, condition, _img_unused, featured) in enumerate(PRODUCTS_DATA):
        seller_id = random.choice(seller_ids)
        cat_id = cat_map.get(cat_slug, 1)
        slug = make_slug(title)
        price_usd = round(price / USD_RATE, 2)
        compat_json = json.dumps(compat)
        tags = json.dumps([brand or '', model or '', cat_slug])
        part_num = f"RP-{random.randint(10000,99999)}"
        views = random.randint(50, 2500)
        leads = random.randint(2, 80)
        img_url = cat_img(cat_slug, i)
        conn.execute("""
            INSERT INTO products(seller_id,category_id,title,slug,short_desc,description,
                price,price_usd,condition,brand,model,compatible_models,stock,
                status,province,city,views,leads_count,featured,part_number,
                image_url,images,tags)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (seller_id, cat_id, title, slug,
             desc[:100] + '...' if len(desc) > 100 else desc, desc,
             price, price_usd, condition, brand, model, compat_json,
             random.randint(3, 50), 'ACTIVO', 'Buenos Aires', 'Mar del Plata',
             views, leads, featured, part_num,
             img_url, json.dumps([img_url]), tags))

    # Extra products to fill catalog
    extra_titles = [
        ('Retenes de horquilla Honda CG 150 (par)', 'horquillas', 'Honda', 'CG 150', ['Honda CG 150'], 1400),
        ('Cadena 420 x 104 Yamaha YBR', 'cadenas-kits', 'Yamaha', 'YBR 125', ['Yamaha YBR 125'], 2200),
        ('Pastillas freno trasero Kawasaki Ninja 400', 'pastillas-freno', 'Kawasaki', 'Ninja 400', ['Kawasaki Ninja 400'], 3100),
        ('Regulador de tension Zanella ZB 110', 'cdi-reguladores', 'Zanella', 'ZB 110', ['Zanella ZB 110'], 1750),
        ('Filtro de aire espuma Motomel S2', 'filtros-aire', 'Motomel', 'CG 150 S2', ['Motomel CG 150'], 680),
        ('Pinon 15T Yamaha FZ 25', 'pinones-coronas', 'Yamaha', 'FZ 25', ['Yamaha FZ 25'], 1450),
        ('Amortiguadores Corven Triax 150 (par)', 'amortiguadores', 'Corven', 'Triax 150', ['Corven Triax 150'], 6800),
        ('Casco abierto Bieffe 3 Sport talle XL', 'cascos', 'Bieffe', '3 Sport', ['Universal'], 18500),
        ('Rodamiento rueda delantera 6301 universal', 'bujes-rodamientos', None, None, ['Universal 6301'], 380),
        ('Cable embrague Zanella ZTT 200', 'embrague', 'Zanella', 'ZTT 200', ['Zanella ZTT 200'], 520),
        ('Cubierta 90/90-18 Fate AR Street II', 'cubiertas', 'Fate', 'AR Street II', ['Universal 90/90-18'], 16800),
        ('Espejo retrovisor derecho Honda CB 190R', 'espejos', 'Honda', 'CB 190R', ['Honda CB 190R'], 890),
        ('Conjunto luz trasera LED universal', 'luces-faros', None, None, ['Universal'], 2600),
        ('Tanque de gasolina Yamaha YBR 125', 'tanques', 'Yamaha', 'YBR 125', ['Yamaha YBR 125'], 14500),
        ('Palanca de freno delantero Motomel CG', 'cables-freno', 'Motomel', 'CG 150', ['Motomel CG 150'], 480),
        ('Punta de eje trasero Honda Wave 110', 'bujes-rodamientos', 'Honda', 'Wave 110', ['Honda Wave 110'], 620),
        ('Escape original Motomel S2 150', 'tubos-escape', 'Motomel', 'CG 150 S2', ['Motomel CG 150 S2'], 6900),
        ('Bateria 12V 7Ah Honda CB 190R', 'baterias', 'Honda', 'CB 190R', ['Honda CB 190R'], 11200),
        ('Cubierta 110/90-17 Pirelli MT 75', 'cubiertas', 'Pirelli', 'MT 75', ['Universal 110/90-17'], 21500),
        ('Guantes anticorte nivel 5 moto', 'guantes', None, None, ['Universal'], 12000),
    ]

    for ei, (title, cat_slug, brand, model, compat, price) in enumerate(extra_titles):
        seller_id = random.choice(seller_ids)
        cat_id = cat_map.get(cat_slug, 1)
        slug = make_slug(title)
        desc = f'{title}. Calidad garantizada. Compatible con modelos: {", ".join(compat)}.'
        eimg = cat_img(cat_slug, ei + 100)
        conn.execute("""
            INSERT INTO products(seller_id,category_id,title,slug,short_desc,description,
                price,price_usd,brand,model,compatible_models,stock,status,
                province,city,views,leads_count,featured,part_number,image_url,images,tags)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (seller_id, cat_id, title, slug, desc[:100], desc,
             price, round(price/USD_RATE, 2), brand, model, json.dumps(compat),
             random.randint(2, 40), 'ACTIVO', 'Buenos Aires', 'Mar del Plata',
             random.randint(10, 800), random.randint(0, 30), 0,
             f"RP-{random.randint(10000,99999)}",
             eimg, json.dumps([eimg]),
             json.dumps([brand or '', cat_slug])))

    conn.commit()

    # ── PRODUCTOS REALES DE TIENDAS MDP ──────────────────────────────────────
    for j, (store_idx, cat_slug, title, brand, model, compat, price, desc, condition, featured) in enumerate(REAL_STORE_PRODUCTS):
        sid = seller_ids[store_idx]
        cat_id = cat_map.get(cat_slug, 1)
        slug = make_slug(title)
        price_usd = round(price / USD_RATE, 2)
        compat_json = json.dumps(compat)
        tags_json = json.dumps([brand or '', model or '', cat_slug])
        part_num = f"RP-{random.randint(10000,99999)}"
        rimg = cat_img(cat_slug, j + 300)
        conn.execute("""
            INSERT INTO products(seller_id,category_id,title,slug,short_desc,description,
                price,price_usd,condition,brand,model,compatible_models,stock,
                status,province,city,views,leads_count,featured,part_number,
                image_url,images,tags)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (sid, cat_id, title, slug,
             desc[:100] + '...' if len(desc) > 100 else desc, desc,
             price, price_usd, condition, brand, model, compat_json,
             random.randint(5, 30), 'ACTIVO', 'Buenos Aires', 'Mar del Plata',
             random.randint(150, 3500), random.randint(5, 120), featured, part_num,
             rimg, json.dumps([rimg]), tags_json))
    conn.commit()

    # ── REVIEWS ───────────────────────────────────────────────────────────────
    buyer_names = ['Carlos M.','Ana P.','Roberto G.','Laura S.','Diego F.',
                   'Marcela V.','Pablo R.','Cecilia T.','Eduardo N.','Silvia K.']
    for sid in seller_ids:
        for _ in range(random.randint(4, 10)):
            conn.execute(
                "INSERT INTO reviews(seller_id,buyer_name,rating,comment,created_at) VALUES(?,?,?,?,?)",
                (sid, random.choice(buyer_names), random.randint(4, 5),
                 random.choice(REVIEW_COMMENTS),
                 (datetime.now() - timedelta(days=random.randint(1,300))).strftime('%Y-%m-%d %H:%M:%S')))

    conn.commit()
    _seed_verticals_if_missing(conn)
    conn.close()
    print("[OK] Base de datos inicializada con datos demo de repuestos de motos MDP")
