"""Conferências de coerência dos dados (seção `conferir:` do dados.yaml).

Cada item é uma comparação simples entre valores do próprio dados.yaml:

    conferir:
      - adutoras.a.extensao + adutoras.b.extensao + adutoras.c.extensao == unidade_02.extensao
      - round(modulo_b.concreto * 0.1) == modulo_b.aco_t     # aço ≈ 100 kg/m³
      - modulo_a.estacas <= modulo_b.estacas

Permitido: números, chaves com ponto, + - * / ( ), round(), abs(), min(), max(),
comparações == != < <= > >=, and/or. Nada mais é executado (avaliação por AST, sem eval).
Uma conferência falsa interrompe a montagem.
"""
from __future__ import annotations

import ast
import operator as op

from .erros import ErroApresentacao
from .formato import Dados

OPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, ast.USub: op.neg}
CMP = {ast.Eq: op.eq, ast.NotEq: op.ne, ast.Lt: op.lt, ast.LtE: op.le, ast.Gt: op.gt, ast.GtE: op.ge}
FUNC = {"round": round, "abs": abs, "min": min, "max": max}


def _nome(no) -> str:
    if isinstance(no, ast.Name):
        return no.id
    if isinstance(no, ast.Attribute):
        return f"{_nome(no.value)}.{no.attr}"
    raise ValueError


def _avalia(no, dados: Dados):
    if isinstance(no, ast.Expression):
        return _avalia(no.body, dados)
    if isinstance(no, ast.Constant) and isinstance(no.value, (int, float)):
        return no.value
    if isinstance(no, (ast.Name, ast.Attribute)):
        v = dados.pega(_nome(no))
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise ErroApresentacao(f"conferir: '{_nome(no)}' não é número")
        return v
    if isinstance(no, ast.BinOp) and type(no.op) in OPS:
        return OPS[type(no.op)](_avalia(no.left, dados), _avalia(no.right, dados))
    if isinstance(no, ast.UnaryOp) and type(no.op) in OPS:
        return OPS[type(no.op)](_avalia(no.operand, dados))
    if isinstance(no, ast.Call) and isinstance(no.func, ast.Name) and no.func.id in FUNC and not no.keywords:
        return FUNC[no.func.id](*[_avalia(a, dados) for a in no.args])
    if isinstance(no, ast.Compare):
        esq = _avalia(no.left, dados)
        for o, d in zip(no.ops, no.comparators):
            dir_ = _avalia(d, dados)
            if type(o) not in CMP:
                raise ValueError
            if not CMP[type(o)](esq, dir_):
                return False
            esq = dir_
        return True
    if isinstance(no, ast.BoolOp):
        vals = [_avalia(v, dados) for v in no.values]
        return all(vals) if isinstance(no.op, ast.And) else any(vals)
    raise ValueError


def conferir(regras: list, dados: Dados) -> None:
    for i, r in enumerate(regras or [], 1):
        try:
            arvore = ast.parse(str(r), mode="eval")
            ok = _avalia(arvore, dados)
        except ErroApresentacao:
            raise
        except (ValueError, SyntaxError, ZeroDivisionError, TypeError):
            raise ErroApresentacao(f"dados.yaml conferir[{i}]: expressão não suportada: {r}")
        if ok is not True:
            raise ErroApresentacao(f"dados.yaml conferir[{i}] FALHOU: {r}")
