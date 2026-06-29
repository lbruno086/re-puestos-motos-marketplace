# Graph Report - re-puestos  (2026-06-29)

## Corpus Check
- 15 files · ~39,558 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 319 nodes · 542 edges · 23 communities (18 shown, 5 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 48 edges (avg confidence: 0.81)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `86ceae7d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Handlers y Renderizado|Handlers y Renderizado]]
- [[_COMMUNITY_App Tornado y Rutas|App Tornado y Rutas]]
- [[_COMMUNITY_Panel del Vendedor (Templates)|Panel del Vendedor (Templates)]]
- [[_COMMUNITY_DB, Seeding y Arranque|DB, Seeding y Arranque]]
- [[_COMMUNITY_Modelo de Datos SQLite|Modelo de Datos SQLite]]
- [[_COMMUNITY_Auth UI y Layout Base|Auth UI y Layout Base]]
- [[_COMMUNITY_Home y Navegacion|Home y Navegacion]]
- [[_COMMUNITY_Catalogo y Busqueda|Catalogo y Busqueda]]
- [[_COMMUNITY_Mapa de Tiendas y Contacto WhatsApp|Mapa de Tiendas y Contacto WhatsApp]]
- [[_COMMUNITY_Sistema de Iconos y Ticker|Sistema de Iconos y Ticker]]
- [[_COMMUNITY_Principios de Diseno Racing|Principios de Diseno Racing]]
- [[_COMMUNITY_Ficha de Producto y Captura de Leads|Ficha de Producto y Captura de Leads]]
- [[_COMMUNITY_Principio Mobile-First|Principio Mobile-First]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]

## God Nodes (most connected - your core abstractions)
1. `BaseHandler` - 41 edges
2. `get_connection()` - 41 edges
3. `Hallazgos detallados` - 14 edges
4. `Changelog` - 12 edges
5. `plan_pulido.md — Plan de depuración y pulido de Re-Puestos MDP` - 12 edges
6. `init_db()` - 10 edges
7. `spec_pulido.md — Re-Puestos MDP como "Agrofy de las motos"` - 10 edges
8. `Vendedor Dashboard Template` - 10 edges
9. `Design` - 9 edges
10. `_PgConnection` - 8 edges

## Surprising Connections (you probably didn't know these)
- `Compatibilidad y localia primera clase` --rationale_for--> `CatalogoHandler`  [INFERRED]
  PRODUCT.md → app.py
- `slugify()` --semantically_similar_to--> `slugify()`  [INFERRED] [semantically similar]
  load_productos.py → database.py
- `Render web service config` --references--> `csv_seed_enabled()`  [INFERRED]
  render.yaml → start.py
- `get_brand_models()` --calls--> `get_connection()`  [INFERRED]
  app.py → db.py
- `get_db()` --calls--> `get_connection()`  [INFERRED]
  load_productos.py → db.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Arranque y seed de la app** — start_init_db, database_init_db, load_productos_load, app_make_app [EXTRACTED 0.85]
- **Pipeline de render de request** — app_basehandler, app_render_template, app_get_current_user, app_get_nav_categories, app_get_market_prices [INFERRED 0.85]
- **Captura de leads (metrica norte)** — app_productohandler, database_leads_table, database_products_table, product_leads_metric [INFERRED 0.75]
- **Page templates extending base layout** — auth_login_template, auth_register_template, templates_home_template, templates_catalogo_template, templates_producto_template, templates_tiendas_template, templates_perfil_vendedor_template, templates_busqueda_template, templates_base_template [EXTRACTED 1.00]
- **Templates consuming the icon() macro** — templates_icons_icon, templates_base_template, templates_home_template, templates_producto_template, templates_tiendas_template, templates_vendedor_menu_vmenu [EXTRACTED 1.00]
- **Shared product-card grid pattern across pages** — templates_busqueda_results, templates_catalogo_product_card, templates_home_featured, domain_products_data [INFERRED 0.80]
- **Seller Dashboard Shared Layout (base + icon + vmenu)** — vendedor_base_template, vendedor_icons_macro, vendedor_vmenu_macro, vendedor_dashboard_template, vendedor_productos_template, vendedor_leads_template [EXTRACTED 1.00]
- **Product CRUD Form Flow (new/edit forms, endpoints, xsrf)** — vendedor_nuevo_producto_template, vendedor_editar_producto_template, vendedor_endpoint_nuevo, vendedor_endpoint_editar, vendedor_xsrf_form, vendedor_product_form_ui [INFERRED 0.85]

## Communities (23 total, 5 thin omitted)

### Community 1 - "App Tornado y Rutas"
Cohesion: 0.06
Nodes (38): AvisosHandler, BaseHandler, BusquedaHandler, CatalogoHandler, DashboardHandler, EstadoPublicacionHandler, FavoritosHandler, FavoritoToggleHandler (+30 more)

### Community 2 - "Panel del Vendedor (Templates)"
Cohesion: 0.26
Nodes (14): base.html Layout, Vendedor Dashboard Template, POST /mi-cuenta/perfil, icon() Macro (_icons.html), Lead Data (leads), Leads (Consultas) Template, Perfil de Tienda Template, Product Data (prod/products) (+6 more)

### Community 3 - "DB, Seeding y Arranque"
Cohesion: 0.18
Nodes (19): cat_img(), img(), init_db(), jitter_mdp_coords(), make_slug(), migrate_schema(), Coordenada aleatoria cerca del centro de Mar del Plata (~6km de radio)., Idempotente: agrega ramas Accesorios/Motos/Avisos si todavia no existen. (+11 more)

### Community 4 - "Modelo de Datos SQLite"
Cohesion: 0.13
Nodes (9): EditarProductoHandler, get_market_prices(), get_nav_categories(), haversine_km(), NuevoProductoHandler, OnboardingHandler, lat/lng para 'cerca de mi': query param (un solo click) > cookie > perfil de usu, unique_product_slug() (+1 more)

### Community 5 - "Auth UI y Layout Base"
Cohesion: 0.40
Nodes (5): Sellers/Tiendas data (company_name/whatsapp/rating/lat-lng), Seller profile (stats, brands, reviews, contact), perfil_vendedor.html (seller profile), Leaflet OpenStreetMap store locator, tiendas.html (stores map)

### Community 6 - "Home y Navegacion"
Cohesion: 0.06
Nodes (33): [2.12.0] - 2026-03-05, [2.13.0] - 2026-03-9, [2.14.0] - 2026-03-13, [2.15.0] - 2026-03-23, [2.15.1] - 2026-03-27, [2.16.0] - 2026-04-29, [2.17.0] - 2026-05-13, [2.18.0] - 2026-05-21 (+25 more)

### Community 7 - "Catalogo y Busqueda"
Cohesion: 0.09
Nodes (21): Acciones recomendadas (orden de prioridad), Audit Health Score, Audit técnico — Re-Puestos MDP, Hallazgos detallados, Hallazgos positivos, [P0] XSS persistente en los popups del mapa de tiendas, [P1] Credenciales demo visibles en producción, [P1] Elementos interactivos sin soporte de teclado (+13 more)

### Community 8 - "Mapa de Tiendas y Contacto WhatsApp"
Cohesion: 0.10
Nodes (19): 0. Nivel de acceso y honestidad de evidencia, 1. Modelo funcional de Agrofy observado (lo que se replica), 2. Arquitectura de información objetivo `[objetivo]`, 3.1 Catálogo (Repuestos / Accesorios) — ya parcialmente implementado, 3.2 Avisos `[objetivo]`, 3.3 Motos `[objetivo]`, 3.4 Servicios `[objetivo]`, 3.5 Geolocalización (núcleo del pedido) `[objetivo]` (+11 more)

### Community 9 - "Sistema de Iconos y Ticker"
Cohesion: 0.18
Nodes (10): add_column_if_missing(), column_exists(), _PgConnection, Capa de datos dual-driver: SQLite en local, PostgreSQL en producción (Render)., Consultas de runtime: '?' -> '%s', LIKE -> ILIKE (case-insensitive)., DDL/seed: además del placeholder, mapea construcciones SQLite-only., Equivalente a sqlite3.executescript: corre DDL/seed multi-statement., ALTER TABLE ADD COLUMN es idempotente acá: solo corre si la columna no existe. (+2 more)

### Community 10 - "Principios de Diseno Racing"
Cohesion: 0.50
Nodes (4): Committed chrome / restrained content, Iconos SVG en vez de emojis, Tema rojo/negro racing, Register: product

### Community 11 - "Ficha de Producto y Captura de Leads"
Cohesion: 0.12
Nodes (15): 1. Matriz de diseño competitiva, 2. Patrones estéticos recurrentes (lo que comparten los mejores), 3.1 Color (tokens OKLCH), 3.2 Tipografía, 3.3 Fotografía y tratamiento de imagen (el mayor salto sobre el estado actual), 3.4 Layout y estructura, 3.5 Componentes (estados completos: default/hover/focus/active/disabled/loading/error), 3.6 Motion (+7 more)

### Community 13 - "Community 13"
Cohesion: 0.15
Nodes (12): Fase 0 — Base sana (🔴 P0) · prerequisito de todo, Fase 1 — Reestructurar la arquitectura de información (🟠 P1), Fase 2 — Autenticación con Google (🟠 P1), Fase 3 — Geolocalización y "Cerca de mí" (🟡 P2) · el diferencial, Fase 4 — Infraestructura de usuario: favoritos, historial, lugares (🟡 P2), Fase 5 — Verticales Motos, Avisos y Servicios (🟡 P2), Fase 6 — Rebrand y pulido visual (🟢 P3), Hitos sugeridos (+4 more)

### Community 14 - "Community 14"
Cohesion: 0.20
Nodes (9): Bans (recordatorio activo para este proyecto), Color, Components, Design, Iconography, Layout, Motion, Theme (+1 more)

### Community 15 - "Community 15"
Cohesion: 0.20
Nodes (10): [2.11.0] - 2026-03-03, Added, Changed, Early Access, Fixed, General, General, Workflows (+2 more)

### Community 16 - "Community 16"
Cohesion: 0.22
Nodes (8): Accessibility & Inclusion, Anti-references, Brand Personality, Design Principles, Product, Product Purpose, Register, Users

### Community 17 - "Community 17"
Cohesion: 0.33
Nodes (5): Contributing, Dev setup, Documentation, Installation, Render CLI

### Community 18 - "Community 18"
Cohesion: 0.40
Nodes (4): Despliegue web, Ejecutar local, Re-Puestos MDP, Variables de entorno

### Community 19 - "Community 19"
Cohesion: 0.50
Nodes (3): Produccion, Ruta recomendada, Variables

## Ambiguous Edges - Review These
- `get_db()` → `CSV_PATH`  [AMBIGUOUS]
  load_productos.py · relation: references

## Knowledge Gaps
- **117 isolated node(s):** `Added`, `Changed`, `Added`, `Changed`, `Added` (+112 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `get_db()` and `CSV_PATH`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `get_connection()` connect `Modelo de Datos SQLite` to `App Tornado y Rutas`, `DB, Seeding y Arranque`, `Sistema de Iconos y Ticker`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `BaseHandler` connect `App Tornado y Rutas` to `Modelo de Datos SQLite`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Why does `Changelog` connect `Home y Navegacion` to `Community 15`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Are the 36 inferred relationships involving `get_connection()` (e.g. with `.get_current_user()` and `.get()`) actually correct?**
  _`get_connection()` has 36 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Mapa marca -> modelos, para el selector de compatibilidad del home.`, `Particulares/avisos: punto aproximado (~circulo de privacidad), no la direccion`, `lat/lng para 'cerca de mi': query param (un solo click) > cookie > perfil de usu` to the rest of the system?**
  _135 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `App Tornado y Rutas` be split into smaller, more focused modules?**
  _Cohesion score 0.06485671191553545 - nodes in this community are weakly interconnected._