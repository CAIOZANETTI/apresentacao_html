"""Monta a apresentação: apresentacao.yaml + dados.yaml + identidade -> 1 arquivo HTML.

Determinismo: mesma entrada => mesmo arquivo, byte a byte (sem data/hora, sem aleatoriedade,
imagens embutidas sem recompressão, coordenadas arredondadas). O SHA-256 da saída é exibido
para conferência.
"""
from __future__ import annotations

import base64
import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .componentes import Contexto, grade
from .conferir import conferir
from .erros import Campos, ErroApresentacao
from .formato import Dados, texto_html, texto_puro

RAIZ = Path(__file__).resolve().parent.parent
ESTATICO = Path(__file__).resolve().parent / "estatico"
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".svg": "image/svg+xml",
        ".webp": "image/webp", ".gif": "image/gif", ".woff2": "font/woff2"}
LIMITE_IMAGEM_KB = 900
TOKENS_COR = ["acento", "bege", "bege_claro", "preto", "agua", "tinta", "suave", "tenue", "linha", "zebra", "papel", "mesa"]


@dataclass
class Resultado:
    saida: Path
    sha256: str
    bytes: int
    slides: int
    avisos: list[str] = field(default_factory=list)


def carrega_yaml(p: Path) -> dict:
    if not p.exists():
        raise ErroApresentacao(f"arquivo não encontrado: {p}")
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        raise ErroApresentacao(f"YAML inválido em {p.name}: {e}")


class Imagens:
    def __init__(self, base: Path, avisos: list[str]):
        self.base, self.avisos, self.cache = base, avisos, {}

    def caminho(self, rel: str, onde: str) -> Path:
        p = (self.base / rel).resolve()
        if not p.exists():
            raise ErroApresentacao(f"{onde}: imagem não encontrada: {rel}")
        if p.suffix.lower() not in MIME:
            raise ErroApresentacao(f"{onde}: formato não suportado: {p.suffix}")
        return p

    def uri(self, rel: str, onde: str) -> str:
        p = self.caminho(rel, onde)
        if p not in self.cache:
            b = p.read_bytes()
            if len(b) > LIMITE_IMAGEM_KB * 1024:
                self.avisos.append(f"{rel}: {len(b) // 1024} KB — recorte ou reduza (limite sugerido {LIMITE_IMAGEM_KB} KB)")
            self.cache[p] = f"data:{MIME[p.suffix.lower()]};base64," + base64.b64encode(b).decode("ascii")
        return self.cache[p]

    def tamanho(self, rel: str, onde: str) -> tuple[int, int]:
        p = self.caminho(rel, onde)
        if p.suffix.lower() == ".svg":
            t = p.read_text(encoding="utf-8")[:2000]
            w, h = re.search(r'\bwidth="([\d.]+)', t), re.search(r'\bheight="([\d.]+)', t)
            if w and h:
                return round(float(w.group(1))), round(float(h.group(1)))
            vb = re.search(r'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"', t)
            if vb:
                return round(float(vb.group(1))), round(float(vb.group(2)))
            raise ErroApresentacao(f"{onde}: SVG sem width/height nem viewBox: {rel}")
        from PIL import Image
        with Image.open(p) as im:
            return im.size


# ------------------------------------------------------------------ identidade
def carrega_identidade(ref: str, base: Path) -> tuple[dict, Path]:
    candidatos = [base / ref, RAIZ / "identidades" / ref]
    for d in candidatos:
        if (d / "identidade.yaml").exists():
            ident = carrega_yaml(d / "identidade.yaml")
            Campos(ident, f"identidade {ref}", ["nome", "fonte", "cores"], ["logos", "rodape", "descricao"])
            return ident, d
    raise ErroApresentacao(f"identidade '{ref}' não encontrada (procurado em {', '.join(str(c) for c in candidatos)})")


def css_identidade(ident: dict, pasta: Path, avisos: list[str]) -> str:
    cf = Campos(ident["fonte"], "identidade.fonte", ["familia"], ["arquivo"])
    partes = []
    if cf.get("arquivo"):
        img = Imagens(pasta, avisos)
        partes.append(f"@font-face{{font-family:'{cf['familia']}';font-style:normal;font-weight:400;font-display:block;"
                      f"src:url({img.uri(cf['arquivo'], 'identidade.fonte')}) format('woff2')}}")
    cores = ident["cores"]
    desconhecidas = sorted(set(cores) - set(TOKENS_COR))
    if desconhecidas:
        raise ErroApresentacao(f"identidade.cores: token desconhecido {desconhecidas} (válidos: {TOKENS_COR})")
    tokens = ";".join(f"--{k.replace('_', '-')}:{v}" for k, v in cores.items())
    partes.append(f":root{{--fonte:'{cf['familia']}';{tokens}}}")
    return "\n".join(partes)


