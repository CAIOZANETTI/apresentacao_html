# apresentacao_html

Modelo para apresentações executivas de **projetos de engenharia** em um único arquivo HTML:
figuras de projeto ampliáveis, números vindos de um `dados.json`, impressão em PDF com 1 slide por página.
Nasceu da apresentação à diretoria do projeto de ETA/adutoras (10 slides) e guarda as decisões de formato
que funcionaram ali.

## Por que HTML e não PowerPoint

- **Pranchas legíveis:** cada figura tem o botão **“+ ampliar”**. O zoom vai até 12x sobre a imagem
  em alta resolução, o que permite ler cotas e textos das pranchas em plena reunião.
- **Um arquivo só:** imagens embutidas. Abre em qualquer navegador, inclusive offline.
- **Números consistentes:** prazos e quantitativos ficam no `dados.json` e aparecem em todos os slides
  que os citam. Se o número muda, muda em todos.
- **Gerado com IA + Python:** o fluxo foi feito para pedir slides à IA e regenerar rápido.

## Estrutura

```
modelo/                  ← NÃO editar para um projeto; copiar
  apresentacao.html      ← modelo com CSS + JS + 9 slides de exemplo (um de cada tipo)
  dados.json             ← números do projeto (fonte única)
  img/                   ← figuras (SVG de exemplo)
scripts/
  pdf_para_imagens.py    ← PDF de projeto → PNG em alta resolução (página ou recorte)
  empacotar.py           ← embute imagens + dados → 1 arquivo HTML final em dist/
  verificar.py           ← testa no Chromium: erros, texto cortado, zoom, PDF 1 pág/slide
docs/
  GUIA_DE_ESTILO.md      ← regras de conteúdo e forma (o que a diretoria aprovou)
  COMPONENTES.md         ← trechos HTML prontos de cada bloco
projetos/                ← uma pasta por apresentação
CLAUDE.md                ← instruções para a IA seguir o modelo
```

## Fluxo para uma nova apresentação

```bash
pip install -r requirements.txt
python -m playwright install chromium         # só para o verificar.py

# 1. copiar o modelo
cp -r modelo projetos/2027_minha_obra

# 2. extrair figuras dos PDFs do projeto
python scripts/pdf_para_imagens.py fontes/fundacoes.pdf --listar
python scripts/pdf_para_imagens.py fontes/fundacoes.pdf -p 3 --recorte 0.05,0.10,0.70,0.85 --dpi 200 \
       -o projetos/2027_minha_obra/img -n locacao_estacas

# 3. preencher dados.json e editar os slides (ou pedir à IA — ver CLAUDE.md)

# 4. gerar o arquivo final e verificar
python scripts/empacotar.py projetos/2027_minha_obra/apresentacao.html
python scripts/verificar.py projetos/2027_minha_obra/dist/APRESENTACAO.html --capturas projetos/2027_minha_obra/dist/capturas --pdf projetos/2027_minha_obra/dist/APRESENTACAO.pdf
```

Durante a edição, abra `projetos/<nome>/apresentacao.html` direto no navegador. As imagens são
lidas de `img/` e os dados do bloco `<script id="dados">` dentro do HTML. O `empacotar.py`
grava o `dados.json` nesse bloco no arquivo final.

## Usando a apresentação

| Ação | Como |
|---|---|
| Próximo / anterior | → ← · PageDown PageUp · Espaço · setas no canto |
| Primeiro / último | Home / End |
| Abrir slide N | `arquivo.html#N` |
| Ampliar figura | botão **+ ampliar** ou clique na figura |
| Zoom | roda do mouse · pinça do trackpad · `+` `−` · duplo clique no ponto |
| Mover figura ampliada | arrastar · setas · rolagem com 2 dedos |
| Ajustar / fechar | `0` / `Esc` |
| PDF | Ctrl+P → Salvar como PDF (paisagem, sem margens, com gráficos de fundo) |
