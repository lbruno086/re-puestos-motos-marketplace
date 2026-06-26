# Audit técnico — Re-Puestos MDP

Auditoría de calidad técnica de las 16 plantillas (`templates/`) contra PRODUCT.md / DESIGN.md. No es una revisión de negocio: chequea lo medible y verificable en el código de UI. No se modificó nada — este documento es el backlog para `/impeccable polish|harden|optimize|...`.

## Audit Health Score

| # | Dimensión | Score | Hallazgo clave |
|---|-----------|-------|-----------------|
| 1 | Accesibilidad | 3/4 | Imágenes y `<div>` clickeables sin soporte de teclado (PDP, mapa de tiendas) |
| 2 | Performance | 2/4 | Tailwind vía CDN de runtime (`cdn.tailwindcss.com`) en producción |
| 3 | Theming | 3/4 | `nuevo_producto.html` / `editar_producto.html` usan tokens legacy (`gray-*`, `moto-*`) en vez de `neutral-*` / `red-*` |
| 4 | Responsive | 3/4 | Algunos targets táctiles de filtros bajo 44px |
| 5 | Anti-Patterns | 4/4 | Cero tells de IA — íconos SVG reales, sin emojis, sin gradientes, sin hero-metric, sin eyebrows |
| **Total** | | **15/20** | **Good — encarar las dimensiones débiles** |

## Veredicto Anti-Patterns — empezar por aquí

**Pass, con margen.** Esta es, con diferencia, la fortaleza más grande del repo: `_icons.html` reemplaza sistemáticamente todos los íconos de UI por SVG (Lucide-style, stroke consistente), no hay un solo emoji de interfaz, no hay gradient text, no hay glassmorphism decorativo, no hay hero-metric template, no hay eyebrows en mayúscula, no hay numeración 01/02/03 de relleno. El chrome oscuro + acento rojo se aplica con disciplina (Restrained en contenido, Committed en chrome) exactamente como pide DESIGN.md. Esto no es el resultado típico de una generación IA — está curado.

## Resumen ejecutivo

- **Score: 15/20 (Good)**
- Issues encontrados: **1 P0**, **5 P1**, **5 P2**, **2 P3**
- Top 5 críticos:
  1. **[P0] XSS persistente vía popups del mapa** — datos de tienda sin sanitizar inyectados como HTML en Leaflet
  2. **[P1] Credenciales demo expuestas** en la pantalla de login pública
  3. **[P1] Elementos clickeables no accesibles por teclado** (miniaturas de producto, tarjetas de tienda en el mapa)
  4. **[P1] Tailwind CDN de runtime en producción** (peso, FOUC, warning de consola)
  5. **[P1] Publicar repuesto depende de tener una URL de imagen** — fricción real para el vendedor no técnico (la persona objetivo)
- Recomendación: resolver el P0 antes de cualquier otra cosa (es explotable hoy); el resto se puede secuenciar con los comandos sugeridos abajo.

## Hallazgos detallados

### [P0] XSS persistente en los popups del mapa de tiendas
- **Ubicación**: [templates/tiendas.html:136-147](templates/tiendas.html:136)
- **Categoría**: Anti-Pattern / Seguridad (fuera de las 5 dimensiones de diseño, pero verificado en código)
- **Impacto**: `tiendas.html` serializa `sellers` a JSON (`{{ sellers | tojson }}`) y luego inyecta `company_name`, `address`, `store_hours` y `brands_list` con template literals JS directo en `m.bindPopup(...)`. Leaflet renderiza ese string como HTML real. Esos campos los escribe el propio vendedor sin sanitizar en [templates/vendedor/perfil.html](templates/vendedor/perfil.html) (`description`, `address`, `store_hours`). Una tienda con `<img src=x onerror=...>` en su dirección ejecuta JS contra **cualquier visitante** que abra `/tiendas`.
- **Estándar**: OWASP A03:2021 (Injection) / Stored XSS
- **Recomendación**: escapar los campos antes de interpolarlos en el template literal (HTML-escape) o construir el popup con DOM (`createElement`/`textContent`) en vez de string HTML. Validar/sanear también en el guardado del perfil (`database.py`) como segunda capa.
- **Comando sugerido**: `/impeccable harden`

