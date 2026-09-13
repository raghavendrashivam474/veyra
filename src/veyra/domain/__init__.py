"""Veyra domain model.

Pure domain concepts for visual identity research.
No infrastructure, no persistence, no ML dependencies.
"""

from veyra.domain.character import Character
from veyra.domain.ids import CharacterId, ObservationId, ReferenceId
from veyra.domain.observations import Observation
from veyra.domain.reference import Reference, ReferenceSourceType
from veyra.domain.representation import CharacterRepresentation
from veyra.domain.traits import Confidence, TraitName, TraitValue

__all__ = [
    "Character",
    "CharacterId",
    "CharacterRepresentation",
    "Confidence",
    "Observation",
    "ObservationId",
    "Reference",
    "ReferenceId",
    "ReferenceSourceType",
    "TraitName",
    "TraitValue",
]
