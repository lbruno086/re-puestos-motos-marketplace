# Graph Report - .  (2026-06-25)

## Corpus Check
- Corpus is ~20,837 words - fits in a single context window. You may not need a graph.

## Summary
- 157 nodes · 343 edges · 13 communities (12 shown, 1 thin omitted)
- Extraction: 88% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 39 edges (avg confidence: 0.87)
- Token cost: 236,249 input · 0 output

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

## God Nodes (most connected - your core abstractions)
1. `get_connection()` - 30 edges
2. `BaseHandler` - 26 edges
3. `base.html (layout shell)` - 13 edges
4. `init_db()` - 11 edges
5. `_icons.html (icon system)` - 10 edges
6. `Vendedor Dashboard Template` - 10 edges
7. `Editar Producto Template` - 10 edges
8. `ProductoHandler` - 9 edges
9. `Nuevo Producto Template` - 9 edges
10. `NuevoProductoHandler` - 8 edges

## Surprising Connections (you probably didn't know these)
- `Compatibilidad y localia primera clase` --rationale_for--> `CatalogoHandler`  [INFERRED]
  PRODUCT.md → app.py
- `get_db()` --semantically_similar_to--> `get_connection()`  [INFERRED] [semantically similar]
  load_productos.py → database.py
- `DB_PATH y disco persistente` --rationale_for--> `get_connection()`  [INFERRED]
  PRODUCCION.md → database.py
- `slugify()` --semantically_similar_to--> `slugify()`  [INFERRED] [semantically similar]
  load_productos.py → database.py
- `Render web service config` --references--> `csv_seed_enabled()`  [INFERRED]
  render.yaml → start.py

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

## Communities (13 total, 1 thin omitted)

### Community 0 - "Handlers y Renderizado"
Cohesion: 0.17
Nodes (6): get_market_prices(), get_nav_categories(), LoginHandler, PerfilTiendaHandler, get_connection(), DB_PATH y disco persistente

### Community 1 - "App Tornado y Rutas"
Cohesion: 0.12
Nodes (19): BaseHandler, BusquedaHandler, CatalogoHandler, DashboardHandler, EditarProductoHandler, BaseHandler.get_current_user, HealthHandler, HomeHandler (+11 more)

### Community 2 - "Panel del Vendedor (Templates)"
Cohesion: 0.19
Nodes (22): base.html Layout, Categories Data (cats), Vendedor Dashboard Template, Editar Producto Template, POST /mi-cuenta/editar/{id}, POST /mi-cuenta/nuevo, POST /mi-cuenta/perfil, icon() Macro (_icons.html) (+14 more)

### Community 3 - "DB, Seeding y Arranque"
Cohesion: 0.19
Nodes (16): Connection, cat_img(), img(), init_db(), make_slug(), slugify(), STORES_MDQ seed data, CSV_PATH (+8 more)

### Community 4 - "Modelo de Datos SQLite"
Cohesion: 0.26
Nodes (11): BaseHandler.enforce_rate_limit, ProductoHandler, RegisterHandler, categories table, leads table, products table, SCHEMA (SQLite DDL), seller_profiles table (+3 more)

### Community 5 - "Auth UI y Layout Base"
Cohesion: 0.27
Nodes (7): Login form / authentication UI, Account role selector (Comprador/Vendedor), Brand design system (red/ink theme, Tailwind config), Mobile drawer navigation, base.html (layout shell), _icons.html (icon system), perfil_vendedor.html (seller profile)

### Community 6 - "Home y Navegacion"
Cohesion: 0.22
Nodes (10): Categories data (slug/name/cnt), current_user (auth context var), nav_categories (category tree var), Navbar + category dropdown nav, Catalog filters (category/price/brand/condition/store), Category grid (cat_counts), Featured + most-viewed products, Hero + search + popular terms (+2 more)

### Community 7 - "Catalogo y Busqueda"
Cohesion: 0.40
Nodes (6): Products data (slug/title/price/brand/image), Search results grid + empty state, busqueda.html (search results), Catalog pagination + sort, Product card component, catalogo.html (product catalog)

### Community 8 - "Mapa de Tiendas y Contacto WhatsApp"
Cohesion: 0.50
Nodes (5): Sellers/Tiendas data (company_name/whatsapp/rating/lat-lng), Seller profile (stats, brands, reviews, contact), WhatsApp seller CTA (wa.me deep link), Leaflet OpenStreetMap store locator, tiendas.html (stores map)

### Community 9 - "Sistema de Iconos y Ticker"
Cohesion: 0.40
Nodes (5): Market prices ticker, icon() macro (Lucide SVG), SVG icon system (no emojis), Seller panel navigation, vmenu() macro (seller panel nav)

### Community 10 - "Principios de Diseno Racing"
Cohesion: 0.50
Nodes (4): Committed chrome / restrained content, Iconos SVG en vez de emojis, Tema rojo/negro racing, Register: product

### Community 11 - "Ficha de Producto y Captura de Leads"
Cohesion: 0.50
Nodes (4): Leads/consultas data (buyer_name/email/message), Product detail (images, compat, price), Lead/consulta contact form, producto.html (product detail)

## Ambiguous Edges - Review These
- `get_db()` → `CSV_PATH`  [AMBIGUOUS]
  load_productos.py · relation: references

## Knowledge Gaps
- **17 isolated node(s):** `Connection`, `STORES_MDQ seed data`, `SVG icon system (no emojis)`, `Seller panel navigation`, `Login form / authentication UI` (+12 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `get_db()` and `CSV_PATH`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `get_connection()` connect `Handlers y Renderizado` to `App Tornado y Rutas`, `DB, Seeding y Arranque`, `Modelo de Datos SQLite`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **Why does `BaseHandler` connect `App Tornado y Rutas` to `Handlers y Renderizado`, `Modelo de Datos SQLite`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `init_db()` connect `DB, Seeding y Arranque` to `Handlers y Renderizado`, `App Tornado y Rutas`, `Modelo de Datos SQLite`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `get_connection()` (e.g. with `get_db()` and `DB_PATH y disco persistente`) actually correct?**
  _`get_connection()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Connection`, `Carga / actualiza productos desde data/productos.csv a la base de datos. Idempo`, `STORES_MDQ seed data` to the rest of the system?**
  _23 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `App Tornado y Rutas` be split into smaller, more focused modules?**
  _Cohesion score 0.1206896551724138 - nodes in this community are weakly interconnected._