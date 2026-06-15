# Produccion

## Ruta recomendada

Para demo publica gratuita, Render Free funciona con `render.yaml`, pero su filesystem es efimero. Eso significa que los leads y cambios hechos desde la web pueden perderse en reinicios o redeploys.

Para produccion real con el menor cambio de arquitectura:

1. Usar Render Web Service pago minimo.
2. Agregar Persistent Disk montado en `/var/data`.
3. Definir `DB_PATH=/var/data/repuestos.db`.
4. Mantener `startCommand: python start.py`.

Para escalar mas adelante, migrar SQLite a Postgres.

## Variables

- `PORT`: lo define el hosting.
- `COOKIE_SECRET`: secreto para cookies seguras.
- `DEBUG`: usar `false` en produccion.
- `DB_PATH`: ruta del archivo SQLite. Para disco persistente en Render usar `/var/data/repuestos.db`.
- `LOAD_CSV_ON_START`: `true` carga `data/productos.csv` al iniciar de forma idempotente.
