/* =========================================================
   Desplegables del nav: categorías/rubros y menú de cuenta
   Pega este bloque dentro de tu DOMContentLoaded, junto a
   los demás bloques de script.js
   ========================================================= */

const desplegables = document.querySelectorAll('.nav__dropdown, .nav__cuenta');

if (desplegables.length) {
  const cerrarTodos = (excepto) => {
    desplegables.forEach(el => {
      if (el !== excepto) {
        el.classList.remove('is-abierto');
        const btn = el.querySelector('[aria-expanded]');
        if (btn) btn.setAttribute('aria-expanded', 'false');
      }
    });
  };

  desplegables.forEach(el => {
    const boton = el.querySelector('[aria-expanded]');
    if (!boton) return;

    boton.addEventListener('click', (evento) => {
      evento.stopPropagation();
      const abierto = el.classList.contains('is-abierto');
      cerrarTodos(el);
      el.classList.toggle('is-abierto', !abierto);
      boton.setAttribute('aria-expanded', String(!abierto));
    });
  });

  document.addEventListener('click', () => cerrarTodos(null));

  document.addEventListener('keydown', (evento) => {
    if (evento.key === 'Escape') cerrarTodos(null);
  });
}
