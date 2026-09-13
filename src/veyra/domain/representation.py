"""Veyra domain CharacterRepresentation model.

A CharacterRepresentation is the structured visual identity
information currently known about a character.

IMPORTANT: This is NOT the full Character Genome.
The Genome is a research deliverable for S2.

S0.3 establishes the container. S1 fills it with real observations.
S2 restructures it into the Genome based on research evidence.

Evolution path:
    S0.3  CharacterRepresentation (this)
      |
    S1    + real perception observations
      |
    S2    -> Character Genome (research-driven)
      |
    S3+   -> Generation / identity enforcement
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from veyra.domain.ids import CharacterId
from veyra.domain.observations import Observation


@dataclass(slots=True)
class CharacterRepresentation:
    """Structured visual identity knowledge about a character.

    Attributes:
        character_id: Which character this represents.
        observations: The set of observations forming this
                      representation.
        version: Monotonically increasing version string.
                 Starts at '0.1' for S0.3.
        metadata: Arbitrary domain-level metadata.
        updated_at: Last modification timestamp.
    """

    character_id: CharacterId
    observations: list[Observation] = field(default_factory=list)
    version: str = "0.1"
    metadata: dict[str, Any] = field(default_factory=dict)
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def add_observation(self, observation: Observation) -> None:
        """Add an observation to this representation."""
        self.observations.append(observation)
        self.updated_at = datetime.now(UTC)

    def observations_for_trait(self, trait: str) -> list[Observation]:
        """Return all observations matching a trait name string."""
        return [o for o in self.observations if o.trait.value == trait]

    @property
    def trait_names(self) -> set[str]:
        """Return the set of distinct trait names observed."""
        return {o.trait.value for o in self.observations}
