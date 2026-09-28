"""Testes do contrato do render.json (templates/contract.schema.json)."""

import copy
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "templates" / "contract.schema.json").read_text(encoding="utf-8"))
FIXTURES = ROOT / "tests" / "fixtures" / "contract"
VALIDATOR = Draft202012Validator(SCHEMA)

Doc = dict[str, Any]


def load(name: str) -> Doc:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def section(doc: Doc, kind: str) -> Doc:
    return next(s for s in doc["sections"] if s["kind"] == kind)


def first_job(doc: Doc) -> Doc:
    return section(doc, "experience")["items"][0]


def test_schema_is_valid_draft_2020_12() -> None:
    Draft202012Validator.check_schema(SCHEMA)


@pytest.mark.parametrize("name", sorted(p.name for p in FIXTURES.glob("*.json")))
def test_valid_fixtures(name: str) -> None:
    errors = [e.message for e in VALIDATOR.iter_errors(load(name))]
    assert errors == []


def _set(path: Callable[[Doc], Doc], key: str, value: Any) -> Callable[[Doc], None]:
    def mutate(doc: Doc) -> None:
        path(doc)[key] = value

    return mutate


def _del(path: Callable[[Doc], Doc], key: str) -> Callable[[Doc], None]:
    def mutate(doc: Doc) -> None:
        del path(doc)[key]

    return mutate


def _root(doc: Doc) -> Doc:
    return doc


def _header(doc: Doc) -> Doc:
    return doc["header"]


def _bullet(doc: Doc) -> Doc:
    return first_job(doc)["bullets"][0]


def _six_bullets(doc: Doc) -> None:
    job = first_job(doc)
    job["bullets"] = [{"id": f"b-{i}", "text": "Texto."} for i in range(6)]


def _empty_section(doc: Doc) -> None:
    section(doc, "projects")["items"] = []


def _unknown_kind(doc: Doc) -> None:
    section(doc, "skills")["kind"] = "hobbies"


INVALID: dict[str, Callable[[Doc], None]] = {
    "versão errada": _set(_root, "contract_version", 2),
    "idioma fora do enum": _set(_root, "lang", "es"),
    "campo desconhecido na raiz": _set(_root, "theme", "classic"),
    "campo obrigatório ausente": _del(_root, "summary"),
    "campo opcional omitido em vez de null": _del(first_job, "context"),
    "resumo com 401 caracteres": _set(_root, "summary", "a" * 401),
    "bullet com 201 caracteres": _set(_bullet, "text", "a" * 201),
    "bullet com quebra de linha": _set(_bullet, "text", "linha 1\nlinha 2"),
    "bullet com espaço no fim": _set(_bullet, "text", "Texto. "),
    "bullet vazio": _set(_bullet, "text", ""),
    "id de bullet fora do formato": _set(_bullet, "id", "Acme_Bullet"),
    "seis bullets num item": _six_bullets,
    "seção vazia": _empty_section,
    "kind de seção desconhecido": _unknown_kind,
    "sem contatos": _set(_header, "contacts", []),
    "contato com http": _set(
        lambda d: d["header"]["contacts"][2], "url", "http://linkedin.com/in/x"
    ),
    "headline null": _set(_header, "headline", None),
}


@pytest.mark.parametrize("mutate", INVALID.values(), ids=INVALID.keys())
def test_invalid_documents_are_rejected(mutate: Callable[[Doc], None]) -> None:
    doc = copy.deepcopy(load("persona-backend-pt.json"))
    mutate(doc)
    assert not VALIDATOR.is_valid(doc)
