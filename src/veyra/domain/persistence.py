"""Veyra domain Persistence Classification models and strategies.

S2.3 answers the critical strategic question:
    "Which characteristics belong to persistent character identity,
     and which are allowed to change across scenes/references?"

Core classifications:
    - STABLE: Invariable identity markers (e.g. facial bone structure, eye shape).
    - TRANSIENT: Ephemeral, situation-dependent features (e.g. clothing, pose, lighting).
    - CONTEXT_DEPENDENT: Traits persistent in some contexts but modifiable (e.g. hairstyle).
    - UNKNOWN: Open fallback for traits without established persistence semantics.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from veyra.domain.evidence import TraitAssessment
from veyra.domain.traits import Confidence, TraitName, TraitValue


class PersistenceCategory(StrEnum):
    """Classification of identity persistence for a visual characteristic."""

    STABLE = "stable"
    TRANSIENT = "transient"
    CONTEXT_DEPENDENT = "context_dependent"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class ClassifiedTraitAssessment:
    """An explainable trait assessment paired with identity persistence semantics.

    Attributes:
        assessment: The underlying evidence-backed TraitAssessment.
        persistence: The persistence category assigned to this trait.
        classification_rationale: Explanation for why this category was assigned.
    """

    assessment: TraitAssessment
    persistence: PersistenceCategory
    classification_rationale: str

    def __post_init__(self) -> None:
        if not self.classification_rationale or not self.classification_rationale.strip():
            raise ValueError("ClassifiedTraitAssessment rationale must be non-empty.")

    @property
    def trait(self) -> TraitName:
        """The assessed trait."""
        return self.assessment.trait

    @property
    def selected_value(self) -> TraitValue:
        """The reconciled trait value."""
        return self.assessment.selected_value

    @property
    def aggregate_confidence(self) -> Confidence:
        """The assessment confidence score."""
        return self.assessment.aggregate_confidence

    @property
    def is_identity_defining(self) -> bool:
        """True if this characteristic is an immutable component of character identity."""
        return self.persistence == PersistenceCategory.STABLE

    @property
    def is_transient(self) -> bool:
        """True if this characteristic is expected to change across scenes or references."""
        return self.persistence == PersistenceCategory.TRANSIENT

    @property
    def is_ambiguous(self) -> bool:
        """True if the characteristic has uncertain or context-dependent persistence."""
        return self.persistence in (
            PersistenceCategory.CONTEXT_DEPENDENT,
            PersistenceCategory.UNKNOWN,
        )


class PersistenceClassifier(Protocol):
    """Protocol for classifying trait assessments into persistence categories."""

    def classify(self, assessment: TraitAssessment) -> ClassifiedTraitAssessment:
        """Classify a TraitAssessment into a ClassifiedTraitAssessment."""
        ...


class BaselinePersistenceClassifier:
    """Default S2.3 research baseline for persistence classification.

    Uses conservative heuristic rules based on trait namespace and name.
    Does NOT prematurely freeze an exhaustive ontology.
    Any unrecognized trait gracefully falls back to PersistenceCategory.UNKNOWN.
    """

    # Heuristic rules: namespace or full trait prefix mappings
    _STABLE_NAMESPACES = frozenset({"facial", "anatomical", "bone_structure"})
    _STABLE_TRAIT_NAMES = frozenset(
        {
            "hair.natural_color",
            "hair.hairline",
            "skin.tone",
            "skin.undertone",
            "body.height_relative",
            "body.proportions",
        }
    )

    _TRANSIENT_NAMESPACES = frozenset({"style", "pose", "lighting", "expression", "scene"})
    _TRANSIENT_TRAIT_NAMES = frozenset(
        {
            "hair.style_temporary",
            "makeup.style",
            "accessories.item",
            "clothing.top",
            "clothing.bottom",
            "clothing.outerwear",
        }
    )

    _CONTEXT_DEPENDENT_TRAIT_NAMES = frozenset(
        {
            "hair.length",
            "hair.color",
            "hair.texture",
            "facial_hair.style",
            "body.tattoos",
            "body.piercings",
        }
    )

    def classify(self, assessment: TraitAssessment) -> ClassifiedTraitAssessment:
        """Classify a TraitAssessment into a ClassifiedTraitAssessment."""
        trait_str = assessment.trait.value
        namespace = assessment.trait.namespace

        if trait_str in self._STABLE_TRAIT_NAMES or namespace in self._STABLE_NAMESPACES:
            category = PersistenceCategory.STABLE
            rationale = (
                f"Trait '{trait_str}' classified as STABLE based on physical "
                f"invariance heuristic for namespace '{namespace}'."
            )
        elif trait_str in self._TRANSIENT_TRAIT_NAMES or namespace in self._TRANSIENT_NAMESPACES:
            category = PersistenceCategory.TRANSIENT
            rationale = (
                f"Trait '{trait_str}' classified as TRANSIENT: characteristic "
                f"is expected to vary across references and scenes."
            )
        elif trait_str in self._CONTEXT_DEPENDENT_TRAIT_NAMES:
            category = PersistenceCategory.CONTEXT_DEPENDENT
            rationale = (
                f"Trait '{trait_str}' classified as CONTEXT_DEPENDENT: feature "
                f"remains stable across short arcs but can change across narrative contexts."
            )
        else:
            category = PersistenceCategory.UNKNOWN
            rationale = (
                f"Trait '{trait_str}' has UNKNOWN persistence: no established "
                f"invariance rule exists in baseline taxonomy."
            )

        return ClassifiedTraitAssessment(
            assessment=assessment,
            persistence=category,
            classification_rationale=rationale,
        )
