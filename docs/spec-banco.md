# Especificação do banco de experiências

Versão 1 (fase 1a). Este documento define o formato dos dados que alimentam o motor e as regras que
o validador (`cv_engine.validation`) precisa aplicar. Os exemplos usam uma pessoa fictícia.

O banco é a **fonte da verdade**: tudo o que aparece num currículo sai daqui. O validador existe
para que um erro de digitação, uma data trocada ou um bullet sem revisão falhe **antes** de chegar
ao PDF, com uma mensagem que diga onde está o problema.

## 0. Visão geral: o que o código faz

Leia esta seção primeiro. As seções seguintes são a referência dos detalhes; esta é o mapa.

### 0.1. O programa, de fora

No fim da fase 1a, um comando recebe a pasta do banco e responde "ok" ou lista os problemas:

```
$ uv run python -m cv_engine.validation examples/persona
ERROR    experience/acme-pagamentos.md  bullets[0].text.en  required in a reviewed bullet
```

### 0.2. As partes, e como se conectam

```
examples/persona/experience/acme-pagamentos.md        arquivo no disco
        │
        ▼
 loader.py     acha os arquivos, separa o bloco YAML entre os "---",
               roda yaml.safe_load  →  dicionário Python
        │
        ▼
 models        Experience.model_validate(dicionário)
 (3 arquivos)  →  objeto Experience, ou ValidationError com os problemas
               (field_types.py, pieces.py e documents.py; ver 0.4)
        │
        ▼
 rules.py      regras que precisam de VÁRIOS arquivos: ids repetidos,
               skill apontando para item que não existe
        │
        ▼
 __main__.py   junta todos os erros e avisos e imprime
```

Tudo fica em `src/cv_engine/validation/`. Os models **não sabem que arquivos existem**: recebem um
dicionário e dizem se ele é válido. Por isso os testes deles usam dicionários escritos à mão, sem
criar arquivos.

### 0.3. As classes

Um model do Pydantic descreve um formato de dicionário. Regra prática: **bloco com campos dentro vira
classe; valor simples com restrição vira tipo anotado** (`Annotated[str, Field(...)]`). Os models
grandes são feitos de peças pequenas, e o Pydantic valida de dentro para fora:

```yaml
type: experience          ┐
id: acme-pagamentos       │  o arquivo inteiro  →  Experience
role:                     │
  pt: Estagiária...       │  role               →  LocalizedText
location:                 │
  city: Recife            │  location           →  Location
start: 2024-08            │  start              →  YearMonth
bullets:                  │
  - id: acme-conciliacao  │  cada item          →  Bullet
    text: {pt: ...}       │  text do bullet     →  LocalizedText
    status: reviewed      ┘
```

Valores simples com restrição, em `field_types.py`:

| Nome | Tipo de construção | O que é | Spec |
|------|--------------------|---------|------|
| `Slug` | tipo anotado | texto `acme-pagamentos` (ids, tags, evidências) | 3.2 |
| `Line` | tipo anotado | texto de uma linha, sem espaço nas pontas | 3.4 |
| `YearMonth` | tipo anotado | data `2024-08` ou `2024` | 3.5 |
| `Link` | tipo anotado | URL como aparece impressa | 3.7 |

Blocos que aparecem dentro dos arquivos, em `pieces.py`:

| Classe | O que é | Spec |
|--------|---------|------|
| `LocalizedText` | o par `{pt, en}` | 3.4 |
| `Location` | `{city, region, country}` | 4.2 |
| `Bullet` | um bullet do currículo | 4.1 |

Um model por tipo de arquivo do banco, em `documents.py`:

| Classe | Arquivo do banco | Spec |
|--------|------------------|------|
| `Experience` | `experience/*.md` | 5.2 |
| `Project` | `projects/*.md` | 5.3 |
| `Education` | `education/*.md` | 5.4 |
| `Course` | `courses/*.md` | 5.5 |
| `Activity` | `activities/*.md` | 5.6 |
| `Profile` (+ contatos e idioma falado) | `profile.md` | 5.1 |
| `Skill` e `SkillsFile` | `skills.yaml` | 6 |

### 0.4. Organização em camadas

Os models ficam em três arquivos, um por **camada**. Cada camada só usa as de baixo:

