"""Formatação de números (padrão brasileiro) e resolução de referências a dados.

Toda string de texto do YAML pode citar um valor do dados.yaml:

    "{modulo_600.forma_m2:milhar} m² de forma"   ->  "2.540 m² de forma"
    "Prazo de {unidade_01.prazo} dias"            ->  "Prazo de 540 dias"

Formatos: milhar, dec1, dec2, pct, pct1, moeda, texto (padrão: milhar para inteiro,
dec1/dec2 conforme o número). Uma chave inexistente interrompe a montagem.
`**trecho**` vira destaque (cor de acento). O resto do texto é escapado.
"""
from __future__ import annotations

import html
import re
from decimal import ROUND_HALF_UP, Decimal

from .erros import ErroApresentacao

RE_REF = re.compile(r"\{([A-Za-z_][\w]*(?:\.[\w]+)*)(?::([a-z0-9]+))?\}")
RE_NEGRITO = re.compile(r"\*\*(.+?)\*\*")


def _agrupa(inteiro: str) -> str:
    neg = inteiro.startswith("-")
    d = inteiro.lstrip("-")
    partes = []
    while len(d) > 3:
        partes.insert(0, d[-3:])
        d = d[:-3]
    partes.insert(0, d)
    return ("-" if neg else "") + ".".join(partes)


def numero(valor: float | int, casas: int = 0) -> str:
    """12345.678, 2 -> '12.345,68' (arredondamento comercial, sem depender de locale)."""
    q = Decimal(str(valor)).quantize(Decimal(1).scaleb(-casas), rounding=ROUND_HALF_UP)
    s = f"{q:f}"
    if "." in s:
        inteiro, frac = s.split(".")
        return f"{_agrupa(inteiro)},{frac}"
    return _agrupa(s)


def formata(valor, fmt: str | None) -> str:
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        if fmt not in (None, "texto"):
            raise ErroApresentacao(f"formato '{fmt}' pede número, recebeu {valor!r}")
        return str(valor)
    if fmt in (None, "milhar"):
        if fmt is None and isinstance(valor, float) and not valor.is_integer():
            casas = min(len(repr(valor).split(".")[1]), 2)
            return numero(valor, casas)
        return numero(valor, 0)
    if fmt == "dec1":
        return numero(valor, 1)
    if fmt == "dec2":
        return numero(valor, 2)
    if fmt == "pct":
        return numero(valor, 0) + "%"
    if fmt == "pct1":
        return numero(valor, 1) + "%"
    if fmt == "moeda":
        return "R$ " + numero(valor, 2)
    if fmt == "texto":
        return str(valor)
    raise ErroApresentacao(f"formato desconhecido: '{fmt}' (use milhar, dec1, dec2, pct, pct1, moeda, texto)")


class Dados:
    """Acesso aos dados com registro das chaves usadas (para avisar sobre dados órfãos)."""

    def __init__(self, dados: dict):
        self.dados = dados or {}
        self.usadas: set[str] = set()

    def pega(self, chave: str):
        atual = self.dados
        for parte in chave.split("."):
            if isinstance(atual, list) and parte.isdigit() and int(parte) < len(atual):
                atual = atual[int(parte)]
            elif isinstance(atual, dict) and parte in atual:
                atual = atual[parte]
            else:
                raise ErroApresentacao(f"dado inexistente: '{{{chave}}}' — confira dados.yaml")
        self.usadas.add(chave)
        return atual

    def resolve(self, texto: str) -> str:
        return RE_REF.sub(lambda m: formata(self.pega(m.group(1)), m.group(2)), texto)

    def folhas(self, base: str = "", no=None) -> list[str]:
        no = self.dados if no is None else no
        if isinstance(no, dict):
            return [f for k, v in no.items() for f in self.folhas(f"{base}{k}.", v)]
        if isinstance(no, list):
            return [f for i, v in enumerate(no) for f in self.folhas(f"{base}{i}.", v)]
        return [base[:-1]]

    def nao_usadas(self) -> list[str]:
        return [f for f in self.folhas() if not any(f == u or f.startswith(u + ".") for u in self.usadas)]


def texto_html(texto, dados: Dados) -> str:
    """Resolve {referências}, escapa HTML e converte **destaque** e quebras de linha."""
    if texto is None:
        return ""
    s = html.escape(dados.resolve(str(texto)), quote=False)
    s = RE_NEGRITO.sub(r"<b>\1</b>", s)
    return s.replace("\n", "<br>")


def texto_puro(texto, dados: Dados) -> str:
    return RE_NEGRITO.sub(r"\1", dados.resolve(str(texto)))
