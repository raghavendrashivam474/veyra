"""Veyra domain layer."""

from veyra.domain.character import Character
from veyra.domain.evidence import (
    BaselineEvidenceAggregator,
    EvidenceAggregationStrategy,
    EvidenceRecord,
    TraitAssessment,
)
from veyra.domain.ids import CharacterId, ObservationId, ReferenceId
from veyra.domain.observations import Observation
from veyra.domain.persistence import (
    BaselinePersistenceClassifier,
    ClassifiedTraitAssessment,
    PersistenceCategory,
    PersistenceClassifier,
)
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
    "BaselineEvidenceAggregator",
    "BaselinePersistenceClassifier",
    "Character",
    "CharacterId",
    "CharacterRepresentation",
    "ClassifiedTraitAssessment",
    "Confidence",
    "ConfidenceWeightedStrategy",
    "EvidenceAggregationStrategy",
    "EvidenceRecord",
    "HighestConfidenceStrategy",
    "Observation",
    "ObservationId",
    "PersistenceCategory",
    "PersistenceClassifier",
    "ReconciledTrait",
    "Reference",
    "ReferenceId",
    "ReferenceSourceType",
    "TraitAssessment",
    "TraitName",
    "TraitReconciliationStrategy",
    "TraitValue",
]
