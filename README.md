# cv-engine

Currículo adaptativo: um banco de experiências em Markdown + YAML, uma seleção por vaga e um PDF de
uma página renderizado em [Typst](https://typst.app).

```
banco (MD+YAML) ──► tailored.yaml ──► render.json ──► Typst ──► PDF
                    seleção por vaga   resolvido        template
```

Estado: fase 1a (formato do banco e validação).

- Formato do banco: [docs/spec-banco.md](docs/spec-banco.md).
- Banco de exemplo (pessoa fictícia): [examples/persona/](examples/persona/).
- Contrato do `render.json`, entrada de todos os temas: [templates/contract.schema.json](templates/contract.schema.json).
  Exemplo: [tests/fixtures/contract/persona-backend-pt.json](tests/fixtures/contract/persona-backend-pt.json).

## Desenvolvimento

Requer [uv](https://docs.astral.sh/uv/). Python 3.12+.

```sh
uv sync                  # cria .venv com dependências e ferramentas
uv run pytest            # testes
uv run ruff check        # lint
uv run ruff format       # formatação
```

`CV_DATA_DIR` aponta para o diretório de dados (padrão: `examples/persona/`).
