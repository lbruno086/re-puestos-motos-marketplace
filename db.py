"""Capa de datos dual-driver: SQLite en local, PostgreSQL en producción (Render).

El resto del código sigue usando la misma API que ya tenía con sqlite3:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM x WHERE id=?", (1,)).fetchall()
    row['col'] / row[0] / dict(row)
    conn.commit(); conn.close()

Si la variable de entorno DATABASE_URL está presente (Render Postgres) usamos
Postgres; si no, SQLite (sin cambios respecto del comportamiento histórico).
Las consultas se escriben con placeholders estilo '?'; acá se traducen a '%s'
para Postgres, y LIKE -> ILIKE para mantener la búsqueda case-insensitive que
SQLite daba por defecto.
"""
import os
import re
import sqlite3

DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()
IS_POSTGRES = bool(DATABASE_URL)

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'repuestos.db')
DB_PATH = os.environ.get('DB_PATH', DEFAULT_DB_PATH)

if IS_POSTGRES:
    import psycopg2
    import psycopg2.extras

    # Render entrega 'postgres://'; psycopg2 espera 'postgresql://'
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = 'postgresql://' + DATABASE_URL[len('postgres://'):]


# ─── Traducción de SQL SQLite → Postgres ─────────────────────────────────────
def _translate_query(sql):
    """Consultas de runtime: '?' -> '%s', LIKE -> ILIKE (case-insensitive)."""
    sql = sql.replace('?', '%s')
    sql = re.sub(r'\bLIKE\b', 'ILIKE', sql)
    return sql


def _translate_ddl(sql):
    """DDL/seed: además del placeholder, mapea construcciones SQLite-only."""
    sql = re.sub(r'INTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT', 'SERIAL PRIMARY KEY',
                 sql, flags=re.IGNORECASE)
    # Las columnas son TEXT; Postgres exige cast explícito de fecha a texto.
    sql = re.sub(r"datetime\('now'\)", "(now()::text)", sql, flags=re.IGNORECASE)
    sql = re.sub(r"date\('now'\)", "(current_date::text)", sql, flags=re.IGNORECASE)
    # PRAGMA no existe en Postgres
    sql = re.sub(r'^\s*PRAGMA[^;]*;', '', sql, flags=re.IGNORECASE | re.MULTILINE)
    return sql


# ─── Wrapper de conexión Postgres con API estilo sqlite3 ─────────────────────
class _PgConnection:
    def __init__(self, dsn):
        self._conn = psycopg2.connect(dsn)

    def execute(self, sql, params=()):
        cur = self._conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(_translate_query(sql), tuple(params))
        return cur  # DictCursor soporta fetchall/fetchone; DictRow soporta row[0], row['c'], dict(row)

    def executescript(self, script):
        """Equivalente a sqlite3.executescript: corre DDL/seed multi-statement."""
        cur = self._conn.cursor()
        cur.execute(_translate_ddl(script))
        cur.close()

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()


def column_exists(conn, table, column):
    if IS_POSTGRES:
        row = conn.execute(
            "SELECT 1 FROM information_schema.columns WHERE table_name=? AND column_name=?",
            (table, column)).fetchone()
        return row is not None
    cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    return column in cols


def add_column_if_missing(conn, table, column, coltype):
    """ALTER TABLE ADD COLUMN es idempotente acá: solo corre si la columna no existe.
    SQLite no soporta ALTER TABLE ADD COLUMN dos veces sobre la misma columna."""
    if not column_exists(conn, table, column):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}")
        conn.commit()


def get_connection():
    if IS_POSTGRES:
        return _PgConnection(DATABASE_URL)
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn
