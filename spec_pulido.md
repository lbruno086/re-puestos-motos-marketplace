# spec_pulido.md — Re-Puestos MDP como "Agrofy de las motos"

Spec de reconstrucción funcional: replicar ~99% el modelo de marketplace de **Agrofy** (agrofy.com.ar) trasladado al rubro motos, sumando geolocalización, Google Auth e infraestructura de usuario (favoritos/historial/lugares visitados), con la **identidad visual del spec [radar-competencia-diseno-motos.md](radar-competencia-diseno-motos.md)** (rojo/negro racing — NO el verde de Agrofy). Construye sobre el código Tornado/SQLite existente.

---

## 0. Nivel de acceso y honestidad de evidencia

> Disciplina de reverse-engineering: **observado vs inferido**, con confianza.

- **Agrofy** bloqueó el scraping directo (HTTP 403). La caracterización de su modelo proviene de su **Centro de Ayuda**, páginas públicas indexadas y descripciones oficiales → confianza **Media** salvo donde se indique. No se observó el DOM/red en vivo, así que detalles finos de UI/endpoints de Agrofy son **inferidos**.
- **Re-Puestos** (el producto a pulir) sí está 100% observado: esquema `database.py`, handlers `app.py`, plantillas `templates/` → confianza **Alta**. El spec se ancla ahí.
- Donde el spec define comportamiento nuevo, es **diseño objetivo** (no observación), marcado como `[objetivo]`.

---

## 1. Modelo funcional de Agrofy observado (lo que se replica)

| # | Capacidad Agrofy | Evidencia | Confianza | Traslado a motos |
|---|---|---|---|---|
| A | **Marketplace multi-categoría** (maquinaria, insumos, vehículos, repuestos, accesorios, servicios, inmuebles, hacienda…) | Centro de ayuda + listados de categorías | Media | Categorías propias del rubro moto (ver §2) |
| B | **Modelo de "Avisos"** (clasificados): publicar aviso por categoría, packs de avisos sin comisión | Help "Publicar/editar/eliminar avisos", "Packs de avisos" | Media | Selector **Avisos** + venta de **Motos** como avisos clasificados |
| C | **Filtros ricos**: condición (nuevo/usado), marca, potencia, rango de precio | Página categoría + help | Media | condición, marca, modelo, año, cilindrada, precio |
| D | **"Cerca de mí" + distancia exacta** según tu ubicación | Help: *"el filtro 'Cerca de mí' ajusta los resultados a tu ubicación, indicando la distancia exacta"* | **Alta** (texto literal) | **Núcleo del pedido**: geo + distancia (ver §4) |
| E | **Orden**: más relevantes / menor precio / mayor precio | Help filtros | Media | Idéntico + "más cercano", "más nuevo" |
| F | **Tipos de vendedor**: Sucursal/Tienda Online vs particular vs concesionaria | Help "Tienda Online", T&C | Media | **Particulares vs Concesionarias** (filtro en Motos) |
| G | **Publicar**: Login → Publicar → elegir categoría → completar info (título optimizado) | Help publicación | Media | Flujo de publicación por tipo de aviso |
| H | **Mi Cuenta > Mis Publicaciones > Activas → Modificar** | Help editar avisos | Media | Panel vendedor ya existente, ampliado |
| I | **Contacto vendedor / financiación / pagos** en ficha | Perfil de empresa / news | Media | Contacto por **WhatsApp/form** (ya existe); financiación = futuro |
| J | **Cuenta de usuario** (login, gestión) | Help | Media | + Google Auth, favoritos, historial (§5) |

**Conclusión:** Agrofy es un **híbrido ecommerce + clasificados ("avisos") con geolocalización y segmentación por tipo de vendedor**. Re-Puestos ya tiene ~60% (catálogo, ficha, vendedores, leads, mapa de tiendas). El delta para llegar al ~99% es: arquitectura de avisos, geo "cerca de mí", Google Auth, favoritos/historial, y los verticales Motos/Servicios.

---

## 2. Arquitectura de información objetivo `[objetivo]`

