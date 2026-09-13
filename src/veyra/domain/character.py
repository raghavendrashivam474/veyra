"""Veyra domain Character entity.

A Character represents the persistent fictional identity being
developed by Veyra. At S0.3 this is deliberately minimal.

DO NOT implement the full Character Genome here.
The Genome is a research result for S2, not an S0 assumption.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from veyra.domain.ids import CharacterId


@dataclass(slots=True)
class Character:
    """A persistent fictional visual identity.

    Attributes:
        id: Unique domain identifier.
        name: Human-readable label for this character.
        description: Optional free-text description.
        created_at: When this character was first created in Veyra.

    This is intentionally mutable (not frozen) because a character's
    name and description may evolve during research. The id is stable.
    """

    id: CharacterId
    name: str
    description: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Character name must be non-empty.")
