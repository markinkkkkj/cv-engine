# Decisões

Cada decisão do projeto com o **motivo**. Serve para responder "por que isto é assim?" sem
depender da memória. Decisão nova entra no fim; decisão revista ganha uma linha nova que cita a
antiga, em vez de ser apagada.

## Arquitetura

| # | Data | Decisão | Motivo |
|---|------|---------|--------|
| 1 | 2026-09-27 | Renderizar com Typst | Boa tipografia, lê JSON direto, recebe texto como string (sem escapar caracteres) e compila para WASM |
| 2 | 2026-09-27 | O template lê só o `render.json`, nunca o banco | Um tema novo não precisa conhecer o formato do banco; o contrato é a única fronteira |
| 3 | 2026-09-28 | Stack: Python 3.12+, Pydantic v2, PyYAML, pytest, ruff, uv | Pydantic valida por declaração de tipos; ruff e uv são rápidos e substituem várias ferramentas |
| 4 | 2026-09-28 | No `render.json`, todo campo está sempre presente; ausente é `null` | O template só testa `none`; nunca quebra por chave que não existe |
| 5 | 2026-09-28 | Densidade (normal ou compacta) fora do contrato | É opção do build, não conteúdo do currículo |

## Formato do banco

| # | Data | Decisão | Motivo |
|---|------|---------|--------|
| 6 | 2026-09-28 | Campo desconhecido é sempre erro, também em rascunho | `stauts: draft` não pode passar em silêncio e apagar o status |
| 7 | 2026-09-28 | Bullet `reviewed` exige `pt`, `en` e evidência | Só entra no currículo o que está traduzido e dá para defender numa entrevista |
| 8 | 2026-09-28 | Datas com precisão de mês (`2024-08`) ou de ano (`2024`) | Currículo não mostra dia; ano sozinho cobre o que não se lembra com exatidão |
| 9 | 2026-09-28 | Trilhas declaradas no perfil, sem nomes fixos no código | O motor serve a qualquer pessoa; chave fora da lista é erro de digitação |
| 10 | 2026-09-28 | Em curso, `completed` é obrigatório e sem valor padrão | Curso incompleto nunca aparece como concluído por omissão |
| 11 | 2026-09-28 | Ids de bullet únicos no banco inteiro, sem prefixo obrigatório | A seleção por vaga referencia o bullet só pelo id |
| 12 | 2026-09-28 | Limites: bullet 200 caracteres, resumo 400 | Cabem em uma página; estouro falha na validação, não no PDF |

## Código

| # | Data | Decisão | Motivo |
|---|------|---------|--------|
| 13 | 2026-09-27 | A lógica de validação é escrita à mão pelo autor; a IA especifica e revisa | O validador é evidência de Python escrito à mão; os commits mostram quem fez o quê |
| 14 | 2026-09-30 | Código, mensagens de erro e commits em inglês; dados do banco em `pt` e `en` | Repositório público e convenção da área; o conteúdo do currículo segue o idioma da vaga |
| 15 | 2026-09-30 | Legibilidade primeiro: nomes descritivos, type hints, docstring com a seção da spec | O código precisa ser entendido por quem está aprendendo, inclusive o autor daqui a meses |
| 16 | 2026-10-01 | Models em três camadas (`field_types`, `pieces`, `documents`), import só para baixo | Três arquivos mostram a estrutura de relance; um por classe seriam 15; import para cima cria ciclo |
| 17 | 2026-10-01 | Unicidade de id é regra entre arquivos (`rules.py`), não do tipo `Slug` | `Slug` também é usado em tags, que se repetem; um model só enxerga o próprio dicionário |
| 18 | 2026-10-01 | Limite de 200 caracteres fica no `Bullet`, não no `LocalizedText` | Cada campo tem o seu limite (200, 120, 80); um limite fixo no tipo quebraria os outros |

## Testes

| # | Data | Decisão | Motivo |
|---|------|---------|--------|
| 19 | 2026-10-01 | Testes espelham os arquivos de código (`test_pieces.py` ↔ `pieces.py`) | Quem procura o teste de uma classe abre o arquivo de mesmo nome |
| 20 | 2026-10-01 | Testes base em toda unidade: completo, `_minimal`, `_empty` e, em classes, `_extra_fields` | Um padrão fixo impede esquecer um dos casos básicos |
| 21 | 2026-10-01 | Nome do teste base diz a entrada, não o resultado | Se a regra mudar, o `assert` muda e o nome continua valendo |
| 22 | 2026-10-01 | Constante com o nome da unidade (`BULLET`) é o caso completo válido; sem prefixo `VALID_` | Um dado-base para todos os testes; o nome já é a convenção |
| 23 | 2026-10-01 | Teste de falha muda um campo só: `{**BULLET, "status": "done"}` | Com vários defeitos juntos, o teste passa mesmo que uma das regras quebre |
| 24 | 2026-10-01 | Regras da camada 1 testadas em `test_field_types.py`; acima, um teste de ligação por tipo | Evita repetir os mesmos casos em cada classe que usa o tipo |

## Em aberto

- Idioma da spec e do README (hoje em português).
- Campo para a média da graduação (CR/GPA): hoje não existe na spec; em aberto se vale incluir como opcional.