### [P1] Credenciales demo visibles en producción
- **Ubicación**: [templates/auth/login.html:41-45](templates/auth/login.html:41)
- **Categoría**: Anti-Pattern / Seguridad
- **Impacto**: el login público muestra `tienda1@repuestos.com.ar / Demo1234!` y `comprador@repuestos.com.ar / Demo1234!` en texto plano. Cualquiera puede entrar como esa tienda demo y, si esa cuenta toca datos reales (leads, productos), manipularlos.
- **Recomendación**: ocultar el bloque demo detrás de una env var (`DEMO_MODE`) o quitarlo del build de producción.
- **Comando sugerido**: `/impeccable harden`

### [P1] Elementos interactivos sin soporte de teclado
- **Ubicación**: [templates/producto.html:26](templates/producto.html:26) (miniaturas con `onclick` en `<img>`), [templates/tiendas.html:34](templates/tiendas.html:34) (tarjeta de tienda con `onclick` en `<div>`)
- **Categoría**: Accesibilidad
- **Impacto**: ningún usuario de teclado o lector de pantalla puede cambiar la imagen principal del producto ni seleccionar una tienda en la lista — quedan fuera del orden de tabulación y sin rol semántico.
- **WCAG**: 2.1.1 Keyboard (Nivel A)
- **Recomendación**: convertir a `<button type="button">` real, o agregar `role="button" tabindex="0"` + manejador de `keydown` (Enter/Space).
- **Comando sugerido**: `/impeccable polish`

### [P1] Tailwind CDN de runtime en producción
- **Ubicación**: [templates/base.html:10](templates/base.html:10) — `<script src="https://cdn.tailwindcss.com">`
- **Categoría**: Performance
- **Impacto**: el propio Tailwind advierte que `cdn.tailwindcss.com` "should not be used in production" — compila el CSS en el navegador en cada carga, sin purgar, bloqueando el render y generando un warning de consola en cada página.
- **Recomendación**: migrar a Tailwind CLI/PostCSS con build estático y purga, servido como `<link>` con el resto de los assets.
- **Comando sugerido**: `/impeccable optimize`

### [P1] Publicar producto depende de pegar una URL de imagen
- **Ubicación**: [templates/vendedor/nuevo_producto.html:113-116](templates/vendedor/nuevo_producto.html:113), [templates/vendedor/editar_producto.html:107-111](templates/vendedor/editar_producto.html:107)
- **Categoría**: Anti-Pattern (fricción de tarea, no estético) — afecta directamente la métrica norte del producto
- **Impacto**: la persona vendedor (PRODUCT.md: "casa de repuestos de MDP") en general no tiene una URL de imagen ya alojada. Sin foto, la ficha pierde la principal señal de confianza y conversión. Esto choca con el principio #1 de PRODUCT.md ("la tarea manda").
- **Recomendación**: agregar carga de archivo (con preview) que suba a un storage y complete `image_url`, dejando el campo URL como fallback avanzado.
- **Comando sugerido**: `/impeccable shape` (es una feature nueva, no solo polish)

### [P1] Texto del mensaje de WhatsApp sin codificar en la URL
- **Ubicación**: [templates/producto.html:110](templates/producto.html:110)
- **Categoría**: Anti-Pattern / bug funcional
- **Impacto**: `?text=Hola! Vi el repuesto *{{ prod.title }}*...` interpola el título crudo en un query string. Títulos con `&`, `%`, `#` rompen el link de WhatsApp — justo el botón de conversión más importante de la ficha.
- **Recomendación**: usar un filtro `urlencode` de Jinja sobre el texto completo del mensaje.
- **Comando sugerido**: `/impeccable harden`

