# Linguagem da apresentação (YAML)

Um projeto tem três arquivos:

```
projetos/2027_minha_obra/
  apresentacao.yaml   ← slides (este documento)
  dados.yaml          ← números (fonte única) + conferências
  img/                ← figuras (PNG de prancha, JPG de foto, SVG)
```

Montar: `python -m apresenta montar projetos/2027_minha_obra` (ou `verificar`, que também testa no navegador).
Qualquer campo ou componente que não esteja aqui **faz a montagem parar** e a mensagem diz onde
está o erro (`slide 5.corpo.celulas[2][1].figura: campo desconhecido 'legend'`).

---

## 1. Texto

Toda string aceita:

| Escrita | Resultado |
|---|---|
| `{modulo_b.forma:milhar} m²` | valor do dados.yaml formatado → `2.540 m²` |
| `**Sem adiantamento**` | destaque na cor de acento |
| quebra de linha (`\n` ou bloco `\|`) | `<br>` |

Formatos: `milhar` (2.540), `dec1` (14,5), `dec2` (14,49), `pct` (70%), `pct1` (12,3%), `moeda`
(R$ 1.234,56), `texto`. Sem formato: inteiro → milhar; decimal → até 2 casas.
Uma chave inexistente interrompe a montagem.

## 2. Cabeçalho do arquivo

```yaml
apresentacao:
  titulo: "{contrato.edital} · Apresentação à diretoria"   # aba do navegador
  identidade: padrao          # identidades/padrao/ (ou caminho relativo ao projeto)
  arquivo: APRESENTACAO_X     # nome do HTML em dist/ (padrão: nome da pasta)
  rodape: "Consórcio X — Obra Y, {contrato.edital}"       # padrão: o da identidade
  logos:                      # opcional: logos do projeto (substituem os da identidade)
    - {arquivo: logos/empresa.svg, nome: Empresa}
    - {arquivo: logos/parceira.png, nome: Parceira, fundo: escuro}
slides: [...]
```

## 3. Slides

### Capa

```yaml
- layout: capa
  chapeu: "Cliente · Licitação {contrato.edital} · Lote único"
  titulo: Ampliação do Sistema de Abastecimento de Água
  subtitulos: ["ETA — módulos de 360 e 600 L/s", "6.420 m de adutoras"]
  destaque: "Abertura de preços · {contrato.abertura}"
  rotulo: "Consórcio X\nApresentação à diretoria — novembro de 2026"
  foto: {imagem: img/capa.jpg, legenda: "ETA — drone"}       # opcional
```

### Conteúdo (todos os outros)

```yaml
- secao: Prazos e marcos          # chapéu: "08 · Prazos e marcos" (número automático)
  titulo: "Unidade 01 em {unidade_01.prazo} dias…"   # frase-CONCLUSÃO, ≤ 80 caracteres
  fonte: Termo de Referência, item 7                  # OBRIGATÓRIO
  notas_orador: texto opcional (não aparece no slide)
  corpo:                                              # uma grade
    colunas: [1.55, 1]          # proporções (fr) — padrão [1]
    linhas: [auto, 1]           # 'auto' = altura do conteúdo; número = proporção; '12cqw' = fixa
    espaco: normal              # normal | justo | largo
    celulas:                    # preenchidas da esquerda p/ direita, de cima p/ baixo
      - vao: 2                  # ocupa 2 colunas
        componentes: [...]
      - [ ...componentes... ]   # forma curta: lista de componentes
```

Opções da célula: `vao` (colunas), `vao_linhas` (linhas), `estilo: faixa | caixa`, `alinhar: topo | centro | base`.
Numa célula, os componentes ficam empilhados e as **figuras ocupam a altura que sobra**.

## 4. Componentes

Cada componente é um bloco de **uma** chave.

