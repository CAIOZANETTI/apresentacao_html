"""Testes do gerador. Rodar: python -m pytest testes -q"""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from apresenta.conferir import conferir
from apresenta.erros import ErroApresentacao
from apresenta.formato import Dados, formata, numero, texto_html
from apresenta.montar import montar

RAIZ = Path(__file__).resolve().parent.parent
EXEMPLO = RAIZ / "exemplos" / "completo"


# ---------------------------------------------------------------- formatação
@pytest.mark.parametrize("valor,fmt,esperado", [
    (2540, None, "2.540"), (2540, "milhar", "2.540"), (6420.0, None, "6.420"), (14.49, None, "14,49"),
    (14.49, "dec1", "14,5"), (1.5, "dec2", "1,50"), (70, "pct", "70%"), (12.25, "pct1", "12,3%"),
    (1234567.891, "moeda", "R$ 1.234.567,89"), (-1500, None, "-1.500"), (0.125, "dec2", "0,13"),
    ("Semi-integrada", None, "Semi-integrada"),
])
def test_formata(valor, fmt, esperado):
    assert formata(valor, fmt) == esperado


def test_numero_arredondamento_comercial():
    assert numero(2.5, 0) == "3" and numero(3.5, 0) == "4"     # não usa arredondamento bancário


def test_referencia_e_escape():
    d = Dados({"m": {"forma": 2540}})
    assert texto_html("<b> {m.forma:milhar} m² **ok**", d) == "&lt;b&gt; 2.540 m² <b>ok</b>"


def test_referencia_inexistente():
    with pytest.raises(ErroApresentacao, match="dado inexistente"):
        Dados({"a": 1}).resolve("{a.b}")


def test_formato_desconhecido():
    with pytest.raises(ErroApresentacao, match="formato desconhecido"):
        formata(1, "x")


# ---------------------------------------------------------------- conferências
def test_conferir_ok_e_falha():
    d = Dados({"a": 1, "b": 2, "t": 3, "c": 202, "s": 20})
    conferir(["a + b == t", "round(c * 0.1) == s", "a < b <= t"], d)
    with pytest.raises(ErroApresentacao, match="FALHOU"):
        conferir(["a + b == 4"], d)


def test_conferir_bloqueia_codigo():
    with pytest.raises(ErroApresentacao, match="não suportada"):
        conferir(["__import__('os').system('ls') == 0"], Dados({}))


# ---------------------------------------------------------------- montagem
@pytest.fixture
def projeto(tmp_path):
    destino = tmp_path / "proj"
    shutil.copytree(EXEMPLO, destino, ignore=shutil.ignore_patterns("dist"))
    return destino


def editar(projeto: Path, funcao):
    p = projeto / "apresentacao.yaml"
    spec = yaml.safe_load(p.read_text(encoding="utf-8"))
    funcao(spec)
    p.write_text(yaml.safe_dump(spec, allow_unicode=True, sort_keys=False), encoding="utf-8")


def test_exemplo_monta_e_e_deterministico(projeto, tmp_path):
    r1 = montar(projeto, tmp_path / "a.html")
    r2 = montar(projeto, tmp_path / "b.html")
    assert r1.slides == 10
    assert r1.sha256 == r2.sha256
    assert (tmp_path / "a.html").read_bytes() == (tmp_path / "b.html").read_bytes()
    assert not r1.avisos, r1.avisos


def test_saida_contem_elementos(projeto, tmp_path):
    html = montar(projeto, tmp_path / "a.html").saida.read_text(encoding="utf-8")
    assert html.count('<section class="slide"') == 10
    assert "05 · Unidade 01" in html                  # chapéu numerado automático
    assert "10 / 10" in html                          # número de página automático
    assert html.count("@font-face") == 1              # fonte embutida uma vez
    assert html.count(".logo-1{background-image") == 1  # logo embutido uma vez
    assert "2.540 m²" in html and "2.541" not in html


def test_campo_desconhecido_falha(projeto):
    editar(projeto, lambda s: s["slides"][1].update({"subtitulo": "x"}))
    with pytest.raises(ErroApresentacao, match="campo desconhecido subtitulo"):
        montar(projeto)


def test_componente_desconhecido_falha(projeto):
    editar(projeto, lambda s: s["slides"][1]["corpo"]["celulas"][0].append({"grafico_pizza": {}}))
    with pytest.raises(ErroApresentacao, match="componente desconhecido 'grafico_pizza'"):
        montar(projeto)


def test_fonte_obrigatoria(projeto):
    editar(projeto, lambda s: s["slides"][1].pop("fonte"))
    with pytest.raises(ErroApresentacao, match="falta o campo fonte"):
        montar(projeto)


def test_imagem_inexistente(projeto):
    (projeto / "img" / "foto_avenida.jpg").unlink()
    with pytest.raises(ErroApresentacao, match="imagem não encontrada"):
        montar(projeto)


def test_conferencia_do_exemplo_pega_divergencia(projeto):
    p = projeto / "dados.yaml"
    p.write_text(p.read_text(encoding="utf-8").replace("extensao: 6420", "extensao: 6421"), encoding="utf-8")
    with pytest.raises(ErroApresentacao, match="conferir"):
        montar(projeto)


def test_barra_segmentada_precisa_somar_100(projeto):
    def muda(s):
        s["slides"][8]["corpo"]["celulas"][0][1]["barra_segmentada"]["grupos"][0]["itens"][0]["valor"] = 2
    editar(projeto, muda)
    with pytest.raises(ErroApresentacao, match="somam 101%"):
        montar(projeto)