```
documents.py     Experience, Project, Education, Course,        camada 3: um model por
                 Activity, Profile, Skill, SkillsFile           tipo de arquivo do banco
      │ importa
      ▼
pieces.py        LocalizedText, Location, Bullet                 camada 2: blocos que aparecem
      │ importa                                                  dentro dos arquivos
      ▼
field_types.py   Slug, Line, YearMonth, Link                     camada 1: valores simples;
                                                                 não importa nada do projeto
```

Regras:

1. **Importação só para baixo.** `pieces.py` importa de `field_types.py`; `documents.py` importa dos
   dois. Nunca o contrário: um import para cima cria importação circular, e o Python falha ao
   carregar o pacote.
2. **Classe nova vai para a camada do seu papel**, não para um arquivo próprio. Pergunta que decide:
   é um valor simples (camada 1), um bloco que aparece dentro de arquivos (camada 2) ou o arquivo
   inteiro (camada 3)?
3. **Testes espelham os arquivos:** `tests/test_field_types.py`, `tests/test_pieces.py` e
   `tests/test_documents.py`. Quem procura o teste de uma classe abre o arquivo de mesmo nome.
4. **Nome dos testes:**
   - `test_<model>` (ex.: `test_localized_text`, `test_bullet`) é o teste **completo válido**:
     preenche **todos** os campos, obrigatórios e opcionais, com valores válidos, e espera que passe.
     Um por model. Ele confere que o model aceita o caso cheio e que cada valor foi guardado.
   - `test_<model>_<caso>` é para todos os outros, com o caso no nome: `test_bullet_minimal`
     (só os obrigatórios), `test_bullet_reviewed_without_evidence_fails`,
     `test_localized_text_unknown_language_fails`. Quem lê o nome sabe o que quebrou sem abrir o teste.
   - **Constante com o nome do model** (`LOCALIZED_TEXT`, `BULLET`), no topo do arquivo de teste:
     o dicionário **completo e válido**, com todos os campos preenchidos. É o dado do
     `test_<model>`. Nunca contém valor inválido.
   - Teste de falha copia essa constante e muda **um** campo só:
     `Bullet.model_validate({**BULLET, "status": "done"})`. Assim o teste só pode falhar pelo campo
     trocado. O defeito fica dentro do teste, nunca numa constante.
5. O nome é `field_types.py`, não `types.py`, porque `types` já é um módulo da biblioteca padrão
   do Python.

Por que camadas, e não um arquivo por classe: seriam 15 arquivos pequenos, no estilo do Java. Em
Python, o comum é agrupar o que tem o mesmo papel. Três arquivos mostram a estrutura de relance,
na mesma ordem em que o Pydantic valida: de dentro (camada 1) para fora (camada 3).

### 0.5. Onde cada regra entra

A pergunta que decide: **quanto a regra precisa enxergar?**

| A regra olha... | Exemplo | Ferramenta |
|-----------------|---------|------------|
| um valor só | formato do slug | `Field(pattern=...)` no tipo anotado, ou `field_validator` |
| um valor que o YAML entrega em tipos diferentes | `2025` vem como `int` | `field_validator(..., mode="before")` |
| vários campos do mesmo bloco | `reviewed` exige `pt` e `en` | `model_validator(mode="after")` |
| campos que não deveriam existir | `stauts: draft` | `model_config = ConfigDict(extra="forbid")` em **cada** classe |
| vários arquivos | id repetido no banco | `rules.py` (seção 7), nunca no model |

Para recusar um dado, o código faz `raise ValueError("mensagem em inglês")`; o Pydantic transforma
em `ValidationError`. `assert` é só para testes.

## 1. Escopo

Dentro da fase 1a:

- formato de cada tipo de arquivo do banco (campos, tipos, obrigatórios, limites);
- regras dentro de um arquivo e entre arquivos;
- formato das mensagens de erro e de aviso.

Fora da fase 1a (ficam para as próximas fases):

- `tailored.yaml` e `gaps.md` (seleção por vaga): fase 1b/2;
- `render.json` (entrada do template): o formato já está em `templates/contract.schema.json`; quem o
  gera é o resolvedor, na fase 1b;
- rótulos fixos (`i18n/*.yaml`): fase 1b.

## 2. Layout do diretório de dados

O motor lê o diretório indicado por `CV_DATA_DIR` (padrão: `examples/persona/`).

