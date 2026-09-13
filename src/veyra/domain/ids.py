"""Veyra domain identifiers.

Strongly-typed value objects for entity identity.
These carry no infrastructure meaning - no SQLite row IDs,
no ORM coupling, no storage assumptions.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CharacterId:
    """Unique identifier for a Veyra character."""

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("CharacterId value must be a non-empty string.")

    @classmethod
    def generate(cls) -> CharacterId:
        """Create a new random CharacterId."""
        return cls(value=str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ReferenceId:
    """Unique identifier for a source reference."""

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("ReferenceId value must be a non-empty string.")

    @classmethod
    def generate(cls) -> ReferenceId:
        return cls(value=str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ObservationId:
    """Unique identifier for a single observation."""

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("ObservationId value must be a non-empty string.")

    @classmethod
    def generate(cls) -> ObservationId:
        return cls(value=str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value
