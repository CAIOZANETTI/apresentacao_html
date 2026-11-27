# Instruções para a IA — apresentações de engenharia com código

Este repositório gera apresentações executivas em HTML a partir de YAML. O usuário é engenheiro civil
e programa em Python (numpy, pandas, plotly). O objetivo é **saída determinística**: a IA escreve dados
estruturados, e o código desenha.

## Regra principal

**Escreva YAML, nunca HTML/CSS/JS.** A apresentação é `apresentacao.yaml` + `dados.yaml` + `img/`.
Só use componentes e campos de `docs/LINGUAGEM.md`. Se faltar um recurso, proponha a mudança no
gerador (`apresenta/`), com teste, em vez de contornar no conteúdo.

## Roteiro para uma apresentação nova

1. Leia `docs/GUIA_DE_ESTILO.md` (conteúdo) e `docs/LINGUAGEM.md` (sintaxe).
   `exemplos/completo/` tem um slide de cada tipo: parta dele.
2. `python -m apresenta novo projetos/<aaaa>_<nome>` (a pasta `projetos/` não vai para o git).
3. Documentos de origem em `projetos/<nome>/fontes/`. Extraia figuras com `python -m apresenta imagens`.
4. Preencha o **`dados.yaml` primeiro**, com todos os números e as `conferir:` que precisam fechar.
   Números que saem de cálculo devem ser gerados por script Python (pandas → yaml), não digitados.
5. Escreva os slides:
   - título = conclusão (≤ 80 caracteres), `secao` curta, `fonte` sempre preenchida
   - todo número por referência `{chave:formato}`; nunca digite um número que esteja no dados.yaml
   - estruturas comparáveis com o mesmo layout
6. `python -m apresenta verificar projetos/<nome>` precisa terminar com **OK**. Depois **olhe as
   capturas** em `dist/capturas/`: o verificador não vê espaço vazio nem desequilíbrio visual.
7. Entregue `dist/<ARQUIVO>.html`. Registre dados faltantes em `PENDENCIAS.md`.

## Nunca

- Inventar números, datas ou fontes. Sem dado, escreva "a definir" e registre em PENDENCIAS.md.
- Reduzir letra para caber. Divida o slide.
- Commitar conteúdo de `projetos/`, logos reais, fotos ou documentos de cliente: **o repositório é público**.
- Editar `apresenta/estatico/` para um projeto específico. Mudança no gerador vale para todos e precisa de teste.

## Mudanças no gerador

- Componentes em `apresenta/componentes.py`, gráficos em `apresenta/graficos.py` (funções puras,
  coordenadas com `f()`), validação estrita com `Campos`.
- Todo componente/gráfico novo deve: (1) entrar no `docs/LINGUAGEM.md`; (2) aparecer no
  `exemplos/completo`; (3) ter teste em `testes/`; (4) manter o teste de determinismo passando.
- `python -m pytest testes -q` e `python -m apresenta verificar exemplos/completo` antes de commitar.
- Pedido de ajuste do usuário que vire regra geral vai para `docs/GUIA_DE_ESTILO.md`.

## Ambiente

Se o Chromium do Playwright não estiver instalado, use um existente:
`CHROMIUM_PATH=/caminho/do/chrome python -m apresenta verificar ...`