def css_logos(logos: list, pasta: Path, avisos: list[str]) -> tuple[str, list[dict]]:
    """Logos entram UMA vez como classes CSS; capa e rodapés só referenciam a classe."""
    img = Imagens(pasta, avisos)
    regras, info = [], []
    for i, lg in enumerate(logos or []):
        c = Campos(lg, f"logos[{i + 1}]", ["arquivo", "nome"], ["fundo"])
        w, h = img.tamanho(c["arquivo"], f"logos[{i + 1}]")
        regras.append(f".logo-{i + 1}{{background-image:url({img.uri(c['arquivo'], f'logos[{i + 1}]')});aspect-ratio:{w}/{h}}}")
        info.append({"classe": f"logo-{i + 1}", "nome": c["nome"], "escuro": c.get("fundo") == "escuro"})
    return "\n".join(regras), info


def html_logos(info: list[dict]) -> str:
    out = []
    for lg in info:
        span = f'<span class="logo {lg["classe"]}" role="img" aria-label="{texto_puro(lg["nome"], Dados({}))}"></span>'
        out.append(f'<span class="selo">{span}</span>' if lg["escuro"] else span)
    return "".join(out)


# ------------------------------------------------------------------ slides
def slide_capa(s: dict, ctx: Contexto, onde: str, logos: str) -> str:
    c = Campos(s, onde, ["layout", "titulo"], ["chapeu", "subtitulos", "destaque", "rotulo", "foto"])
    t = ctx.t
    subs = "".join(f'<p class="subtitulo">{t(x)}</p>' for x in c.lista("subtitulos"))
    dest = f'<p class="data-capa">{t(c["destaque"])}</p>' if c.get("destaque") else ""
    foto = ""
    if c.get("foto"):
        cf = Campos(c["foto"], f"{onde}.foto", ["imagem"], ["legenda"])
        leg = f'<span class="legenda-foto">{t(cf["legenda"])}</span>' if cf.get("legenda") else ""
        alt = texto_puro(cf.get("legenda", ""), ctx.dados).replace('"', "&quot;")
        foto = f'<div class="capa-foto"><img src="{ctx.imagem_uri(cf["imagem"], onde + ".foto")}" alt="{alt}">{leg}</div>'
    chapeu = f'<p class="chapeu">{t(c["chapeu"])}</p>' if c.get("chapeu") else ""
    rot = f'<span class="rotulo">{t(c["rotulo"])}</span>' if c.get("rotulo") else ""
    classe = "capa" if foto else "capa sem-foto"
    return (f'<div class="palco" style="padding:0"><div class="{classe}"><div class="capa-texto">{chapeu}'
            f'<h1 class="titulo-capa">{t(c["titulo"])}</h1><div class="faixa"></div>{subs}{dest}'
            f'<div class="logos-capa">{logos}{rot}</div></div>{foto}</div></div>')


def slide_conteudo(s: dict, ctx: Contexto, onde: str, n: int, total: int, logos: str, rodape: str, avisos: list[str]) -> str:
    c = Campos(s, onde, ["secao", "titulo", "fonte", "corpo"], ["layout", "notas_orador"])
    titulo = texto_puro(c["titulo"], ctx.dados)
    if len(titulo) > 95:
        avisos.append(f"{onde}: título com {len(titulo)} caracteres — mais de 2 linhas; encurte (alvo ≤ 80)")
    corpo = grade(c["corpo"], ctx, f"{onde}.corpo")
    return (f'<div class="palco"><header><p class="chapeu">{n:02d} · {ctx.t(c["secao"])}</p>'
            f'<h2>{ctx.t(c["titulo"])}</h2></header><div class="corpo">{corpo}</div>'
            f'<p class="fonte">Fonte: {ctx.t(c["fonte"])}</p>'
            f'<footer><span class="marca">{logos}</span><span>{ctx.t(rodape)}</span><span>{n} / {total}</span></footer></div>')


