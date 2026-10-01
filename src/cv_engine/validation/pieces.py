"""Layer 2: blocks that appear inside database files. Spec 0.4."""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, model_validator

from cv_engine.validation.field_types import Line, Slug


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
    status: Literal["draft", "reviewed"]
    tags: list[Slug] = []
    evidence: list[Slug] = []
    metric: Line | None = None
    priority: Literal["low", "medium", "high"] = "medium"
    note: Line | None = None
