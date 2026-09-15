"""Unit tests for S2.2 Evidence & Confidence Aggregation domain models."""

from __future__ import annotations

import pytest

from veyra.domain.evidence import (
    BaselineEvidenceAggregator,
    EvidenceRecord,
    TraitAssessment,
)
from veyra.domain.ids import ObservationId, ReferenceId
from veyra.domain.observations import Observation
from veyra.domain.reconciliation import (
    ConfidenceWeightedStrategy,
)
from veyra.domain.traits import Confidence, TraitName, TraitValue


def _make_obs(
    trait: str = "hair.color",
    value: str = "dark_brown",
    confidence: float = 0.9,
    source: str = "qwen-vl",
    obs_id: str | None = None,
    ref_id: str | None = None,
    evidence: dict | None = None,
) -> Observation:
    return Observation(
        id=ObservationId(obs_id) if obs_id else ObservationId.generate(),
        reference_id=ReferenceId(ref_id) if ref_id else ReferenceId.generate(),
        trait=TraitName(trait),
        value=TraitValue(value),
        confidence=Confidence(confidence),
        source=source,
        evidence=evidence or {},
    )


def _make_evidence(
    obs_id: str = "obs-1",
    ref_id: str = "ref-1",
    source: str = "qwen-vl",
    confidence: float = 0.9,
    payload: dict | None = None,
) -> EvidenceRecord:
    return EvidenceRecord(
        observation_id=ObservationId(obs_id),
        reference_id=ReferenceId(ref_id),
        source=source,
        confidence=Confidence(confidence),
        evidence_payload=payload or {},
    )


class TestEvidenceRecord:
    """Tests for EvidenceRecord value object."""

    def test_valid_creation(self) -> None:
        ev = _make_evidence()
        assert ev.observation_id == ObservationId("obs-1")
        assert ev.reference_id == ReferenceId("ref-1")
        assert ev.source == "qwen-vl"
        assert ev.confidence == Confidence(0.9)
        assert ev.evidence_payload == {}

    def test_with_rich_payload(self) -> None:
        payload = {"bbox": [10, 20, 30, 40], "detection_score": 0.97}
        ev = _make_evidence(payload=payload)
        assert ev.evidence_payload == payload

    def test_rejects_empty_source(self) -> None:
        with pytest.raises(ValueError, match="source must be non-empty"):
            EvidenceRecord(
                observation_id=ObservationId("obs-1"),
                reference_id=ReferenceId("ref-1"),
                source="   ",
                confidence=Confidence(0.5),
                evidence_payload={},
            )

    def test_is_frozen(self) -> None:
        ev = _make_evidence()
        with pytest.raises(AttributeError):
            ev.source = "other-model"  # type: ignore[misc]


class TestTraitAssessment:
    """Tests for TraitAssessment entity."""

    def test_valid_creation_no_conflict(self) -> None:
        ev1 = _make_evidence(obs_id="obs-1", source="qwen-vl", confidence=0.9)
        ev2 = _make_evidence(obs_id="obs-2", source="qwen-vl", confidence=0.85)

        assessment = TraitAssessment(
            trait=TraitName("hair.color"),
            selected_value=TraitValue("dark_brown"),
            aggregate_confidence=Confidence(0.9),
            supporting_evidence=(ev1, ev2),
            conflicting_evidence=(),
            rationale="Full agreement across 2 observations.",
        )

        assert assessment.trait == TraitName("hair.color")
        assert assessment.selected_value == TraitValue("dark_brown")
        assert assessment.has_conflict is False
        assert assessment.total_evidence_count == 2
        assert assessment.source_diversity == 1
        assert assessment.has_evidence is True

    def test_with_conflicting_evidence(self) -> None:
        ev_support = _make_evidence(obs_id="obs-1", source="qwen-vl")
        ev_conflict = _make_evidence(obs_id="obs-2", source="insightface-v3", confidence=0.6)

        assessment = TraitAssessment(
            trait=TraitName("hair.color"),
            selected_value=TraitValue("dark_brown"),
            aggregate_confidence=Confidence(0.75),
            supporting_evidence=(ev_support,),
            conflicting_evidence=(ev_conflict,),
            rationale="Supported by qwen-vl, conflicted by insightface-v3.",
        )

        assert assessment.has_conflict is True
        assert assessment.total_evidence_count == 2
        assert assessment.source_diversity == 2

    def test_rejects_empty_rationale(self) -> None:
        ev = _make_evidence()
        with pytest.raises(ValueError, match="rationale must be non-empty"):
            TraitAssessment(
                trait=TraitName("hair.color"),
                selected_value=TraitValue("dark_brown"),
                aggregate_confidence=Confidence(0.9),
                supporting_evidence=(ev,),
                conflicting_evidence=(),
                rationale="   ",
            )

    def test_has_evidence_false_when_empty(self) -> None:
        # Edge case: an assessment with no evidence at all.
        # This is semantically different from low confidence.
        assessment = TraitAssessment(
            trait=TraitName("hair.color"),
            selected_value=TraitValue("unknown"),
            aggregate_confidence=Confidence(0.0),
            supporting_evidence=(),
            conflicting_evidence=(),
            rationale="No observations available for this trait.",
        )

        assert assessment.has_evidence is False
        assert assessment.total_evidence_count == 0
        assert assessment.source_diversity == 0

    def test_is_frozen(self) -> None:
        ev = _make_evidence()
        assessment = TraitAssessment(
            trait=TraitName("hair.color"),
            selected_value=TraitValue("dark_brown"),
            aggregate_confidence=Confidence(0.9),
            supporting_evidence=(ev,),
            conflicting_evidence=(),
            rationale="Test.",
        )
        with pytest.raises(AttributeError):
            assessment.rationale = "Changed."  # type: ignore[misc]


