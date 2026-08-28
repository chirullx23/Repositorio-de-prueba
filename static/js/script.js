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
     Comparte lógica entre el MODAL de index.html y la página
     independiente index-auth.html — solo UI, sin backend real.
     ========================================================= */
  const modal = document.getElementById('authModal');       // solo existe en index.html
  const overlay = document.getElementById('authOverlay');   // solo existe en index.html
  const panel = document.getElementById('authPanel');
  const btnCerrar = document.getElementById('authCerrar');  // solo existe en index.html
  const titulo = document.getElementById('authModalTitulo');
  const subtitulo = document.getElementById('authModalSubtitulo');
  const pie = document.getElementById('authPie');
  const track = document.getElementById('authTrack');
  const indicador = document.getElementById('authIndicador');
  const tabLogin = document.getElementById('tabLogin');
  const tabRegistro = document.getElementById('tabRegistro');
  const panelLogin = document.getElementById('panelLogin');
  const panelRegistro = document.getElementById('panelRegistro');

  // "track" es el elemento común a ambos contextos (modal y página independiente).
  // Si existe, esta página tiene el formulario de autenticación y hay que inicializarlo.
  if (track && tabLogin && tabRegistro && panelLogin && panelRegistro) {
    const TEXTOS = {
      login: {
        titulo: 'Bienvenido de vuelta',
        subtitulo: 'Ingresa a tu cuenta Sonricks Store',
        pie: '¿Aún no tienes cuenta? <button type="button" class="auth-modal__enlace" data-tab-ir="registro">Regístrate aquí</button>'
      },
      registro: {
        titulo: 'Únete a Sonricks',
        subtitulo: 'Crea tu cuenta y golpea con estilo',
        pie: '¿Ya tienes cuenta? <button type="button" class="auth-modal__enlace" data-tab-ir="login">Inicia sesión</button>'
      }
    };

    /* ----- Cambiar entre pestañas (login / registro) ----- */
    function cambiarPestaña(destino, animar = true) {
      const esRegistro = destino === 'registro';

      tabLogin.classList.toggle('is-activa', !esRegistro);
      tabLogin.setAttribute('aria-selected', String(!esRegistro));
      tabRegistro.classList.toggle('is-activa', esRegistro);
      tabRegistro.setAttribute('aria-selected', String(esRegistro));
      if (indicador) indicador.classList.toggle('is-derecha', esRegistro);

      track.classList.toggle('is-registro', esRegistro);
      track.style.transition = animar ? '' : 'none';

      panelLogin.hidden = esRegistro;
      panelRegistro.hidden = !esRegistro;

      if (titulo) titulo.textContent = TEXTOS[destino].titulo;
      if (subtitulo) subtitulo.textContent = TEXTOS[destino].subtitulo;
      if (pie) pie.innerHTML = TEXTOS[destino].pie;

      if (!animar) {
        // fuerza reflow para restaurar la transición después del salto instantáneo
        void track.offsetHeight;
        track.style.transition = '';
      }
    }

    tabLogin.addEventListener('click', () => cambiarPestaña('login'));
    tabRegistro.addEventListener('click', () => cambiarPestaña('registro'));

    document.addEventListener('click', (evento) => {
      const enlace = evento.target.closest('[data-tab-ir]');
      if (enlace) cambiarPestaña(enlace.dataset.tabIr);
    });

    if (modal) {
      /* ================= CONTEXTO: MODAL (index.html) ================= */
      let ultimoFoco = null;

      const abrirModal = (pestañaInicial = 'login') => {
        ultimoFoco = document.activeElement;
        cambiarPestaña(pestañaInicial, false);
        modal.classList.add('is-abierto');
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
        const primerCampo = (pestañaInicial === 'login' ? panelLogin : panelRegistro).querySelector('input');
        window.setTimeout(() => primerCampo && primerCampo.focus(), 320);
      };

      const cerrarModal = () => {
        modal.classList.remove('is-abierto');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        if (ultimoFoco) ultimoFoco.focus();
      };

      document.querySelectorAll('[data-modal-open]').forEach(boton => {
        boton.addEventListener('click', () => abrirModal(boton.dataset.modalOpen === 'registro' ? 'registro' : 'login'));
      });

      if (btnCerrar) btnCerrar.addEventListener('click', cerrarModal);
      if (overlay) overlay.addEventListener('click', cerrarModal);

      document.addEventListener('keydown', (evento) => {
        if (evento.key === 'Escape' && modal.classList.contains('is-abierto')) {
          cerrarModal();
        }
      });

      // Trampa de foco básica dentro del modal
      modal.addEventListener('keydown', (evento) => {
        if (evento.key !== 'Tab' || !modal.classList.contains('is-abierto')) return;
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

      // Al terminar login/registro con éxito, el modal se cierra solo
      window.sonricksAuthAlTerminar = () => window.setTimeout(cerrarModal, 1400);

    } else {
      /* ========== CONTEXTO: PÁGINA INDEPENDIENTE (index-auth.html) ========== */
      // Los botones "Iniciar sesión" / "Registro" del nav solo cambian de
      // pestaña y llevan el scroll hasta la tarjeta, ya que no hay overlay.
      document.querySelectorAll('[data-modal-open]').forEach(boton => {
        boton.addEventListener('click', (evento) => {
          evento.preventDefault();
          cambiarPestaña(boton.dataset.modalOpen === 'registro' ? 'registro' : 'login');
          panel.scrollIntoView({ behavior: 'smooth', block: 'center' });
        });
      });

      // Si la URL trae #registro, abre directamente esa pestaña
      if (window.location.hash === '#registro') cambiarPestaña('registro', false);

      window.sonricksAuthAlTerminar = () => {};
    }

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

    const sacudirPanel = () => {
      panel.classList.remove('esta-sacudiendo');
      void panel.offsetWidth;
      panel.classList.add('esta-sacudiendo');
    };

    /* ----- Envío simulado (login) ----- */
    panelLogin.addEventListener('submit', (evento) => {
      evento.preventDefault();
      const mensaje = panelLogin.querySelector('[data-mensaje-para="login"]');
      const boton = panelLogin.querySelector('.auth-form__enviar');
      let valido = true;

      panelLogin.querySelectorAll('input').forEach(input => {
        const ok = input.checkValidity();
        marcarEstado(input, ok);
        if (!ok) valido = false;
      });

      if (!valido) {
        sacudirPanel();
        mensaje.textContent = 'Corrige los campos marcados para continuar.';
        mensaje.classList.add('es-error');
        return;
      }

      mensaje.classList.remove('es-error');
      boton.classList.add('is-cargando');
      boton.disabled = true;

      window.setTimeout(() => {
        boton.classList.remove('is-cargando');
        boton.disabled = false;
        const correo = panelLogin.querySelector('#loginEmail').value;
        mensaje.textContent = `¡Sesión iniciada! Bienvenido, ${correo}.`;
        window.sonricksAuthAlTerminar();
      }, 1100);
    });

    /* ----- Envío simulado (registro) ----- */
    panelRegistro.addEventListener('submit', (evento) => {
      evento.preventDefault();
      const mensaje = panelRegistro.querySelector('[data-mensaje-para="registro"]');
      const boton = panelRegistro.querySelector('.auth-form__enviar');
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
        sacudirPanel();
        mensaje.textContent = 'Revisa los campos marcados y acepta los términos.';
        mensaje.classList.add('es-error');
        return;
      }

      mensaje.classList.remove('es-error');
      boton.classList.add('is-cargando');
      boton.disabled = true;

      window.setTimeout(() => {
        boton.classList.remove('is-cargando');
        boton.disabled = false;
        const nombre = panelRegistro.querySelector('#regNombre').value;
        mensaje.textContent = `¡Cuenta creada! Nos vemos en la cancha, ${nombre}.`;
        window.sonricksAuthAlTerminar();
      }, 1100);
    });
  }

});