```
<CV_DATA_DIR>/
  profile.md              # obrigatório, exatamente um
  skills.yaml             # obrigatório
  experience/<id>.md      # type: experience
  projects/<id>.md        # type: project
  education/<id>.md       # type: education
  courses/<id>.md         # type: course
  activities/<id>.md      # type: activity
  _qualquer-coisa.md      # ignorado pelo motor (notas, pendências)
```

- Arquivos e pastas cujo nome começa com `_` ou `.` são **ignorados**. Servem para anotações.
- Pastas de tipo ausentes equivalem a pastas vazias.
- Qualquer outro arquivo fora deste layout (por exemplo `experience/notas.txt` ou uma pasta
  `outros/`) gera **aviso**, não erro.

### 2.1. Arquivo Markdown com frontmatter

Todo `.md` do banco começa com um bloco YAML entre linhas `---`:

```markdown
---
type: experience
id: acme-pagamentos
...
---

# Texto livre

Notas, contexto, "como falar disso" e pendências. O motor não lê esta parte.
```

- O frontmatter precisa ser a primeira coisa do arquivo (linha 1 = `---`).
- O frontmatter precisa ser um **mapeamento** YAML (não lista, não texto solto).
- O corpo Markdown é livre e **nunca** é lido pelo motor. É compatível com o Obsidian
  (`[[links]]` funcionam).
- Arquivo `.md` sem frontmatter, ou com YAML inválido: **erro**, com a linha informada pelo YAML
  quando houver.
- Use `yaml.safe_load`. Nunca `yaml.load` sem `Loader` seguro.

## 3. Convenções gerais

### 3.1. Campos desconhecidos

**Campo que não está nesta spec é erro.** Um `stat: reviewed` no lugar de `status: reviewed` não
pode passar em silêncio. (Em Pydantic: `model_config = ConfigDict(extra="forbid")`.)

Anotações vão em comentário YAML (`# ...`), no campo `note` do bullet ou no corpo Markdown.

### 3.2. Slug

Ids, tags e fontes de evidência são **slugs**:

```
^[a-z0-9]+(-[a-z0-9]+)*$
```

Válidos: `acme-pagamentos`, `rest-api`, `ci-cd`, `entrevista-2026-03-01`.
Inválidos: `Acme` (maiúscula), `rest_api` (sublinhado), `-api` (hífen na ponta), `api--rest`
(hífen duplo), `café` (acento).

### 3.3. Ids

- Todo item (experiência, projeto, formação, curso, atividade) tem `id` em slug.
- O `id` é **igual ao nome do arquivo** sem `.md`: `experience/acme-pagamentos.md` →
  `id: acme-pagamentos`.
- Ids de item são únicos **no banco inteiro**, não só no tipo (o `skills.yaml` referencia qualquer
  item pelo id, sem dizer o tipo).
- Ids de bullet são únicos **no banco inteiro**. Recomendação (não regra): prefixar com o id do
  item ou uma abreviação dele (`acme-dashboard`).
- Um id de bullet não pode ser igual a um id de item.

### 3.4. Texto localizado (`LocalizedText`)

Campos de texto que aparecem no currículo são mapas idioma → texto:

```yaml
role:
  pt: Desenvolvedora Full Stack
  en: Full-Stack Developer
```

- Idiomas aceitos na versão 1: `pt` e `en`. Outra chave (`es`, `PT`, `pt-BR`): erro.
- Precisa ter **pelo menos um** idioma.
- Cada texto: string, sem espaço no início ou no fim, sem quebra de linha, não vazia.
- Faltar um idioma é permitido no banco (a IA pode gerar a tradução depois, como `draft`), mas
  bullets `reviewed` exigem os dois idiomas (ver 4.1).

Alguns campos aceitam **string simples ou `LocalizedText`** (nomes próprios que normalmente não se
traduzem). Nesses, a string vale para todos os idiomas. A spec indica quando é o caso.

### 3.5. Datas (`YearMonth`)

Precisão máxima: **mês**. Formatos aceitos:

| Escrito no YAML | O que o `safe_load` devolve | Aceito? |
|-----------------|-----------------------------|---------|
| `2025-03`       | `str` `"2025-03"`           | sim     |
| `"2025-03"`     | `str` `"2025-03"`           | sim     |
| `2025`          | `int` `2025`                | sim (só ano) |
| `"2025"`        | `str` `"2025"`              | sim (só ano) |
| `2025-03-10`    | `datetime.date`             | **não**: dia não faz parte do formato |
| `2025-13`       | `str`                       | **não**: mês inválido |
| `03/2025`       | `str`                       | **não** |

Atenção à tabela: o YAML converte `2025` em inteiro e `2025-03-10` em `date` sozinho. O validador
precisa tratar esses tipos de propósito, não só strings.

- Ano entre 1950 e 2100; mês entre 01 e 12, com dois dígitos.
- Só ano (`2025`) significa "precisão de ano": o currículo mostra só o ano.
- Para comparar datas (regra `end >= start`), uma data só com ano vale como o ano inteiro:
  `start: 2025-06` com `end: 2025` é válido.

### 3.6. Período (`start`/`end`)

- `start` obrigatório onde a spec indicar.
- `end: null` ou `end` ausente = em andamento ("Atual"/"Present" no currículo).
- `end` não pode ser anterior a `start` (erro).
- `end` no futuro só é permitido com `expected: true` (formação) ou em projeto/atividade com data
  planejada; em experiência, `end` no futuro gera **aviso**.
- `start` no futuro: aviso.

"Futuro" é comparado com o mês atual. Para os testes não dependerem do relógio, a função que valida
deve receber a data de referência como parâmetro (com o padrão = hoje).

### 3.7. Link

URLs são gravadas **como aparecem impressas**, sem esquema: `github.com/usuaria/projeto`.

- Aceito: `github.com/usuaria`, `exemplo.dev`, `https://cert.exemplo.org/abc` (com `https://`,
  para certificados cujo link exato importa).
- Erro: `http://...` (sem TLS), espaço no meio, string sem ponto no domínio (`localhost`),
  `javascript:...`.
- Regra sugerida: `^(https://)?[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}(/\S*)?$`.
- O resolvedor (fase 1b) é quem acrescenta `https://` no link clicável.
- No YAML, link com `?`, `#` ou `:` depois do domínio vai **entre aspas**
  (`["youtube.com/watch?v=abc"]`). Sem aspas, dentro de lista em linha (`[...]`), o parser falha.

### 3.8. Status

| Valor      | Significado |
|------------|-------------|
| `draft`    | Escrito, ainda não confirmado pela pessoa. Nunca entra num currículo. |
| `reviewed` | Confirmado. Pode entrar num currículo. |

`skills.yaml` tem um terceiro valor, `unverified` (ver 6).

### 3.9. Prioridade

Campo opcional `priority`: `low`, `medium` ou `high`. Ausente = `medium`. Serve ao `/cv-tailor`
para desempatar; o validador só confere o valor.

### 3.10. Tags

Lista de slugs, sem repetição dentro da mesma lista (repetição: erro). Vocabulário livre; o motor
não mantém lista fixa de tags.

## 4. Tipos compartilhados

### 4.1. Bullet

A unidade atômica do currículo. Vive dentro de `bullets:` em experiência, projeto e atividade.

| Campo      | Tipo                 | Obrigatório | Regra |
|------------|----------------------|-------------|-------|
| `id`       | slug                 | sim         | único no banco (3.3) |
| `text`     | `LocalizedText`      | sim         | cada idioma com **no máximo 200 caracteres** |
| `tags`     | lista de slug        | não (padrão `[]`) | 3.10 |
| `metric`   | string ou `null`     | não         | nota interna, não é renderizada (ver abaixo) |
| `evidence` | lista de slug        | não (padrão `[]`) | fontes que comprovam o bullet |
| `status`   | `draft` \| `reviewed`| sim         | |
| `priority` | `low` \| `medium` \| `high` | não  | 3.9 |
| `note`     | string               | não         | nota interna, não é renderizada |

Regras:

1. **Bullet `reviewed` exige `pt` e `en`.** Faltou um idioma: erro.
2. **Bullet `reviewed` exige `evidence` não vazia.** Sem fonte, não há como defender o bullet
   numa entrevista.
3. Limite de 200 caracteres contado com `len()` do texto Python (acentos contam 1).
4. `metric` é só um lembrete para a seleção ("14 rotas", "2º lugar"). O número que o recrutador vê
   precisa estar no próprio `text`. O validador não compara os dois.