class TestBaselineEvidenceAggregator:
    """Tests for BaselineEvidenceAggregator end-to-end."""

    def setup_method(self) -> None:
        self.aggregator = BaselineEvidenceAggregator()
        self.reconciler = ConfidenceWeightedStrategy()

    def test_single_observation_assessment(self) -> None:
        obs = _make_obs(
            trait="facial.eye_shape",
            value="almond",
            confidence=0.75,
            source="qwen-vl",
            obs_id="obs-1",
            ref_id="ref-100",
            evidence={"bbox": [5, 10, 15, 20]},
        )
        reconciled = self.reconciler.reconcile(TraitName("facial.eye_shape"), [obs])
        assessment = self.aggregator.assess(reconciled)

        assert assessment.trait == TraitName("facial.eye_shape")
        assert assessment.selected_value == TraitValue("almond")
        assert assessment.aggregate_confidence == Confidence(0.75)
        assert len(assessment.supporting_evidence) == 1
        assert len(assessment.conflicting_evidence) == 0
        assert assessment.has_conflict is False

        # Verify evidence payload survived intact
        ev = assessment.supporting_evidence[0]
        assert ev.observation_id == ObservationId("obs-1")
        assert ev.reference_id == ReferenceId("ref-100")
        assert ev.source == "qwen-vl"
        assert ev.evidence_payload == {"bbox": [5, 10, 15, 20]}

    def test_agreeing_observations_full_confidence(self) -> None:
        obs1 = _make_obs(value="dark_brown", confidence=0.91, obs_id="obs-1")
        obs2 = _make_obs(value="dark_brown", confidence=0.87, obs_id="obs-2")
        obs3 = _make_obs(value="dark_brown", confidence=0.82, obs_id="obs-3")

        reconciled = self.reconciler.reconcile(TraitName("hair.color"), [obs1, obs2, obs3])
        assessment = self.aggregator.assess(reconciled)

        assert assessment.selected_value == TraitValue("dark_brown")
        assert assessment.aggregate_confidence == Confidence(0.91)
        assert len(assessment.supporting_evidence) == 3
        assert len(assessment.conflicting_evidence) == 0
        assert "no conflicting observations" in assessment.rationale

    def test_conflicting_observations_preserves_all_evidence(self) -> None:
        obs1 = _make_obs(value="dark_brown", confidence=0.90, source="qwen-vl", obs_id="obs-1")
        obs2 = _make_obs(value="black", confidence=0.74, source="insightface-v3", obs_id="obs-2")

        reconciled = self.reconciler.reconcile(TraitName("hair.color"), [obs1, obs2])
        assessment = self.aggregator.assess(reconciled)

        assert assessment.selected_value == TraitValue("dark_brown")
        assert len(assessment.supporting_evidence) == 1
        assert len(assessment.conflicting_evidence) == 1
        assert assessment.has_conflict is True
        assert assessment.source_diversity == 2

        # Verify conflicting evidence details
        conflict_ev = assessment.conflicting_evidence[0]
        assert conflict_ev.observation_id == ObservationId("obs-2")
        assert conflict_ev.source == "insightface-v3"
        assert conflict_ev.confidence == Confidence(0.74)

        # Rationale should mention the conflict
        assert "conflicted" in assessment.rationale.lower()
        assert "black" in assessment.rationale

    def test_multi_source_provenance(self) -> None:
        obs1 = _make_obs(
            trait="facial.eye_color",
            value="hazel",
            confidence=0.85,
            source="qwen-vl-72b",
            obs_id="obs-1",
        )
        obs2 = _make_obs(
            trait="facial.eye_color",
            value="hazel",
            confidence=0.80,
            source="llava-1.6",
            obs_id="obs-2",
        )
        obs3 = _make_obs(
            trait="facial.eye_color",
            value="green",
            confidence=0.60,
            source="human-annotation",
            obs_id="obs-3",
        )

        reconciled = self.reconciler.reconcile(TraitName("facial.eye_color"), [obs1, obs2, obs3])
        assessment = self.aggregator.assess(reconciled)

        assert assessment.source_diversity == 3
        assert "3 distinct sources" in assessment.rationale

    def test_rationale_mentions_confidence(self) -> None:
        obs = _make_obs(value="silver", confidence=0.95, obs_id="obs-1")
        reconciled = self.reconciler.reconcile(TraitName("hair.color"), [obs])
        assessment = self.aggregator.assess(reconciled)

        assert "0.95" in assessment.rationale
        assert "hair.color" in assessment.rationale
        assert "silver" in assessment.rationale

    def test_duplicate_observations_preserved(self) -> None:
        # Same source, same value, same confidence — should still appear
        obs1 = _make_obs(value="dark_brown", confidence=0.90, obs_id="obs-1")
        obs2 = _make_obs(value="dark_brown", confidence=0.90, obs_id="obs-2")

        reconciled = self.reconciler.reconcile(TraitName("hair.color"), [obs1, obs2])
        assessment = self.aggregator.assess(reconciled)

        # Both observations should appear as separate evidence records
        assert assessment.total_evidence_count == 2
        obs_ids = {e.observation_id for e in assessment.supporting_evidence}
        assert ObservationId("obs-1") in obs_ids
        assert ObservationId("obs-2") in obs_ids
