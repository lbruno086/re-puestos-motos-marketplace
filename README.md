# Re-Puestos MDP

Ecommerce de repuestos de motos para tiendas de Mar del Plata, construido con Tornado, Jinja2 y SQLite.

## Ejecutar local

```bash
pip install -r requirements.txt
python app.py
```

La app queda disponible en:

```text
http://localhost:8889
```

## Despliegue web

Este proyecto necesita un servidor Python. No es compatible con GitHub Pages porque usa Tornado y SQLite.

La opción recomendada es Render:

1. Subir el repositorio a GitHub.
2. Entrar a Render y crear un nuevo **Blueprint** o **Web Service** desde este repositorio.
3. Render detecta `render.yaml`.
4. Deploy.

También funciona en Railway/Heroku con:

```text
web: python app.py
```

## Variables de entorno

- `PORT`: lo define el hosting.
- `COOKIE_SECRET`: secreto para cookies seguras.
- `DEBUG`: usar `false` en producción.
