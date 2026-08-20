/* =========================================================
   SONRICKS STORE — script.js
   JavaScript vanilla — SOLO interacción de diseño frontal
   (sin lógica de backend, carrito real ni pagos)
   ========================================================= */

document.addEventListener('DOMContentLoaded', () => {

  /* ---------- 1. Menú móvil (hamburguesa) ---------- */
  const navToggle = document.getElementById('navToggle');
  const navMenu = document.getElementById('navMenu');

  if (navToggle && navMenu) {
    navToggle.addEventListener('click', () => {
      const abierto = navMenu.classList.toggle('is-open');
      navToggle.setAttribute('aria-expanded', String(abierto));
      navToggle.setAttribute(
        'aria-label',
        abierto ? 'Cerrar menú de navegación' : 'Abrir menú de navegación'
      );
    });

    // Cierra el menú al elegir una opción (mejora la UX en móvil)
    navMenu.querySelectorAll('a').forEach(enlace => {
      enlace.addEventListener('click', () => {
        navMenu.classList.remove('is-open');
        navToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* ---------- 2. Encabezado con sombra al hacer scroll ---------- */
  const header = document.querySelector('.site-header');
  const aplicarSombraHeader = () => {
    if (window.scrollY > 8) {
      header.style.boxShadow = '0 6px 18px rgba(16, 22, 20, 0.08)';
    } else {
      header.style.boxShadow = 'none';
    }
  };
  aplicarSombraHeader();
  window.addEventListener('scroll', aplicarSombraHeader, { passive: true });

  /* ---------- 3. Botón "Agregar" con feedback visual (solo UI) ---------- */
  document.querySelectorAll('.producto .btn--pequeno').forEach(boton => {
    boton.addEventListener('click', () => {
      const textoOriginal = boton.textContent;
      boton.textContent = 'Agregado ✓';
      boton.disabled = true;

      setTimeout(() => {
        boton.textContent = textoOriginal;
        boton.disabled = false;
      }, 1500);
    });
  });

  /* ---------- 4. Formulario de newsletter (simulación visual) ---------- */
  const form = document.getElementById('newsletterForm');
  const mensaje = document.getElementById('ofertaMensaje');

  if (form && mensaje) {
    form.addEventListener('submit', (evento) => {
      evento.preventDefault();
      const email = form.querySelector('#email').value.trim();

      if (email) {
        mensaje.textContent = `¡Listo! Enviamos tu código de descuento a ${email}.`;
        form.reset();
      } else {
        mensaje.textContent = 'Ingresa un correo válido para continuar.';
      }
    });
  }

  /* ---------- 5. Revelado suave de secciones al hacer scroll ---------- */
  const elementosAnimados = document.querySelectorAll(
    '.producto, .beneficio, .testimonio'
  );

  if ('IntersectionObserver' in window) {
    elementosAnimados.forEach(el => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(16px)';
      el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    });

    const observador = new IntersectionObserver((entradas) => {
      entradas.forEach(entrada => {
        if (entrada.isIntersecting) {
          entrada.target.style.opacity = '1';
          entrada.target.style.transform = 'translateY(0)';
          observador.unobserve(entrada.target);
        }
      });
    }, { threshold: 0.15 });

    elementosAnimados.forEach(el => observador.observe(el));
  }

});
