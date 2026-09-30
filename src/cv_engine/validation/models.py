"""Pydantic models for the experience database. Rules: docs/spec-banco.md."""

from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

# Lowercase id like "acme-payments": letters, digits and single hyphens. Spec 3.2.
Slug = Annotated[str, Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")]
# One line of text, no leading/trailing spaces, no line breaks. Spec 3.4.
Line = Annotated[str, Field(pattern=r"^\S(.*\S)?$")]


class LocalizedText(BaseModel):
    """Text in the CV languages ('pt' and/or 'en'); at least one is required. Spec 3.4."""

    model_config = ConfigDict(extra="forbid")

    pt: Line | None = None
    en: Line | None = None

    @model_validator(mode="after")
    def at_least_one_language(self) -> Self:
        if self.pt is None and self.en is None:
            raise ValueError("at least one language is required: 'pt' or 'en'")
        return self


class Bullet(BaseModel):
    """Shared type of little pieces of experience in the CV. Spec 4.1."""

    model_config = ConfigDict(extra="forbid")

    id: Slug
    text: LocalizedText
