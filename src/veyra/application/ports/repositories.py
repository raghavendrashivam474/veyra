"""Repository ports for Veyra application.

These are abstract interfaces defining the persistence needs of the application layer.
They operate purely on domain objects and domain IDs. No SQL, no ORM, no DB-specific concepts.
"""

from abc import ABC, abstractmethod

from veyra.domain.character import Character
from veyra.domain.ids import CharacterId, ObservationId, ReferenceId
from veyra.domain.observations import Observation
from veyra.domain.reference import Reference


class CharacterRepository(ABC):
    """Port for persistent storage of Character entities."""

    @abstractmethod
    def save(self, character: Character) -> None:
        """Persist a character entity."""
        pass

    @abstractmethod
    def get(self, character_id: CharacterId) -> Character | None:
        """Retrieve a character by ID, or None if not found."""
        pass


class ReferenceRepository(ABC):
    """Port for persistent storage of Reference entities."""

    @abstractmethod
    def save(self, reference: Reference) -> None:
        """Persist a reference entity."""
        pass

    @abstractmethod
    def get(self, reference_id: ReferenceId) -> Reference | None:
        """Retrieve a reference by ID, or None if not found."""
        pass


class ObservationRepository(ABC):
    """Port for persistent storage of Observation entities."""

    @abstractmethod
    def save(self, observation: Observation) -> None:
        """Persist an observation model."""
        pass

    @abstractmethod
    def get(self, observation_id: ObservationId) -> Observation | None:
        """Retrieve an observation by ID, or None if not found."""
        pass

    @abstractmethod
    def get_by_reference(self, reference_id: ReferenceId) -> list[Observation]:
        """Retrieve all observations associated with a given Reference ID."""
        pass
