"""Componentes HTML dos slides — catálogo fechado.

Cada componente é um dicionário de UMA chave no YAML (o tipo), por exemplo:

    - kpis: {colunas: 4, itens: [{valor: "540 dias", texto: "prazo"}]}
    - figura: {imagem: img/corte.png, legenda: "Corte A-A"}

Tipos: titulo, texto, leitura, citacao, notas, lista, kpis, destaques, tabela, figura,
legenda_cores, alerta, barras, barra_segmentada, grade.
Campos desconhecidos interrompem a montagem (pega erro de digitação da IA ou do usuário).
"""
from __future__ import annotations

import html
import re

from . import graficos
from .erros import Campos, ErroApresentacao
from .formato import Dados, texto_html, texto_puro

RE_MEDIDA = re.compile(r"^\d+(\.\d+)?(fr|cqw|%)$")


class Contexto:
    """O que os componentes precisam do montador: dados e acesso a imagens."""

    def __init__(self, dados: Dados, imagem_uri, tamanho_imagem):
        self.dados = dados
        self.imagem_uri = imagem_uri
        self.tamanho_imagem = tamanho_imagem

    def t(self, s) -> str:
        return texto_html(s, self.dados)


def medida(v, onde: str) -> str:
    if v == "auto":
        return "auto"
    if isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0:
        return f"minmax(0,{v:g}fr)"
    if isinstance(v, str) and RE_MEDIDA.match(v):
        return f"minmax(0,{v})" if v.endswith("fr") else v
    raise ErroApresentacao(f"{onde}: medida inválida {v!r} (use número = proporção, 'auto', ou '12cqw', '30%')")


# ------------------------------------------------------------------ componentes simples
def c_titulo(v, ctx, onde):
    return f'<h3>{ctx.t(v)}</h3>'


def c_texto(v, ctx, onde):
    return f'<p class="texto">{ctx.t(v)}</p>'


def c_leitura(v, ctx, onde):
    return f'<p class="leitura">{ctx.t(v)}</p>'


def c_citacao(v, ctx, onde):
    return f'<blockquote>{ctx.t(v)}</blockquote>'


def c_notas(v, ctx, onde):
    if not isinstance(v, list):
        raise ErroApresentacao(f"{onde}: notas é uma lista de frases")
    return '<div class="notas">' + "".join(f"<div>{ctx.t(n)}</div>" for n in v) + "</div>"


def c_lista(v, ctx, onde):
    if isinstance(v, list):
        v = {"itens": v}
    c = Campos(v, onde, ["itens"], ["titulo", "numerada"])
    tag = "ol" if c.get("numerada") else "ul"
    tit = f"<h3>{ctx.t(c['titulo'])}</h3>" if c.get("titulo") else ""
    itens = "".join(f"<li>{ctx.t(i)}</li>" for i in c.lista("itens"))
    return f'<div class="lista">{tit}<{tag}>{itens}</{tag}></div>'


def c_kpis(v, ctx, onde):
    if isinstance(v, list):
        v = {"itens": v}
    c = Campos(v, onde, ["itens"], ["colunas", "tamanho"])
    itens = c.lista("itens")
    n = int(c.get("colunas", len(itens)))
    tam = c.get("tamanho", "normal")
    if tam not in ("normal", "grande", "menor"):
        raise ErroApresentacao(f"{onde}.tamanho: normal, grande ou menor")
    html_itens = []
    for i, k in enumerate(itens):
        ck = Campos(k, f"{onde}.itens[{i + 1}]", ["valor"], ["texto"])
        html_itens.append(f'<div class="kpi"><b>{ctx.t(ck["valor"])}</b><span>{ctx.t(ck.get("texto", ""))}</span></div>')
    return f'<div class="kpis kpis-{tam}" style="--n:{n}">' + "".join(html_itens) + "</div>"


