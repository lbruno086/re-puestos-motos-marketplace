# plan_pulido.md — Plan de depuración y pulido de Re-Puestos MDP

Plan de ejecución por fases para llevar el ecommerce actual al objetivo de [spec_pulido.md](spec_pulido.md) (modelo Agrofy → motos: avisos, geolocalización "cerca de mí", Google Auth, favoritos/historial/lugares, verticales Motos/Servicios) con la identidad de [radar-competencia-diseno-motos.md](radar-competencia-diseno-motos.md). Anclado en el código real (Tornado + SQLite: `app.py`, `database.py`, `templates/`).

## Modelo de priorización

Cada tarea se evalúa por **Impacto** (valor para la métrica norte = consultas enviadas), **Esfuerzo** y **Riesgo**. Orden = primero base sana, luego estructura, luego features de valor, luego rebrand.

| Banda | Significado |
|---|---|
| 🔴 P0 | Bloqueante / seguridad — antes que cualquier feature |
| 🟠 P1 | Estructura núcleo del nuevo modelo |
| 🟡 P2 | Features de valor diferencial |
| 🟢 P3 | Pulido visual y refinamiento |

---

## Fase 0 — Base sana (🔴 P0) · prerequisito de todo

No se construye encima de fallas conocidas. Cierra los hallazgos críticos de [AUDIT.md](AUDIT.md).

| # | Tarea | Archivos | Criterio de aceptación |
|---|---|---|---|
| 0.1 | Corregir **XSS persistente** en popups del mapa | `templates/tiendas.html`, `database.py` (sanitizar al guardar) | Inyectar `<img onerror>` en dirección de tienda no ejecuta JS en `/tiendas` |
| 0.2 | Quitar **credenciales demo** del login en prod | `templates/auth/login.html`, env `DEMO_MODE` | El bloque demo no aparece con `DEMO_MODE=0` |
| 0.3 | `urlencode` en el texto del link de WhatsApp | `templates/producto.html` | Título con `&`/`#` genera link de WhatsApp válido |
| 0.4 | Accesibilidad teclado en miniaturas y tarjetas de mapa | `templates/producto.html`, `tiendas.html` | Navegables por Tab + Enter/Espacio |

**Impacto** Alto (seguridad/confianza) · **Esfuerzo** Bajo · **Riesgo** Bajo. **Salida:** repo seguro para sumar Google Auth y datos de usuario.

---

## Fase 1 — Reestructurar la arquitectura de información (🟠 P1)

Llevar de "catálogo único de repuestos" a los 4 verticales del spec.

| # | Tarea | Archivos | Aceptación |
|---|---|---|---|
| 1.1 | Migración de esquema: agregar `listing_type` a `products` + tablas nuevas (`favorites`, `view_history`, `visited_places`, `services`) | `database.py` | Migración idempotente corre en arranque sin romper data existente |
| 1.2 | Rama raíz **Accesorios** en `categories` (hoy todo es Repuestos) | `database.py` (seed), `_icons.html` (íconos rubro) | Catálogo muestra Repuestos y Accesorios como dos ramas |
| 1.3 | Verticales como rutas: `/avisos`, `/motos`, `/servicios` (variantes de `CatalogoHandler` filtrando `listing_type`) | `app.py` | Cada vertical lista solo su tipo |
| 1.4 | Nav de `base.html`: selector de verticales (Catálogo · Avisos · Motos · Servicios) | `templates/base.html` | Header refleja la nueva IA en desktop y drawer mobile |

**Impacto** Alto · **Esfuerzo** Medio · **Riesgo** Medio (migración). **Dependencia:** Fase 0.

---

## Fase 2 — Autenticación con Google (🟠 P1)