# ------------------------------------------------------------------ montagem
def montar(pasta: Path, saida: Path | None = None) -> Resultado:
    pasta = Path(pasta).resolve()
    spec = carrega_yaml(pasta / "apresentacao.yaml")
    c = Campos(spec, "apresentacao.yaml", ["apresentacao", "slides"])
    meta = Campos(c["apresentacao"], "apresentacao", ["titulo", "identidade"], ["arquivo", "rodape", "logos", "idioma"])
    dados_arq = pasta / "dados.yaml"
    bruto = carrega_yaml(dados_arq) if dados_arq.exists() else {}
    regras = bruto.pop("conferir", []) if isinstance(bruto, dict) else []
    conferir(regras, Dados(bruto))          # instância separada: não conta como "usado" nos slides
    dados = Dados(bruto)
    avisos: list[str] = []

    ident, pasta_ident = carrega_identidade(meta["identidade"], pasta)
    css_ident = css_identidade(ident, pasta_ident, avisos)
    # logos: os do projeto (privados) têm prioridade sobre os da identidade
    if meta.get("logos") is not None:
        css_lg, info_lg = css_logos(meta["logos"], pasta, avisos)
    else:
        css_lg, info_lg = css_logos(ident.get("logos", []), pasta_ident, avisos)
    logos = html_logos(info_lg)
    rodape = meta.get("rodape") or ident.get("rodape") or ""

    imgs = Imagens(pasta, avisos)
    ctx = Contexto(dados, imgs.uri, imgs.tamanho)
    slides = c.lista("slides")
    if not slides:
        raise ErroApresentacao("apresentacao.yaml: nenhum slide")
    total = len(slides)
    html_slides = []
    for i, s in enumerate(slides, 1):
        onde = f"slide {i}"
        if not isinstance(s, dict):
            raise ErroApresentacao(f"{onde}: esperado um bloco com campos")
        layout = s.get("layout", "conteudo")
        if layout == "capa":
            corpo = slide_capa(s, ctx, onde, logos)
        elif layout == "conteudo":
            corpo = slide_conteudo(s, ctx, onde, i, total, logos, rodape, avisos)
        else:
            raise ErroApresentacao(f"{onde}.layout: capa ou conteudo (padrão)")
        notas = s.get("notas_orador")
        aside = f'<aside class="notas-orador">{texto_html(notas, dados)}</aside>' if notas else ""
        html_slides.append(f'<section class="slide" id="s{i}">{corpo}{aside}</section>')

    for chave in dados.nao_usadas():
        avisos.append(f"dados.yaml: '{chave}' não é usado em nenhum slide")

    css = (ESTATICO / "base.css").read_text(encoding="utf-8")
    js = (ESTATICO / "apresentacao.js").read_text(encoding="utf-8")
    titulo = texto_puro(meta["titulo"], dados).replace("<", "&lt;")
    doc = (f'<!DOCTYPE html>\n<html lang="{meta.get("idioma", "pt-BR")}"><head><meta charset="utf-8">'
           f'<meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<meta name="generator" content="apresenta">'
           f"<title>{titulo}</title>\n<style>\n{css}\n{css_ident}\n{css_lg}\n</style></head>\n<body>"
           f'<button class="imprimir" onclick="print()" title="Imprimir ou salvar PDF">Imprimir / PDF</button>\n'
           + "\n".join(html_slides) +
           '\n<div class="lupa" id="lupa" hidden><div class="lupa-palco"></div>'
           '<button class="lupa-fechar" title="Fechar (Esc)">×</button><div class="lupa-barra">'
           '<button data-acao="menos" title="Afastar (−)">−</button><button data-acao="ajustar" title="Ajustar à tela (0)">ajustar</button>'
           '<button data-acao="mais" title="Aproximar (+)">+</button><span class="lupa-legenda"></span></div></div>\n'
           f"<script>\n{js}</script>\n</body></html>\n")

    nome = meta.get("arquivo") or pasta.name.upper()
    saida = Path(saida) if saida else pasta / "dist" / f"{nome}.html"
    saida.parent.mkdir(parents=True, exist_ok=True)
    dados_bytes = doc.encode("utf-8")
    saida.write_bytes(dados_bytes)
    return Resultado(saida, hashlib.sha256(dados_bytes).hexdigest(), len(dados_bytes), total, avisos)