5. Texto com `**`, `__` ou `` ` ``: **aviso** (Markdown não é interpretado no PDF).

Válido:

```yaml
- id: acme-dashboard
  text:
    pt: "Criei um painel em Angular que reduziu de 3 para 1 dia o fechamento mensal do time financeiro."
    en: "Built an Angular dashboard that cut the finance team's monthly close from 3 days to 1."
  tags: [frontend, angular, typescript]
  metric: "3 → 1 dia"
  evidence: [repo-interno, gestora-2025-11]
  status: reviewed
```

Inválidos (cada um é um caso de teste):

```yaml
# 1. reviewed sem inglês
- id: acme-a
  text: { pt: "Criei um painel." }
  evidence: [repo]
  status: reviewed

# 2. reviewed sem evidência
- id: acme-b
  text: { pt: "Criei um painel.", en: "Built a dashboard." }
  status: reviewed

# 3. texto com 201 caracteres (qualquer idioma)
# 4. idioma desconhecido
- id: acme-c
  text: { pt: "Criei um painel.", es: "Creé un panel." }
  status: draft

# 5. status fora do enum
- id: acme-d
  text: { pt: "Criei um painel." }
  status: done

# 6. campo desconhecido (erro de digitação)
- id: acme-e
  text: { pt: "Criei um painel." }
  stauts: draft

# 7. id fora do formato
- id: Acme_Dashboard
  text: { pt: "Criei um painel." }
  status: draft

# 8. texto vazio ou só com espaços
- id: acme-f
  text: { pt: "   " }
  status: draft
```

Válido (bullet `draft` pode ter um idioma só e nenhuma evidência):

```yaml
- id: acme-g
  text: { pt: "Automatizei o relatório semanal." }
  status: draft
```

### 4.2. Location

| Campo     | Tipo   | Obrigatório | Regra |
|-----------|--------|-------------|-------|
| `city`    | string | sim         | não vazia |
| `region`  | string | não         | sigla ou nome (`SP`, `Minas Gerais`) |
| `country` | string | sim         | ISO 3166-1 alfa-2, maiúsculo (`BR`, `PT`, `US`) |

O validador confere o formato (`^[A-Z]{2}$`), não se o código existe.

## 5. Tipos de arquivo

Todo item tem `type` e `id`. O `type` precisa bater com a pasta (`experience/` → `experience`);
divergência é erro.

### 5.1. `profile.md` (`type: profile`)

Não tem `id`. Existe exatamente um.

| Campo               | Tipo | Obrigatório | Regra |
|---------------------|------|-------------|-------|
| `type`              | `profile` | sim | |
| `name`              | string | sim | nome civil completo; vai nos metadados do PDF |
| `display_name`      | string | não | nome no topo do currículo; padrão = `name` |
| `headline`          | `LocalizedText` | sim | até 80 caracteres por idioma |
| `tracks`            | lista de slug | não | trilhas que esta pessoa usa (ver abaixo) |
| `headline_by_track` | mapa trilha → `LocalizedText` | não | substitui `headline` na trilha |
| `summary`           | mapa trilha → nível → `LocalizedText` | não | até 400 caracteres por idioma |
| `location`          | `Location` | não | |
| `contacts`          | objeto | sim | ver abaixo |
| `languages`         | lista | não | ver abaixo |
| `status`            | `draft` \| `reviewed` | sim | |

**Trilhas.** O motor não conhece nomes de trilha. Cada pessoa declara as suas em `tracks`
(ex.: `[backend, data]`). Toda chave de `headline_by_track` e de `summary` precisa estar em
`tracks` (senão, erro: provável erro de digitação). Trilha declarada sem resumo: aviso.

**Níveis** (chaves internas de `summary`): `internship`, `trainee`, `junior`, `mid`, `senior`.
Outro valor: erro. Não é preciso ter todos.

**`contacts`:**

| Campo      | Tipo | Obrigatório | Regra |
|------------|------|-------------|-------|
| `email`    | string | sim | `algo@dominio.tld`, sem espaço |
| `phone`    | string | não | só dígitos, espaço, `+`, `-`, `(`, `)`; ao menos 8 dígitos |
| `linkedin` | `Link` | não | |
| `github`   | `Link` | não | |
| `website`  | `Link` | não | |

**`languages`** (itens):

| Campo        | Tipo | Obrigatório |
|--------------|------|-------------|
| `name`       | `LocalizedText` | sim |
| `level`      | `LocalizedText` | sim |
| `credential` | `Link` | não |
| `issued`     | `YearMonth` | não |

Exemplo:

```yaml
---
type: profile
name: Beatriz Nogueira Lima
display_name: Beatriz Lima
headline:
  pt: Desenvolvedora de Software
  en: Software Developer