def c_destaques(v, ctx, onde):
    if not isinstance(v, list):
        raise ErroApresentacao(f"{onde}: destaques é uma lista de {{valor, titulo, texto}}")
    out = []
    for i, k in enumerate(v):
        ck = Campos(k, f"{onde}[{i + 1}]", ["valor", "titulo"], ["texto"])
        out.append(f'<div class="destaque"><b>{ctx.t(ck["valor"])}</b><h4>{ctx.t(ck["titulo"])}</h4>'
                   f'<span>{ctx.t(ck.get("texto", ""))}</span></div>')
    return '<div class="destaques">' + "".join(out) + "</div>"


def c_alerta(v, ctx, onde):
    c = Campos(v, onde, ["titulo"], ["texto"])
    return f'<div class="alerta"><b>{ctx.t(c["titulo"])}</b><span>{ctx.t(c.get("texto", ""))}</span></div>'


def c_legenda_cores(v, ctx, onde):
    if not isinstance(v, list):
        raise ErroApresentacao(f"{onde}: legenda_cores é uma lista de {{cor, titulo, texto}}")
    out = []
    for i, k in enumerate(v):
        ck = Campos(k, f"{onde}[{i + 1}]", ["cor", "titulo"], ["texto"])
        out.append(f'<div><i style="background:{graficos.cor(ck["cor"], "acento")}"></i>'
                   f'<b>{ctx.t(ck["titulo"])}</b><span>{ctx.t(ck.get("texto", ""))}</span></div>')
    return f'<div class="legenda-cores" style="--n:{len(v)}">' + "".join(out) + "</div>"


def c_tabela(v, ctx, onde):
    c = Campos(v, onde, ["colunas", "linhas"], ["titulo", "total", "compacta"])
    cols = []
    for i, col in enumerate(c.lista("colunas")):
        if isinstance(col, str):
            col = {"titulo": col}
        cc = Campos(col, f"{onde}.colunas[{i + 1}]", ["titulo"], ["alinhar"])
        if cc.get("alinhar", "esquerda") not in ("esquerda", "direita", "centro"):
            raise ErroApresentacao(f"{cc.onde}.alinhar: esquerda, direita ou centro")
        cols.append((cc["titulo"], cc.get("alinhar", "esquerda")))
    classe = {"esquerda": "", "direita": ' class="n"', "centro": ' class="c"'}

    def linha(cels, onde_l, tag="td"):
        if not isinstance(cels, list) or len(cels) != len(cols):
            raise ErroApresentacao(f"{onde_l}: a linha precisa de {len(cols)} células")
        return "<tr>" + "".join(f"<{tag}{classe[cols[k][1]]}>{ctx.t(x)}</{tag}>" for k, x in enumerate(cels)) + "</tr>"

    cab = "<tr>" + "".join(f"<th{classe[a]}>{ctx.t(t)}</th>" for t, a in cols) + "</tr>"
    corpo = "".join(linha(l, f"{onde}.linhas[{i + 1}]") for i, l in enumerate(c.lista("linhas")))
    pe = f'<tfoot>{linha(c["total"], f"{onde}.total")}</tfoot>' if c.get("total") else ""
    tit = f"<h3>{ctx.t(c['titulo'])}</h3>" if c.get("titulo") else ""
    compacta = " compacta" if c.get("compacta") else ""
    return f'<div class="tabela{compacta}">{tit}<table><thead>{cab}</thead><tbody>{corpo}</tbody>{pe}</table></div>'


