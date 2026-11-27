"""Gera as imagens FICTÍCIAS do exemplo (determinístico: semente fixa).

Num projeto real, as imagens vêm de:
  - pranchas em PDF  -> python -m apresenta imagens prancha.pdf -p 3 --recorte ... -o img -n corte
  - fotos de drone / ortofotos / Google Earth -> JPG recortado, até ~1600 px de largura
Rodar:  python exemplos/completo/gerar_imagens.py
"""
from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

PASTA = Path(__file__).resolve().parent / "img"


def terreno(w: int, h: int, semente: int, ruas: bool = True) -> Image.Image:
    """Vista aérea fictícia: quadras, ruas e vegetação."""
    rnd = random.Random(semente)
    im = Image.new("RGB", (w, h), (92, 112, 74))
    d = ImageDraw.Draw(im)
    for _ in range(int(w * h / 900)):
        x, y, r = rnd.randrange(w), rnd.randrange(h), rnd.randrange(4, 18)
        g = rnd.randrange(70, 125)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(g - 25, g, g - 40))
    if ruas:
        passo = max(60, w // 14)
        for x in range(rnd.randrange(passo), w, passo):
            d.line((x, 0, x + rnd.randrange(-40, 40), h), fill=(150, 148, 140), width=7)
        for y in range(rnd.randrange(passo), h, passo):
            d.line((0, y, w, y + rnd.randrange(-30, 30)), fill=(150, 148, 140), width=7)
        for _ in range(int(w * h / 5000)):
            x, y = rnd.randrange(w), rnd.randrange(h)
            c = rnd.choice([(205, 200, 190), (170, 90, 70), (215, 215, 210), (120, 120, 125)])
            d.rectangle((x, y, x + rnd.randrange(12, 40), y + rnd.randrange(10, 30)), fill=c)
    return im.filter(ImageFilter.GaussianBlur(0.8))


def estacao(w: int, h: int, semente: int, sobreposicao: bool = False) -> Image.Image:
    """Foto aérea fictícia de uma estação de tratamento (tanques e prédios)."""
    rnd = random.Random(semente)
    im = terreno(w, h, semente, ruas=False)
    d = ImageDraw.Draw(im)
    d.rectangle((w * .08, h * .55, w * .95, h * .63), fill=(140, 138, 130))
    for i in range(5):
        x = w * (.15 + i * .14)
        d.rectangle((x, h * .2, x + w * .1, h * .5), fill=(185, 190, 192), outline=(90, 90, 90), width=3)
        d.rectangle((x + 8, h * .24, x + w * .1 - 8, h * .46), fill=(60, 95, 110))
    for i in range(3):
        cx, cy, r = w * (.2 + i * .12), h * .78, w * .045
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(200, 200, 195), outline=(90, 90, 90), width=3)
    if sobreposicao:
        d.rectangle((w * .62, h * .66, w * .9, h * .92), outline=(47, 111, 214), width=8)
        d.rectangle((w * .1, h * .66, w * .5, h * .95), outline=(162, 79, 176), width=8)
        d.rectangle((w * .14, h * .18, w * .86, h * .52), outline=(95, 191, 98), width=8)
    return im


def svg_corte(n_estacas: int, comprimentos: list[int], titulo: str) -> str:
    W, H = 2200, 900
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Arial">',
         f'<rect width="{W}" height="{H}" fill="#fff"/>',
         f'<text x="80" y="70" font-size="40" font-weight="bold">{titulo} — EXEMPLO FICTÍCIO</text>',
         '<rect x="100" y="200" width="2000" height="80" fill="#e5e5e5" stroke="#222" stroke-width="4"/>']
    for i in range(6):
        x = 160 + i * 380
        s.append(f'<rect x="{x}" y="110" width="22" height="90" fill="#fff" stroke="#222" stroke-width="3"/>')
        s.append(f'<text x="{x + 30}" y="150" font-size="18">PAR {i + 1:02d}</text>')
    for i in range(n_estacas):
        x = 150 + i * (1900 / max(1, n_estacas - 1))
        L = comprimentos[i % len(comprimentos)]
        s.append(f'<rect x="{x - 12:.1f}" y="280" width="24" height="{L * 36}" fill="#bbb" stroke="#222" stroke-width="2"/>')
        s.append(f'<text x="{x + 16:.1f}" y="{290 + L * 36}" font-size="16">L={L} m</text>')
    s.append('<line x1="60" y1="280" x2="2140" y2="280" stroke="#7a5230" stroke-width="4" stroke-dasharray="20 10"/>')
    s.append('<text x="1700" y="860" font-size="26">CORTE A-A · ESC. 1:50</text></svg>')
    return "\n".join(s)


def svg_locacao(colunas: int, linhas: int) -> str:
    W, H = 1300, 1500
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Arial">',
         f'<rect width="{W}" height="{H}" fill="#fff"/>',
         '<rect x="100" y="120" width="1100" height="1260" fill="none" stroke="#222" stroke-width="5"/>',
         '<text x="100" y="80" font-size="36" font-weight="bold">LOCAÇÃO DAS ESTACAS — EXEMPLO</text>']
    k = 0
    for i in range(colunas):
        for j in range(linhas):
            k += 1
            x, y = 180 + i * (940 / max(1, colunas - 1)), 200 + j * (1100 / max(1, linhas - 1))
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="20" fill="none" stroke="#b42318" stroke-width="4"/>')
            s.append(f'<text x="{x + 24:.1f}" y="{y - 22:.1f}" font-size="16">E{k:02d}</text>')
    s.append("</svg>")
    return "\n".join(s)


def main() -> None:
    PASTA.mkdir(exist_ok=True)
    estacao(1250, 1000, 1).save(PASTA / "capa_estacao.jpg", quality=85)
    estacao(1000, 850, 2).save(PASTA / "estacao_hoje.jpg", quality=85)
    estacao(1100, 940, 2, sobreposicao=True).save(PASTA / "estacao_intervencoes.jpg", quality=85)
    terreno(1600, 1345, 3).save(PASTA / "mapa_geral.jpg", quality=82)
    terreno(1600, 780, 4).save(PASTA / "mapa_adutora_a.jpg", quality=82)
    terreno(1600, 840, 5).save(PASTA / "mapa_adutora_b.jpg", quality=82)
    for nome, sem in (("foto_trecho_lt", 6), ("foto_avenida", 7), ("foto_pavimento", 8)):
        terreno(900, 620, sem).save(PASTA / f"{nome}.jpg", quality=82)
    (PASTA / "corte_modulo_a.svg").write_text(svg_corte(9, [8, 12, 16], "MÓDULO A — CORTE LONGITUDINAL"), encoding="utf-8")
    (PASTA / "corte_modulo_b.svg").write_text(svg_corte(12, [9, 14, 16, 11], "MÓDULO B — CORTE LONGITUDINAL"), encoding="utf-8")
    (PASTA / "locacao_modulo_a.svg").write_text(svg_locacao(5, 8), encoding="utf-8")
    (PASTA / "locacao_modulo_b.svg").write_text(svg_locacao(8, 11), encoding="utf-8")
    for p in sorted(PASTA.iterdir()):
        print(f"  {p.name}  {p.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
