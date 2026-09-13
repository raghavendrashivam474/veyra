"""In-memory adapters (fakes) for application ports.

These are used for unit testing the application services and showcasing
workflows without requiring infrastructure (e.g., SQLite, actual VLMs).
"""

from veyra.application.ports.perception import PerceptionEngine
from veyra.application.ports.repositories import (
    CharacterRepository,
    ObservationRepository,
    ReferenceRepository,
)
from veyra.domain.character import Character
from veyra.domain.ids import CharacterId, ObservationId, ReferenceId
from veyra.domain.observations import Observation
from veyra.domain.reference import Reference
from veyra.domain.traits import Confidence, TraitName, TraitValue


class InMemoryCharacterRepository(CharacterRepository):
    """In-memory Character store."""

    def __init__(self) -> None:
        self._store: dict[CharacterId, Character] = {}

    def save(self, character: Character) -> None:
        self._store[character.id] = character

    def get(self, character_id: CharacterId) -> Character | None:
        return self._store.get(character_id)


class InMemoryReferenceRepository(ReferenceRepository):
    """In-memory Reference store."""

    def __init__(self) -> None:
        self._store: dict[ReferenceId, Reference] = {}

    def save(self, reference: Reference) -> None:
        self._store[reference.id] = reference

    def get(self, reference_id: ReferenceId) -> Reference | None:
        return self._store.get(reference_id)


class InMemoryObservationRepository(ObservationRepository):
    """In-memory Observation store."""

    def __init__(self) -> None:
        self._store: dict[ObservationId, Observation] = {}

    def save(self, observation: Observation) -> None:
        self._store[observation.id] = observation

    def get(self, observation_id: ObservationId) -> Observation | None:
        return self._store.get(observation_id)

    def get_by_reference(self, reference_id: ReferenceId) -> list[Observation]:
        return [obs for obs in self._store.values() if obs.reference_id == reference_id]


class FakePerceptionEngine(PerceptionEngine):
    """Fake perception engine simulating model observations.

    Can be pre-seeded with custom trait-to-value behaviors or dynamic fallbacks.
    """

    def __init__(
        self,
        default_confidence: float = 0.9,
        source: str = "fake-vlm-v1",
        preset_values: dict[str, str | float | int] | None = None,
    ) -> None:
        self.default_confidence = default_confidence
        self.source = source
        self.preset_values = preset_values or {}

    def observe(self, reference: Reference, traits: list[TraitName]) -> list[Observation]:
        observations = []
        for trait in traits:
            # Determine mock value
            raw_val = self.preset_values.get(trait.value, "observed-default")
            val = TraitValue(raw=raw_val)

            obs = Observation(
                id=ObservationId.generate(),
                reference_id=reference.id,
                trait=trait,
                value=val,
                confidence=Confidence(score=self.default_confidence),
                source=self.source,
            )
            observations.append(obs)
        return observations