tracks: [backend, data]
headline_by_track:
  data: { pt: Desenvolvedora de Dados, en: Data Developer }
summary:
  backend:
    junior:
      pt: "Desenvolvedora backend com 2 anos de experiência em APIs Python e PostgreSQL."
      en: "Backend developer with 2 years of experience building Python APIs on PostgreSQL."
location: { city: Recife, region: PE, country: BR }
contacts:
  email: beatriz@example.com
  github: github.com/beatriz-lima-example
languages:
  - name: { pt: Inglês, en: English }
    level: { pt: Avançado (B2), en: Upper-intermediate (B2) }
status: reviewed
---
```

Inválidos: `summary` com chave `fullstak` fora de `tracks`; nível `pleno`; e-mail `beatriz@`;
`contacts` ausente.

### 5.2. `experience/<id>.md` (`type: experience`)

| Campo        | Tipo | Obrigatório | Regra |
|--------------|------|-------------|-------|
| `type`       | `experience` | sim | |
| `id`         | slug | sim | = nome do arquivo |
| `org`        | string | sim | nome da organização |
| `role`       | `LocalizedText` | sim | até 80 caracteres |
| `employment` | enum | sim | `full-time`, `part-time`, `internship`, `trainee`, `apprenticeship`, `freelance`, `scholarship`, `volunteer` |
| `location`   | `Location` | não | |
| `mode`       | enum | não | `onsite`, `hybrid`, `remote` |
| `start`      | `YearMonth` | sim | |
| `end`        | `YearMonth` \| `null` | não | 3.6 |
| `context`    | `LocalizedText` | não | uma linha sobre o time ou o produto; até 120 caracteres |
| `hours`      | número > 0 | não | carga horária total (extensão, voluntariado) |
| `priority`   | enum | não | 3.9 |
| `tags`       | lista de slug | não | |
| `status`     | `draft` \| `reviewed` | sim | |
| `bullets`    | lista de `Bullet` | não (padrão `[]`) | lista vazia: aviso |

Exemplo:

```yaml
---
type: experience
id: acme-pagamentos
org: Acme Pagamentos
role: { pt: Estagiária de Desenvolvimento, en: Software Development Intern }
employment: internship
location: { city: Recife, region: PE, country: BR }
mode: hybrid
start: 2024-08
end: 2025-07
tags: [backend, python]
status: reviewed
bullets:
  - id: acme-conciliacao
    text:
      pt: "Automatizei a conciliação diária de pagamentos em Python, eliminando 4 h de trabalho manual por semana."
      en: "Automated daily payment reconciliation in Python, removing 4 hours of manual work per week."
    evidence: [gestora-2025-07]
    status: reviewed
