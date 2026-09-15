"""Veyra domain layer."""

from veyra.domain.character import Character
from veyra.domain.ids import CharacterId, ObservationId, ReferenceId
from veyra.domain.observations import Observation
from veyra.domain.reconciliation import (
    ConfidenceWeightedStrategy,
    HighestConfidenceStrategy,
    ReconciledTrait,
    TraitReconciliationStrategy,
)
from veyra.domain.reference import Reference, ReferenceSourceType
from veyra.domain.representation import CharacterRepresentation
from veyra.domain.traits import Confidence, TraitName, TraitValue

__all__ = [
    "Character",
    "CharacterId",
    "CharacterRepresentation",
    "Confidence",
    "ConfidenceWeightedStrategy",
    "HighestConfidenceStrategy",
    "Observation",
    "ObservationId",
    "ReconciledTrait",
    "Reference",
    "ReferenceId",
    "ReferenceSourceType",
    "TraitName",
    "TraitReconciliationStrategy",
    "TraitValue",
]
