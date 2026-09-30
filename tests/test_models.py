"""Tests for the small types and LocalizedText (spec 3.2 and 3.4)."""

import pytest
from pydantic import ValidationError

from cv_engine.validation.models import LocalizedText

PT_TEXT = "Oiee"
EN_TEXT = "Helloo"
ES_TEXT = "Holaa"


def test_localized_text_two_languages() -> None:
    text = LocalizedText.model_validate({"pt": PT_TEXT, "en": EN_TEXT})
    assert text.pt == PT_TEXT


def test_localized_text_language_pt() -> None:
    text = LocalizedText.model_validate({"pt": PT_TEXT})
    assert text.pt == PT_TEXT
    assert text.en is None


def test_localized_text_language_en() -> None:
    text = LocalizedText.model_validate({"en": EN_TEXT})
    assert text.en == EN_TEXT
    assert text.pt is None


def test_localized_text_no_language() -> None:
    with pytest.raises(ValidationError):
        LocalizedText.model_validate({})


def test_localized_text_more_than_two_languages() -> None:
    with pytest.raises(ValidationError):
        LocalizedText.model_validate({"pt": PT_TEXT, "en": EN_TEXT, "es": ES_TEXT})