Estructura de navegación pedida, segmentada en 4 verticales de primer nivel:

```
Re-Puestos MDP
├── CATÁLOGO (productos de tienda — ecommerce)
│   ├── Repuestos        (motor, frenos, transmisión, eléctrico, suspensión…)
│   └── Accesorios       (cascos, indumentaria, baúles, GPS, candados…)
│
├── AVISOS (clasificados de particulares y comercios)
│   └── (publicaciones sueltas de repuestos/accesorios usados, lotes, etc.)
│
├── MOTOS (venta de unidades — clasificado tipo aviso)
│   ├── filtro: Particulares
│   └── filtro: Concesionarias
│
└── SERVICIOS (talleres, mecánica, gomería, electricidad, grabado, seguros…)
```

- **Catálogo** = lo que hoy existe (`products`), subdividido en dos ramas raíz: **Repuestos** y **Accesorios** (hoy las categorías son todas de repuestos; se agrega la rama Accesorios).
- **Avisos** = nuevo tipo de publicación, más liviano que un producto de tienda (un particular publica sin ser "vendedor verificado").
- **Motos** = avisos cuyo objeto es una moto completa; filtro obligatorio **Particular / Concesionaria**.
- **Servicios** = directorio de prestadores con ficha + ubicación + contacto (no tiene precio/stock; tiene rubro).

Cada vertical comparte el mismo chasis de **listado filtrable + ficha + contacto + geolocalización**.

---

## 3. Requisitos funcionales (RF)

### 3.1 Catálogo (Repuestos / Accesorios) — ya parcialmente implementado
- **RF-1** Listado con grilla densa, filtros (categoría, precio, marca, modelo, condición, tienda) y orden. *Evidence: `CatalogoHandler`, `catalogo.html` — Alta.*
- **RF-2** Sub-segmentación raíz Repuestos vs Accesorios mediante categorías padre. `[objetivo]`
- **RF-3** Ficha de producto con compatibilidad, vendedor sticky, contacto WhatsApp/form. *Evidence: `producto.html` — Alta.*

### 3.2 Avisos `[objetivo]`
- **RF-4** Un usuario logueado (comprador o vendedor) puede publicar un **aviso** (título, categoría, fotos, precio opcional, condición, ubicación, descripción).
- **RF-5** Los avisos se listan en su propio vertical con los mismos filtros + "cerca de mí".
- **RF-6** Moderación mínima: estado `PENDIENTE/ACTIVO/PAUSADO/VENCIDO`; gestión en Mi Cuenta.

### 3.3 Motos `[objetivo]`
- **RF-7** Aviso de moto con campos propios: marca, modelo, año, cilindrada (cc), kilometraje, condición, papeles al día (bool), precio.
- **RF-8** **Filtro Particular / Concesionaria** (deriva de `users.role` / `seller_profiles`): el comprador puede acotar por tipo de vendedor.
- **RF-9** Concesionarias muestran badge verificado + ficha de tienda; particulares muestran contacto directo.

### 3.4 Servicios `[objetivo]`
- **RF-10** Directorio de prestadores (taller, gomería, eléctrica, grabado de autopartes, seguro) con rubro, descripción, ubicación en mapa, horarios y contacto.
- **RF-11** Filtrable por rubro + "cerca de mí".

### 3.5 Geolocalización (núcleo del pedido) `[objetivo]`
- **RF-12** **Al loguearse**, solicitar permiso de ubicación del navegador (Geolocation API). Si se concede, guardar lat/lng del usuario (sesión + opcional perfil); si se deniega, fallback a selección manual de zona/partido.
- **RF-13** **Filtro "Cerca de mí"** en todos los verticales: ordena/filtra por distancia y **muestra la distancia exacta** a cada publicación (réplica directa de Agrofy, Confianza Alta del patrón origen).
- **RF-14** **Cada publicación lleva ubicación en mapa + descripción textual de dónde es** (barrio/partido/referencia), no solo "Mar del Plata". Visible en la ficha (mini-mapa Leaflet, ya disponible) y como dato jerárquico.
- **RF-15** Cálculo de distancia haversine entre usuario y publicación (lat/lng). Privacidad: a particulares se les puede mostrar ubicación aproximada (offset/círculo) hasta que haya contacto.

