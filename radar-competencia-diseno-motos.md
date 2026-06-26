# Radar de Diseño — Las mejores páginas de motos del mundo → Spec superador para Re-Puestos MDP

Investigación competitiva con lente **estética** (no de features): se mapearon los sistemas visuales (paleta, tipografía, layout, fotografía, patrón de impacto) de las principales marcas y ecommerce de motos del mundo, se identificaron los patrones recurrentes, y se sintetiza un sistema de diseño **superador** para el ecommerce de repuestos Re-Puestos MDP. Trabaja sobre el register `product` de PRODUCT.md/DESIGN.md (el diseño sirve a la tarea de comprar el repuesto), aplicando las reglas anti-slop de frontend-design.

> Método: WebFetch + WebSearch sobre los sitios reales. Donde un sitio bloqueó el bot (403) se usó su paleta oficial verificada en fuentes de marca. Todo lo `[observado]` viene del HTML/CSS real del sitio; lo `[inferido]` está marcado.

---

## 1. Matriz de diseño competitiva

| Sitio | Categoría | Paleta (núcleo) | Tipografía | Layout | Fotografía | Patrón de impacto |
|---|---|---|---|---|---|---|
| **RevZilla** (revzilla.com) | Ecommerce gear/parts (benchmark) | Vermilion `#FF4C00` + Regal Blue `#014770` + Gold `#E0A45D`, base oscura `[fuente de marca]` | Sans custom, titulares bold | Nav multinivel, grilla densa filtrable, video reviews embebidos | Producto sobre fondo limpio + lifestyle | Ecommerce dense + confianza por contenido/review |
| **Ducati** (ducati.com) | OEM premium | **Ducati Red `#B00E0A`** + blanco + negro `[fuente de marca]` | Sans bold, mayúsculas en claims | Hero full-bleed, ritmo editorial | Moto cinematográfica, alto contraste, fondos dramáticos | Rojo = pasión/racing; lujo contenido |
| **KTM** (ktm.com) | OEM agresivo/racing | **Orange `#F2771A`** + negro `#1C1919` + blanco | Sans bold UPPERCASE ("READY TO RACE") condensada | Nav multinivel, carrusel flagship, cards modulares | Estudio, perfil lateral limpio, foco mecánico | "Orange never fades": agresivo, líneas filosas, mínima decoración |
| **Harley-Davidson** (harley-davidson.com) | OEM heritage | **Orange `#FF6600`** + negro + crema | Sans display bold, UPPERCASE en secciones | Nav sticky, hero full-width con texto sobre imagen, grilla 3-4 col | Americana, riders en movimiento, bandera/ruta | Heritage americano + alto contraste |
| **Triumph** (triumphmotorcycles.com) | OEM británico refinado | Blanco/neutros + texto casi negro, **sin accent cromático fuerte** `[observado]` | Sans bold titulares, sentence case (poca mayúscula) | Nav sticky, hero full-width foto+CTA, storytelling top-down | Estudio premium + lifestyle atmosférico | La FOTO es el color; refinamiento corporativo |
| **Benelli** (benelli.com) | OEM moderno | **Oscuro/charcoal** dominante + blanco | Sans, model names UPPERCASE ("DOMINATE THE STORM") | Header con toggle, hero con **video de fondo**, cards de modelo | Video cinematográfico + producto sobre fondo limpio | Oscuro, cinematográfico, taglines aspiracionales |
| **Zero Motorcycles** (zeromotorcycles.com) | EV premium | Blanco/neutro, accent sutil, **restraint** | Sans, mayúscula solo en siglas (SR/F) | Nav sticky + país, modelos en bloques tipo card | Limpia, product-focused, sleek/minimalista | Premium tech por contención, no por vibración |
| **BikeEXIF** (bikeexif.com) | Editorial custom | **Near-black bg + texto blanco**, monocromático | Sans bold mixed-case, UPPERCASE sólo en tags ("CAFE RACER") | Grilla editorial 3-col, card = thumb+título+tag | **La foto domina el whitespace**, contraste alto, saturación rica en pintura/cromo | Minimalista: la moto manda, cero adorno |

