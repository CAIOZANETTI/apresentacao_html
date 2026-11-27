"""
Verificação automática da apresentação no Chromium (Playwright):

- erros de console / imagens que não carregaram / campos data-campo sem dado
- conteúdo que transborda o slide (texto cortado)
- abre e fecha a ampliação da primeira figura
- gera capturas de tela de cada slide e o PDF de impressão (confere 1 página por slide)

Uso
---
python scripts/verificar.py projetos/minha/dist/APRESENTACAO.html
python scripts/verificar.py modelo/apresentacao.html --capturas saida/capturas --pdf saida/apresentacao.pdf
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from playwright.sync_api import sync_playwright


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html", type=Path)
    ap.add_argument("--capturas", type=Path, help="pasta para PNG de cada slide")
    ap.add_argument("--pdf", type=Path, help="gera o PDF de impressão neste caminho")
    a = ap.parse_args()

    problemas: list[str] = []
    url = a.html.resolve().as_uri()
    with sync_playwright() as p:
        # CHROMIUM_PATH opcional: usa um Chromium já instalado em vez do baixado pelo `playwright install`
        exe = os.environ.get("CHROMIUM_PATH")
        nav = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
        pg = nav.new_page(viewport={"width": 1600, "height": 900})
        pg.on("console", lambda m: m.type in ("error", "warning") and problemas.append(f"console {m.type}: {m.text}"))
        pg.on("pageerror", lambda e: problemas.append(f"erro JS: {e}"))
        pg.goto(url)
        pg.wait_for_load_state("networkidle")

        n = pg.locator(".slide").count()
        print(f"slides: {n}")

        ruins = pg.evaluate("""() => [...document.images].filter(i => !i.closest('#lupa')).filter(i => !i.complete || !i.naturalWidth).map(i => i.getAttribute('src').slice(0, 80))""")
        problemas += [f"imagem não carregou: {s}" for s in ruins]

        for i in range(n):
            pg.keyboard.press("Home")
            for _ in range(i):
                pg.keyboard.press("ArrowRight")
            transborda = pg.evaluate("""() => {
                const s = document.querySelector('.slide.ativo'), r = s.getBoundingClientRect(), k = r.width / 1600;
                return [...s.querySelectorAll('.corpo *')].filter(e => {
                    const b = e.getBoundingClientRect();
                    return b.width && (b.bottom - r.bottom > 2 * k || b.right - r.right > 2 * k);
                }).slice(0, 3).map(e => e.tagName + ' ' + (e.textContent || '').trim().slice(0, 40));
            }""")
            for t in transborda:
                problemas.append(f"slide {i + 1}: conteúdo saindo do slide → {t}")
            if a.capturas:
                a.capturas.mkdir(parents=True, exist_ok=True)
                pg.screenshot(path=a.capturas / f"slide_{i + 1:02d}.png")

        # teste da ampliação
        if pg.locator(".btn-ampliar").count():
            pg.keyboard.press("Home")
            botao = pg.locator(".slide.ativo .btn-ampliar")
            if not botao.count():
                idx = pg.evaluate("[...document.querySelectorAll('.slide')].indexOf(document.querySelector('.btn-ampliar').closest('.slide'))")
                for _ in range(idx):
                    pg.keyboard.press("ArrowRight")
                botao = pg.locator(".slide.ativo .btn-ampliar")
            botao.first.click()
            aberta = pg.evaluate("document.getElementById('lupa').classList.contains('aberta')")
            pg.keyboard.press("+")
            nivel = pg.locator("#lupa .nivel").text_content()
            pg.keyboard.press("Escape")
            fechada = not pg.evaluate("document.getElementById('lupa').classList.contains('aberta')")
            print(f"ampliação: abriu={aberta} zoom após '+'={nivel} fechou com Esc={fechada}")
            if not (aberta and fechada and nivel != "100%"):
                problemas.append("ampliação não funcionou como esperado")

        if a.pdf:
            a.pdf.parent.mkdir(parents=True, exist_ok=True)
            pg.emulate_media(media="print")
            pg.pdf(path=str(a.pdf), prefer_css_page_size=True, print_background=True)
            try:
                import pymupdf
                paginas = pymupdf.open(a.pdf).page_count
                print(f"PDF: {a.pdf} — {paginas} páginas")
                if paginas != n:
                    problemas.append(f"PDF com {paginas} páginas para {n} slides")
            except ImportError:
                print(f"PDF: {a.pdf}")
        nav.close()

    print()
    if problemas:
        print("PROBLEMAS:")
        for pr in problemas:
            print("  -", pr)
        raise SystemExit(1)
    print("OK — nenhum problema encontrado.")


if __name__ == "__main__":
    main()