| # | Tarea | Archivos | Aceptación |
|---|---|---|---|
| 2.1 | Columnas `google_id/avatar_url/auth_provider`, `password` nullable | `database.py` | Usuario Google se crea sin password |
| 2.2 | Flujo OAuth `/auth/google` + `/auth/google/callback` (validar `state`, verificar `id_token` server-side) | `app.py`, `requirements.txt` (lib OAuth) | Login con Google crea/vincula sesión por email |
| 2.3 | Botón "Ingresar con Google" | `templates/auth/login.html`, `register.html` | Visible y funcional junto al login local |
| 2.4 | Onboarding primer login: elegir rol (Comprador/Vendedor) + disparar permiso de ubicación | nuevo `templates/auth/onboarding.html` | Primer login Google pide rol y ubicación una vez |

**Impacto** Alto (fricción de registro) · **Esfuerzo** Medio · **Riesgo** Medio (secrets/privacidad). **Dependencia:** Fase 0. Secrets por env, nunca en repo.

---

## Fase 3 — Geolocalización y "Cerca de mí" (🟡 P2) · el diferencial

| # | Tarea | Archivos | Aceptación |
|---|---|---|---|
| 3.1 | Pedir permiso de ubicación al loguear (Geolocation API) + `POST /api/ubicacion` que persiste lat/lng del usuario; fallback a selección manual de partido | `templates/base.html` (JS), `app.py`, `users.lat/lng/location_label` | Conceder ubicación guarda coords; denegar ofrece elegir zona |
| 3.2 | Geo por publicación: `products.lat/lng/location_label` + captura en publicar/editar (pin en mini-mapa Leaflet) | `database.py`, `nuevo_producto.html`, `editar_producto.html` | Publicación guarda ubicación + descripción textual |
| 3.3 | Filtro/orden **"Cerca de mí"** con **distancia exacta** (haversine + bounding-box) en todos los verticales | `app.py`, `catalogo.html` | Listado ordenable por distancia; cada card muestra "a X km" |
| 3.4 | Ubicación en la ficha como momento de marca (mini-mapa + chip rojo de distancia) | `producto.html` | Ficha muestra mapa + "a X km de vos" |
| 3.5 | Ofuscar ubicación de particulares hasta el contacto (círculo aprox.) | `app.py`, `producto.html` | Particular muestra zona aproximada, no dirección exacta |

**Impacto** Muy alto (el pedido central; cuña competitiva) · **Esfuerzo** Medio-Alto · **Riesgo** Medio (privacidad). **Dependencia:** Fases 1-2.

---

## Fase 4 — Infraestructura de usuario: favoritos, historial, lugares (🟡 P2)

| # | Tarea | Archivos | Aceptación |
|---|---|---|---|
| 4.1 | Favoritos: toggle `POST /api/favoritos/:id` + corazón en cards/ficha | `app.py`, `producto.html`, macro card | Favorito persiste y se refleja en toda la UI |
| 4.2 | Vista "Mis favoritos" en Mi Cuenta | `app.py`, nuevo `templates/cuenta/favoritos.html` | Lista los favoritos del usuario |
| 4.3 | Historial automático de vistas (`view_history`) + "Vistos recientemente" | `app.py` (en `ProductoHandler`), `cuenta/historial.html` | Abrir ficha registra; vista lista lo visto |
| 4.4 | Lugares visitados (tiendas/concesionarias/servicios) + mapa "Lugares que visitaste" | `app.py`, `cuenta/lugares.html` | Abrir ficha de tienda registra el lugar con su ubicación |

**Impacto** Medio-Alto (recurrencia, recomendaciones) · **Esfuerzo** Medio · **Riesgo** Bajo. **Dependencia:** Fases 1-3 (geo para lugares).

---

## Fase 5 — Verticales Motos, Avisos y Servicios (🟡 P2)

