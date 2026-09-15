"""Unit tests for S2.3 Persistence Classification domain models and classifier."""

from __future__ import annotations

import pytest

from veyra.domain.evidence import (
    BaselineEvidenceAggregator,
    EvidenceRecord,
    TraitAssessment,
)
from veyra.domain.ids import ObservationId, ReferenceId
from veyra.domain.observations import Observation
from veyra.domain.persistence import (
    BaselinePersistenceClassifier,
    ClassifiedTraitAssessment,
    PersistenceCategory,
)
from veyra.domain.reconciliation import ConfidenceWeightedStrategy
from veyra.domain.traits import Confidence, TraitName, TraitValue


def _make_assessment(
    trait: str = "facial.eye_shape",
    value: str = "almond",
    confidence: float = 0.9,
    source: str = "qwen-vl",
) -> TraitAssessment:
    ev = EvidenceRecord(
        observation_id=ObservationId.generate(),
        reference_id=ReferenceId.generate(),
        source=source,
        confidence=Confidence(confidence),
        evidence_payload={"test": True},
    )
    return TraitAssessment(
        trait=TraitName(trait),
        selected_value=TraitValue(value),
        aggregate_confidence=Confidence(confidence),
        supporting_evidence=(ev,),
        conflicting_evidence=(),
        rationale=f"Assessment for {trait}",
    )


class TestPersistenceCategoryEnum:
    """Tests for PersistenceCategory enum."""

    def test_enum_values(self) -> None:
        assert PersistenceCategory.STABLE.value == "stable"
        assert PersistenceCategory.TRANSIENT.value == "transient"
        assert PersistenceCategory.CONTEXT_DEPENDENT.value == "context_dependent"
        assert PersistenceCategory.UNKNOWN.value == "unknown"


class TestClassifiedTraitAssessment:
    """Tests for ClassifiedTraitAssessment value object/entity."""

    def test_valid_creation(self) -> None:
        assessment = _make_assessment()
        classified = ClassifiedTraitAssessment(
            assessment=assessment,
            persistence=PersistenceCategory.STABLE,
            classification_rationale="Facial geometry is an invariable physical trait.",
        )

        assert classified.trait == TraitName("facial.eye_shape")
        assert classified.selected_value == TraitValue("almond")
        assert classified.aggregate_confidence == Confidence(0.9)
        assert classified.is_identity_defining is True
        assert classified.is_transient is False
        assert classified.is_ambiguous is False
        assert classified.assessment == assessment

    def test_transient_classification_properties(self) -> None:
        assessment = _make_assessment(trait="style.outerwear", value="red_jacket")
        classified = ClassifiedTraitAssessment(
            assessment=assessment,
            persistence=PersistenceCategory.TRANSIENT,
            classification_rationale="Clothing is expected to vary between scenes.",
        )

        assert classified.is_identity_defining is False
        assert classified.is_transient is True
        assert classified.is_ambiguous is False

    def test_context_dependent_classification_properties(self) -> None:
        assessment = _make_assessment(trait="hair.length", value="shoulder_length")
        classified = ClassifiedTraitAssessment(
            assessment=assessment,
            persistence=PersistenceCategory.CONTEXT_DEPENDENT,
            classification_rationale="Hairstyle can change across narrative arcs.",
        )

        assert classified.is_identity_defining is False
        assert classified.is_transient is False
        assert classified.is_ambiguous is True

    def test_unknown_classification_properties(self) -> None:
        assessment = _make_assessment(trait="custom.aura_color", value="cerulean")
        classified = ClassifiedTraitAssessment(
            assessment=assessment,
            persistence=PersistenceCategory.UNKNOWN,
            classification_rationale="No classification heuristic exists for this trait.",
        )

        assert classified.is_identity_defining is False
        assert classified.is_transient is False
        assert classified.is_ambiguous is True

    def test_rejects_empty_rationale(self) -> None:
        assessment = _make_assessment()
        with pytest.raises(ValueError, match="rationale must be non-empty"):
            ClassifiedTraitAssessment(
                assessment=assessment,
                persistence=PersistenceCategory.STABLE,
                classification_rationale="   ",
            )

    def test_is_frozen(self) -> None:
        assessment = _make_assessment()
        classified = ClassifiedTraitAssessment(
            assessment=assessment,
            persistence=PersistenceCategory.STABLE,
            classification_rationale="Stable trait.",
        )
        with pytest.raises(AttributeError):
            classified.persistence = PersistenceCategory.TRANSIENT  # type: ignore[misc]


