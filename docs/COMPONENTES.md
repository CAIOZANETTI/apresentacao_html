# Componentes — trechos prontos

Cole dentro de `<div class="corpo">` de um slide. Os exemplos em funcionamento estão em `modelo/apresentacao.html`.

## Slide (esqueleto)

```html
<section class="slide">
  <header>
    <div><h1>Título curto</h1><p class="sub">A pergunta que o slide responde</p></div>
    <div class="selo"><span class="tag">em execução</span></div>   <!-- opcional -->
  </header>
  <div class="corpo">
    ...
  </div>
  <div class="rodape"><span data-campo="projeto.nome"></span><span class="num-slide"></span></div>
</section>
```

## Número do dados.json

```html
<span data-campo="unidades.0.prazo_dias"></span> dias
<span data-campo="modulo.aco_kg" data-formato="milhar"></span> kg      <!-- 31.000 -->
<span data-campo="contrato.valor" data-formato="moeda"></span>        <!-- R$ 12.345.678 -->
<span data-campo="pagamento.entrega" data-formato="pct"></span>       <!-- 70% -->
```

Um campo inexistente aparece como aviso no console, e o `verificar.py` acusa o problema.

## KPIs

```html
<div class="kpis" style="--n:4">
  <div class="kpi"><div class="valor">540 <small>dias</small></div><div class="rotulo">prazo Unidade 01</div></div>
  <div class="kpi cinza"><div class="valor">2</div><div class="rotulo">linhas (Fase 2)</div></div>
</div>
```

## Grades

| Classe | Uso |
|---|---|
| `grade-2` / `grade-3` / `grade-4` | blocos iguais |
| `grade-2-1` / `grade-1-2` | figura grande + coluna de tabela |
| `grade-cheia` (junto com a grade) | força a ocupar a altura toda mesmo sem figura |
| `coluna` | empilha blocos dentro de uma célula |

Uma grade que contém `<figure>` ocupa automaticamente toda a altura livre do slide.

## Figura ampliável

```html
<figure class="zoom">
  <div class="moldura"><img src="img/corte_AA.png" alt="Corte A-A"></div>
  <figcaption>Corte longitudinal A-A — Módulo 360 L/s</figcaption>
</figure>
```

## Bloco

```html
<div class="bloco">        <!-- .bloco.azul = destaque/Fase 1 · .bloco.cinza = futuro/secundário -->
  <h3>Título</h3>
  <ul><li>...</li></ul>
</div>
```

## Tabela

```html
<table class="tabela">            <!-- .tabela.compacta para 3+ colunas -->
  <tr><th>Item</th><th class="num">Qtd.</th></tr>
  <tr><td>Concreto</td><td class="num">310 m³</td></tr>
  <tr class="total"><td>Total</td><td class="num">620 m³</td></tr>
</table>
```

## Etapas numeradas

```html
<div class="etapas" style="--n:4">
  <div data-n="1"><b>Sem adiantamento</b>Mobilização com recursos próprios</div>
  <div data-n="2"><b>Medição mensal</b>...</div>
</div>
```

## Barra de percentuais

```html
<div class="pct">
  <div style="--p:70">70% entrega</div>
  <div style="--p:20">20% instalação</div>
  <div style="--p:10">10%</div>
</div>
```

## Cronograma

`--total` é o número de meses. `--ini` e `--fim` são os meses de início e fim (0 = início da OS).
`--em` é o mês do marco. Use `.marco.fim` quando o marco estiver no último mês.

```html
<div class="crono" style="--total:18">
  <div class="escala"><div></div><div class="meses"><span>1</span>...<span>18</span></div></div>
  <div class="linha">
    <div class="nome">Unidade 01<small>540 dias</small></div>
    <div class="trilho">
      <div class="barra" style="--ini:0;--fim:18">execução</div>      <!-- .barra.claro / .barra.cinza -->
      <div class="marco fim" style="--em:18"><span>entrega</span></div>
    </div>
  </div>
</div>
```

## Etiquetas

```html
<span class="tag">Fase 1</span> <span class="tag fase2">Fase 2</span>
<span class="tag laranja">só equipamentos</span> <span class="tag vermelho">obrigatório</span>
```
