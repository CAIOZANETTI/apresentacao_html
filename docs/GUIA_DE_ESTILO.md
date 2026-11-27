# Guia de estilo — apresentações à diretoria

Regras tiradas das rodadas de revisão da apresentação da ETA/adutoras. Cada regra veio de um ajuste
pedido na revisão. Siga-as antes de mostrar a primeira versão.

## 1. Público e objetivo

- O público é a **diretoria**. Ela quer escopo, números, prazos, dinheiro e decisões. Não quer o
  detalhamento técnico do projeto.
- **10 slides é o alvo.** Mais que 12 indica que algo deve virar anexo ou outra apresentação.
- O último slide é **síntese + decisões pedidas**.
- Cada slide responde a uma pergunta. O subtítulo diz qual é.

## 2. Texto

- **Texto grande:** corpo de 24 px, tabelas de 21 px e nada abaixo de 15 px (só fontes e notas de rodapé).
  O slide tem 1600 x 900 px e é escalado para a tela.
- **Sem espaço vazio sobrando.** Se sobra espaço, aumente a figura ou o texto, ou junte com outro slide.
  Se falta espaço, divida o slide. Não reduza a fonte.
- Use frases curtas, até 3 a 5 tópicos por bloco e números com unidade (`540 dias`, `310 m³`, `Ø 40–50 cm`).
- Formato brasileiro: `31.000 kg`, `4,2 km`, `nov/2026`. Use `data-formato="milhar"` para números grandes.
- Dados ainda incertos levam a marcação explícita: “a definir”, “estimado”, “~”.

## 3. Figuras de projeto

- Toda figura de projeto (planta, corte, sondagem, imagem de satélite, gráfico) leva `figure.zoom`,
  o que gera o botão “+ ampliar”.
- **Não comprima.** Use PNG a 200 dpi (250–300 dpi para detalhes com texto pequeno). A versão de
  referência tinha cerca de 6 MB. Para reduzir o arquivo, **recorte** a região de interesse.
- **Recorte** a região que importa (`--recorte`). Não use a prancha inteira com carimbo e margens.
- Em cada módulo/estrutura, mostre **planta + corte longitudinal**, mais a sondagem quando houver fundação.
- Para imagens de satélite, realce o traçado (linha grossa e cor forte) e marque as interferências
  (ex.: “~1 km sob linha de transmissão”).
- A legenda (`figcaption`) diz o que é a figura. A fonte vai em `.fonte` no pé do slide.

## 4. Layout

- **Blocos do mesmo tamanho** lado a lado (`grade-2`, `grade-3`). Na revisão, três blocos de tamanhos
  diferentes foram reprovados.
- Use tabelas limpas: cabeçalho azul, linhas zebradas, números alinhados à direita e unidade na célula.
  Não use grade pesada.
- Use **KPIs** (`.kpis`) no topo para os 3 ou 4 números principais.
- Para duas unidades, duas linhas ou dois módulos, mostre **lado a lado com a mesma estrutura**
  (mesma tabela, mesmas linhas), para facilitar a comparação.

## 5. Cores com significado

| Cor | Uso |
|---|---|
| Azul (`--azul`) | Fase 1, em execução, o que está sendo contratado agora |
| Cinza (`--cinza`) | Fase 2, futuro, fora do escopo atual |
| Vermelho tracejado | Marco **obrigatório do contrato** |
| Laranja | Atenção, regra que vale só para parte do escopo |
| Verde | Concluído / ok |

Não use cor só para decorar.

## 6. Prazos e cronograma

- Deixe claro **de quem é o prazo**. O slide de prazos mostra os **limites obrigatórios do cliente**
  (subtítulo: “não é o planejamento detalhado”). O planejamento interno vai em outra apresentação.
- Não misture o cronograma de fornecedores com o do cliente.
- Para unidades com prazos diferentes (ex.: 540 e 360 dias), use uma barra para cada, com o marco de entrega.
- Para frentes em paralelo, use uma linha por frente na mesma escala de meses.

## 7. Dinheiro

- O fluxo de pagamento padrão vai em etapas numeradas (`.etapas`): adiantamento? medição? prazo? 1º recebimento?
- Destaque o **impacto no caixa** (ex.: “1º recebimento ~dia 70”).
- Para condições especiais (ex.: 70/20/10 para equipamentos), use a barra de percentuais (`.pct`)
  com as **condições de cada parcela** e uma etiqueta dizendo **a que itens se aplica**.

## 8. O que evitar (já foi retirado em revisão)

- Matriz de riscos genérica (“pontos de atenção”), a menos que seja pedida.
- Cronograma de fornecedores no deck da diretoria.
- Texto pequeno para caber mais conteúdo.
- Blocos vazios ou desproporcionais.

## 9. Antes de entregar

- [ ] `python scripts/verificar.py ...` sem problemas (console, texto cortado, zoom, PDF com N páginas)
- [ ] Capturas revisadas: nenhum slide com espaço vazio sobrando ou texto apertado
- [ ] Todos os números vêm do `dados.json` ou têm fonte citada
- [ ] Documentos de origem (editais, anexos, PDFs) guardados em `projetos/<nome>/fontes/` para rastreabilidade
- [ ] Pendências marcadas como “a definir” e listadas no `projetos/<nome>/PENDENCIAS.md`
