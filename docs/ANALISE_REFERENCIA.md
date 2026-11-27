# Análise da apresentação de referência

Arquivo analisado: apresentação à diretoria de uma licitação de saneamento — ETA e adutoras (10 slides, HTML único de 6,5 MB).
O arquivo **não está neste repositório**, que é público e onde não entram dados de cliente, logos nem
fotos. O exemplo `exemplos/completo/` reproduz a mesma estrutura com dados fictícios.

Verificação técnica do original: nenhum erro de console, nenhum conteúdo saindo dos slides, PDF com
10 páginas.

---

## 1. Arquitetura do arquivo

| Item | Como era | Avaliação | No gerador |
|---|---|---|---|
| Formato | 1 HTML com CSS, JS, fonte e imagens embutidos (base64) | ✅ abre offline em qualquer navegador | mantido |
| Origem | gerado por Python ("os números já vêm prontos do Python"; `identidade.py` monta o @font-face) | ✅ a ideia certa | formalizado: YAML → `python -m apresenta` |
| CSS | ~300 linhas: metade de estilo de documento A4 (fórmulas, código, índice) que os slides não usam; outra metade com classes por slide (`.s2`, `.s3`, `.s8`, `.s9c`, `.modulo`) | ⚠️ classes por slide impedem reaproveitar | só o que os slides usam, mais uma **grade genérica** no lugar de classes por slide |
| HTML | escrito à mão/por template, com estrutura diferente em cada slide | ⚠️ cada apresentação nova recomeça do zero | gerado a partir de um **catálogo fechado de componentes** |
| Tamanho | 6,42 MB de base64; os 2 logos repetidos em 10 slides somam ~440 KB | ⚠️ desperdício | logos embutidos **uma vez** (classe CSS) |

## 2. Layout e escala

| Elemento | Como era | Avaliação | No gerador |
|---|---|---|---|
| Slide | `aspect-ratio:16/9`, `width:min(100vw,177.78vh)`, `container-type:inline-size` | ✅ escala o slide inteiro sem JS | mantido |
| Unidades | tudo em `cqw`/`em`; texto base 1,62cqw (~26 px a 1600 px) | ✅ proporção idêntica em qualquer tela | mantido, com **escala de texto documentada** |
| Navegação | rolagem vertical com `scroll-snap`, um slide centralizado por vez | ✅ funciona em projetor, notebook e celular | mantido |
| Estrutura | `palco` (flex coluna): cabeçalho → corpo (flex:1) → fonte → rodapé | ✅ corpo sempre ocupa o que sobra | mantido |
| Grades | CSS grid por slide com proporções (38%/62%, 1.55fr/1fr, 73%/27%) | ✅ visual / ⚠️ fixo no CSS | `corpo: {colunas: [38, 62], linhas: [...], celulas: [...]}` no YAML |
| Figuras | `figure > .quadro > img/svg`, `object-fit: contain`; `.cobre` para fotos | ✅ nunca distorce | mantido (`ajuste: conter/cobrir`) |

## 3. Tipografia e cores

| Elemento | Como era | Avaliação | No gerador |
|---|---|---|---|
| Fonte | Share Tech (OFL) embutida em woff2, subconjunto de 216 caracteres | ✅ identidade forte / ⚠️ sem ≈ ≥ ≤ → μ ∅ (o navegador usa Arial para esses símbolos) | `identidades/padrao/`; limitação registrada |
| Paleta | acento laranja `#b74912`, bege `#c8bcac`, preto, azul-água; variáveis CSS | ✅ coerente; os gráficos usam as mesmas variáveis | tokens no `identidade.yaml` |
| Negrito | `strong` sem peso, só na cor de acento | ✅ funciona bem com fonte de um peso só | `**texto**` no YAML |
| Tamanhos | legendas/fonte de 0,56–0,62em (~14–16 px); legendas da barra 70/20/10, tabela de marcos e síntese ≈ 14 px | ⚠️ pequeno para projetor | mínimo 0,58em (~15 px) e verificação automática (`--min-px`) |

## 4. Elementos fixos de todo slide

| Elemento | Como era | Avaliação | No gerador |
|---|---|---|---|
| Chapéu | "05 · Unidade 01 — módulo…" (número + seção, caixa alta, acento) | ✅ orienta sem ocupar espaço | **automático**: `secao:` + número do slide |
| Título | frase-conclusão ("Módulo 360 L/s: 39 estacas num solo que não passa de NSPT 15…") | ✅ **o melhor recurso da apresentação** | obrigatório; aviso acima de 95 caracteres |
| Fonte | linha "Fonte: prancha…, relatório…, item do TR" em todo slide | ✅ rastreabilidade | **campo obrigatório** (sem fonte, a montagem para) |
| Rodapé | logos + nome do consórcio/edital + "n / 10" | ✅ | **automático** (logos, texto, numeração) |
| Botão Imprimir/PDF | fixo no canto, sempre visível | ⚠️ aparece sobre o slide durante a apresentação | discreto (opacidade 15%), aparece ao passar o mouse |

## 5. Capa

Grade de 47/53%: chapéu, título grande, faixa de acento, subtítulos, caixa com data/hora em destaque,
logos e rótulo no pé; foto de drone ocupando a metade direita, com legenda.
✅ Limpa e informativa. → `layout: capa` com os mesmos campos; sem foto, o texto ocupa tudo.

## 6. Slide a slide

