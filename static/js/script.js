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

  /* =========================================================
   6. Autenticación (Iniciar sesión / Registro)
   Dos modales independientes — cada uno con su propio
    overlay, panel y formulario. Solo UI, sin backend real.
     ========================================================= */
  const modales = document.querySelectorAll('.auth-modal');

  if (modales.length) {
    let ultimoFoco = null;

    const abrirModal = (modal) => {
      if (!modal) return;
      ultimoFoco = document.activeElement;
      modal.classList.add('is-abierto');
      modal.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
      const primerCampo = modal.querySelector('input');
      window.setTimeout(() => primerCampo && primerCampo.focus(), 320);
    };

    const cerrarModal = (modal) => {
      if (!modal) return;
      modal.classList.remove('is-abierto');
      modal.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
      if (ultimoFoco) ultimoFoco.focus();
    };

    /* ----- Abrir modal desde los botones del nav ----- */
    document.querySelectorAll('[data-modal-open]').forEach(boton => {
      boton.addEventListener('click', () => {
        abrirModal(document.getElementById(boton.dataset.modalOpen));
      });
    });

    /* ----- Reabrir el modal correcto tras un redirect del backend
       (ej. /signin o /signup responden con ?auth=login o ?auth=registro) ----- */
    const parametrosURL = new URLSearchParams(window.location.search);
    const authParam = parametrosURL.get('auth');
    if (authParam === 'login') {
      abrirModal(document.getElementById('authModalLogin'));
    } else if (authParam === 'registro') {
      abrirModal(document.getElementById('authModalRegistro'));
    }

    /* ----- Cerrar con la X o el overlay ----- */
    document.querySelectorAll('[data-modal-close]').forEach(elemento => {
      elemento.addEventListener('click', (evento) => {
        cerrarModal(evento.target.closest('.auth-modal'));
      });
    });

    /* ----- Saltar de un modal a otro ("¿Ya tienes cuenta?" / "Regístrate aquí") ----- */
    document.querySelectorAll('[data-modal-switch]').forEach(boton => {
      boton.addEventListener('click', () => {
        const actual = boton.closest('.auth-modal');
        const destino = document.getElementById(boton.dataset.modalSwitch);
        cerrarModal(actual);
        window.setTimeout(() => abrirModal(destino), 220);
      });
    });

    /* ----- Cerrar con Escape (el modal que esté abierto) ----- */
    document.addEventListener('keydown', (evento) => {
      if (evento.key === 'Escape') {
        modales.forEach(modal => {
          if (modal.classList.contains('is-abierto')) cerrarModal(modal);
        });
      }
    });

    /* ----- Trampa de foco básica dentro de cada modal ----- */
    modales.forEach(modal => {
      modal.addEventListener('keydown', (evento) => {
        if (evento.key !== 'Tab' || !modal.classList.contains('is-abierto')) return;
        const panel = modal.querySelector('.auth-modal__panel');
        const focosVisibles = panel.querySelectorAll('button:not([disabled]), input:not([disabled]), a[href]');
        if (!focosVisibles.length) return;
        const primero = focosVisibles[0];
        const ultimo = focosVisibles[focosVisibles.length - 1];
        if (evento.shiftKey && document.activeElement === primero) {
          evento.preventDefault();
          ultimo.focus();
        } else if (!evento.shiftKey && document.activeElement === ultimo) {
          evento.preventDefault();
          primero.focus();
        }
      });
    });

    /* ----- Mostrar / ocultar contraseña ----- */
    document.querySelectorAll('[data-toggle-pass]').forEach(boton => {
      boton.addEventListener('click', () => {
        const input = document.getElementById(boton.dataset.togglePass);
        if (!input) return;
        const oculto = input.type === 'password';
        input.type = oculto ? 'text' : 'password';
        boton.setAttribute('aria-label', oculto ? 'Ocultar contraseña' : 'Mostrar contraseña');
        boton.style.color = oculto ? 'var(--color-primario)' : '';
      });
    });

    /* ----- Medidor de fuerza de contraseña (registro) ----- */
    const regPassword = document.getElementById('regPassword');
    const medidor = document.querySelector('.auth-form__medidor');
    if (regPassword && medidor) {
      regPassword.addEventListener('input', () => {
        const valor = regPassword.value;
        let nivel = 0;
        if (valor.length >= 6) nivel = 1;
        if (valor.length >= 8 && /[0-9]/.test(valor) && /[A-Za-z]/.test(valor)) nivel = 2;
        if (valor.length >= 10 && /[0-9]/.test(valor) && /[a-z]/.test(valor) && /[A-Z]/.test(valor)) nivel = 3;
        medidor.classList.remove('nivel-1', 'nivel-2', 'nivel-3');
        if (nivel > 0) medidor.classList.add(`nivel-${nivel}`);
      });
    }

    /* ----- Validación en vivo ----- */
    const panelLogin = document.getElementById('panelLogin');
    const panelRegistro = document.getElementById('panelRegistro');

    const marcarEstado = (input, valido) => {
      const campo = input.closest('.auth-form__campo');
      if (!campo) return;
      campo.classList.toggle('is-invalido', !valido);
      campo.classList.toggle('is-valido', valido && input.value.trim() !== '');
      const error = campo.querySelector('.auth-form__error');
      if (error) {
        error.textContent = valido ? '' : (input.validationMessage || 'Revisa este campo.');
      }
    };

    [panelLogin, panelRegistro].forEach(formulario => {
      if (!formulario) return;
      formulario.querySelectorAll('input').forEach(input => {
        input.addEventListener('blur', () => {
          if (input.type === 'checkbox') return;
          marcarEstado(input, input.checkValidity());
        });
        input.addEventListener('input', () => {
          const campo = input.closest('.auth-form__campo');
          if (campo && campo.classList.contains('is-invalido')) {
            marcarEstado(input, input.checkValidity());
          }
        });
      });
    });

    const sacudirPanel = (panel) => {
      if (!panel) return;
      panel.classList.remove('esta-sacudiendo');
      void panel.offsetWidth;
      panel.classList.add('esta-sacudiendo');
    };

    /* ----- Envío (login) -----
       Si hay errores, se bloquea el envío para mostrarlos.
       Si todo es válido, se deja que el navegador mande el
       formulario de verdad a /signin (backend real). ----- */
    if (panelLogin) {
      panelLogin.addEventListener('submit', (evento) => {
        const mensaje = panelLogin.querySelector('[data-mensaje-para="login"]');
        const boton = panelLogin.querySelector('.auth-form__enviar');
        const modal = panelLogin.closest('.auth-modal');
        const panel = modal ? modal.querySelector('.auth-modal__panel') : null;
        let valido = true;

        panelLogin.querySelectorAll('input').forEach(input => {
          const ok = input.checkValidity();
          marcarEstado(input, ok);
          if (!ok) valido = false;
        });

        if (!valido) {
          evento.preventDefault();
          sacudirPanel(panel);
          mensaje.textContent = 'Corrige los campos marcados para continuar.';
          mensaje.classList.add('es-error');
          return;
        }

        // Válido: no se cancela el evento, el formulario se envía al servidor.
        mensaje.classList.remove('es-error');
        boton.classList.add('is-cargando');
        boton.disabled = true;
      });
    }

    /* ----- Envío (registro) -----
       Misma lógica: solo se bloquea si hay errores; si no,
       se envía de verdad a /signup. ----- */
    if (panelRegistro) {
      panelRegistro.addEventListener('submit', (evento) => {
        const mensaje = panelRegistro.querySelector('[data-mensaje-para="registro"]');
        const boton = panelRegistro.querySelector('.auth-form__enviar');
        const modal = panelRegistro.closest('.auth-modal');
        const panel = modal ? modal.querySelector('.auth-modal__panel') : null;
        let valido = true;

        panelRegistro.querySelectorAll('input').forEach(input => {
          if (input.type === 'checkbox') {
            if (!input.checkValidity()) valido = false;
            return;
          }
          const ok = input.checkValidity();
          marcarEstado(input, ok);
          if (!ok) valido = false;
        });

        if (!valido) {
          evento.preventDefault();
          sacudirPanel(panel);
          mensaje.textContent = 'Revisa los campos marcados y acepta los términos.';
          mensaje.classList.add('es-error');
          return;
        }

        // Válido: no se cancela el evento, el formulario se envía al servidor.
        mensaje.classList.remove('es-error');
        boton.classList.add('is-cargando');
        boton.disabled = true;
      });
    }
  }

});