### 3.6 Autenticación Google `[objetivo]`
- **RF-16** "Ingresar con Google" (OAuth 2.0 / OpenID Connect) además del email/password actual. Crea/vincula `users` por email.
- **RF-17** Primer login con Google dispara el permiso de ubicación (RF-12) y la elección de rol (Comprador / Vendedor).

### 3.7 Infraestructura de usuario `[objetivo]`
- **RF-18** **Favoritos**: guardar/quitar publicaciones; vista "Mis favoritos".
- **RF-19** **Historial**: registro automático de publicaciones vistas; vista "Vistos recientemente".
- **RF-20** **Lugares visitados**: registro de tiendas/concesionarias/servicios cuya ficha se abrió, con su ubicación; vista en mapa "Lugares que visitaste".
- **RF-21** Estas vistas viven en **Mi Cuenta** y alimentan recomendaciones ("cerca tuyo y parecido a lo que viste").

---

## 4. Modelo de datos — deltas sobre el esquema actual

Esquema actual relevante (observado, Alta): `users(role, province, …)`, `seller_profiles(lat, lng, address, city, verified, …)`, `products(province, city, compatible_models, …)`, `leads`, `reviews`, `categories(parent_id)`, `market_prices`.

### Cambios en tablas existentes
```sql
-- users: Google Auth + geo del usuario
ALTER TABLE users ADD COLUMN google_id TEXT UNIQUE;       -- sub de Google
ALTER TABLE users ADD COLUMN avatar_url TEXT;
ALTER TABLE users ADD COLUMN auth_provider TEXT DEFAULT 'LOCAL'; -- LOCAL|GOOGLE
ALTER TABLE users ADD COLUMN lat REAL;                    -- ubicación consentida
ALTER TABLE users ADD COLUMN lng REAL;
ALTER TABLE users ADD COLUMN location_label TEXT;         -- "Centro, MDP"
ALTER TABLE users ADD COLUMN password TEXT NULL;          -- nullable si entra por Google

-- products: geo por publicación (hoy solo province/city)
ALTER TABLE products ADD COLUMN lat REAL;
ALTER TABLE products ADD COLUMN lng REAL;
ALTER TABLE products ADD COLUMN location_label TEXT;      -- "barrio / referencia"
ALTER TABLE products ADD COLUMN listing_type TEXT DEFAULT 'PRODUCTO'; -- PRODUCTO|AVISO|MOTO|SERVICIO
ALTER TABLE products ADD COLUMN seller_kind TEXT;         -- PARTICULAR|CONCESIONARIA (para MOTO)
-- campos moto (NULL salvo listing_type=MOTO)
ALTER TABLE products ADD COLUMN moto_year INTEGER;
ALTER TABLE products ADD COLUMN moto_cc INTEGER;
ALTER TABLE products ADD COLUMN moto_km INTEGER;
ALTER TABLE products ADD COLUMN papers_ok INTEGER;        -- 0/1
```

### Tablas nuevas
```sql
CREATE TABLE favorites (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER REFERENCES users(id),
  product_id INTEGER REFERENCES products(id),
  created_at TEXT DEFAULT (datetime('now')),
  UNIQUE(user_id, product_id)
);

CREATE TABLE view_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER REFERENCES users(id),
  product_id INTEGER REFERENCES products(id),
  viewed_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE visited_places (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER REFERENCES users(id),
  seller_id INTEGER REFERENCES users(id),   -- tienda/concesionaria/servicio
  lat REAL, lng REAL, label TEXT,
  visited_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE services (                       -- vertical Servicios
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  seller_id INTEGER REFERENCES users(id),
  name TEXT, rubro TEXT,                      -- TALLER|GOMERIA|ELECTRICA|GRABADO|SEGURO
  description TEXT, phone TEXT, whatsapp TEXT,
  lat REAL, lng REAL, location_label TEXT, address TEXT,
  store_hours TEXT, verified INTEGER DEFAULT 0,
  created_at TEXT DEFAULT (datetime('now'))
);
```
*Nota: `seller_profiles` ya tiene `lat/lng/address` — reutilizar para concesionarias y servicios ligados a un vendedor.*

