"""Veyra domain trait definitions.

A Trait represents a visual characteristic Veyra can reason about.
The taxonomy is intentionally open - S0.3 establishes the abstraction,
not the final ontology. Research in S1/S2 will determine the real set.

Trait names use a namespace.name convention:
    facial.eye_shape
    hair.texture
    silhouette.shoulder_width
    style.clothing
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_TRAIT_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$")


@dataclass(frozen=True, slots=True)
class TraitName:
    """A namespaced trait identifier.

    Format: 'namespace.name' (e.g. 'facial.eye_shape').
    This is a value object - equality is based on the string.
    """

    value: str

    def __post_init__(self) -> None:
        if not _TRAIT_NAME_PATTERN.match(self.value):
            raise ValueError(
                f"TraitName must match 'namespace.name' pattern "
                f"(lowercase, underscore). Got: '{self.value}'"
            )

    @property
    def namespace(self) -> str:
        return self.value.split(".", 1)[0]

    @property
    def name(self) -> str:
        return self.value.split(".", 1)[1]

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class TraitValue:
    """The observed value of a trait.

    Intentionally flexible: a trait value might be categorical ('almond'),
    numerical (0.73), or textual ('wavy with highlights').

    S0.3 keeps this simple. If S1 research demands a richer polymorphic
    value system, that evolution should be documented and justified.
    """

    raw: str | float | int

    def __post_init__(self) -> None:
        if isinstance(self.raw, str) and not self.raw.strip():
            raise ValueError("TraitValue string must be non-empty.")

    def __str__(self) -> str:
        return str(self.raw)


@dataclass(frozen=True, slots=True)
class Confidence:
    """Normalized confidence score for a perception observation.

    Domain rule: 0.0 <= score <= 1.0
    This is model-agnostic - it does not assume any particular
    VLM or perception engine's internal confidence mechanism.
    """

    score: float

    def __post_init__(self) -> None:
        if not (0.0 <= self.score <= 1.0):
            raise ValueError(f"Confidence score must be in [0.0, 1.0]. Got: {self.score}")

    def __str__(self) -> str:
        return f"{self.score:.2f}"
