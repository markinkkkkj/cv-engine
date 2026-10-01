"""Layer 1: simple value types. Spec 0.4."""

from typing import Annotated

from pydantic import Field

# Lowercase id like "acme-payments": letters, digits and single hyphens. Spec 3.2.
Slug = Annotated[str, Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")]
# One line of text, no leading/trailing spaces, no line breaks. Spec 3.4.
Line = Annotated[str, Field(pattern=r"^\S(.*\S)?$")]
