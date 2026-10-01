"""Tests for pieces.py: LocalizedText and Bullet."""

import pytest
from pydantic import ValidationError

from cv_engine.validation.pieces import Bullet, LocalizedText

LOCALIZED_TEXT = {
    "pt": "Oiee",
    "en": "Helloo",
}

BULLET = {
    "id": "id-example",
    "text": LOCALIZED_TEXT,
    "status": "reviewed",
    "tags": ["example1", "example2"],
    "evidence": ["example1", "example2"],
    "metric": "Correct text example.",
    "priority": "high",
    "note": "Correct text example.",
}


def test_localized_text() -> None:
    text = LocalizedText.model_validate(LOCALIZED_TEXT)
    assert text.pt == LOCALIZED_TEXT["pt"]
    assert text.en == LOCALIZED_TEXT["en"]


def test_localized_text_minimal() -> None:
    text = LocalizedText.model_validate({"pt": LOCALIZED_TEXT["pt"]})
    assert text.pt == LOCALIZED_TEXT["pt"]
    assert text.en is None
    text = LocalizedText.model_validate({"en": LOCALIZED_TEXT["en"]})
    assert text.en == LOCALIZED_TEXT["en"]
    assert text.pt is None


def test_localized_text_empty() -> None:
    with pytest.raises(ValidationError):
        LocalizedText.model_validate({})


def test_localized_text_extra_fields() -> None:
    with pytest.raises(ValidationError):
        LocalizedText.model_validate({**LOCALIZED_TEXT, "es": "Holaa"})


def test_bullet() -> None:
    bullet = Bullet.model_validate(BULLET)
    assert bullet.model_dump() == BULLET


def test_bullet_minimal() -> None:
    bullet = Bullet.model_validate(
        {"id": BULLET["id"], "text": BULLET["text"], "status": BULLET["status"]}
    )
    assert bullet.id == BULLET["id"]
    assert bullet.text.model_dump() == BULLET["text"]
    assert bullet.status == BULLET["status"]
    assert bullet.tags == []
    assert bullet.evidence == []
    assert bullet.metric is None
    assert bullet.priority == "medium"
    assert bullet.note is None


def test_bullet_empty() -> None:
    with pytest.raises(ValidationError):
        Bullet.model_validate({})


def test_bullet_extra_fields() -> None:
    with pytest.raises(ValidationError):
        Bullet.model_validate({**BULLET, "example": "example"})