### [P2] Inputs de precio en el filtro sin `<label>`
- **Ubicación**: [templates/catalogo.html:56-57](templates/catalogo.html:56)
- **Categoría**: Accesibilidad
- **Impacto**: "Mínimo $" / "Máximo $" son solo `placeholder`, no `<label>` — un lector de pantalla no anuncia qué representa cada campo una vez que el usuario empieza a tipar (el placeholder desaparece).
- **WCAG**: 1.3.1 Info and Relationships, 3.3.2 Labels or Instructions
- **Recomendación**: agregar `<label class="sr-only">` o visible para ambos inputs.
- **Comando sugerido**: `/impeccable polish`

### [P2] Tokens de color legacy en los formularios de producto
- **Ubicación**: [templates/vendedor/nuevo_producto.html](templates/vendedor/nuevo_producto.html), [templates/vendedor/editar_producto.html](templates/vendedor/editar_producto.html) — únicos dos archivos del repo con `text-gray-*`, `border-gray-*`, `focus:border-moto-500`
- **Categoría**: Theming
- **Impacto**: el resto del sitio (14 plantillas) usa consistentemente `neutral-*` / `red-*` / `ink-*`. Estos dos formularios — justo los de mayor fricción para el vendedor — quedaron en el sistema de tokens anterior al rebrand rojo/negro. Visualmente casi no se nota (el alias `moto-*` resuelve al mismo rojo), pero es deuda de mantenimiento real: el próximo cambio de marca tendría que tocar dos lugares más.
- **Recomendación**: reemplazar `gray-*` → `neutral-*` y `moto-*` → `red-*` en ambos archivos.
- **Comando sugerido**: `/impeccable colorize`

### [P2] Sin error inline por campo en ningún formulario
- **Ubicación**: [templates/auth/login.html](templates/auth/login.html), [templates/auth/register.html](templates/auth/register.html), [templates/producto.html:128](templates/producto.html:128), formularios de vendedor
- **Categoría**: Componentes / Anti-Pattern
- **Impacto**: todos los formularios del sitio solo muestran un banner de error genérico arriba del form (`{% if error %}`). DESIGN.md lo marca explícitamente como un estado faltante a construir: *"error de formulario inline junto al campo"*. Es un gap consistente, no aislado.
- **Recomendación**: pasar errores por campo desde el backend y renderizar el mensaje bajo el input correspondiente, con `aria-describedby` y `border-red-600` en el campo afectado.
- **Comando sugerido**: `/impeccable harden`

### [P2] Targets táctiles bajo 44px en filtros y migas
- **Ubicación**: [templates/catalogo.html:35-114](templates/catalogo.html:35) (links de categoría/marca/condición, `py-1.5` ≈ 28-30px), breadcrumbs en `catalogo.html` / `producto.html`
- **Categoría**: Responsive
- **Impacto**: en mobile, donde según PRODUCT.md ocurre "alto porcentaje" del tráfico, varios links de filtro quedan bajo el mínimo de 44×44px recomendado para el pulgar.
- **Recomendación**: subir el padding vertical de esos links a `py-2.5` o agregar área de toque invisible.
- **Comando sugerido**: `/impeccable adapt`

### [P2] Reload completo de página al reordenar el catálogo
- **Ubicación**: [templates/catalogo.html:138](templates/catalogo.html:138) — `<select onchange="window.location=...">`
- **Categoría**: Performance / percepción
- **Impacto**: cambiar el orden dispara una navegación completa sin ningún feedback visual (no hay skeleton ni indicador), lo que en una conexión mobile variable (contexto de uso explícito en PRODUCT.md) se siente como que la página "se rompió" por un instante.
- **Recomendación**: mostrar un overlay de loading breve o, a futuro, mover el ordenamiento a fetch parcial.
- **Comando sugerido**: `/impeccable optimize`

