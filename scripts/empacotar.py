"""
Gera a versão final da apresentação em UM ÚNICO arquivo HTML (para enviar por e-mail,
abrir offline, apresentar em qualquer computador):

1. Embute todas as imagens <img src="img/..."> como base64 (sem recomprimir — mantém a nitidez da ampliação).
2. Substitui o bloco <script type="application/json" id="dados"> pelo conteúdo do dados.json.
3. Informa o tamanho final e avisa sobre imagens ausentes.

Uso
---
python scripts/empacotar.py projetos/minha/apresentacao.html
python scripts/empacotar.py projetos/minha/apresentacao.html -d projetos/minha/dados.json -o dist/APRESENTACAO.html

Padrões: dados.json na mesma pasta do HTML (se existir); saída em <pasta>/dist/<NOME>.html
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import re
from pathlib import Path

MIME_EXTRA = {".svg": "image/svg+xml", ".webp": "image/webp"}
RE_IMG = re.compile(r'(<img\b[^>]*?\bsrc=")([^"]+)(")', re.IGNORECASE)
RE_DADOS = re.compile(r'(<script type="application/json" id="dados">)(.*?)(</script>)', re.DOTALL)


def data_uri(arquivo: Path) -> str:
    mime = MIME_EXTRA.get(arquivo.suffix.lower()) or mimetypes.guess_type(arquivo.name)[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(arquivo.read_bytes()).decode("ascii")


def empacota(html_path: Path, dados_path: Path | None, saida: Path) -> Path:
    html = html_path.read_text(encoding="utf-8")
    base = html_path.parent
    faltando: list[str] = []
    embutidas = 0

    def troca(m: re.Match) -> str:
        nonlocal embutidas
        src = m.group(2)
        if src.startswith(("data:", "http://", "https://")):
            return m.group(0)
        arq = (base / src).resolve()
        if not arq.exists():
            faltando.append(src)
            return m.group(0)
        embutidas += 1
        return m.group(1) + data_uri(arq) + m.group(3)

    html = RE_IMG.sub(troca, html)

    if dados_path and dados_path.exists():
        dados = json.loads(dados_path.read_text(encoding="utf-8"))  # valida o JSON
        bloco = "\n" + json.dumps(dados, ensure_ascii=False, indent=2) + "\n"
        html, n = RE_DADOS.subn(lambda m: m.group(1) + bloco + m.group(3), html, count=1)
        print(f"dados: {dados_path} {'aplicado' if n else 'NÃO aplicado (bloco id=dados não encontrado)'}")

    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(html, encoding="utf-8")
    mb = saida.stat().st_size / 1024 ** 2
    print(f"imagens embutidas: {embutidas}")
    for f in faltando:
        print(f"  AVISO: imagem não encontrada: {f}")
    print(f"saída: {saida}  ({mb:.2f} MB)")
    if mb > 15:
        print("  AVISO: arquivo grande para e-mail; recorte as figuras ou reduza o dpi das maiores.")
    return saida


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html", type=Path)
    ap.add_argument("-d", "--dados", type=Path)
    ap.add_argument("-o", "--saida", type=Path)
    a = ap.parse_args()
    dados = a.dados or (a.html.parent / "dados.json")
    saida = a.saida or (a.html.parent / "dist" / f"{a.html.stem.upper()}.html")
    empacota(a.html, dados, saida)


if __name__ == "__main__":
    main()