| # | Conteúdo | Elementos | Avaliação |
|---|---|---|---|
| 1 | Capa | foto, logos, data | ✅ |
| 2 | Regime de contratação | 4 KPIs-texto, linha do tempo SVG (7 eventos, um cancelado riscado, o final em destaque), citação do edital | ✅ / ⚠️ posição dos rótulos ajustada à mão → automática no gerador |
| 3 | A obra | duas colunas de listas (KPIs + lista numerada) + mapa: imagem de satélite escurecida, traçados com contorno branco, pontas, legenda e rótulo | ✅ / ⚠️ uma das 3 adutoras está na lista e não aparece no mapa |
| 4 | ETA hoje × 1ª fase | 2 fotos de drone + legenda de cores (azul 1ª etapa, verde existente, roxo 2ª etapa) | ✅ cores iguais às das pranchas |
| 5 | Módulo 360 L/s | corte (prancha), locação das estacas, 5 KPIs, sondagem SVG (camadas, NSPT, NA, fundo, impenetrável) + leitura | ✅ excelente: mostra a fundação inteira num slide |
| 6 | Módulo 600 L/s | **mesmo layout do 5** | ✅ comparação imediata |
| 7 | Adutoras | 3 destaques (extensão, DE, ruas) + tópicos + mosaico 2 mapas + 3 fotos | ✅ / ⚠️ espaço vazio entre destaques e tópicos |
| 8 | Prazos e marcos | gráfico de marcos (losangos MI01…MI06 com dia) + tabela de 9 marcos + 3 notas | ✅ / ⚠️ tabela e notas pequenas |
| 9 | Condições comerciais | ciclo medição → fatura → pagamento (dia 70/100/130) + barra 70/20/10 por item + blocos + barras 90/10 e 80/20 | ✅ conteúdo / ⚠️ o slide mais denso; legendas em ~14 px |
| 10 | Síntese | 4 frentes (miniatura + 3 números) + marcos de todas as frentes com aviso "não é o planejamento do consórcio" | ✅ / ⚠️ **forma: 2.540 m² no slide 6 e 2.541 m² aqui** |

## 7. Gráficos (todos SVG gerados por código)

| Gráfico | Slide | No gerador (`grafico: {tipo: …}`) |
|---|---|---|
| Linha do tempo do edital | 2 | `linha_do_tempo`: datas ISO, estados normal/destaque/cancelado, níveis automáticos sem sobreposição |
| Mapa com traçados | 3, 7 | `mapa`: imagem + escurecimento + traçados (contorno, pontas, tracejado) + rótulos + legenda |
| Sondagem SPT | 5, 6 | `sondagem`: camadas, NSPT por metro (cor por faixa ≤8 / ≤15 / >15), NA, fundo, impenetrável |
| Marcos / prazos | 8, 10 | `marcos`: barras de prazo, losangos, rótulo acima/abaixo, dia, legenda |
| Ciclo de pagamento | 9 | `ciclo_pagamento`: execução → medição → pagamento, dia de cada recebimento calculado |
| Barra 70/20/10 | 9 | `barra_segmentada` (HTML, não SVG): grupos + itens + legenda; **soma tem de dar 100%** |
| Barras 90/10, 80/20 | 9 | `barras` (HTML) |

Ponto forte: SVG fica nítido em qualquer zoom, pesa pouco e herda a paleta.
Ponto fraco: textos dos gráficos a ~9–11 px na tela (compensados pela lupa). No gerador, os textos
dos gráficos subiram de 2 a 3 pontos.

## 8. Imagens

37 imagens: 20 são os 2 logos repetidos; as demais são fotos de drone, ortofotos, recortes de
prancha (cortes 1:50, locação) e satélite. JPEG de 30–615 KB, de 700 a 2.620 px.
✅ Resolução boa para a lupa. → Gerador: `python -m apresenta imagens` (PNG para desenho, JPG para
foto), aviso acima de 900 KB, imagens lidas sem recompressão.

## 9. Interatividade (JS de ~120 linhas)

| Recurso | Avaliação | No gerador |
|---|---|---|
| Lupa: clona a figura (imagem **ou SVG a 2x**), zoom de 1x a 14x no ponto do cursor | ✅ | mantido |
| Roda do mouse, pinça (2 dedos), arraste, duplo clique (3x / volta) | ✅ | mantido + pinça de trackpad (ctrl+roda) suave |
| Teclado: + − 0 Esc na lupa; setas/PageUp/PageDown/Espaço nos slides | ✅ | mantido + setas movem a imagem na lupa, Home/End, F (tela cheia), `#5` na URL |
| "+ ampliar" via CSS `::after` (some na impressão) | ✅ | mantido |

## 10. Impressão

`@page 13,333 × 7,5 in` (widescreen do PowerPoint), 1 slide por página, sem botões.
✅ → mantido; a verificação confere páginas = slides.

## 11. O que mudou para ficar determinístico

1. **A IA escreve YAML, não HTML**: um catálogo fechado de componentes, e qualquer campo
   desconhecido faz a montagem parar com mensagem dizendo onde está o erro.
2. **Números só no `dados.yaml`**, citados como `{modulo_b.forma:milhar}`. Isso impede o 2.540/2.541.
3. **Conferências** no `dados.yaml` (`soma das adutoras == extensão total`, `aço ≈ 100 kg/m³`).
4. **Saída idêntica byte a byte** para a mesma entrada (SHA-256 exibido e testado).
5. **Verificação automática** no Chromium: texto cortado, letra pequena, lupa, PDF.
