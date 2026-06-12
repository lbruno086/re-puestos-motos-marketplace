# Design

Sistema visual de Re-Puestos MDP. Register: **product** (el diseño sirve a la tarea de encontrar repuesto y contactar tienda). Dirección: estructura tipo Agrofy (grilla densa, profesional, foco en producto) con identidad **rojo / negro racing**. Reemplaza el tema naranja anterior por decisión explícita de marca.

## Theme

Light por defecto en el contenido (catálogo, fichas, formularios se leen mejor en superficie clara y con fotos de producto sobre blanco), con **chrome oscuro**: header y footer near-black que enmarcan el contenido y cargan la identidad racing. Escena física: un mecánico o motociclista mirando el celu en el taller o en la vereda, luz de día, resolviendo rápido — necesita contraste alto y lectura inmediata, no un dark mode de ambiente.

Color strategy: **Committed en el chrome, Restrained en el contenido.** El negro carga el header/footer; el rojo es exclusivamente acción primaria, selección y estado activo (≤10% de la superficie de contenido). El contenido es neutral para que las fotos de repuestos y los precios manden.

## Color

OKLCH. Tokens (a definir como CSS variables en `base.html`, reemplazando la config naranja de Tailwind):

| Rol | Token | OKLCH | Hex aprox | Uso |
|---|---|---|---|---|
| Rojo racing (primario) | `--red-600` | `oklch(0.57 0.214 27)` | `#e01b24` | Acción primaria, precio destacado, selección, links activos |
| Rojo hover | `--red-700` | `oklch(0.50 0.205 27)` | `#c01018` | Hover de botones primarios |
| Rojo tint | `--red-50` | `oklch(0.96 0.02 27)` | `#fdec ed` | Fondos de chip/badge seleccionado, no para texto |
| Negro racing (chrome) | `--ink-950` | `oklch(0.20 0.012 250)` | `#15171c` | Header, footer, ticker, texto display |
| Negro suave | `--ink-900` | `oklch(0.27 0.012 250)` | `#23262d` | Superficie secundaria oscura, hover en nav |
| Tinta texto | `--ink-800` | `oklch(0.34 0.01 250)` | `#33373f` | Cuerpo de texto sobre claro (≥4.5:1) |
| Gris medio | `--neutral-500` | `oklch(0.62 0.008 250)` | `#8b8f97` | Texto secundario, metadatos (solo ≥18px o como label) |
| Borde | `--neutral-200` | `oklch(0.92 0.004 250)` | `#e6e7ea` | Bordes de card, divisores |
| Superficie | `--surface` | `oklch(0.99 0.002 250)` | `#fcfcfd` | Fondo de contenido |
| Blanco card | `--surface-card` | `oklch(1 0 0)` | `#ffffff` | Cards de producto, paneles |

Semánticos de estado (estandarizar): `--success` verde WhatsApp `oklch(0.65 0.16 150)` `#22c55e` (solo CTA WhatsApp, es código de marca reconocido), `--warning` ámbar para "Usado", `--info` azul tenue. **Nunca comunicar estado solo por color** (agregar ícono/label a verificado, nuevo/usado, stock).

Contraste verificado: `--ink-800` sobre `--surface` ≈ 9:1 ✓. Rojo `--red-600` sobre blanco ≈ 4.6:1 ✓ para texto grande/bold y para fills con texto blanco encima (blanco sobre `--red-600` ≈ 4.6:1 ✓). Texto rojo fino sobre blanco: solo bold/≥18px. Gris `--neutral-500` nunca como body sobre tinte.

## Typography

Una familia para casi todo (regla product). **Body/UI: Inter** (ya cargada) en pesos 400/500/600/700 — carga labels, botones, datos, precios. Para el **display del header/hero** un sans con más carácter mecánico/industrial que aporte la garra racing sin romper la familiaridad: **Archivo** o **Archivo Narrow** (condensada, evoca números de carrera y carteles de taller) en 700/800 para el logo, títulos de sección y el precio grande. Par sobre eje de contraste (geométrica-humanista Inter + grotesca-industrial Archivo), no dos sans iguales.

