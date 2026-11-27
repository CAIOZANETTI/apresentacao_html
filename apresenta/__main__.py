"""Linha de comando.

    python -m apresenta novo projetos/2027_minha_obra        # copia o exemplo completo
    python -m apresenta montar projetos/2027_minha_obra      # gera dist/<ARQUIVO>.html
    python -m apresenta verificar projetos/2027_minha_obra   # monta + testa no Chromium + capturas + PDF
    python -m apresenta imagens arquivo.pdf --listar         # PDF de projeto -> PNG/JPG
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from .erros import ErroApresentacao
from .montar import RAIZ, montar


def cmd_montar(pasta: Path, saida: Path | None = None):
    r = montar(pasta, saida)
    print(f"ok: {r.saida}  {r.slides} slides  {r.bytes / 1024 ** 2:.2f} MB  sha256 {r.sha256[:16]}")
    for a in r.avisos:
        print(f"  aviso: {a}")
    return r


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "imagens":
        from .imagens import main as imagens
        imagens(argv[1:])
        return 0
    ap = argparse.ArgumentParser(prog="python -m apresenta", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("novo", help="cria um projeto a partir do exemplo")
    n.add_argument("pasta", type=Path)
    m = sub.add_parser("montar", help="gera o HTML")
    m.add_argument("pasta", type=Path)
    m.add_argument("-o", "--saida", type=Path)
    m.add_argument("--estrito", action="store_true", help="avisos viram erro")
    v = sub.add_parser("verificar", help="monta e testa no navegador")
    v.add_argument("pasta", type=Path)
    v.add_argument("--min-px", type=float, default=14.0, help="menor letra aceita, em px numa tela de 1600 px")
    v.add_argument("--sem-capturas", action="store_true")
    sub.add_parser("imagens", help="PDF -> imagens (ver: python -m apresenta imagens -h)")
    a = ap.parse_args(argv)

    try:
        if a.cmd == "novo":
            if a.pasta.exists():
                raise ErroApresentacao(f"{a.pasta} já existe")
            shutil.copytree(RAIZ / "exemplos" / "completo", a.pasta, ignore=shutil.ignore_patterns("dist"))
            print(f"criado: {a.pasta}\n  edite apresentacao.yaml e dados.yaml; troque as imagens em img/")
        elif a.cmd == "montar":
            r = cmd_montar(a.pasta, a.saida)
            if a.estrito and r.avisos:
                return 1
        elif a.cmd == "verificar":
            from .verificar import verificar
            r = cmd_montar(a.pasta)
            dist = r.saida.parent
            problemas = verificar(r.saida, None if a.sem_capturas else dist / "capturas",
                                  dist / (r.saida.stem + ".pdf"), a.min_px)
            if problemas:
                print("\nPROBLEMAS:")
                for p in problemas:
                    print(f"  - {p}")
                return 1
            print("\nOK — nenhum problema encontrado.")
    except ErroApresentacao as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
