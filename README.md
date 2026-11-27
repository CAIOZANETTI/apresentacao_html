# apresentacao_html

Gerador de **apresentações executivas de engenharia** em um único arquivo HTML, a partir de YAML + Python.
A apresentação vira dados, e o código desenha os slides sempre do mesmo jeito: a mesma entrada gera
o mesmo arquivo, byte a byte.

Feito a partir de uma apresentação real à diretoria (licitação de ETA e adutoras, 10 slides).
A análise completa dela está em [`docs/ANALISE_REFERENCIA.md`](docs/ANALISE_REFERENCIA.md).

## O que o arquivo final tem

- **Slides 16:9** que escalam com a tela (cqw) e passam com rolagem/teclado. Funcionam offline.
- **Lupa** em toda figura: roda do mouse, pinça, arraste, duplo clique, `+ − 0`, `Esc`. Figuras SVG ampliam a 2x.
- **Gráficos SVG gerados por código**: linha do tempo, sondagem SPT, marcos de prazo, ciclo de
  pagamento, mapa com traçados.
- **Automático**: chapéu numerado ("05 · Seção"), número de página, rodapé com logos (embutidos uma
  vez só), fonte da identidade embutida.
- **Obrigatório**: título-conclusão e fonte em todo slide.
- **Impressão**: 1 slide por página no formato widescreen (13,333 × 7,5 in).

## Como fica determinístico

| Garantia | Como |
|---|---|
| A IA não "inventa" layout | Ela escreve só **YAML** num catálogo fechado de componentes ([`docs/LINGUAGEM.md`](docs/LINGUAGEM.md)). Campo desconhecido faz a montagem parar. |
| Número igual em todo slide | Números só no `dados.yaml`, citados como `{modulo_b.forma:milhar}`. |
| Contas que fecham | `conferir:` no `dados.yaml` (ex.: soma das adutoras = total). Se falhar, a montagem para. |
| Mesma saída sempre | Sem data/hora nem aleatoriedade, imagens sem recompressão, coordenadas arredondadas. SHA-256 exibido e testado. |
| Nada cortado ou ilegível | `verificar` abre no Chromium e checa transbordamento, letra < 14 px, lupa e PDF. |

## Uso

```bash
pip install -r requirements.txt
python -m playwright install chromium          # para o "verificar"

python -m apresenta novo projetos/2027_minha_obra           # copia o exemplo completo
python -m apresenta imagens fontes/prancha.pdf --listar     # PDF -> imagens
python -m apresenta imagens fontes/prancha.pdf -p 3 --recorte 0.05,0.10,0.70,0.85 -o projetos/2027_minha_obra/img -n corte
# editar projetos/2027_minha_obra/apresentacao.yaml e dados.yaml
python -m apresenta verificar projetos/2027_minha_obra      # monta + testa + capturas + PDF
# entregar: projetos/2027_minha_obra/dist/<ARQUIVO>.html
```

O exemplo completo (10 slides fictícios com todos os componentes e gráficos):

```bash
python exemplos/completo/gerar_imagens.py    # (re)gera as imagens fictícias
python -m apresenta verificar exemplos/completo
```

Testes: `python -m pytest testes -q`

## Estrutura

```
apresenta/              gerador (Python)
  montar.py             YAML -> HTML único
  componentes.py        catálogo de componentes (grade, kpis, lista, tabela, figura…)
  graficos.py           gráficos SVG (linha do tempo, sondagem, marcos, ciclo de pagamento, mapa)
  formato.py            números pt-BR e referências {dados}
  conferir.py           conferências do dados.yaml
  verificar.py          teste no Chromium
  imagens.py            PDF -> PNG/JPG
  estatico/             base.css e apresentacao.js (iguais em toda apresentação)
identidades/padrao/     fonte Share Tech (OFL), paleta, logos genéricos
exemplos/completo/      exemplo de referência (dados fictícios)
projetos/               suas apresentações (IGNORADO pelo git — repositório público)
docs/                   análise da referência, linguagem YAML, guia de estilo
testes/                 pytest
```

## Identidade visual

`identidades/padrao/identidade.yaml` define fonte, cores e logos. Para outra marca, copie a pasta e
troque os valores. **Logos reais de empresas não vão para este repositório público.** Coloque-os em
`projetos/<nome>/logos/` e declare-os em `apresentacao.yaml → logos`.