---
```

Inválidos: `end: 2024-02` com `start: 2024-08`; `employment: estagio`; `mode: presencial`;
`start` ausente; `id: acme` no arquivo `acme-pagamentos.md`.

### 5.3. `projects/<id>.md` (`type: project`)

| Campo              | Tipo | Obrigatório | Regra |
|--------------------|------|-------------|-------|
| `type`             | `project` | sim | |
| `id`               | slug | sim | |
| `name`             | string \| `LocalizedText` | sim | até 60 caracteres |
| `tagline`          | `LocalizedText` | não | o que é, em uma linha; até 120 caracteres |
| `context`          | `LocalizedText` | não | disciplina, equipe, cliente; até 120 caracteres |
| `role`             | `LocalizedText` | não | até 80 caracteres |
| `start`            | `YearMonth` | sim | |
| `end`              | `YearMonth` \| `null` | não | |
| `links`            | mapa tipo → `Link` | não | tipos: `repo`, `demo`, `download`, `post`, `docs`, `video`, `website` |
| `demo_online`      | bool | não | ver regras |
| `hands_on`         | bool | não | `true` = código escrito pela pessoa; `false` = arquitetura/orquestração, código gerado por IA ou por terceiros; ausente = não informado |
| `sole_contributor` | bool | não | único contribuidor técnico |
| `priority`         | enum | não | |
| `tags`             | lista de slug | não | |
| `status`           | `draft` \| `reviewed` | sim | |
| `bullets`          | lista de `Bullet` | não | lista vazia: aviso |

Regras:

1. `demo_online` sem `links.demo`: erro (não há demo para estar online).
2. `links.demo` sem `demo_online`: aviso (o `/cv-tailor` não sabe se pode usar o link).
3. Tipo de link fora da lista: erro.

### 5.4. `education/<id>.md` (`type: education`)

| Campo         | Tipo | Obrigatório | Regra |
|---------------|------|-------------|-------|
| `type`        | `education` | sim | |
| `id`          | slug | sim | |
| `institution` | string | sim | |
| `degree`      | `LocalizedText` | sim | |
| `start`       | `YearMonth` | sim | |
| `end`         | `YearMonth` \| `null` | não | |
| `expected`    | bool | não (padrão `false`) | `true` = `end` é previsão |
| `capstone`    | slug | não | id de um projeto (TCC) |
| `status`      | `draft` \| `reviewed` | sim | |

Regras:

1. `expected: true` exige `end` preenchido.
2. `expected: false` com `end` no futuro: erro (conclusão futura precisa ser marcada como prevista).
3. `capstone` precisa ser o id de um arquivo em `projects/` (regra entre arquivos, seção 7).

Formação não tem bullets na versão 1. **Não existe campo para CR/GPA** de propósito: o campo seria
rejeitado como desconhecido.

### 5.5. `courses/<id>.md` (`type: course`)

| Campo        | Tipo | Obrigatório | Regra |
|--------------|------|-------------|-------|
| `type`       | `course` | sim | |
| `id`         | slug | sim | |
| `title`      | string \| `LocalizedText` | sim | |
| `provider`   | string | sim | |
| `hours`      | número > 0 | não | |
| `completed`  | bool | **sim** | sem valor padrão, de propósito |
| `issued`     | `YearMonth` | não | data do certificado |
| `credential` | `Link` | não | |
| `priority`   | enum | não | |
| `tags`       | lista de slug | não | |
| `status`     | `draft` \| `reviewed` | sim | |

Regras:

1. `completed` é obrigatório para que um curso incompleto nunca apareça como concluído por omissão.
2. `completed: false` com `issued` ou `credential`: erro (certificado de curso não concluído).

### 5.6. `activities/<id>.md` (`type: activity`)

Hackathons, prêmios, monitoria, eventos.

| Campo              | Tipo | Obrigatório | Regra |
|--------------------|------|-------------|-------|
| `type`             | `activity` | sim | |
| `id`               | slug | sim | |
| `name`             | string \| `LocalizedText` | sim | |
| `start`            | `YearMonth` | sim | |
| `end`              | `YearMonth` \| `null` | não | `null` = evento pontual |
| `date_approximate` | bool | não (padrão `false`) | `true` = o currículo mostra só o ano |
| `priority`         | enum | não | |
| `tags`             | lista de slug | não | |
| `status`           | `draft` \| `reviewed` | sim | |
| `bullets`          | lista de `Bullet` | não | |

Diferente de experiência e projeto, em atividade `end` ausente significa **evento pontual**, não
"em andamento".

## 6. `skills.yaml`

YAML puro (sem frontmatter), com uma chave `skills` contendo uma lista.

| Campo            | Tipo | Obrigatório | Regra |
|------------------|------|-------------|-------|
| `name`           | string | sim | nome oficial, como aparece no currículo |
| `aliases`        | lista de string | não | termos de ATS que devem casar com esta skill |
| `category`       | enum | sim | `language`, `runtime`, `framework`, `library`, `database`, `cloud`, `platform`, `tool`, `protocol`, `process`, `domain`, `ai` |
| `evidence`       | lista de slug | não | **ids de itens** do banco |
| `evidence_links` | lista de `Link` | não | comprovação externa (post, vídeo) sem item no banco |
| `hands_on`       | bool | não (padrão `true`) | `false` = só arquitetura ou código gerado |
| `depth`          | enum | não | `basic`, `working`, `solid` (autoavaliação) |
| `status`         | `draft` \| `reviewed` \| `unverified` | sim | |

Regras:

1. `name` único, sem diferenciar maiúsculas (`Python` e `python` colidem): erro.
2. Alias igual ao `name` da própria skill: aviso (redundante).
3. Alias igual ao `name` de **outra** skill: aviso (ambíguo para o ATS).
4. Alias repetido entre skills diferentes é permitido (`SQL` pode apontar para vários bancos).
5. Todo id em `evidence` precisa existir no banco (seção 7).
6. `draft` ou `reviewed` exige `evidence` ou `evidence_links` não vazio. Skill sem lastro é
   `unverified`.
7. `unverified` nunca entra num currículo (regra da seleção; o validador só garante o enum).

Exemplo:

```yaml
skills:
  - name: PostgreSQL
    aliases: [Postgres, SQL]
    category: database
    evidence: [acme-pagamentos]
    depth: working
    status: reviewed
  - { name: Go, aliases: [Golang], category: language, evidence: [], status: unverified }