def c_figura(v, ctx, onde):
    c = Campos(v, onde, [], ["imagem", "grafico", "legenda", "ajuste", "ampliavel", "moldura", "altura", "descricao"])
    if bool(c.get("imagem")) == bool(c.get("grafico")):
        raise ErroApresentacao(f"{onde}: informe 'imagem' OU 'grafico'")
    ajuste = c.get("ajuste", "conter")
    if ajuste not in ("conter", "cobrir"):
        raise ErroApresentacao(f"{onde}.ajuste: conter (mostra tudo) ou cobrir (preenche e corta)")
    altura = c.get("altura", "preenche")
    altura_fixa = None
    if altura not in ("preenche", "natural"):
        if not (isinstance(altura, str) and re.match(r"^\d+(\.\d+)?cqw$", altura)):
            raise ErroApresentacao(f"{onde}.altura: preenche (ocupa o espaço livre), natural (altura do conteúdo) ou fixa em cqw, ex.: 15cqw")
        altura_fixa = altura
    legenda = c.get("legenda")
    if c.get("imagem"):
        alt = html.escape(texto_puro(c.get("descricao") or legenda or "", ctx.dados), quote=True)
        conteudo = f'<img src="{ctx.imagem_uri(c["imagem"], onde)}" alt="{alt}">'
    else:
        conteudo = graficos.gera(c["grafico"], ctx.dados, f"{onde}.grafico",
                                 imagem_uri=ctx.imagem_uri, tamanho_imagem=ctx.tamanho_imagem)
    classes = ["fig"]
    if c.get("ampliavel", True):
        classes.append("ampliavel")
    if ajuste == "cobrir":
        classes.append("cobre")
    if not c.get("moldura", True):
        classes.append("sem-moldura")
    if altura != "preenche":
        classes.append("natural")
    st = f' style="height:{altura_fixa}"' if altura_fixa else ""
    cap = f"<figcaption>{ctx.t(legenda)}</figcaption>" if legenda else ""
    return f'<figure class="{" ".join(classes)}"><div class="quadro"{st}>{conteudo}</div>{cap}</figure>'


def c_barras(v, ctx, onde):
    """Barras horizontais de percentuais (ex.: 90% trecho concluído / 10% as built)."""
    c = Campos(v, onde, ["itens"], ["titulo"])
    out = [f"<h3>{ctx.t(c['titulo'])}</h3>"] if c.get("titulo") else []
    for i, it in enumerate(c.lista("itens")):
        ci = Campos(it, f"{onde}.itens[{i + 1}]", ["rotulo", "partes"], ["nota"])
        partes = []
        for j, p in enumerate(ci.lista("partes")):
            cp = Campos(p, f"{ci.onde}.partes[{j + 1}]", ["valor"], ["texto", "final"])
            val = graficos.numero_ou_dado(cp["valor"], ctx.dados, cp.onde)
            txt = ctx.t(cp.get("texto", f"{val:g}%"))
            fim = ' class="fim"' if cp.get("final") else ""
            partes.append(f'<i style="flex:{val:g}"{fim}>{txt}</i>')
        nota = f"<small>{ctx.t(ci['nota'])}</small>" if ci.get("nota") else ""
        out.append(f'<div class="barra-pag"><span>{ctx.t(ci["rotulo"])}</span><div>{"".join(partes)}</div>{nota}</div>')
    return '<div class="barras">' + "".join(out) + "</div>"


def c_barra_segmentada(v, ctx, onde):
    """Barra 100% dividida em grupos e itens (ex.: pagamento 70/20/10 por etapa), com legenda em colunas."""
    c = Campos(v, onde, ["grupos"], ["titulo", "legenda"])
    tons = ("forte", "medio", "escuro")
    barra, cab, leg = [], [], []
    total = 0.0
    for i, g in enumerate(c.lista("grupos")):
        cg = Campos(g, f"{onde}.grupos[{i + 1}]", ["rotulo", "itens"], ["tom"])
        tom = cg.get("tom", tons[i % 3])
        if tom not in tons:
            raise ErroApresentacao(f"{cg.onde}.tom: forte, medio ou escuro")
        soma = 0.0
        itens_leg = []
        for j, it in enumerate(cg.lista("itens")):
            ci = Campos(it, f"{cg.onde}.itens[{j + 1}]", ["valor", "texto"])
            val = graficos.numero_ou_dado(ci["valor"], ctx.dados, ci.onde)
            soma += val
            barra.append(f'<i class="{tom}" style="flex:{val:g}">{val:g}</i>')
            itens_leg.append(f"<li><b>{val:g}%</b> {ctx.t(ci['texto'])}</li>")
        total += soma
        cab.append(f'<span class="{tom}" style="flex:{soma:g}">{ctx.t(cg["rotulo"])}</span>')
        leg.append(f'<ul style="flex:{max(soma, 24):g}">{"".join(itens_leg)}</ul>')  # mínimo p/ texto caber
    if abs(total - 100) > 0.01:
        raise ErroApresentacao(f"{onde}: os itens somam {total:g}%, deveriam somar 100%")
    tit = f"<h3>{ctx.t(c['titulo'])}</h3>" if c.get("titulo") else ""
    legenda = f'<div class="seg-legenda">{"".join(leg)}</div>' if c.get("legenda", True) else ""
    return (f'<div class="segmentada">{tit}<div class="seg-cab">{"".join(cab)}</div>'
            f'<div class="seg-barra">{"".join(barra)}</div>{legenda}</div>')


