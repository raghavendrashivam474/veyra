"""Representation application service.

Aggregates observations to construct or update CharacterRepresentation aggregates.
"""

from veyra.domain.ids import CharacterId
from veyra.domain.observations import Observation
from veyra.domain.representation import CharacterRepresentation


class RepresentationService:
    """Orchestrates CharacterRepresentation updates and aggregation."""

    def create_representation(
        self, character_id: CharacterId, observations: list[Observation]
    ) -> CharacterRepresentation:
        """Construct a CharacterRepresentation from a list of Observations."""
        representation = CharacterRepresentation(character_id=character_id)
        for observation in observations:
            representation.add_observation(observation)
        return representation
