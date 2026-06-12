# Product

## Register

product

## Users

**Comprador (primario):** motociclista de Mar del Plata y la costa que necesita un repuesto concreto para su moto (Honda Wave, YBR 125, CB 190R, XR, Zanella, etc.). Llega con intención de compra y a menudo desde el celular. Su trabajo: encontrar la pieza compatible con su modelo, ver si hay stock en una tienda local, comparar precio y contactar al vendedor (mayormente por WhatsApp) lo más rápido posible. No quiere navegar una landing: quiere buscar, filtrar por modelo/categoría/tienda y resolver.

**Vendedor (secundario):** casa de repuestos de MDP (MDR Motos, Emiliozzi, LC Motoparts, etc.). Publica productos, gestiona su perfil de tienda y recibe consultas (leads). Su trabajo: aparecer cuando alguien busca una pieza que tiene, y convertir la visita en una consulta de WhatsApp.

**Contexto de uso:** alto porcentaje mobile, conexión variable, sesiones cortas y orientadas a tarea. La confianza importa: el comprador necesita señales de que la tienda es real y local (verificación, ubicación en mapa, reseñas, horarios).

## Product Purpose

Re-Puestos MDP conecta a motociclistas de Mar del Plata con las casas de repuestos locales en un solo catálogo. Existe porque hoy esa búsqueda está fragmentada entre MercadoLibre, grupos de Facebook y llamar tienda por tienda. Éxito = el comprador encuentra la pieza compatible y contacta a una tienda local en pocos clics; la tienda recibe leads calificados. La métrica norte es **consultas enviadas a vendedores** (leads vía WhatsApp/formulario), no pageviews.

## Brand Personality

**Pro confiable + energía racing.** Profesional y digno de confianza como un buen marketplace B2C (referencia de estructura: Agrofy — grilla densa, filtros claros, foco en producto, cero adorno gratuito), pero con el carácter rojo/negro del mundo motero. Voz directa, argentina, sin solemnidad: "Encontrá tu repuesto", "Consultá por WhatsApp". Tres palabras: **confiable, local, con garra.** La energía racing se transmite en el acento de color, la tipografía y la contundencia — nunca en ruido visual que estorbe la compra.

## Anti-references

- **Plantilla AI genérica (anti-ref principal):** evitar el look "hecho por IA" — grillas de cards idénticas repetidas hasta el infinito, emojis decorativos como íconos de UI, gradientes violetas, "eyebrows" en mayúscula sobre cada sección, hero-metric template, glassmorphism porque sí. Cada elemento se gana su lugar.
- **MercadoLibre amarillo saturado:** sin recarga de banners, sin amarillo chillón, sin diez llamados a la acción compitiendo.
- **Tienda de repuestos anticuada (2010):** sin tablas grises, fotos miniatura ni tipografía apretada.

## Design Principles

1. **La tarea manda, no la marca.** Cada pantalla sirve a "encontrar la pieza y contactar la tienda". El diseño desaparece en la tarea (register product). La personalidad vive en momentos, no en cada pixel.
2. **Compatibilidad y localía como información de primera clase.** "Compatible con tu modelo" y "tienda local verificada" son las dos señales que cierran la compra: deben ser visibles y jerárquicas, no letra chica.
3. **Íconos reales, no emojis.** Reemplazar emojis de UI (🔧🏪📍💬) por un set de íconos SVG consistente. Los emojis son un tell de plantilla AI y rompen la jerarquía. (Ver anti-ref principal.)
4. **Mobile es el caso real, no el responsive de cortesía.** Zona del pulgar, targets ≥44px, estado preservado, WhatsApp a un toque.
5. **Confianza por evidencia.** Verificación, mapa, horarios, reseñas y precio claro reducen la fricción de "¿le compro a este desconocido?". Mostrar la evidencia, no afirmar la confianza.

## Accessibility & Inclusion

WCAG AA estándar: contraste de texto ≥4.5:1 (cuidado especial con el rojo sobre negro y el texto gris sobre tintes), large text ≥3:1, navegación completa por teclado con foco visible, `alt` significativo en fotos de producto y logos de tienda, y estados (loading, error, vacío) anunciados. No depender solo del color para comunicar estado (verificado, nuevo/usado, stock). Respetar `prefers-reduced-motion`.