---

## 5. API / rutas nuevas (sobre los Handlers Tornado actuales)

Observado (Alta): `Home, Catalogo, Producto, Busqueda, Tiendas, PerfilVendedor, Login, Register, Logout, Dashboard, MisProductos, NuevoProducto, EditarProducto, Leads, PerfilTienda`.

Nuevos `[objetivo]`:
- `GET /auth/google` + `GET /auth/google/callback` — OAuth.
- `POST /api/ubicacion` — guarda lat/lng del usuario (consentida).
- `GET /avisos`, `GET /motos` (con `?vendedor=particular|concesionaria`), `GET /servicios` — verticales (variantes de `CatalogoHandler` filtrando `listing_type`).
- `POST /api/favoritos/:product_id` (toggle), `GET /mi-cuenta/favoritos`.
- `GET /mi-cuenta/historial`, `GET /mi-cuenta/lugares`.
- `POST /mi-cuenta/publicar-aviso`, `/publicar-moto`, `/publicar-servicio` — flujos de publicación por tipo.
- Parámetro transversal `?cerca=1&lat=&lng=` en todos los listados → orden por distancia + columna distancia.

---

## 6. Diseño visual (no Agrofy)

La **funcionalidad** se replica de Agrofy; la **estética NO**. Se aplica íntegro [radar-competencia-diseno-motos.md](radar-competencia-diseno-motos.md):
- Paleta **rojo `#e01b24` + negro `#15171c`** (chrome cinematográfico), nunca el verde Agrofy.
- Tipografía Archivo (display industrial) + Inter (UI).
- Fotografía que comanda el whitespace; hero cinematográfico.
- Íconos SVG (`_icons.html`), cero emojis.
- Selector de compatibilidad marca→modelo→año como cuña diferencial.
- "Cerca de mí" + distancia se vuelve un **momento de marca** (chip rojo con la distancia), no letra chica.

---

## 7. Requisitos no funcionales

- **Privacidad geo**: permiso explícito (RF-12), consentimiento revocable, ubicación de particulares ofuscada hasta el contacto, banner de privacidad. Cumplir espíritu de la ley 25.326 (datos personales, AR).
- **Seguridad OAuth**: validar `state`, verificar `id_token` de Google server-side, no exponer client_secret. Resolver primero el **XSS P0** del mapa ([AUDIT.md](AUDIT.md)) antes de sumar más HTML dinámico de usuario.
- **Performance**: índices en `products(listing_type, lat, lng)`, `favorites(user_id)`, `view_history(user_id)`; distancia calculada en SQL o en memoria con bounding-box previo.
- **Mobile-first**: el permiso de ubicación y "cerca de mí" son sobre todo mobile (contexto real del comprador).

---

## 8. Gaps, riesgos y supuestos

- **Gap (Agrofy)**: no se observó el DOM/red en vivo → endpoints, paginación exacta y micro-UX de Agrofy son inferidos (Media/Baja). Validar con una pasada autenticada por Chrome si se requiere fidelidad fina.
- **Supuesto**: el modelo "avisos" de Agrofy mapea a publicaciones livianas sin verificación de vendedor. Confianza Media.
- **Riesgo**: el esquema actual mezcla "producto de tienda" y futuros "avisos/motos/servicios" en una sola tabla `products` vía `listing_type`. Es pragmático para SQLite, pero si los verticales divergen mucho convendría tablas separadas. Decisión a tomar en el plan.
- **Riesgo**: Google Auth + geo añaden superficie de seguridad/privacidad; no avanzar sin cerrar los P0/P1 del audit.
- **Supuesto**: stack se mantiene Tornado + SQLite (observado); el plan no propone reescritura de framework.

> Entregable complementario: **[plan_pulido.md](plan_pulido.md)** — plan de ejecución por fases priorizadas para llevar el ecommerce actual a este spec.