| Componente | Campos | Uso |
|---|---|---|
| `titulo: "texto"` | — | subtítulo de bloco (acento) |
| `texto: "…"` | — | parágrafo |
| `leitura: "…"` | — | interpretação curta sob figura (com filete) |
| `citacao: "…"` | — | trecho de documento |
| `notas: [..]` | — | observações com filete de acento |
| `lista` | `itens`, `titulo?`, `numerada?` — ou só a lista | tópicos |
| `kpis` | `itens: [{valor, texto}]`, `colunas?`, `tamanho?: normal/grande/menor` | números grandes |
| `destaques` | lista de `{valor, titulo, texto?}` | ex.: extensão + DE + ruas de cada adutora |
| `alerta` | `titulo`, `texto?` | caixa vermelha (risco, condição crítica) |
| `legenda_cores` | lista de `{cor, titulo, texto?}` | etapas/fases coloridas das pranchas |
| `tabela` | `colunas: [texto ou {titulo, alinhar: direita}]`, `linhas`, `total?`, `titulo?`, `compacta?` | tabela limpa |
| `figura` | `imagem` **ou** `grafico`; `legenda?`, `ajuste: conter/cobrir`, `altura: preenche/natural/15cqw`, `moldura?`, `ampliavel?` (padrão sim), `descricao?` | figura com lupa |
| `barras` | `itens: [{rotulo, partes: [{valor, texto?, final?}], nota?}]`, `titulo?` | 90% / 10% retido |
| `barra_segmentada` | `grupos: [{rotulo, tom: forte/medio/escuro, itens: [{valor, texto}]}]`, `titulo?`, `legenda?` | 70/20/10 por item; **soma = 100** |
| `grade` | igual ao `corpo` | grade dentro de célula |

Cores (`cor:`): token da identidade (`acento`, `agua`, `preto`, `bege`…) ou hexadecimal (`"#2f6fd6"`).

## 5. Gráficos (`figura: {grafico: {tipo: …}}`)

Números de gráfico também aceitam referência: `prazo: "{unidade_01.prazo}"`.

```yaml
tipo: linha_do_tempo
inicio: 2026-06            # AAAA-MM
fim: 2026-12
eventos:
  - {data: 2026-06-15, texto: Termo de Referência assinado}
  - {data: 2026-10-13, texto: Data original, estado: cancelado}   # normal | destaque | cancelado
  - {data: 2026-12-01, texto: Abertura, estado: destaque, rotulo: "01/12 10h", nivel: 1}  # nivel: ±1..3 (opcional)
```

```yaml
tipo: sondagem
furo: SP-02
camadas: [{ate: 4.65, descricao: argila siltosa mole}, {ate: 14.49, descricao: silte rijo, cor: "#e3d3a8"}]
nspt: [{prof: 1, n: 6}, {prof: 2, n: 4}]     # profundidade em m
nivel_agua: 9.0          # opcionais
fundo: 1.2
impenetravel: 14.49
```

```yaml
tipo: marcos
escala: {max: 540, passo: 60, unidade: d}
legenda: true             # opcional
linhas:
  - nome: Unidade 01
    prazo: "{unidade_01.prazo}"
    marcos: [{dia: 150, rotulo: MI01, lado: cima, mostrar_dia: true}]   # lado: cima | baixo
```

```yaml
tipo: ciclo_pagamento
meses: 3
dias_mes: 30
dias_medicao: 10
prazo_pagamento: 30       # dia do recebimento = fim do mês + medição + prazo
```

```yaml
tipo: mapa
imagem: img/satelite.jpg            # coordenadas em PIXELS desta imagem
escurecer: 0.32
tracados:
  - {pontos: [[995,95],[925,130],[378,296]], cor: "#1e88e5", rotulo: "AAT 03 · 2.923 m"}
  - {pontos: [[435,306],[805,1108]], cor: "#f5d742", tracejado: true, rotulo: "≈ 5,2 km"}
rotulos: [{x: 1021, y: 105, texto: ETA}]
legenda: {x: 840, y: 420}           # canto superior esquerdo da caixa
```

Para pegar coordenadas de traçado: abra a imagem num editor (GIMP, Paint, Photoshop) e anote os
pixels, ou converta coordenadas geográficas (KML do Google Earth) para pixels com Python.

## 6. dados.yaml

```yaml
modulo_b: {vazao: 600, concreto: 478, aco_t: 48, forma: 2540}
adutoras:
  a: {nome: AAT 01, extensao: 3160}
conferir:                                    # verificadas a cada montagem
  - adutoras.a.extensao + adutoras.b.extensao == unidade_02.extensao
  - round(modulo_b.concreto * 0.1) == modulo_b.aco_t
```

Conferências aceitam `+ - * /`, `round abs min max`, comparações e `and/or`. Nada mais é executado.
Dados que nenhum slide usa geram **aviso**: `montar --estrito` transforma avisos em erro.
