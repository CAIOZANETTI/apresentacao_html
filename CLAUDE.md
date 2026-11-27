# Instruções para a IA — apresentações HTML de engenharia

Este repositório é o **modelo** das apresentações executivas do usuário, engenheiro civil que programa
em Python (numpy, pandas, plotly). Ao criar ou alterar uma apresentação, siga este roteiro.

## Antes de começar

1. Leia `docs/GUIA_DE_ESTILO.md` (regras de conteúdo) e `docs/COMPONENTES.md` (trechos HTML).
2. Crie a apresentação em `projetos/<aaaa>_<nome_curto>/` copiando `modelo/` inteiro.
   Nunca edite `modelo/` para um projeto específico. Altere `modelo/` só quando a melhoria valer para
   todas as apresentações, e registre a mudança no README.

## Construção

- Mantenha **intactos** os blocos de CSS e JS do modelo (estrutura, ampliação, navegação, impressão).
  Para mudar cores, altere os tokens em `:root`.
- Os números vão em `dados.json` e aparecem com `data-campo`. Não digite o mesmo número em dois slides.
- As figuras saem de `scripts/pdf_para_imagens.py` (PNG 200 dpi, recortadas), em `img/`, com `figure.zoom`.
- Os documentos de origem ficam em `projetos/<nome>/fontes/`. As pendências (dados a confirmar,
  propostas que ainda vão chegar) ficam em `projetos/<nome>/PENDENCIAS.md`.
- Não invente números. Se um dado falta, escreva “a definir” e registre em PENDENCIAS.md.
- Gráficos calculados (curvas, histogramas, fluxo de caixa) podem ser gerados em Python (plotly →
  `fig.write_image('img/x.png', scale=2)` ou SVG) e entram como figura ampliável.

## Verificação (obrigatória antes de entregar)

```bash
python scripts/empacotar.py projetos/<nome>/apresentacao.html
python scripts/verificar.py projetos/<nome>/dist/APRESENTACAO.html --capturas projetos/<nome>/dist/capturas --pdf projetos/<nome>/dist/APRESENTACAO.pdf
```

- `verificar.py` precisa terminar com “OK”. Se o Chromium do Playwright não estiver instalado,
  use `CHROMIUM_PATH=/caminho/do/chrome`.
- Olhe as capturas. Espaço vazio sobrando, texto pequeno e blocos desproporcionais foram os ajustes
  mais pedidos nas revisões.

## Revisões

- Cada pedido de ajuste do usuário que vire regra geral (ex.: “tirar matriz de riscos”, “blocos do
  mesmo tamanho”) deve ser acrescentado ao `docs/GUIA_DE_ESTILO.md`.
- `dist/` não é versionado. Para entregar, envie o arquivo `dist/*.html`.