**Fuentes:** [RevZilla brand](https://brandfetch.com/revzilla.com) · [RevZilla guidelines](https://www.petercamburn.com/revzilla-brand-guidelines) · [Ducati colors](https://www.schemecolor.com/ducati-logo-colors.php) · [Ducati brand code](https://www.brandcolorcode.com/ducati) · [Harley orange](https://www.color-name.com/harley-davidson-orange.color) · [KTM colors](https://www.schemecolor.com/ktm-logo-colors.php) · [Harley-Davidson](https://www.harley-davidson.com/) · [KTM](https://www.ktm.com/) · [Triumph](https://www.triumphmotorcycles.com/) · [Benelli](https://www.benelli.com/) · [Zero](https://www.zeromotorcycles.com/) · [BikeEXIF](https://www.bikeexif.com/) · [50 best moto sites](https://sage.agency/industry/best-motorcycle-websites/)

---

## 2. Patrones estéticos recurrentes (lo que comparten los mejores)

1. **Un solo color saturado ES la marca.** Orange (KTM, Harley), Red (Ducati). Nunca dos acentos compitiendo. El color carga energía/racing; todo lo demás es neutro. → *Re-Puestos ya acertó con el rojo; el error a evitar es diluirlo.*

2. **Dos familias de superficie, nunca el beige.** Los mejores eligen (a) **claro/blanco** product-forward (KTM, Triumph, Zero) o (b) **near-black cinematográfico** (Benelli, BikeEXIF, Harley chrome). Ninguno usa el crema/sand tibio que es el default de IA. El negro aparece como *chrome* (header/footer/hero) que enmarca contenido claro — exactamente la estrategia "Committed en chrome, Restrained en contenido".

3. **La fotografía es el héroe, no la decoración.** Consenso total: la moto/el producto **comanda el whitespace**. Fondos limpios o negros de alto contraste, iluminación dramática, perfil lateral nítido para claridad de producto. Benelli usa **video de fondo** para impacto. Nadie rellena con cards genéricas ni ilustraciones CSS.

4. **Tipografía: bold sans + UPPERCASE para los momentos.** Titulares pesados; mayúscula condensada/industrial para model names y claims ("READY TO RACE", "DOMINATE THE STORM", "ORANGE NEVER FADES"). Cuerpo: sans limpia y legible. El contraste de carácter (display industrial vs cuerpo neutro) es universal.

5. **Layout: chrome oscuro sticky + hero full-bleed + grilla modular + footer denso.** En ecommerce se suma el **selector de vehículo / fitment** y la grilla densa filtrable (RevZilla, Partzilla). La confianza se construye con review/video (RevZilla) y con claridad de producto (KTM).

6. **Impacto = alto contraste + tipo bold + foto dramática + un acento.** La fórmula que todos comparten produce "competencia técnica + herencia racing + aspiración".

### El hueco (whitespace / cuña competitiva)
Ninguno de los benchmarks globales resuelve lo que Re-Puestos necesita y puede ganar:
- **Compatibilidad/fitment como información de primera clase en un marketplace local.** RevZilla/Partzilla tienen fitment pero son catálogos masivos impersonales; las OEM no venden repuestos cross-marca. Nadie combina *"compatible con tu moto" + "tienda local verificada a 15 cuadras" + contacto directo por WhatsApp*.
- **La localía como estética, no solo como dato.** Ningún sitio global transmite "tu barrio, tu mecánico de confianza". Esa es la cuña: el impacto racing global **aplicado a la cercanía marplatense**.

---

## 3. Spec de diseño superador para Re-Puestos MDP

Síntesis: tomar el **rojo-como-marca de Ducati**, el **chrome negro cinematográfico de Benelli/BikeEXIF**, la **claridad de producto y disciplina de grilla de KTM**, la **densidad filtrable + fitment de RevZilla/Partzilla**, y la **fotografía-que-comanda-el-whitespace de BikeEXIF** — pero subordinado a la TAREA (register product) y a la **localía** como diferencial. Construye sobre el DESIGN.md actual y lo eleva.

### 3.1 Color (tokens OKLCH)

Mantiene rojo/ink existente y lo sistematiza. **Estrategia: Committed en chrome (negro), Restrained en contenido (neutro + rojo ≤10%), con momentos cinematográficos full-bleed.**

| Rol | Token | OKLCH | Hex | Uso |
|---|---|---|---|---|
| Rojo racing (primario) | `--red-600` | `oklch(0.57 0.214 27)` | `#e01b24` | Acción primaria, precio, selección, links activos |
| Rojo hover | `--red-700` | `oklch(0.50 0.205 27)` | `#c01018` | Hover botones primarios |
| Rojo tint | `--red-50` | `oklch(0.96 0.02 27)` | `#fdeced` | Chips/badges seleccionados (no texto) |
| Negro racing (chrome) | `--ink-950` | `oklch(0.20 0.012 250)` | `#15171c` | Header, footer, hero cinematográfico |
| Negro suave | `--ink-900` | `oklch(0.27 0.012 250)` | `#23262d` | Superficie oscura secundaria |
| Tinta texto | `--ink-800` | `oklch(0.34 0.01 250)` | `#33373f` | Cuerpo sobre claro (≥9:1) |
| Gris medio | `--neutral-500` | `oklch(0.62 0.008 250)` | `#8b8f97` | Metadatos (solo ≥18px o label) |
| Borde | `--neutral-200` | `oklch(0.92 0.004 250)` | `#e6e7ea` | Bordes de card, divisores |
| Superficie | `--surface` | `oklch(0.99 0.002 250)` | `#fcfcfd` | Fondo de contenido |
| Card | `--surface-card` | `oklch(1 0 0)` | `#ffffff` | Cards de producto |
| WhatsApp | `--wa` | `oklch(0.65 0.16 150)` | `#22c55e` | Exclusivo CTA WhatsApp (código de marca reconocido) |

**Decisión clave (superador):** el rojo de Re-Puestos `#e01b24` está deliberadamente más cerca del **Ducati Red** que del naranja KTM/Harley → posiciona la marca en el carril "pasión/velocidad" premium, no en el "off-road/aventura". El naranja queda libre para la competencia; el rojo+negro es defendible y distintivo en MDP. **Nunca** introducir un segundo acento saturado (el error que evita RevZilla con su azul+gold disperso).

### 3.2 Tipografía

Sobre eje de contraste, como hacen todos los benchmarks (display industrial vs cuerpo neutro):

- **Display / titulares / model-moments: `Archivo` (o `Archivo Narrow`)** en 700/800. Condensada e industrial — evoca números de carrera y carteles de taller. Es el equivalente al UPPERCASE condensado de KTM/Benelli. Uso: logo, H1/H2 de sección, **precio grande** (ancla visual de la card), y los "momentos garra" en mayúscula ("ENCONTRÁ TU REPUESTO", "100% MAR DEL PLATA").
- **Body / UI / data: `Inter`** 400/500/600/700. Labels, botones, descripciones, precios de card.
- **Regla de mayúsculas:** UPPERCASE reservado para momentos de marca (hero claim, badges de sección), **no** como eyebrow en cada sección (ban anti-slop). Es la diferencia entre la voz de KTM (deliberada) y el AI-grammar.

Escala rem fija (register product, no fluida): display 2rem, h1 1.5rem, h2 1.25rem, h3 1.0625rem, body 0.875–0.9375rem, caption 0.75rem. `text-wrap: balance` en h1–h3. Letter-spacing display ≥ -0.02em (nunca por debajo de -0.04em).

### 3.3 Fotografía y tratamiento de imagen (el mayor salto sobre el estado actual)

Es donde Re-Puestos puede pasar de "catálogo correcto" a "se ve como las grandes". Aprendizaje de BikeEXIF/Benelli/KTM:

- **Producto sobre fondo limpio y consistente.** Toda foto de repuesto sobre blanco/`--surface` con encuadre 1:1, sombra suave. Penalizar visualmente el ruido de fondo (la foto manda el whitespace de la card).
- **Hero y CTAs de tienda = momento cinematográfico.** El hero `--ink-950` ya existe; elevarlo con una **fotografía real de moto/taller marplatense** a sangre (no patrón de puntos genérico), con overlay oscuro y el rojo como único acento. Opción de impacto: **video de fondo corto** (loop silencioso de moto/ruta de la costa) como Benelli, con `prefers-reduced-motion` → imagen estática.
- **Lifestyle local, no stock genérico.** La cuña de localía pide fotos de la costa/MDP, no riders americanos. Donde no haya foto real, **no rellenar con scenery CSS** — usar el repuesto sobre negro de alto contraste (estética BikeEXIF) antes que una card vacía.
- **Tratamiento:** alto contraste, saturación preservada en pintura/cromo, lazy-load below the fold, `srcset` responsive, formatos modernos (WebP/AVIF).

### 3.4 Layout y estructura

| Zona | Spec (síntesis superadora) |
|---|---|
| **Chrome** | Header `--ink-950` sticky de dos niveles (buscador protagonista + nav categorías con íconos) + ticker fino arriba. Footer `--ink-950` denso multi-columna. Es el marco cinematográfico que enmarca el contenido claro (estrategia Benelli/Harley). |
| **Hero (home)** | Full-bleed `--ink-950` con foto/video real, claim en Archivo, buscador gigante, chips de búsquedas populares. Un solo acento rojo. |
| **Selector de compatibilidad (NUEVO — la cuña)** | Componente de primera clase "Encontrá repuestos para TU moto": marca → modelo → año, persistente. Inspirado en el fitment de Partzilla/RevZilla pero arriba y central, no escondido. Filtra todo el catálogo. |
| **Grilla de catálogo** | `repeat(auto-fill, minmax(220px, 1fr))` densa estilo KTM/RevZilla. Card = foto 1:1, marca (label), título 2 líneas, **precio Archivo rojo**, tienda + badge verificado. Sidebar de filtros (categoría, precio, marca, **tienda/ubicación**, condición), colapsable a hoja inferior en mobile. |
| **Ficha de producto** | Galería 5/12 · info 4/12 · panel vendedor sticky 3/12. **Compatibilidad y localía jerárquicas** (no letra chica): chips "Compatible con tu modelo" + tienda local verificada con mapa/horario. |
| **Tiendas** | Mapa Leaflet (pan/zoom animado, pines verificado vs normal) + lista + grilla. La localía hecha estética. |
| **Footer** | Denso, multi-columna (categorías, marcas, info), © + claim "Hecho para los moteros de la costa". |

### 3.5 Componentes (estados completos: default/hover/focus/active/disabled/loading/error)

- **Botón primario:** fill `--red-600`, texto blanco, hover `--red-700`, radio 0.75rem, focus = anillo rojo 2px. **WhatsApp:** fill verde exclusivo. **Secundario:** borde `--neutral-200`.
- **Card de producto:** blanco, borde `--neutral-200`, hover eleva sombra + borde rojo tenue + `scale(1.04)` de la imagen (ya implementado). Badge "Verificado"/"Usado" con ícono, nunca solo color.
- **Chip de compatibilidad/filtro:** pill, seleccionado = `--red-50` bg + `--red-700` + borde rojo.
- **Estados faltantes (de DESIGN.md, aún pendientes):** skeleton de card en loading (no spinner), empty state que enseña, **error inline por campo** (gap detectado en AUDIT.md).
- **Íconos:** sistema SVG `_icons.html` (Lucide-style) — **cero emojis**. Es una fortaleza ya ganada; mantenerla.

### 3.6 Motion

150–250 ms, ease-out (quart/expo). Solo estado y feedback: hover de card, apertura de filtros, foco, toast "consulta enviada", pan/zoom del mapa. Hero con video → loop suave. **Sin secuencias orquestadas de carga** (product carga a la tarea). `prefers-reduced-motion: reduce` → crossfade/instantáneo y video→imagen estática en todo.

### 3.7 El "patrón de impacto" sintetizado (la fórmula)

> **Chrome negro cinematográfico** (Benelli/BikeEXIF) **+ rojo único como marca** (Ducati) **+ fotografía de alto contraste que comanda el whitespace** (BikeEXIF/KTM) **+ display industrial condensado en los momentos** (KTM/Benelli) **+ densidad filtrable con fitment** (RevZilla/Partzilla) **— todo subordinado a la tarea y teñido de localía marplatense.**

---

## 4. Cómo SUPERA a cada benchmark

- **vs RevZilla:** misma densidad filtrable y fitment, pero sin el ruido de tres colores de marca dispersos (vermilion+azul+gold) ni la frialdad de catálogo masivo. Un acento, más confianza local.
- **vs Ducati/KTM/Harley:** toma su disciplina cromática (un acento) y claridad de producto, pero resuelve algo que ellos no: **comprar el repuesto compatible a una tienda real cercana**, no admirar una moto.
- **vs Benelli/BikeEXIF:** adopta su cine oscuro y su foto-héroe, pero no se queda en lo aspiracional/editorial: lo pone al servicio de una conversión (consulta por WhatsApp).
- **vs Triumph/Zero:** iguala su refinamiento y restraint, pero agrega la **garra racing** (rojo+Archivo) que ellos deliberadamente evitan, porque el público motero de MDP la pide.
- **El diferencial que nadie tiene:** compatibilidad + localía verificada + contacto directo, con estética de marca premium global. Ese es el producto superador.

---

## 5. Mapeo al código actual (qué cambia vs lo que ya está)

Re-Puestos ya implementa ~70% de este spec (chrome negro, rojo, Archivo+Inter, íconos SVG, grilla densa, mapa). El salto "superador" está en:

1. **Selector de compatibilidad marca→modelo→año de primera clase** (no existe; es la cuña). → `/impeccable shape`
2. **Fotografía real cinematográfica en hero/CTAs** reemplazando el patrón de puntos genérico; opción video. → `/impeccable craft`
3. **Carga de imagen de producto por archivo** (hoy depende de pegar URL — fricción detectada en AUDIT.md). → `/impeccable shape`
4. **Estados faltantes**: skeleton, error inline por campo. → `/impeccable harden`
5. **Unificar tokens legacy** (`gray-*`/`moto-*` en los forms de producto). → `/impeccable colorize`
6. **Disciplina de un solo acento**: auditar que ningún ámbar/azul compita con el rojo fuera de su rol semántico.

> Nota: estos cambios son de diseño/frontend sobre las plantillas de `templates/`. Ver [AUDIT.md](AUDIT.md) para los issues técnicos (incl. el XSS P0 del mapa) que conviene resolver en paralelo.

---

### Fuentes
[RevZilla](https://www.revzilla.com/) · [RevZilla brand assets](https://brandfetch.com/revzilla.com) · [RevZilla guidelines (Camburn)](https://www.petercamburn.com/revzilla-brand-guidelines) · [Ducati](https://www.ducati.com/) · [Ducati logo colors](https://www.schemecolor.com/ducati-logo-colors.php) · [Harley-Davidson](https://www.harley-davidson.com/) · [Harley orange hex](https://www.color-name.com/harley-davidson-orange.color) · [KTM](https://www.ktm.com/) · [KTM logo colors](https://www.schemecolor.com/ktm-logo-colors.php) · [Triumph](https://www.triumphmotorcycles.com/) · [Benelli](https://www.benelli.com/) · [Zero Motorcycles](https://www.zeromotorcycles.com/) · [BikeEXIF](https://www.bikeexif.com/) · [50 Best Motorcycle Websites (Sage)](https://sage.agency/industry/best-motorcycle-websites/)