def c_grade(v, ctx, onde):
    return grade(v, ctx, onde)


COMPONENTES = {
    "titulo": c_titulo, "texto": c_texto, "leitura": c_leitura, "citacao": c_citacao, "notas": c_notas,
    "lista": c_lista, "kpis": c_kpis, "destaques": c_destaques, "alerta": c_alerta,
    "legenda_cores": c_legenda_cores, "tabela": c_tabela, "figura": c_figura, "barras": c_barras,
    "barra_segmentada": c_barra_segmentada, "grade": c_grade,
}


def componente(item, ctx, onde) -> str:
    if not isinstance(item, dict) or len(item) != 1:
        raise ErroApresentacao(f"{onde}: cada componente é um bloco de UMA chave (ex.: '- lista: [...]'), recebido {item!r}")
    tipo, valor = next(iter(item.items()))
    if tipo not in COMPONENTES:
        raise ErroApresentacao(f"{onde}: componente desconhecido '{tipo}' (válidos: {', '.join(COMPONENTES)})")
    return COMPONENTES[tipo](valor, ctx, f"{onde}.{tipo}")


# ------------------------------------------------------------------ grade
def grade(v, ctx, onde) -> str:
    """Grade de células. Cada célula empilha componentes; figuras ocupam o espaço que sobra."""
    c = Campos(v, onde, ["celulas"], ["colunas", "linhas", "espaco"])
    cols = " ".join(medida(x, f"{onde}.colunas") for x in c.lista("colunas", [1]))
    lins = " ".join(medida(x, f"{onde}.linhas") for x in c.lista("linhas", [1]))
    esp = c.get("espaco", "normal")
    if esp not in ("normal", "justo", "largo"):
        raise ErroApresentacao(f"{onde}.espaco: normal, justo ou largo")
    celulas = []
    for i, cel in enumerate(c.lista("celulas")):
        o = f"{onde}.celulas[{i + 1}]"
        if isinstance(cel, list):
            cel = {"componentes": cel}
        cc = Campos(cel, o, ["componentes"], ["vao", "vao_linhas", "estilo", "alinhar"])
        estilo = []
        if cc.get("vao"):
            estilo.append(f"grid-column:span {int(cc['vao'])}")
        if cc.get("vao_linhas"):
            estilo.append(f"grid-row:span {int(cc['vao_linhas'])}")
        classes = ["celula"]
        if cc.get("estilo"):
            if cc["estilo"] not in ("faixa", "caixa"):
                raise ErroApresentacao(f"{o}.estilo: faixa (linha de acento no topo) ou caixa (fundo claro)")
            classes.append("cel-" + cc["estilo"])
        if cc.get("alinhar"):
            if cc["alinhar"] not in ("topo", "centro", "base"):
                raise ErroApresentacao(f"{o}.alinhar: topo, centro ou base")
            classes.append("al-" + cc["alinhar"])
        corpo = "".join(componente(x, ctx, f"{o}[{k + 1}]") for k, x in enumerate(cc.lista("componentes")))
        st = f' style="{";".join(estilo)}"' if estilo else ""
        celulas.append(f'<div class="{" ".join(classes)}"{st}>{corpo}</div>')
    return (f'<div class="grade esp-{esp}" style="grid-template-columns:{cols};grid-template-rows:{lins}">'
            + "".join(celulas) + "</div>")
