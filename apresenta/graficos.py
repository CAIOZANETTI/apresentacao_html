"""Gráficos SVG gerados a partir de dados — funções puras e determinísticas.

Cada função recebe o bloco `grafico:` do YAML (já validado) e devolve uma string <svg>.
As cores usam as variáveis CSS da identidade (var(--acento) etc.), então o gráfico
acompanha a paleta do projeto. Coordenadas são arredondadas para 1 casa: a mesma
entrada gera sempre o mesmo SVG.

Tipos: linha_do_tempo, sondagem, marcos, ciclo_pagamento, mapa.
"""
from __future__ import annotations

import datetime as dt
import html
import math
import textwrap

from .erros import Campos, ErroApresentacao
from .formato import Dados, texto_puro

MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def f(x: float) -> str:
    """Número para coordenada SVG: 1 casa, sem '-0.0', sem zeros inúteis."""
    s = f"{round(x, 1):.1f}"
    s = s.rstrip("0").rstrip(".") if "." in s else s
    return "0" if s in ("-0", "") else s


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def cor(c: str | None, padrao: str) -> str:
    c = c or padrao
    return c if c.startswith("#") else f"var(--{c})"


def svg(largura: float, altura: float, corpo: list[str], rotulo: str = "") -> str:
    aria = f' role="img" aria-label="{esc(rotulo)}"' if rotulo else ""
    return (f'<svg viewBox="0 0 {f(largura)} {f(altura)}" xmlns="http://www.w3.org/2000/svg"{aria}>'
            + "".join(corpo) + "</svg>")


def texto(x, y, t, tam=14, preenche="var(--preto)", ancora="start", extra="") -> str:
    a = "" if ancora == "start" else f' text-anchor="{ancora}"'
    return f'<text x="{f(x)}" y="{f(y)}"{a} font-size="{tam}" fill="{preenche}"{extra}>{esc(t)}</text>'


def quebra(t: str, largura: int, max_linhas: int = 3) -> list[str]:
    linhas = textwrap.wrap(t, largura) or [""]
    if len(linhas) > max_linhas:
        linhas = linhas[:max_linhas]
        linhas[-1] = linhas[-1][: max(0, largura - 1)].rstrip() + "…"
    return linhas


def numero_ou_dado(v, dados: Dados, onde: str) -> float:
    """Aceita 540 ou '{unidade_01.prazo}' — assim o gráfico usa o mesmo número do texto."""
    if isinstance(v, str):
        s = v.strip()
        bruto = dados.pega(s[1:-1].split(":")[0]) if s.startswith("{") and s.endswith("}") else s
        try:
            return float(bruto)
        except (TypeError, ValueError):
            raise ErroApresentacao(f"{onde}: esperado número, recebido {v!r}")
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    raise ErroApresentacao(f"{onde}: esperado número, recebido {v!r}")


