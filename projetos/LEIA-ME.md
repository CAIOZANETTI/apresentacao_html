# projetos/

Pasta de trabalho das apresentações reais. **O conteúdo é ignorado pelo git**: o repositório é público,
e aqui ficam dados de cliente, logos, fotos e editais.

```bash
python -m apresenta novo projetos/2027_minha_obra
```

Estrutura de cada projeto:

```
projetos/2027_minha_obra/
  apresentacao.yaml     slides
  dados.yaml            números + conferências
  img/                  figuras
  logos/                logos reais (declarados em apresentacao.yaml -> logos)
  fontes/               editais, pranchas, relatórios (rastreabilidade)
  PENDENCIAS.md         dados a confirmar
  dist/                 HTML final, capturas e PDF (gerados)
```

Para guardar histórico de um projeto, crie um repositório **privado** só para ele (ou para `projetos/`).
