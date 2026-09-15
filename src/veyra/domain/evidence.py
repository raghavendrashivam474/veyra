"""Veyra domain Evidence & Confidence Aggregation models.

S2.2 builds on S2.1 reconciliation to answer:
    "Why does Veyra believe a particular trait value?"

Key distinction from S2.1:
    - ReconciledTrait tells us WHAT was selected.
    - TraitAssessment tells us WHY, with structured evidence.

Critical semantic rule:
    Confidence is NOT evidence.
    "No evidence" is NOT the same as "low confidence".
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from veyra.domain.ids import ObservationId, ReferenceId
from veyra.domain.reconciliation import ReconciledTrait
from veyra.domain.traits import Confidence, TraitName, TraitValue


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    """Structured provenance for a single observation's contribution.

    Captures the essential metadata needed to explain WHY a trait
    value was selected, without requiring access to the full
    Observation object.

    Attributes:
        observation_id: Which observation this evidence came from.
        reference_id: Which reference material produced it.
        source: Identifier for the perception model/method.
        confidence: The observation's confidence score.
        evidence_payload: Model-specific structured evidence
            (e.g. bounding boxes, attention weights, detection scores).
    """

    observation_id: ObservationId
    reference_id: ReferenceId
    source: str
    confidence: Confidence
    evidence_payload: dict[str, Any]

    def __post_init__(self) -> None:
        if not self.source or not self.source.strip():
            raise ValueError("EvidenceRecord source must be non-empty.")


@dataclass(frozen=True, slots=True)
class TraitAssessment:
    """Explainable assessment of a single trait backed by structured evidence.

    This is the S2.2 evolution of ReconciledTrait. It preserves all
    provenance while adding explainability through:
        - Separated EvidenceRecord objects (not raw Observations)
        - A human-readable rationale string
        - Explicit source diversity tracking

    Attributes:
        trait: The assessed trait.
        selected_value: The chosen trait value.
        aggregate_confidence: Overall confidence in the assessment.
        supporting_evidence: Evidence records backing the selected value.
        conflicting_evidence: Evidence records offering alternatives.
        rationale: Human-readable explanation of why this value was chosen.
    """

    trait: TraitName
    selected_value: TraitValue
    aggregate_confidence: Confidence
    supporting_evidence: tuple[EvidenceRecord, ...]
    conflicting_evidence: tuple[EvidenceRecord, ...]
    rationale: str

    def __post_init__(self) -> None:
        if not self.rationale or not self.rationale.strip():
            raise ValueError("TraitAssessment rationale must be non-empty.")

    @property
    def has_conflict(self) -> bool:
        """True if conflicting evidence exists."""
        return len(self.conflicting_evidence) > 0

    @property
    def total_evidence_count(self) -> int:
        """Total number of evidence records considered."""
        return len(self.supporting_evidence) + len(self.conflicting_evidence)

    @property
    def source_diversity(self) -> int:
        """Number of distinct perception sources contributing evidence."""
        sources = {e.source for e in self.supporting_evidence}
        sources.update(e.source for e in self.conflicting_evidence)
        return len(sources)

    @property
    def has_evidence(self) -> bool:
        """True if any evidence exists at all.

        Important: absence of evidence is semantically different
        from low confidence. This property makes that distinction
        explicit.
        """
        return self.total_evidence_count > 0


class EvidenceAggregationStrategy(Protocol):
    """Protocol for evidence aggregation algorithms.

    Implementations transform a ReconciledTrait (S2.1 output) into
    a TraitAssessment (S2.2 output) by extracting and structuring
    the evidence that supports or contradicts the selected value.
    """

    def assess(self, reconciled: ReconciledTrait) -> TraitAssessment:
        """Produce an explainable TraitAssessment from a ReconciledTrait."""
        ...


class BaselineEvidenceAggregator:
    """Default S2.2 evidence aggregation strategy.

    Extracts EvidenceRecord objects from the observations within a
    ReconciledTrait and constructs a TraitAssessment with a structured
    rationale explaining the selection.

    This is intentionally conservative. It does NOT:
        - Weight sources by reliability (no source trust model yet)
        - Deduplicate observations from the same source+reference
        - Apply Bayesian updating or advanced statistical models

    Those are research questions for later S2 iterations.
    """

    def assess(self, reconciled: ReconciledTrait) -> TraitAssessment:
        """Build a TraitAssessment from a ReconciledTrait."""
        supporting = tuple(
            EvidenceRecord(
                observation_id=obs.id,
                reference_id=obs.reference_id,
                source=obs.source,
                confidence=obs.confidence,
                evidence_payload=dict(obs.evidence),
            )
            for obs in reconciled.supporting_observations
        )

        conflicting = tuple(
            EvidenceRecord(
                observation_id=obs.id,
                reference_id=obs.reference_id,
                source=obs.source,
                confidence=obs.confidence,
                evidence_payload=dict(obs.evidence),
            )
            for obs in reconciled.conflicting_observations
        )

        rationale = self._build_rationale(reconciled, supporting, conflicting)

        return TraitAssessment(
            trait=reconciled.trait,
            selected_value=reconciled.selected_value,
            aggregate_confidence=reconciled.confidence,
            supporting_evidence=supporting,
            conflicting_evidence=conflicting,
            rationale=rationale,
        )

    def _build_rationale(
        self,
        reconciled: ReconciledTrait,
        supporting: tuple[EvidenceRecord, ...],
        conflicting: tuple[EvidenceRecord, ...],
    ) -> str:
        """Generate a human-readable explanation of the assessment."""
        n_support = len(supporting)
        n_conflict = len(conflicting)
        sources = {e.source for e in supporting} | {e.source for e in conflicting}

        parts = [
            f"Trait '{reconciled.trait}' assessed as '{reconciled.selected_value}' "
            f"with confidence {reconciled.confidence.score:.2f}.",
            f"Supported by {n_support} observation(s)",
        ]

        if n_conflict > 0:
            conflict_values = {
                str(reconciled.conflicting_observations[i].value) for i in range(n_conflict)
            }
            parts.append(
                f"conflicted by {n_conflict} observation(s) "
                f"suggesting {', '.join(sorted(conflict_values))}"
            )
        else:
            parts.append("no conflicting observations")

        if len(sources) > 1:
            parts.append(f"across {len(sources)} distinct sources")

        return "; ".join(parts) + "."
