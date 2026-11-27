# Guia de estilo — apresentações à diretoria

Regras de conteúdo, tiradas da apresentação de referência (ver `ANALISE_REFERENCIA.md`) e das
revisões. A forma (CSS, componentes) já está resolvida pelo gerador; este guia trata do **que** escrever.

## 1. Estrutura

- **10 slides é o alvo.** Mais de 12 indica que algo deve ir para anexo.
- A sequência que funcionou: capa → cliente e regras → a obra (visão geral + mapa) → uma sequência
  por unidade/estrutura → prazos e marcos → condições comerciais → síntese.
- **Estruturas comparáveis (módulos, unidades, trechos) usam o mesmo layout**, copiado e com os
  dados trocados, como os slides 5 e 6 do exemplo.
- O último slide é a **síntese**: frentes de obra lado a lado e os limites do contrato.

## 2. Título, chapéu e fonte

- O **título é a conclusão**, não o assunto:
  - ❌ "Módulo 360 L/s — fundações"
  - ✅ "Módulo 360 L/s: 39 estacas num solo que não passa de NSPT 15 até a rocha"
- Título com até ~80 caracteres (2 linhas). Acima de 95, a montagem avisa.
- `secao:` curta ("Unidade 01 — ETA"). O número do chapéu é automático.
- `fonte:` é **obrigatória**: documento, prancha, item do TR, relatório. A diretoria precisa saber de onde vem cada número.

## 3. Números

- **Todo número vem do `dados.yaml`**, citado como `{chave:formato}`. Não digite o mesmo número em dois slides.
- Use `conferir:` para as contas que precisam fechar: somas de extensões, vazões, taxas
  (aço ≈ 100 kg/m³), percentuais = 100%, dia do 1º pagamento.
- Use unidade sempre (`540 dias`, `202 m³`, `Ø 40 e 50 cm`) e o formato brasileiro (o gerador cuida disso).
- Valor aproximado leva `≈`; dado ainda não confirmado leva "a definir" e entra em `PENDENCIAS.md`.
- Não invente números. Sem dado, sem número.

## 4. Figuras

- Toda figura é ampliável (padrão). Use figuras de **alta resolução e recortadas**: o recorte
  reduz o arquivo sem perder nitidez.
  - Pranchas: `python -m apresenta imagens prancha.pdf -p 3 --recorte x0,y0,x1,y1 --dpi 200` (PNG)
  - Fotos/ortofotos/satélite: JPG de até ~1.600 px de largura (`--formato jpg`)
- Para estrutura com fundação, mostre **corte + locação + KPIs + sondagem com leitura**.
- Em mapas, traçados com cor forte, contorno branco e legenda. **Todo item listado deve aparecer no mapa**
  (na referência, uma adutora estava na lista e não no mapa).
- Use as cores das pranchas na legenda de etapas (azul 1ª etapa, verde existente, roxo 2ª etapa).
- `legenda` diz o que é a figura. A origem vai na `fonte` do slide.

## 5. Densidade e legibilidade

- O verificador recusa letra abaixo de 14 px numa tela de 1.600 px. Se não cabe, **divida o slide**:
  não reduza a fonte nem esconda informação.
- Tabelas com mais de 8 linhas: `compacta: true`, ou mova a tabela para um anexo.
- Um slide denso (como o de condições comerciais) é aceitável **uma vez**. Os demais devem respirar.
- Evite espaço vazio grande dentro de uma célula: reorganize as `linhas` e `colunas` da grade.

## 6. Prazos e dinheiro

- Deixe claro **de quem é o prazo**: o gráfico de marcos mostra os limites do cliente, com o aviso
  "não é o planejamento do consórcio, que será apresentado à parte".
- Não misture o cronograma de fornecedores com o do cliente.
- No fluxo de pagamento, mostre **quando entra o 1º dinheiro** (ciclo de pagamento) e o que fica retido (barras).
- Para condição de pagamento que vale só para parte do escopo (ex.: equipamentos especiais),
  diga a quais itens se aplica no `titulo` do componente.

## 7. O que evitar (já foi retirado em revisões)

- Matriz genérica de riscos ("pontos de atenção"), a menos que seja pedida.
- Cronograma de fornecedores no material da diretoria.
- Texto pequeno para caber mais conteúdo.
- Blocos de tamanhos diferentes lado a lado sem motivo.

## 8. Antes de entregar

- [ ] `python -m apresenta verificar projetos/<nome>` termina com **OK**
- [ ] Capturas em `dist/capturas/` revisadas uma a uma
- [ ] Nenhum aviso de dado não usado (ou justificado)
- [ ] Documentos de origem em `projetos/<nome>/fontes/`; pendências em `PENDENCIAS.md`
