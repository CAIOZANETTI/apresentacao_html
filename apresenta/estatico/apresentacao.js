// apresenta — interatividade. Só apresentação: nenhuma conta sobre dados (os números vêm prontos do Python).
// Lupa: clique na figura · roda do mouse / pinça = zoom no ponto · arrastar = mover · duplo clique · + − 0 · Esc.
// Slides: → ↓ PageDown Espaço = próximo · ← ↑ PageUp = anterior · Home/End · F = tela cheia · URL #5 abre o slide 5.
(function () {
  'use strict';
  const lupa = document.getElementById('lupa');
  const palco = lupa.querySelector('.lupa-palco');
  const legenda = lupa.querySelector('.lupa-legenda');
  const estado = {alvo: null, largura: 0, altura: 0, escala: 1, ajuste: 1, x: 0, y: 0};
  const ESCALA_MAX = 14;
  const toques = new Map();
  let arraste = null, pinca = null;

  function aplicar() {
    estado.alvo.style.transform = `translate(${estado.x}px,${estado.y}px) scale(${estado.escala})`;
  }

  function ajustar() {
    const w = palco.clientWidth, h = palco.clientHeight;
    estado.ajuste = Math.min(w / estado.largura, h / estado.altura) * 0.94;
    estado.escala = estado.ajuste;
    estado.x = (w - estado.largura * estado.escala) / 2;
    estado.y = (h - estado.altura * estado.escala) / 2;
    aplicar();
  }

  function ampliar(fator, px, py) {
    const nova = Math.min(Math.max(estado.escala * fator, estado.ajuste), estado.ajuste * ESCALA_MAX);
    const real = nova / estado.escala;
    estado.x = px - (px - estado.x) * real;
    estado.y = py - (py - estado.y) * real;
    estado.escala = nova;
    aplicar();
  }

  function abrir(figura) {
    const original = figura.querySelector('.quadro > img, .quadro > svg');
    if (!original) return;
    const copia = original.cloneNode(true);
    if (copia.tagName === 'IMG') {
      estado.largura = original.naturalWidth;
      estado.altura = original.naturalHeight;
    } else {                       // SVG: desenha a 2x do viewBox para nitidez
      const caixa = original.viewBox.baseVal;
      estado.largura = caixa.width * 2;
      estado.altura = caixa.height * 2;
    }
    copia.style.width = estado.largura + 'px';
    copia.style.height = estado.altura + 'px';
    copia.draggable = false;
    palco.replaceChildren(copia);
    estado.alvo = copia;
    const texto = figura.querySelector('figcaption');
    legenda.textContent = texto ? texto.textContent : '';
    lupa.hidden = false;
    ajustar();
  }

  function fechar() { lupa.hidden = true; palco.replaceChildren(); }
  const centro = () => [palco.clientWidth / 2, palco.clientHeight / 2];

  document.addEventListener('click', ev => {
    const figura = ev.target.closest('.ampliavel');
    if (figura && !lupa.contains(figura)) abrir(figura);
  });
  lupa.querySelector('.lupa-fechar').addEventListener('click', fechar);
  lupa.querySelector('[data-acao="mais"]').addEventListener('click', () => ampliar(1.4, ...centro()));
  lupa.querySelector('[data-acao="menos"]').addEventListener('click', () => ampliar(1 / 1.4, ...centro()));
  lupa.querySelector('[data-acao="ajustar"]').addEventListener('click', ajustar);

  palco.addEventListener('wheel', ev => {
    ev.preventDefault();
    const r = palco.getBoundingClientRect();
    // pinça do trackpad chega como wheel com ctrlKey: zoom proporcional e suave
    const fator = ev.ctrlKey ? Math.exp(-ev.deltaY * 0.01) : (ev.deltaY < 0 ? 1.18 : 1 / 1.18);
    ampliar(fator, ev.clientX - r.left, ev.clientY - r.top);
  }, {passive: false});

  palco.addEventListener('dblclick', ev => {
    const r = palco.getBoundingClientRect();
    if (estado.escala > estado.ajuste * 1.5) ajustar();
    else ampliar(3, ev.clientX - r.left, ev.clientY - r.top);
  });

  palco.addEventListener('pointerdown', ev => {
    palco.setPointerCapture(ev.pointerId);
    toques.set(ev.pointerId, {x: ev.clientX, y: ev.clientY});
    if (toques.size === 1) arraste = {x: ev.clientX, y: ev.clientY};
    if (toques.size === 2) { const [a, b] = [...toques.values()]; pinca = Math.hypot(a.x - b.x, a.y - b.y); }
    palco.classList.add('arrastando');
  });
  palco.addEventListener('pointermove', ev => {
    if (!toques.has(ev.pointerId)) return;
    toques.set(ev.pointerId, {x: ev.clientX, y: ev.clientY});
    if (toques.size === 2 && pinca) {
      const [a, b] = [...toques.values()];
      const d = Math.hypot(a.x - b.x, a.y - b.y), r = palco.getBoundingClientRect();
      ampliar(d / pinca, (a.x + b.x) / 2 - r.left, (a.y + b.y) / 2 - r.top);
      pinca = d;
    } else if (arraste) {
      estado.x += ev.clientX - arraste.x;
      estado.y += ev.clientY - arraste.y;
      arraste = {x: ev.clientX, y: ev.clientY};
      aplicar();
    }
  });
  function soltar(ev) {
    toques.delete(ev.pointerId);
    if (toques.size < 2) pinca = null;
    if (toques.size === 0) { arraste = null; palco.classList.remove('arrastando'); }
  }
  palco.addEventListener('pointerup', soltar);
  palco.addEventListener('pointercancel', soltar);

  // ---- navegação entre slides (rolagem vertical com encaixe) ----
  const slides = [...document.querySelectorAll('.slide')];
  function atual() {
    const meio = window.innerHeight / 2;
    const i = slides.findIndex(s => { const c = s.getBoundingClientRect(); return c.top <= meio && c.bottom >= meio; });
    return i < 0 ? 0 : i;
  }
  function vai(i, suave = true) {
    const alvo = slides[Math.min(Math.max(i, 0), slides.length - 1)];
    alvo.scrollIntoView({behavior: suave ? 'smooth' : 'auto', block: 'center'});
    history.replaceState(null, '', '#' + (slides.indexOf(alvo) + 1));
  }
  document.addEventListener('keydown', ev => {
    if (!lupa.hidden) {
      const [cx, cy] = centro(), passo = 80;
      if (ev.key === 'Escape') fechar();
      else if (ev.key === '+' || ev.key === '=') ampliar(1.4, cx, cy);
      else if (ev.key === '-') ampliar(1 / 1.4, cx, cy);
      else if (ev.key === '0') ajustar();
      else if (ev.key === 'ArrowLeft') { estado.x += passo; aplicar(); }
      else if (ev.key === 'ArrowRight') { estado.x -= passo; aplicar(); }
      else if (ev.key === 'ArrowUp') { estado.y += passo; aplicar(); }
      else if (ev.key === 'ArrowDown') { estado.y -= passo; aplicar(); }
      else return;
      ev.preventDefault();
      return;
    }
    if (ev.ctrlKey || ev.metaKey || ev.altKey) return;
    const PROX = ['ArrowRight', 'ArrowDown', 'PageDown', ' '], ANT = ['ArrowLeft', 'ArrowUp', 'PageUp'];
    if (PROX.includes(ev.key)) { ev.preventDefault(); vai(atual() + 1); }
    else if (ANT.includes(ev.key)) { ev.preventDefault(); vai(atual() - 1); }
    else if (ev.key === 'Home') { ev.preventDefault(); vai(0); }
    else if (ev.key === 'End') { ev.preventDefault(); vai(slides.length - 1); }
    else if (ev.key === 'f' || ev.key === 'F') {
      if (document.fullscreenElement) document.exitFullscreen(); else document.documentElement.requestFullscreen();
    }
  });
  window.addEventListener('resize', () => { if (!lupa.hidden) ajustar(); });
  const n = parseInt(location.hash.slice(1), 10);
  if (n > 1) vai(n - 1, false);
})();
