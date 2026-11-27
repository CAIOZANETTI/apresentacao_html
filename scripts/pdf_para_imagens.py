"""
Renderiza páginas (ou recortes) de PDFs de projeto em PNG de alta resolução,
para usar como figuras ampliáveis na apresentação.

Exemplos
--------
# listar páginas e tamanhos
python scripts/pdf_para_imagens.py projeto.pdf --listar

# página 3 inteira a 200 dpi
python scripts/pdf_para_imagens.py projeto.pdf -p 3 --dpi 200 -o projetos/minha/img -n planta

# recorte da página 5 (frações da página: x0,y0,x1,y1 — 0 = esquerda/topo, 1 = direita/base)
python scripts/pdf_para_imagens.py projeto.pdf -p 5 --recorte 0.05,0.10,0.70,0.85 -o projetos/minha/img -n corte_AA

# várias páginas
python scripts/pdf_para_imagens.py projeto.pdf -p 1,2,7-9 -o projetos/minha/img

Dicas
-----
- 200 dpi é um bom padrão para pranchas A1/A0; 250–300 dpi para detalhes com texto pequeno.
- Recorte antes de aumentar o dpi: o tamanho do arquivo cresce com a área.
- Não comprima em JPEG: PNG mantém linhas e textos nítidos na ampliação.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pymupdf


def faixa_paginas(texto: str, total: int) -> list[int]:
    """'1,3,5-7' -> [1,3,5,6,7] (base 1)."""
    paginas: list[int] = []
    for parte in texto.split(","):
        parte = parte.strip()
        if "-" in parte:
            a, b = parte.split("-")
            paginas.extend(range(int(a), int(b) + 1))
        elif parte:
            paginas.append(int(parte))
    for p in paginas:
        if not 1 <= p <= total:
            raise SystemExit(f"página {p} fora do intervalo 1..{total}")
    return paginas


def renderiza(pdf: Path, pagina: int, dpi: int, recorte: tuple[float, float, float, float] | None,
              saida: Path, rotacao: int = 0) -> Path:
    doc = pymupdf.open(pdf)
    pg = doc[pagina - 1]
    clip = None
    if recorte:
        r = pg.rect
        x0, y0, x1, y1 = recorte
        clip = pymupdf.Rect(r.x0 + x0 * r.width, r.y0 + y0 * r.height,
                            r.x0 + x1 * r.width, r.y0 + y1 * r.height)
    mat = pymupdf.Matrix(dpi / 72, dpi / 72).prerotate(rotacao)
    pix = pg.get_pixmap(matrix=mat, clip=clip, alpha=False)
    saida.parent.mkdir(parents=True, exist_ok=True)
    pix.save(saida)
    kb = saida.stat().st_size / 1024
    print(f"  {saida}  {pix.width}x{pix.height}px  {kb:,.0f} KB")
    return saida


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("-p", "--paginas", default="1", help="ex.: 1,3,5-7 (base 1)")
    ap.add_argument("--dpi", type=int, default=200)
    ap.add_argument("--recorte", help="x0,y0,x1,y1 em frações da página (0–1)")
    ap.add_argument("--rotacao", type=int, default=0, choices=[0, 90, 180, 270])
    ap.add_argument("-o", "--saida", type=Path, default=Path("img"))
    ap.add_argument("-n", "--nome", help="nome base do arquivo (padrão: nome do PDF)")
    ap.add_argument("--listar", action="store_true", help="só lista páginas e tamanhos")
    a = ap.parse_args()

    doc = pymupdf.open(a.pdf)
    if a.listar:
        print(f"{a.pdf.name}: {doc.page_count} páginas")
        for i, pg in enumerate(doc, 1):
            w, h = pg.rect.width / 72 * 25.4, pg.rect.height / 72 * 25.4
            titulo = (pg.get_text().strip().splitlines() or [""])[0][:60]
            print(f"  p{i:>3}: {w:,.0f} x {h:,.0f} mm  {titulo}")
        return

    recorte = tuple(float(v) for v in a.recorte.split(",")) if a.recorte else None
    if recorte and (len(recorte) != 4 or not all(0 <= v <= 1 for v in recorte)):
        raise SystemExit("--recorte precisa de 4 frações entre 0 e 1: x0,y0,x1,y1")

    paginas = faixa_paginas(a.paginas, doc.page_count)
    base = a.nome or a.pdf.stem
    for p in paginas:
        nome = f"{base}.png" if len(paginas) == 1 else f"{base}_p{p:02d}.png"
        renderiza(a.pdf, p, a.dpi, recorte, a.saida / nome, a.rotacao)


if __name__ == "__main__":
    main()
