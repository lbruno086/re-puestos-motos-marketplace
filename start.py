import os

import tornado.ioloop

from app import PORT, make_app
from database import init_db
from load_productos import CSV_PATH, load


def csv_seed_enabled() -> bool:
    return os.environ.get("LOAD_CSV_ON_START", "true").lower() in {"1", "true", "yes"}


if __name__ == "__main__":
    init_db()
    if csv_seed_enabled() and os.path.exists(CSV_PATH):
        load(CSV_PATH)

    app = make_app()
    app.listen(PORT)
    print(f"\n{'=' * 50}")
    print("  Re-Puestos MDP - Repuestos de Motos")
    print(f"{'=' * 50}")
    print(f"  http://localhost:{PORT}")
    print(f"{'=' * 50}")
    print("  Ctrl+C para detener\n")
    tornado.ioloop.IOLoop.current().start()