# ---------------------------------------------------------------- linha do tempo
def linha_do_tempo(g: dict, dados: Dados, onde: str, **_) -> str:
    c = Campos(g, onde, ["tipo", "inicio", "fim", "eventos"], ["rotulo"])
    try:
        a = dt.date.fromisoformat(c["inicio"] + "-01")
        ano, mes = map(int, c["fim"].split("-"))
        b = dt.date(ano + mes // 12, mes % 12 + 1, 1)
    except Exception:
        raise ErroApresentacao(f"{onde}: inicio/fim no formato AAAA-MM")
    W, H, X0, X1, Y = 1000, 300, 20, 985, 150
    total = (b - a).days
    X = lambda d: X0 + (d - a).days / total * (X1 - X0)
    out = [f'<line x1="{X0}" x2="{X1}" y1="{Y}" y2="{Y}" stroke="var(--preto)" stroke-width="2"/>']
    d = a
    while d < b:
        x = X(d)
        out.append(f'<line x1="{f(x)}" x2="{f(x)}" y1="{Y - 5}" y2="{Y + 5}" stroke="var(--preto)"/>')
        out.append(texto(x + 4, Y + 18, MESES[d.month - 1], 13, "var(--tenue)"))
        d = dt.date(d.year + d.month // 12, d.month % 12 + 1, 1)
    # níveis: 1 = acima, -1 = abaixo, 2/-2 mais afastados. Escolha automática e determinística.
    Y_ROT = {1: 88, -1: 194, 2: 30, -2: 252, 3: -28, -3: 310}
    ocupado: dict[int, list[tuple[float, float]]] = {}
    eventos = []
    for i, e in enumerate(c.lista("eventos")):
        ce = Campos(e, f"{onde}.eventos[{i + 1}]", ["data", "texto"], ["rotulo", "estado", "nivel"])
        try:
            data = dt.date.fromisoformat(str(ce["data"]))
        except ValueError:
            raise ErroApresentacao(f"{ce.onde}: data no formato AAAA-MM-DD")
        eventos.append((data, ce))
    eventos.sort(key=lambda t: t[0])
    for data, ce in eventos:
        x = X(data)
        direita = x > X1 - 200
        linhas_txt = quebra(texto_puro(ce["texto"], dados), 28, 2)
        larg = max(len(l) for l in linhas_txt) * 7.2 + 12      # largura estimada do texto (14 px)
        faixa = (x - larg, x + 4) if direita else (x - 4, x + larg)
        nivel = ce.get("nivel")
        if nivel is None:   # primeiro nível sem sobreposição: acima, abaixo, mais acima, mais abaixo...
            livre = lambda n: all(faixa[1] < a0 or faixa[0] > a1 for a0, a1 in ocupado.get(n, []))
            nivel = next((n for n in (1, -1, 2, -2, 3, -3) if livre(n)), 1)
        ocupado.setdefault(nivel, []).append(faixa)
        estado = ce.get("estado", "normal")
        if estado not in ("normal", "destaque", "cancelado"):
            raise ErroApresentacao(f"{ce.onde}.estado: use normal, destaque ou cancelado")
        tinta = {"normal": "var(--preto)", "destaque": "var(--acento)", "cancelado": "var(--tenue)"}[estado]
        risco = ' text-decoration="line-through"' if estado == "cancelado" else ""
        yr = Y_ROT[nivel]
        topo = yr - 16 if nivel > 0 else yr - 16
        out.append(f'<line x1="{f(x)}" x2="{f(x)}" y1="{Y}" y2="{f(topo + (48 if nivel > 0 else -4))}" stroke="{tinta}"/>')
        out.append(f'<circle cx="{f(x)}" cy="{Y}" r="{7 if estado == "destaque" else 5}" fill="{tinta}"/>')
        tx, anc = (x - 6, "end") if direita else (x + 6, "start")
        rot = ce.get("rotulo") or data.strftime("%d/%m")
        out.append(texto(tx, yr, texto_puro(rot, dados), 17, tinta, anc, risco))
        for k, linha in enumerate(linhas_txt):
            out.append(texto(tx, yr + 16 * (k + 1), linha, 14, tinta, anc, risco))
    return svg(W, H, out, texto_puro(c.get("rotulo", "linha do tempo"), dados))


# ---------------------------------------------------------------- sondagem
CORES_SOLO = ["#a8998a", "#d9b9a3", "#b98c6e", "#e3d3a8", "#c9b07c", "#bfae94"]


def sondagem(g: dict, dados: Dados, onde: str, **_) -> str:
    c = Campos(g, onde, ["tipo", "furo", "camadas", "nspt"], ["nivel_agua", "fundo", "impenetravel", "rotulo"])
    camadas = [Campos(k, f"{onde}.camadas[{i + 1}]", ["ate"], ["descricao", "cor"]) for i, k in enumerate(c.lista("camadas"))]
    nspt = [Campos(k, f"{onde}.nspt[{i + 1}]", ["prof", "n"]) for i, k in enumerate(c.lista("nspt"))]
    imp = c.get("impenetravel")
    pmax = max([float(k["ate"]) for k in camadas] + [float(k["prof"]) for k in nspt] + [float(imp or 0)])
    pmax = 2 * math.ceil(pmax / 2)
    W, H, YT, YB = 400, 580, 40, 540
    Y = lambda p: YT + p / pmax * (YB - YT)
    XC, WC, XN, WN, NMAX = 34, 116, 168, 220, 30
    out = [texto(XN, 18, "NSPT (golpes/30 cm)", 14, "var(--suave)"),
           texto(XC, 18, f"{texto_puro(c['furo'], dados)} · prof. (m)", 14, "var(--suave)")]
    for n in (10, 20, 30):
        x = XN + n / NMAX * WN
        out.append(f'<line x1="{f(x)}" x2="{f(x)}" y1="{YT}" y2="{YB}" stroke="var(--linha)" stroke-dasharray="3 3"/>')
        out.append(texto(x, 34, n, 13, "var(--tenue)", "middle"))
    for p in range(0, pmax + 1, 2):
        out.append(texto(XC - 5, Y(p) + 5, p, 13, "var(--suave)", "end"))
    topo = 0.0
    for i, k in enumerate(camadas):
        base = float(k["ate"])
        y0, y1 = Y(topo), Y(base)
        out.append(f'<rect x="{XC}" y="{f(y0)}" width="{WC}" height="{f(y1 - y0)}" fill="{k.get("cor") or CORES_SOLO[i % len(CORES_SOLO)]}" stroke="#fff" stroke-width=".8"/>')
        if k.get("descricao") and y1 - y0 > 40:
            linhas = quebra(texto_puro(k["descricao"], dados), 16, max(1, int((y1 - y0 - 8) // 16)))
            yc = (y0 + y1) / 2 - (len(linhas) - 1) * 8 + 5
            for j, linha in enumerate(linhas):
                out.append(texto(XC + WC / 2, yc + 16 * j, linha, 13, "var(--preto)", "middle"))
        topo = base
    if imp:
        out.append(f'<rect x="{XC}" y="{f(Y(float(imp)))}" width="{WC}" height="10" fill="var(--preto)"/>')
        out.append(texto(XC, Y(float(imp)) + 28, f"impenetrável · {str(imp).replace('.', ',')} m", 13))
    passo = (YB - YT) / pmax
    for k in nspt:
        n, p = float(k["n"]), float(k["prof"])
        larg = min(n, NMAX) / NMAX * WN
        tom = "var(--bege)" if n <= 8 else ("#d98a5f" if n <= 15 else "var(--acento)")
        out.append(f'<rect x="{XN}" y="{f(Y(p) - passo * 0.35)}" width="{f(larg)}" height="{f(passo * 0.7)}" fill="{tom}"/>')
        out.append(texto(XN + larg + 4, Y(p) + 5, int(n) if n.is_integer() else n, 13))
    for chave, estilo, tinta, nome in (("nivel_agua", 'stroke-width="2"', "var(--agua)", "nível d'água"),
                                       ("fundo", 'stroke-dasharray="6 3"', "var(--preto)", "fundo da estrutura")):
        v = c.get(chave)
        if v is not None:
            y = Y(float(v))
            out.append(f'<line x1="{XC}" x2="388" y1="{f(y)}" y2="{f(y)}" stroke="{tinta}" {estilo}/>')
            out.append(texto(388, y - 5, f"{nome} {str(v).replace('.', ',')} m", 13, tinta, "end"))
    return svg(W, H, out, texto_puro(c.get("rotulo", f"sondagem {c['furo']}"), dados))


# ---------------------------------------------------------------- marcos / prazos
def marcos(g: dict, dados: Dados, onde: str, **_) -> str:
    c = Campos(g, onde, ["tipo", "escala", "linhas"], ["legenda", "rotulo", "grade"])
    ce = Campos(c["escala"], f"{onde}.escala", ["max", "passo"], ["unidade"])
    vmax, passo = numero_ou_dado(ce["max"], dados, onde), numero_ou_dado(ce["passo"], dados, onde)
    un = ce.get("unidade", "d")
    linhas = c.lista("linhas")
    W, XL, X0, X1 = 1000, 250, 262, 930
    TOPO, ALT = 44, 74
    H = TOPO + ALT * len(linhas) + (34 if c.get("legenda") else 6)
    X = lambda v: X0 + v / vmax * (X1 - X0)
    out = []
    v = 0.0
    while v <= vmax + 1e-9:
        x = X(v)
        out.append(texto(x, 22, f"{int(v) if v.is_integer() else v} {un}" if v == 0 else (int(v) if v.is_integer() else v), 16, "var(--tenue)", "middle"))
        if c.get("grade", True):
            out.append(f'<line x1="{f(x)}" x2="{f(x)}" y1="30" y2="{f(TOPO + ALT * len(linhas) - 10)}" stroke="var(--linha)"/>')
        v += passo
    for i, linha in enumerate(linhas):
        cl = Campos(linha, f"{onde}.linhas[{i + 1}]", ["nome", "prazo"], ["marcos"])
        yc = TOPO + ALT * i + ALT / 2
        prazo = numero_ou_dado(cl["prazo"], dados, cl.onde)
        out.append(texto(XL, yc + 6, texto_puro(cl["nome"], dados), 19, "var(--preto)", "end"))
        out.append(f'<rect x="{X0}" y="{f(yc - 7)}" width="{f(X(prazo) - X0)}" height="14" fill="var(--bege)"/>')
        out.append(texto(X(prazo) + 14, yc + 6, f"{int(prazo)} {un}", 17, "var(--preto)"))   # +14: não encosta no losango final
        for j, m in enumerate(cl.lista("marcos")):
            cm = Campos(m, f"{cl.onde}.marcos[{j + 1}]", ["dia"], ["rotulo", "lado", "mostrar_dia"])
            dia = numero_ou_dado(cm["dia"], dados, cm.onde)
            x = X(dia)
            lado = cm.get("lado", "cima")
            if lado not in ("cima", "baixo"):
                raise ErroApresentacao(f"{cm.onde}.lado: use cima ou baixo")
            out.append(f'<rect x="{f(x - 7)}" y="{f(yc - 7)}" width="14" height="14" fill="var(--acento)" transform="rotate(45 {f(x)} {f(yc)})"/>')
            ycima, ybaixo = yc - 16, yc + 28
            if cm.get("rotulo"):
                out.append(texto(x, ycima if lado == "cima" else ybaixo, texto_puro(cm["rotulo"], dados), 16,
                                 "var(--acento)" if lado == "cima" else "var(--suave)", "middle"))
            if cm.get("mostrar_dia", False):
                out.append(texto(x, ybaixo if lado == "cima" else ycima, int(dia), 15, "var(--suave)", "middle"))
    if c.get("legenda"):
        y = H - 12
        out.append(f'<rect x="{X0}" y="{y - 11}" width="26" height="12" fill="var(--bege)"/>')
        out.append(texto(X0 + 34, y, "prazo-limite exigido", 14, "var(--suave)"))
        out.append(f'<rect x="{X0 + 220}" y="{y - 11}" width="11" height="11" fill="var(--acento)" transform="rotate(45 {X0 + 225.5} {y - 5.5})"/>')
        out.append(texto(X0 + 240, y, "marco intermediário", 14, "var(--suave)"))
    return svg(W, H, out, texto_puro(c.get("rotulo", "prazos e marcos"), dados))


# ---------------------------------------------------------------- ciclo de pagamento
def ciclo_pagamento(g: dict, dados: Dados, onde: str, **_) -> str:
    c = Campos(g, onde, ["tipo"], ["meses", "dias_mes", "dias_medicao", "prazo_pagamento", "rotulo"])
    n = int(c.get("meses", 3))
    dm = numero_ou_dado(c.get("dias_mes", 30), dados, onde)
    med = numero_ou_dado(c.get("dias_medicao", 10), dados, onde)
    pz = numero_ou_dado(c.get("prazo_pagamento", 30), dados, onde)
    vmax = math.ceil((n * dm + med + pz + 10) / dm) * dm
    W, X0, X1, TOPO, ALT = 1000, 120, 960, 50, 110
    H = TOPO + ALT * n + 50
    X = lambda v: X0 + v / vmax * (X1 - X0)
    out = []
    v = 0.0
    while v <= vmax:
        out.append(texto(X(v), 24, f"{int(v)} d", 18, "var(--tenue)", "middle"))
        out.append(f'<line x1="{f(X(v))}" x2="{f(X(v))}" y1="32" y2="{TOPO + ALT * n}" stroke="var(--linha)"/>')
        v += dm
    for i in range(n):
        yc = TOPO + ALT * i + ALT / 2
        ini, fim = i * dm, (i + 1) * dm
        pg = fim + med + pz
        out.append(texto(X0 - 14, yc + 7, f"mês {i + 1}", 20, "var(--preto)", "end"))
        out.append(f'<rect x="{f(X(ini))}" y="{f(yc - 12)}" width="{f(X(fim) - X(ini))}" height="24" fill="var(--bege)"/>')
        out.append(f'<rect x="{f(X(fim - med * 0.0))}" y="{f(yc - 12)}" width="{f(X(fim + med) - X(fim))}" height="24" fill="#9c8f7d"/>')
        out.append(f'<rect x="{f(X(fim + med))}" y="{f(yc - 12)}" width="{f(X(pg) - X(fim + med))}" height="24" fill="none" stroke="var(--acento)" stroke-dasharray="5 3"/>')
        out.append(f'<circle cx="{f(X(pg))}" cy="{f(yc)}" r="13" fill="var(--acento)"/>')
        out.append(texto(X(pg), yc + 6, "$", 16, "#fff", "middle"))
        out.append(texto(X(pg) + 20, yc + 7, f"dia {int(pg)}", 20, "var(--acento)"))
    y = H - 16
    for k, (desenho, rot) in enumerate([('fill="var(--bege)"', "execução do mês"),
                                        ('fill="#9c8f7d"', f"medição e fatura (~{int(med)} d)"),
                                        ('fill="none" stroke="var(--acento)" stroke-dasharray="5 3"', f"pagamento em {int(pz)} d")]):
        x = X0 + k * 270
        out.append(f'<rect x="{x}" y="{y - 12}" width="26" height="14" {desenho}/>')
        out.append(texto(x + 34, y, rot, 18, "var(--suave)"))
    return svg(W, H, out, texto_puro(c.get("rotulo", "ciclo de medição e pagamento"), dados))


# ---------------------------------------------------------------- mapa com traçados
def mapa(g: dict, dados: Dados, onde: str, *, imagem_uri, tamanho_imagem, **_) -> str:
    c = Campos(g, onde, ["tipo", "imagem"], ["escurecer", "tracados", "rotulos", "legenda", "rotulo"])
    W, H = tamanho_imagem(c["imagem"], onde)
    esp = W / 90           # espessura base proporcional à imagem
    fonte = round(W / 45)
    out = [f'<image href="{imagem_uri(c["imagem"], onde)}" width="{W}" height="{H}"/>']
    if c.get("escurecer"):
        out.append(f'<rect width="{W}" height="{H}" fill="#000" opacity="{float(c["escurecer"])}"/>')
    itens_legenda = []
    for i, t in enumerate(c.lista("tracados")):
        ct = Campos(t, f"{onde}.tracados[{i + 1}]", ["pontos"], ["cor", "tracejado", "rotulo", "pontas"])
        pts = ct.lista("pontos")
        if len(pts) < 2 or not all(isinstance(p, list) and len(p) == 2 for p in pts):
            raise ErroApresentacao(f"{ct.onde}.pontos: lista de [x, y] em pixels da imagem (mínimo 2)")
        s_pts = " ".join(f"{f(x)},{f(y)}" for x, y in pts)
        tinta = cor(ct.get("cor"), "acento")
        if ct.get("tracejado"):
            out.append(f'<polyline points="{s_pts}" fill="none" stroke="{tinta}" stroke-width="{f(esp * 0.4)}" stroke-dasharray="{f(esp * 1.4)} {f(esp)}"/>')
        else:
            comum = 'fill="none" stroke-linejoin="round" stroke-linecap="round"'
            out.append(f'<polyline points="{s_pts}" {comum} stroke="#fff" stroke-width="{f(esp * 1.7)}"/>')
            out.append(f'<polyline points="{s_pts}" {comum} stroke="{tinta}" stroke-width="{f(esp)}"/>')
            if ct.get("pontas", True):
                for x, y in (pts[0], pts[-1]):
                    out.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(esp * 1.15)}" fill="{tinta}" stroke="#fff" stroke-width="{f(esp * 0.4)}"/>')
        if ct.get("rotulo"):
            itens_legenda.append((tinta, texto_puro(ct["rotulo"], dados), bool(ct.get("tracejado"))))
    for i, r in enumerate(c.lista("rotulos")):
        cr = Campos(r, f"{onde}.rotulos[{i + 1}]", ["x", "y", "texto"])
        out.append(texto(cr["x"], cr["y"], texto_puro(cr["texto"], dados), fonte, "#fff",
                         extra=f' stroke="#1a1a1a" stroke-width="{f(fonte / 6)}" paint-order="stroke"'))
    leg = c.get("legenda")
    if leg and itens_legenda:
        cl = Campos(leg, f"{onde}.legenda", ["x", "y"])
        lh = fonte * 2.4
        larg = max(len(t) for _, t, _ in itens_legenda) * fonte * 0.5 + fonte * 4
        out.append(f'<rect x="{f(cl["x"])}" y="{f(cl["y"])}" width="{f(larg)}" height="{f(lh * len(itens_legenda) + fonte)}" rx="6" fill="#fff"/>')
        for k, (tinta, rot, tracejado) in enumerate(itens_legenda):
            y = cl["y"] + fonte * 0.5 + lh * k + lh / 2
            traco = f' stroke-dasharray="{f(esp)} {f(esp * 0.7)}"' if tracejado else ""
            out.append(f'<line x1="{f(cl["x"] + fonte * 0.8)}" x2="{f(cl["x"] + fonte * 2.8)}" y1="{f(y)}" y2="{f(y)}" stroke="{tinta}" stroke-width="{f(esp * 0.9)}" stroke-linecap="round"{traco}/>')
            out.append(texto(cl["x"] + fonte * 3.4, y + fonte * 0.35, rot, fonte, "#1a1a1a"))
    return svg(W, H, out, texto_puro(c.get("rotulo", "mapa"), dados))


TIPOS = {"linha_do_tempo": linha_do_tempo, "sondagem": sondagem, "marcos": marcos,
         "ciclo_pagamento": ciclo_pagamento, "mapa": mapa}


def gera(g: dict, dados: Dados, onde: str, **ctx) -> str:
    if not isinstance(g, dict) or "tipo" not in g:
        raise ErroApresentacao(f"{onde}: grafico precisa de 'tipo' ({', '.join(TIPOS)})")
    if g["tipo"] not in TIPOS:
        raise ErroApresentacao(f"{onde}: tipo de gráfico desconhecido '{g['tipo']}' (válidos: {', '.join(TIPOS)})")
    return TIPOS[g["tipo"]](g, dados, f"{onde}.{g['tipo']}", **ctx)
