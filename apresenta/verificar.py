"""Verificação da apresentação montada, no Chromium (Playwright).

Checa, em tela de 1600 x 900:
- erros de JavaScript / console e imagens que não carregaram
- conteúdo do corpo que passa do limite (invade fonte/rodapé ou sai do slide)
- letra menor que o mínimo (padrão 14 px; texto dentro de gráficos SVG não conta — é ampliável)
- lupa: abre na primeira figura ampliável, aproxima com '+', fecha com Esc
- impressão: PDF com 1 página por slide
Opcional: captura PNG de cada slide (para revisão visual) e o PDF.
"""
from __future__ import annotations

import os
from pathlib import Path

JS_MEDIDAS = """(minPx) => {
  const res = [];
  document.querySelectorAll('.slide').forEach((s, i) => {
    const corpo = s.querySelector('.corpo');
    if (!corpo) return;
    const r = corpo.getBoundingClientRect();
    const fora = [...corpo.querySelectorAll('*')].filter(e => {
      if (e.closest('svg') && e.tagName.toLowerCase() !== 'svg') return false;
      const b = e.getBoundingClientRect();
      return b.width > 0 && (b.bottom > r.bottom + 2 || b.right > r.right + 2);
    }).slice(0, 3).map(e => e.tagName.toLowerCase() + ': ' + (e.textContent || '').trim().slice(0, 50));
    const pequenos = new Set();
    const w = document.createTreeWalker(s, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = w.nextNode())) {
      const el = n.parentElement;
      if (!n.textContent.trim() || el.closest('svg') || el.closest('.notas-orador')) continue;
      const tam = parseFloat(getComputedStyle(el).fontSize);
      if (tam < minPx) pequenos.add(tam.toFixed(1) + 'px "' + n.textContent.trim().slice(0, 30) + '"');
    }
    res.push({slide: i + 1, fora, pequenos: [...pequenos].slice(0, 3)});
  });
  return res;
}"""


def verificar(html: Path, capturas: Path | None = None, pdf: Path | None = None, min_px: float = 14.0) -> list[str]:
    from playwright.sync_api import sync_playwright

    problemas: list[str] = []
    with sync_playwright() as p:
        exe = os.environ.get("CHROMIUM_PATH")
        nav = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
        pg = nav.new_page(viewport={"width": 1600, "height": 900})
        pg.on("console", lambda m: m.type == "error" and problemas.append(f"console: {m.text}"))
        pg.on("pageerror", lambda e: problemas.append(f"erro JS: {e}"))
        pg.goto(Path(html).resolve().as_uri())
        pg.wait_for_load_state("load")
        n = pg.locator(".slide").count()
        print(f"slides: {n}")

        ruins = pg.evaluate("[...document.images].filter(i => !i.complete || !i.naturalWidth).length")
        if ruins:
            problemas.append(f"{ruins} imagem(ns) não carregaram")

        for m in pg.evaluate(JS_MEDIDAS, min_px):
            for t in m["fora"]:
                problemas.append(f"slide {m['slide']}: conteúdo passa do limite do corpo → {t}")
            for t in m["pequenos"]:
                problemas.append(f"slide {m['slide']}: letra abaixo de {min_px:g}px → {t}")

        if capturas:
            capturas.mkdir(parents=True, exist_ok=True)
            for i in range(n):
                pg.locator(".slide").nth(i).screenshot(path=str(capturas / f"slide_{i + 1:02d}.png"))
            print(f"capturas: {capturas}")

        fig = pg.locator(".ampliavel").first
        if fig.count():
            fig.scroll_into_view_if_needed()
            fig.click()
            aberta = pg.evaluate("!document.getElementById('lupa').hidden")
            antes = pg.evaluate("getComputedStyle(document.querySelector('.lupa-palco > *')).transform")
            pg.keyboard.press("+")
            depois = pg.evaluate("getComputedStyle(document.querySelector('.lupa-palco > *')).transform")
            pg.keyboard.press("Escape")
            fechada = pg.evaluate("document.getElementById('lupa').hidden")
            ok = aberta and fechada and antes != depois
            print(f"lupa: {'ok' if ok else 'FALHOU'}")
            if not ok:
                problemas.append("lupa não abriu/aproximou/fechou como esperado")

        if pdf:
            pdf.parent.mkdir(parents=True, exist_ok=True)
            pg.emulate_media(media="print")
            pg.pdf(path=str(pdf), prefer_css_page_size=True, print_background=True)
            try:
                import pymupdf
                paginas = pymupdf.open(pdf).page_count
                print(f"pdf: {pdf} ({paginas} páginas)")
                if paginas != n:
                    problemas.append(f"PDF com {paginas} páginas para {n} slides")
            except ImportError:
                print(f"pdf: {pdf}")
        nav.close()
    return problemas