```

Inválidos: `evidence: [acme]` sem item `acme`; `category: banco`; `status: reviewed` com
`evidence: []` e sem `evidence_links`; `depth: expert`.

## 7. Regras entre arquivos

Só rodam depois que todos os arquivos passaram na validação individual (não faz sentido cruzar
dados de um arquivo que nem carregou).

1. Ids de item únicos no banco (3.3).
2. Ids de bullet únicos no banco, e diferentes de ids de item.
3. `education.capstone` aponta para um projeto existente.
4. `skills[].evidence` aponta para itens existentes.
5. Exatamente um `profile.md`.
6. Item `reviewed` com todos os bullets `draft`: aviso (nada dele pode entrar num currículo).

## 8. Erros e avisos

- **Erro:** o banco é inválido. O build para, o comando sai com código 1.
- **Aviso:** o banco é válido, mas algo merece atenção. O build segue. Uma opção `--strict` (fase
  1d, no CI) transforma avisos em erros.

O validador **junta todos os problemas** e mostra de uma vez; não para no primeiro. Cada mensagem
diz arquivo, caminho do campo e o motivo. **Mensagens em inglês**, como o código e os commits:

```
ERROR    experience/acme-pagamentos.md  bullets[0].text.en     required in a reviewed bullet
ERROR    experience/acme-pagamentos.md  end                    2024-02 is before start (2024-08)
ERROR    skills.yaml                    skills[3].evidence[0]  item 'acme' does not exist
WARNING  projects/loja.md               links.demo             demo link without demo_online
```

Caminhos de campo usam a notação `a.b[0].c`. O Pydantic já entrega o caminho em `error["loc"]`;
é trabalho do validador convertê-lo para esse formato e acrescentar o arquivo.

## 9. Ordem de implementação sugerida

Cada etapa com testes antes de passar para a próxima. Arquivo de cada etapa entre parênteses.

1. `Slug`, `Line` e `YearMonth` (`field_types.py`) e `LocalizedText` (`pieces.py`): tipos
   pequenos, muitos casos de borda.
2. `Bullet` com as regras de 4.1; os oito casos inválidos viram testes (`pieces.py`). O limite de
   200 caracteres fica no `Bullet`, não no `LocalizedText`, porque cada campo tem o seu limite.
3. `Link` (`field_types.py`), `Location` (`pieces.py`), `Experience` e `Project` (`documents.py`).
4. `Profile`, `Education`, `Course`, `Activity` e `Skill` (`documents.py`).
5. Carregamento: ler o diretório, separar frontmatter, escolher o modelo pelo `type`, conferir
   `id` = nome do arquivo e `type` = pasta (`loader.py`).
6. Regras entre arquivos, seção 7 (`rules.py`).
7. Relatório de erros e avisos, seção 8, e o comando de linha de comando (`__main__.py`).

Em todas as etapas: nomes descritivos, type hints, docstring explicando a regra da spec que o código
implementa, um caso por teste, e `uv run ruff check`, `uv run ruff format` e `uv run pytest` verdes
antes do commit. Rode os comandos de dentro de `cv-engine/`.

## 10. Mudanças nesta spec

Esta spec é versionada junto com o código. Mudou uma regra: atualize este arquivo, os testes e as
fixtures no mesmo commit.