class TestBaselinePersistenceClassifier:
    """Tests for BaselinePersistenceClassifier."""

    def setup_method(self) -> None:
        self.classifier = BaselinePersistenceClassifier()

    def test_classifies_facial_namespaces_as_stable(self) -> None:
        assessment = _make_assessment(trait="facial.eye_shape", value="almond")
        classified = self.classifier.classify(assessment)

        assert classified.persistence == PersistenceCategory.STABLE
        assert classified.is_identity_defining is True
        assert "STABLE" in classified.classification_rationale

    def test_classifies_bone_structure_as_stable(self) -> None:
        assessment = _make_assessment(trait="bone_structure.cheekbones", value="prominent")
        classified = self.classifier.classify(assessment)

        assert classified.persistence == PersistenceCategory.STABLE
        assert classified.is_identity_defining is True

    def test_classifies_skin_tone_as_stable(self) -> None:
        assessment = _make_assessment(trait="skin.tone", value="warm_olive")
        classified = self.classifier.classify(assessment)

        assert classified.persistence == PersistenceCategory.STABLE
        assert classified.is_identity_defining is True

    def test_classifies_style_and_pose_as_transient(self) -> None:
        style_assess = _make_assessment(trait="style.outerwear", value="leather_jacket")
        pose_assess = _make_assessment(trait="pose.sitting", value="true")
        expression_assess = _make_assessment(trait="expression.smile", value="subtle")

        c_style = self.classifier.classify(style_assess)
        c_pose = self.classifier.classify(pose_assess)
        c_expr = self.classifier.classify(expression_assess)

        assert c_style.persistence == PersistenceCategory.TRANSIENT
        assert c_pose.persistence == PersistenceCategory.TRANSIENT
        assert c_expr.persistence == PersistenceCategory.TRANSIENT
        assert c_style.is_transient is True

    def test_classifies_hair_color_and_length_as_context_dependent(self) -> None:
        color_assess = _make_assessment(trait="hair.color", value="dark_brown")
        length_assess = _make_assessment(trait="hair.length", value="short")

        c_color = self.classifier.classify(color_assess)
        c_length = self.classifier.classify(length_assess)

        assert c_color.persistence == PersistenceCategory.CONTEXT_DEPENDENT
        assert c_length.persistence == PersistenceCategory.CONTEXT_DEPENDENT
        assert c_color.is_ambiguous is True

    def test_classifies_unrecognized_traits_as_unknown(self) -> None:
        unknown_assess = _make_assessment(trait="novelty.vibe_metric", value="mysterious")
        classified = self.classifier.classify(unknown_assess)

        assert classified.persistence == PersistenceCategory.UNKNOWN
        assert classified.is_ambiguous is True
        assert "UNKNOWN" in classified.classification_rationale

    def test_classification_is_deterministic(self) -> None:
        assessment = _make_assessment(trait="facial.jawline", value="sharp")

        result1 = self.classifier.classify(assessment)
        result2 = self.classifier.classify(assessment)

        assert result1.persistence == result2.persistence
        assert result1.classification_rationale == result2.classification_rationale

    def test_full_pipeline_reconciliation_to_classification(self) -> None:
        # Full integration: Observation -> ReconciledTrait -> TraitAssessment -> Classified
        reconciler = ConfidenceWeightedStrategy()
        aggregator = BaselineEvidenceAggregator()

        obs1 = Observation(
            id=ObservationId.generate(),
            reference_id=ReferenceId.generate(),
            trait=TraitName("facial.eye_color"),
            value=TraitValue("amber"),
            confidence=Confidence(0.92),
            source="qwen-vl-72b",
            evidence={"detection_bbox": [10, 20, 30, 40]},
        )
        obs2 = Observation(
            id=ObservationId.generate(),
            reference_id=ReferenceId.generate(),
            trait=TraitName("facial.eye_color"),
            value=TraitValue("amber"),
            confidence=Confidence(0.88),
            source="insightface-v3",
            evidence={"confidence_score": 0.99},
        )

        reconciled = reconciler.reconcile(TraitName("facial.eye_color"), [obs1, obs2])
        assessment = aggregator.assess(reconciled)
        classified = self.classifier.classify(assessment)

        assert classified.trait == TraitName("facial.eye_color")
        assert classified.selected_value == TraitValue("amber")
        assert classified.persistence == PersistenceCategory.STABLE
        assert classified.is_identity_defining is True
        assert classified.assessment.total_evidence_count == 2
        assert classified.assessment.source_diversity == 2