Escala rem fija (no fluida): display 2rem/1.75rem, h1 1.5rem, h2 1.25rem, h3 1.0625rem, body 0.875–0.9375rem, caption 0.75rem. Ratio ~1.2. Precio de producto en Archivo 700 para que sea el ancla visual de la card. `text-wrap: balance` en títulos.

## Iconography

**Reemplazar todos los emojis de UI por íconos SVG** (principio #3 de PRODUCT.md; los emojis son tell de plantilla AI). Set sugerido: **Lucide** (línea, 1.5px, consistente, gratis) vía SVG inline o sprite. Mapa de reemplazo:

- 🔧 categorías/repuesto → `wrench` / íconos por categoría (engine, disc, battery, etc.)
- 🏪 tienda → `store`
- 📍 ubicación → `map-pin`
- 💬 WhatsApp → ícono de WhatsApp de marca (excepción: logo reconocido) o `message-circle`
- 🕐 horario → `clock`
- ★ rating → `star` (fill parcial real, no carácter unicode)
- 🏍️ logo → marca de moto custom o `bike` estilizado
- 👁️ vistas → `eye` · 📦 stock → `package` · ⚡ → `zap` · 🚚 → `truck`

Categorías del catálogo: cada una con su ícono SVG temático (no emoji), tamaño y stroke uniformes.

## Layout

- Contenedor `max-w-7xl`, grilla de producto `repeat(auto-fill, minmax(220px, 1fr))` (Agrofy-style densa) en vez de breakpoints manuales donde aplique.
- Header oscuro sticky de dos niveles: barra superior (logo + buscador protagonista + cuenta) y barra de categorías con íconos. Ticker de precios arriba, fino.
- Sidebar de filtros en catálogo (categorías, precio, marca, **tienda/ubicación**, condición) — colapsable en mobile como hoja inferior o acordeón, no oculto.
- Ficha de producto: galería 5/12, info 4/12, panel vendedor sticky 3/12 (ya existe, conservar estructura, restilar).
- Flexbox para 1D, Grid para 2D. Cards solo donde son el affordance correcto (producto, tienda); nada de cards anidadas.

## Components

Cada componente interactivo con estados: default, hover, focus (anillo rojo `--red-600` a 2px), active, disabled, loading, error.

- **Botón primario:** fill `--red-600`, texto blanco, hover `--red-700`, radio 0.75rem. **Botón WhatsApp:** fill verde, exclusivo para esa acción. **Secundario:** borde `--neutral-200`, texto `--ink-800`.
- **Card de producto:** blanco, borde `--neutral-200`, hover eleva sombra + borde rojo tenue; foto 1:1 sobre blanco, marca (label gris), título 2 líneas, precio Archivo rojo, tienda (caption). Badge "Verificado"/"Usado" con ícono, no solo color.
- **Chip de filtro / compatibilidad:** pill, seleccionado = `--red-50` bg + `--red-700` texto + borde rojo.
- **Estados faltantes a construir:** skeleton de card en loading (no spinner centrado), empty state que enseña ("No hay repuestos con estos filtros → limpiar filtros / buscar por modelo"), error de formulario inline junto al campo.
- **Badge verificado:** fondo sólido de marca + ícono check + texto, reconocible sin color.

## Motion

150–250 ms, ease-out (quart/expo), solo para estado y feedback (hover de card, apertura de filtros, foco, toast de "consulta enviada"). Sin secuencias orquestadas de carga de página (product carga a la tarea). El mapa de tiendas (Leaflet) anima el pan/zoom al seleccionar tienda — conservar. `@media (prefers-reduced-motion: reduce)`: crossfade o instantáneo en todo.

## Bans (recordatorio activo para este proyecto)

Emojis como íconos de UI · cards idénticas en grilla infinita sin jerarquía · gradientes violetas · eyebrows en mayúscula por sección · side-stripe borders · gradient text · glass por defecto · amarillo ML · tablas grises anticuadas.
