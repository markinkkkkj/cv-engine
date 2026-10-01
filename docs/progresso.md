# Progresso

O que já foi feito, o que vem a seguir e **para que serve** cada passo. Atualizado a cada commit
de código. Regras detalhadas: [spec-banco.md](spec-banco.md). Motivos das escolhas:
[decisoes.md](decisoes.md).

## Onde este projeto quer chegar

```
banco (MD+YAML) ──► tailored.yaml ──► render.json ──► Typst ──► PDF
     fase 1a          fase 2            fase 1b       fase 1c
```

Um currículo de uma página gerado a partir de um banco de experiências. Cada fase entrega uma
parte desse caminho.

| Fase | Entrega | Estado |
|------|---------|--------|
| 1a | Formato do banco e **validador** (este documento) | em andamento |
| 1b | Resolvedor: banco → `render.json`, com idioma e datas formatadas | não começou |
| 1c | Tema `classic` em Typst, fontes versionadas, modo compacto | não começou |
| 1d | Fixtures `minimal`, `maximal`, `nasty`; CI que renderiza; proteção contra vazamento | não começou |
| 2 | `/cv-tailor`: seleção de bullets por vaga | não começou |

## Fase 1a: o validador

**Para que serve:** garantir que um erro de digitação, uma data trocada ou um bullet sem revisão
seja apontado **antes** de virar PDF, com arquivo, campo e motivo.

**Pronto quando:** `uv run python -m cv_engine.validation examples/persona` roda sem erros, e cada
regra da spec tem um teste.

### Preparação

| Entrega | Para que serve | Commit |
|---------|----------------|--------|
| Spec do banco | Define o que é válido; é a referência de cada regra do código | `2799a20` |
| Esqueleto (uv, pytest, ruff, CI) | Todo commit passa por lint, formatação e testes | `55e204f` |
| Persona fictícia | Banco de exemplo completo; o validador pronto precisa aceitá-la | `f412b13` |
| Contrato do `render.json` | Formato da saída da fase 1b, fixado cedo para o template não depender do banco | `5f4f00a` |
| Visão geral na spec (seção 0) | Mapa do código antes das tabelas de campos | `588b4ae` |
| Camadas e convenções de teste (seção 0.4) | Onde fica cada classe e como nomear cada teste | `121d49a` … `6399469` |

### Camada 1: `field_types.py` (valores simples)

| Unidade | Para que serve | Código | Testes |
|---------|----------------|--------|--------|
| `Slug` | Um formato só para ids, tags e evidências; a regra fica escrita uma vez | feito (`52ce520`) | **a fazer** |
| `Line` | Texto de uma linha sem espaço nas pontas; evita lixo invisível no PDF | feito (`52ce520`) | **a fazer** |
| `YearMonth` | Datas `2024-08` ou `2024`; trata o que o YAML converte sozinho (`int`, `date`) | a fazer | a fazer |
| `Link` | URL como aparece impressa; recusa `http://` e texto que não é link | a fazer | a fazer |

### Camada 2: `pieces.py` (blocos dentro dos arquivos)

| Unidade | Para que serve | Código | Testes |
|---------|----------------|--------|--------|
| `LocalizedText` | O par `{pt, en}`; garante pelo menos um idioma e nenhum idioma desconhecido | feito (`52ce520`) | base feitos (`2266997`); faltam os por regra |
| `Bullet`: campos | A unidade do currículo: id, texto, status, tags, evidência | feito (`2266997`) | base feitos (`2266997`); faltam os por regra |
| `Bullet`: regras | `reviewed` exige dois idiomas e evidência; limite de 200 caracteres; tags sem repetição | **a fazer** | a fazer |
| `Location` | Cidade, região e país de experiências e do perfil | a fazer | a fazer |

### Camada 3: `documents.py` (um model por tipo de arquivo)

| Unidade | Arquivo do banco | Estado |
|---------|------------------|--------|
| `Experience` | `experience/*.md` | a fazer |
| `Project` | `projects/*.md` | a fazer |
| `Education` | `education/*.md` | a fazer |
| `Course` | `courses/*.md` | a fazer |
| `Activity` | `activities/*.md` | a fazer |
| `Profile` | `profile.md` | a fazer |
| `Skill`, `SkillsFile` | `skills.yaml` | a fazer |

### Depois dos models

| Entrega | Para que serve | Estado |
|---------|----------------|--------|
| `loader.py` | Lê a pasta, separa o YAML de cada arquivo e escolhe o model pelo `type` | a fazer |
| `rules.py` | Regras entre arquivos: ids únicos, referências que existem | a fazer |
| `__main__.py` | O comando: junta erros e avisos e imprime no formato da spec, seção 8 | a fazer |

## Próximos passos, em ordem

1. `tests/test_field_types.py`: testes base de `Slug` e `Line`, e os inválidos com `parametrize`.
2. Testes por regra de `LocalizedText` e `Bullet` em `tests/test_pieces.py`.
3. Regras do `Bullet` (spec 4.1 e 3.10): o teste primeiro, o código depois.
4. `YearMonth`, com os casos da tabela da spec 3.5.
5. `Link` e `Location`; depois `Experience` e `Project`.

## Histórico de código

| Data | Commit | O que entrou |
|------|--------|--------------|
| 2026-09-30 | `52ce520` | `Slug`, `Line`, `LocalizedText` com testes; esqueleto do `Bullet` |
| 2026-10-01 | `2266997` | Divisão em camadas (`field_types.py`, `pieces.py`); campos do `Bullet`; testes base |