| # | Tarea | Archivos | Aceptación |
|---|---|---|---|
| 5.1 | Campos moto (`moto_year/cc/km/papers_ok`, `seller_kind`) + flujo "Publicar moto" | `database.py`, nuevo `cuenta/publicar_moto.html` | Se publica una moto con sus campos |
| 5.2 | **Filtro Particular / Concesionaria** en `/motos` | `app.py`, `catalogo.html` | El comprador acota por tipo de vendedor |
| 5.3 | Flujo "Publicar aviso" liviano (sin verificación de vendedor) | `cuenta/publicar_aviso.html` | Comprador logueado publica un aviso |
| 5.4 | Vertical Servicios: tabla `services`, listado por rubro + "cerca de mí", ficha con mapa | `database.py`, `app.py`, `servicios.html` | Se lista y contacta un prestador por rubro y cercanía |
| 5.5 | Gestión en Mi Cuenta de avisos/motos/servicios (estados ACTIVO/PAUSADO/VENCIDO) | `vendedor/productos.html` ampliado | Usuario gestiona todas sus publicaciones |

**Impacto** Alto (completa el ~99% Agrofy) · **Esfuerzo** Alto · **Riesgo** Medio. **Dependencia:** Fases 1-4.

---

## Fase 6 — Rebrand y pulido visual (🟢 P3)

Aplicar [radar-competencia-diseno-motos.md](radar-competencia-diseno-motos.md) y cerrar deuda de [AUDIT.md](AUDIT.md).

| # | Tarea | Archivos | Aceptación |
|---|---|---|---|
| 6.1 | Unificar tokens legacy (`gray-*`/`moto-*` → `neutral-*`/`red-*`) | `nuevo_producto.html`, `editar_producto.html` | Cero clases legacy en el repo |
| 6.2 | Selector de compatibilidad marca→modelo→año (la cuña) | `base.html`/`home.html`, `app.py` | Selector filtra el catálogo por compatibilidad |
| 6.3 | Hero cinematográfico con foto/video real + chip de distancia | `home.html` | Hero usa imagen real, no patrón de puntos |
| 6.4 | Carga de imagen por archivo (no solo URL) | `nuevo_producto.html`, `app.py` | Vendedor sube foto desde el dispositivo |
| 6.5 | Estados faltantes: skeleton de carga, error inline por campo | varias plantillas | Loading muestra skeleton; errores junto al campo |
| 6.6 | Tailwind build estático (sacar CDN runtime) + targets táctiles ≥44px | pipeline build, `catalogo.html` | Sin warning de CDN; filtros ≥44px |
| 6.7 | Macro `product_card` reutilizable | nuevo `_product_card.html` | Una sola fuente de verdad para la card |

**Impacto** Medio (percepción/conversión) · **Esfuerzo** Medio · **Riesgo** Bajo. **Dependencia:** puede solaparse con Fases 1-5.

---

## Resumen de secuencia y dependencias

```
Fase 0 (seguridad) ──> Fase 1 (IA/esquema) ──> Fase 2 (Google Auth)
                                   │                    │
                                   └──> Fase 3 (Geo "cerca de mí") <──┘
                                              │
                                              ├──> Fase 4 (favoritos/historial/lugares)
                                              └──> Fase 5 (Motos/Avisos/Servicios)
Fase 6 (rebrand) ── transversal, cierra el ciclo
```

## Hitos sugeridos

- **MVP "Agrofy de motos" v1**: Fases 0 + 1 + 3 (estructura + geolocalización con distancia) — entrega el corazón del pedido.
- **v2**: Fase 2 (Google Auth) + Fase 4 (favoritos/historial/lugares).
- **v3**: Fase 5 (verticales completos) + Fase 6 (rebrand) → ~99% de paridad funcional con identidad propia.

## Riesgos transversales

- **Migración de `products` con `listing_type`**: si los verticales divergen, evaluar tablas separadas (decidir al inicio de Fase 5).
- **Privacidad geo + OAuth**: no avanzar Fases 2-3 con los P0/P1 de seguridad abiertos (de ahí que Fase 0 sea bloqueante).
- **Stack**: el plan asume Tornado + SQLite (observado); ningún paso exige reescritura de framework, pero SQLite limita concurrencia si crece el tráfico (riesgo a futuro, no de este plan).

> Cada fase puede ejecutarse con los comandos de diseño de `/impeccable` (shape/craft/harden/colorize/adapt) y revisarse con `/impeccable audit` para medir el progreso.
