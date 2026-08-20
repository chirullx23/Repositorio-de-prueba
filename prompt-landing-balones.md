# Prompt: Landing Page — Tienda de Balones de Fútbol Soccer

## Rol
Actúa como desarrollador frontend senior especializado en HTML5 semántico, CSS moderno y buenas prácticas de accesibilidad y rendimiento web.

## Objetivo
Desarrolla una landing page en **español** para una aplicación web de venta en línea de balones de fútbol soccer. El sitio debe tener una estructura de código limpia, semántica, accesible y optimizada para conversión (venta de producto).

---

## 1. Requisitos técnicos generales
- HTML5 semántico (nada de `<div>` genéricos donde exista una etiqueta semántica adecuada).
- CSS puro con **variables CSS (custom properties)** para la paleta de colores.
- Tipografía importada desde **Google Fonts**.
- Imágenes servidas desde un **CDN en línea** (ej. Unsplash, Cloudinary, o similar) — no imágenes locales.
- Logotipo en **SVG inline** dentro del `<nav>`.
- Diseño **responsive** (mobile-first), con breakpoints para tablet y escritorio.
- Código validado, indentado y comentado por secciones.

---

## 2. Estructura semántica requerida

```
<header>
  <nav>
    <!-- logo SVG + menú de navegación -->
  </nav>
</header>

<main>
  <section class="hero">
    <!-- Hero: titular, subtítulo, CTA principal, imagen destacada -->
  </section>

  <section class="productos">
    <article><!-- balón 1: imagen, nombre, precio, botón --></article>
    <article><!-- balón 2 --></article>
    <article><!-- balón 3 --></article>
    <article><!-- balón 4 --></article>
  </section>

  <section class="beneficios">
    <article><!-- envío gratis --></article>
    <article><!-- garantía --></article>
    <article><!-- calidad FIFA --></article>
  </section>

  <section class="testimonios">
    <article><!-- reseña de cliente --></article>
  </section>

  <aside class="oferta">
    <!-- promoción, descuento por tiempo limitado, newsletter -->
  </aside>
</main>

<footer>
  <!-- contacto, redes sociales, mapa del sitio, copyright -->
</footer>
```

**Reglas de uso semántico:**
- `<header>`: contiene el `<nav>` con logo y menú.
- `<main>`: un único `<main>` que envuelve todo el contenido central.
- `<section>`: agrupa bloques temáticos (hero, productos, beneficios, testimonios).
- `<article>`: cada balón individual, cada testimonio, cada beneficio (contenido autónomo y reutilizable).
- `<aside>`: contenido complementario no esencial al flujo principal (oferta, newsletter, tips).
- `<footer>`: cierre del documento con información de contacto y legal.

---

## 3. Header y navegación
- Logotipo en **SVG inline** (balón de fútbol estilizado o iniciales de marca), colocado dentro de un `<a href="#">` que enlace al inicio.
- Menú de navegación (`<ul><li><a>`) con anclas internas: Inicio, Productos, Beneficios, Testimonios, Contacto.
- Botón CTA visible en el nav (ej. "Comprar ahora").
- Nav responsive con menú hamburguesa en móvil (puede resolverse solo con CSS o JS mínimo).

## 4. Hero
- Titular potente orientado a venta (ej. "Balones profesionales al mejor precio").
- Subtítulo de apoyo con propuesta de valor.
- Botón CTA principal ("Ver catálogo" / "Comprar ahora").
- Imagen de balón de fútbol de alta calidad desde CDN, con `alt` descriptivo.

## 5. Sección de productos
- Grid de mínimo 4 `<article>` (tarjetas de producto).
- Cada tarjeta: imagen (CDN), nombre del balón, precio, breve descripción, botón "Agregar al carrito".
- Usar `<figure>` + `<figcaption>` dentro de cada `<article>` si aplica.

## 6. Beneficios / propuesta de valor
- 3 a 4 `<article>` con ícono (SVG o emoji), título corto y descripción breve.

## 7. Testimonios
- 2 a 3 `<article>` con cita de cliente, nombre, y valoración (estrellas).

## 8. Aside (oferta / newsletter)
- Bloque visualmente diferenciado con descuento por tiempo limitado o formulario de suscripción.

## 9. Footer
- Enlaces de contacto, redes sociales (íconos SVG), mapa del sitio y copyright.

---

## 10. Paleta de colores (variables CSS)

Definir en `:root` con nombres semánticos:

```css
:root {
  --color-primario: #1B5E20;   /* verde cancha */
  --color-secundario: #FFC107; /* amarillo balón/energía */
  --color-acento: #E53935;     /* rojo CTA */
  --color-texto: #1A1A1A;
  --color-fondo: #FFFFFF;
  --color-fondo-alt: #F5F5F5;
}
```

Todos los estilos de color deben referenciar estas variables (`color: var(--color-texto)`), nunca valores hardcodeados.

---

## 11. Tipografía (Google Fonts)

- Importar mínimo 2 familias: una para títulos (display, ej. "Poppins" o "Montserrat") y otra para texto (ej. "Inter" o "Roboto").
- Incluir el `<link>` de Google Fonts en el `<head>`.
- Definir variables CSS también para tipografía:

```css
:root {
  --fuente-titulos: 'Poppins', sans-serif;
  --fuente-texto: 'Inter', sans-serif;
}
```

---

## 12. Imágenes vía CDN
- Usar URLs de un CDN público (ej. `https://images.unsplash.com/...`) para: hero, tarjetas de producto, testimonios.
- Todas las etiquetas `<img>` deben incluir `alt` descriptivo en español, `loading="lazy"` (excepto la imagen del hero) y dimensiones (`width`/`height`) para evitar layout shift.

---

## 13. Logotipo SVG
- Código SVG inline (no `<img src="logo.svg">`) directamente en el `<nav>`, para permitir estilizado con CSS (`fill: var(--color-primario)`).
- Debe incluir `role="img"` y `aria-label="Logotipo [nombre de marca]"` para accesibilidad.

---

## 14. Accesibilidad y SEO
- Un solo `<h1>` en el hero; jerarquía correcta de `<h2>`–`<h3>` en el resto de secciones.
- Atributos `alt`, `aria-label` y `lang="es"` en el `<html>`.
- Meta etiquetas: `title`, `description`, Open Graph básicas.
- Contraste de color suficiente entre texto y fondo (validar con la paleta definida).

---

## 15. Entregable esperado
Un solo archivo (o conjunto HTML + CSS) que incluya:
1. HTML semántico completo según la estructura anterior.
2. CSS con variables de color y tipografía, responsive.
3. Comentarios indicando el propósito de cada sección.
4. Sin frameworks pesados (vanilla HTML/CSS, JS mínimo solo si es necesario para el menú móvil).