### [P3] Duplicación de markup de card de producto
- **Ubicación**: repetido casi idéntico en `home.html`, `catalogo.html`, `busqueda.html`, `producto.html`, `perfil_vendedor.html`
- **Categoría**: Patrón sistémico (mantenibilidad, no defecto visible)
- **Impacto**: la tarjeta de producto (imagen + marca + título + precio + tienda) está copiada en 5 plantillas con pequeñas variaciones. Cualquier ajuste de diseño futuro (ej. agregar el badge "Usado" a todas) requiere tocar 5 archivos.
- **Recomendación**: extraer un macro Jinja `product_card(p)` reutilizable, similar a `_vendedor_menu.html`.
- **Comando sugerido**: `/impeccable extract`

### [P3] Stock mínimo forzado a 1
- **Ubicación**: [templates/vendedor/nuevo_producto.html:101](templates/vendedor/nuevo_producto.html:101) / `editar_producto.html:97` — `min="1"`
- **Categoría**: Componentes
- **Impacto**: un vendedor no puede marcar un producto como agotado (`stock=0`) sin desactivarlo del todo. Menor, pero limita un estado real del negocio.
- **Comando sugerido**: `/impeccable polish`

## Patrones sistémicos

- **Excelente disciplina de iconografía**: ni un solo emoji de UI en 16 plantillas — el sistema `_icons.html` se respeta al 100%. Mantenerlo así en cualquier feature nueva.
- **Elementos clickeables no semánticos** aparecen 2 veces (miniaturas, tarjetas de mapa) — vale la pena un lint/checklist para que no se repita en código nuevo.
- **Los dos únicos archivos con tokens de color legacy** son, justamente, los formularios más importantes para la conversión del vendedor (publicar/editar producto) — sugiere que se escribieron antes del rebrand y no se revisitaron.
- **Ningún formulario del sitio tiene validación inline por campo** — es la brecha más consistente entre lo que pide DESIGN.md y lo que hay implementado.

## Hallazgos positivos

- Cero tells de IA — el caso más limpio que se puede auditar en esta categoría.
- `prefers-reduced-motion` respetado de forma centralizada en `base.html` para ticker, hover de imagen y drawers.
- Foco visible y `aria-expanded`/`aria-controls`/`aria-label` correctos en el menú mobile y el toggle de filtros.
- Compatibilidad de moto y verificación de tienda — las dos señales de confianza que pide PRODUCT.md — están presentes y jerárquicas en la ficha de producto, no en letra chica.
- Estados vacíos ("No hay repuestos con estos filtros…") enseñan y ofrecen una salida, en vez de un simple "sin resultados".
- El mapa de Leaflet con pines diferenciados (verificado vs. no) y pan/zoom animado es un detalle de marca bien ejecutado (más allá del riesgo de seguridad ya señalado en el popup).

## Acciones recomendadas (orden de prioridad)

1. **[P0] `/impeccable harden`** — sanear/escapar los campos de tienda antes de inyectarlos en los popups de Leaflet (XSS).
2. **[P1] `/impeccable harden`** — ocultar credenciales demo de producción; codificar el texto del link de WhatsApp con `urlencode`; agregar errores de formulario inline.
3. **[P1] `/impeccable polish`** — convertir miniaturas de producto y tarjetas de tienda en elementos accesibles por teclado.
4. **[P1] `/impeccable optimize`** — reemplazar el Tailwind CDN de runtime por un build estático purgado.
5. **[P1] `/impeccable shape`** — diseñar la carga de imagen de producto por archivo (no solo URL).
6. **[P2] `/impeccable colorize`** — unificar tokens (`gray-*`/`moto-*` → `neutral-*`/`red-*`) en los formularios de producto.
7. **[P2] `/impeccable adapt`** — subir targets táctiles de filtros a ≥44px.
8. **[P2] `/impeccable optimize`** — feedback visual al reordenar el catálogo.
9. **[P3] `/impeccable extract`** — extraer macro `product_card` reutilizable.
10. **[P3] `/impeccable polish`** — paso final de pulido general una vez resuelto lo anterior.

Podés pedirme que corra estos uno por uno, todos juntos, o en el orden que prefieras.

Volvé a correr `/impeccable audit` después de los fixes para ver el score subir.
