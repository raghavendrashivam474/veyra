"""Unit tests for domain observation reconciliation models and strategies."""

from __future__ import annotations

import pytest

from veyra.domain.ids import ObservationId, ReferenceId
from veyra.domain.observations import Observation
from veyra.domain.reconciliation import (
    ConfidenceWeightedStrategy,
    HighestConfidenceStrategy,
    ReconciledTrait,
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


class TestReconciledTraitEntity:
    """Tests for ReconciledTrait value object/entity invariants."""

    def test_valid_reconciled_trait_creation(self) -> None:
        obs1 = _make_obs(value="dark_brown", confidence=0.9)
        obs2 = _make_obs(value="black", confidence=0.6)

        reconciled = ReconciledTrait(
            trait=TraitName("hair.color"),
            selected_value=TraitValue("dark_brown"),
            confidence=Confidence(0.85),
            supporting_observations=(obs1,),
            conflicting_observations=(obs2,),
        )

        assert reconciled.trait == TraitName("hair.color")
        assert reconciled.selected_value == TraitValue("dark_brown")
        assert reconciled.confidence == Confidence(0.85)
        assert reconciled.supporting_observations == (obs1,)
        assert reconciled.conflicting_observations == (obs2,)
        assert reconciled.total_observations == 2
        assert reconciled.has_conflict is True
        assert reconciled.agreement_ratio == 0.5

    def test_reconciled_trait_without_conflicts(self) -> None:
        obs1 = _make_obs(value="dark_brown", confidence=0.9)
        obs2 = _make_obs(value="dark_brown", confidence=0.8)

        reconciled = ReconciledTrait(
            trait=TraitName("hair.color"),
            selected_value=TraitValue("dark_brown"),
            confidence=Confidence(0.9),
            supporting_observations=(obs1, obs2),
            conflicting_observations=(),
        )

        assert reconciled.total_observations == 2
        assert reconciled.has_conflict is False
        assert reconciled.agreement_ratio == 1.0

    def test_rejects_empty_supporting_observations(self) -> None:
        with pytest.raises(ValueError, match="at least one supporting observation"):
            ReconciledTrait(
                trait=TraitName("hair.color"),
                selected_value=TraitValue("dark_brown"),
                confidence=Confidence(0.9),
                supporting_observations=(),
                conflicting_observations=(),
            )

    def test_rejects_supporting_observation_with_mismatched_trait(self) -> None:
        obs_wrong_trait = _make_obs(trait="facial.eye_shape", value="dark_brown")
        with pytest.raises(ValueError, match="does not match"):
            ReconciledTrait(
                trait=TraitName("hair.color"),
                selected_value=TraitValue("dark_brown"),
                confidence=Confidence(0.9),
                supporting_observations=(obs_wrong_trait,),
                conflicting_observations=(),
            )

    def test_rejects_supporting_observation_with_mismatched_value(self) -> None:
        obs_wrong_val = _make_obs(trait="hair.color", value="blonde")
        with pytest.raises(ValueError, match="does not match selected value"):
            ReconciledTrait(
                trait=TraitName("hair.color"),
                selected_value=TraitValue("dark_brown"),
                confidence=Confidence(0.9),
                supporting_observations=(obs_wrong_val,),
                conflicting_observations=(),
            )

    def test_rejects_conflicting_observation_with_mismatched_trait(self) -> None:
        obs_supp = _make_obs(trait="hair.color", value="dark_brown")
        obs_conf = _make_obs(trait="facial.eye_shape", value="black")
        with pytest.raises(ValueError, match="does not match"):
            ReconciledTrait(
                trait=TraitName("hair.color"),
                selected_value=TraitValue("dark_brown"),
                confidence=Confidence(0.9),
                supporting_observations=(obs_supp,),
                conflicting_observations=(obs_conf,),
            )

    def test_rejects_conflicting_observation_with_identical_value(self) -> None:
        obs_supp = _make_obs(trait="hair.color", value="dark_brown")
        obs_conf = _make_obs(trait="hair.color", value="dark_brown")
        with pytest.raises(ValueError, match="identical to selected value"):
            ReconciledTrait(
                trait=TraitName("hair.color"),
                selected_value=TraitValue("dark_brown"),
                confidence=Confidence(0.9),
                supporting_observations=(obs_supp,),
                conflicting_observations=(obs_conf,),
            )

    def test_reconciled_trait_is_frozen(self) -> None:
        obs = _make_obs()
        reconciled = ReconciledTrait(
            trait=TraitName("hair.color"),
            selected_value=TraitValue("dark_brown"),
            confidence=Confidence(0.9),
            supporting_observations=(obs,),
            conflicting_observations=(),
        )
        with pytest.raises(AttributeError):
            reconciled.confidence = Confidence(0.5)  # type: ignore[misc]


class TestHighestConfidenceStrategy:
    """Tests for HighestConfidenceStrategy reconciliation."""

    def setup_method(self) -> None:
        self.strategy = HighestConfidenceStrategy()

    def test_single_observation(self) -> None:
        obs = _make_obs(trait="hair.color", value="dark_brown", confidence=0.88)
        result = self.strategy.reconcile(TraitName("hair.color"), [obs])

        assert result.trait == TraitName("hair.color")
        assert result.selected_value == TraitValue("dark_brown")
        assert result.confidence == Confidence(0.88)
        assert result.supporting_observations == (obs,)
        assert result.conflicting_observations == ()

    def test_multiple_agreeing_observations(self) -> None:
        obs1 = _make_obs(value="dark_brown", confidence=0.91, obs_id="obs-1")
        obs2 = _make_obs(value="dark_brown", confidence=0.85, obs_id="obs-2")
        result = self.strategy.reconcile(TraitName("hair.color"), [obs2, obs1])

        assert result.selected_value == TraitValue("dark_brown")
        assert result.confidence == Confidence(0.91)
        assert len(result.supporting_observations) == 2
        assert result.conflicting_observations == ()

    def test_conflicting_observations_selects_highest(self) -> None:
        obs_winner = _make_obs(value="dark_brown", confidence=0.91, obs_id="obs-1")
        obs_loser = _make_obs(value="black", confidence=0.74, obs_id="obs-2")
        result = self.strategy.reconcile(TraitName("hair.color"), [obs_loser, obs_winner])

        assert result.selected_value == TraitValue("dark_brown")
        assert result.confidence == Confidence(0.91)
        assert result.supporting_observations == (obs_winner,)
        assert result.conflicting_observations == (obs_loser,)
        assert result.has_conflict is True

    def test_tie_breaking_is_deterministic(self) -> None:
        obs_a = _make_obs(value="black", confidence=0.80, obs_id="obs-1")
        obs_b = _make_obs(value="brown", confidence=0.80, obs_id="obs-2")

        # Alphabetical 'black' wins over 'brown'
        result1 = self.strategy.reconcile(TraitName("hair.color"), [obs_a, obs_b])
        result2 = self.strategy.reconcile(TraitName("hair.color"), [obs_b, obs_a])

        assert result1.selected_value == TraitValue("black")
        assert result2.selected_value == TraitValue("black")

    def test_rejects_empty_observations(self) -> None:
        with pytest.raises(ValueError, match="Cannot reconcile empty observations"):
            self.strategy.reconcile(TraitName("hair.color"), [])

    def test_rejects_mismatched_trait_observation(self) -> None:
        obs = _make_obs(trait="facial.eye_shape", value="almond")
        with pytest.raises(ValueError, match="does not match target trait"):
            self.strategy.reconcile(TraitName("hair.color"), [obs])


class TestConfidenceWeightedStrategy:
    """Tests for ConfidenceWeightedStrategy (S2.1 default baseline)."""

    def setup_method(self) -> None:
        self.strategy = ConfidenceWeightedStrategy()

    def test_single_observation(self) -> None:
        obs = _make_obs(trait="facial.eye_shape", value="almond", confidence=0.75)
        result = self.strategy.reconcile(TraitName("facial.eye_shape"), [obs])

        assert result.selected_value == TraitValue("almond")
        assert result.confidence == Confidence(0.75)
        assert result.supporting_observations == (obs,)
        assert result.conflicting_observations == ()

    def test_multiple_agreeing_observations_preserves_max_confidence(self) -> None:
        obs1 = _make_obs(value="dark_brown", confidence=0.91, obs_id="obs-1")
        obs2 = _make_obs(value="dark_brown", confidence=0.87, obs_id="obs-2")
        obs3 = _make_obs(value="dark_brown", confidence=0.82, obs_id="obs-3")

        result = self.strategy.reconcile(TraitName("hair.color"), [obs1, obs2, obs3])

        assert result.selected_value == TraitValue("dark_brown")
        assert result.confidence == Confidence(0.91)
        assert len(result.supporting_observations) == 3
        assert result.conflicting_observations == ()
        assert result.has_conflict is False

    def test_conflicting_observations_weighted_voting(self) -> None:
        # dark_brown: 0.60 + 0.60 = 1.20 support
        # black: 0.85 support
        # total = 2.05. winner_weight = 1.20, conflict_weight = 0.85
        # penalty = 0.5 * 0.85 = 0.425
        # calc_conf = (1.20 - 0.425) / 2.05 = 0.775 / 2.05 ~= 0.3780
        obs1 = _make_obs(value="dark_brown", confidence=0.60, obs_id="obs-1")
        obs2 = _make_obs(value="dark_brown", confidence=0.60, obs_id="obs-2")
        obs3 = _make_obs(value="black", confidence=0.85, obs_id="obs-3")

        result = self.strategy.reconcile(TraitName("hair.color"), [obs1, obs2, obs3])

        assert result.selected_value == TraitValue("dark_brown")
        assert result.confidence.score == pytest.approx(0.3780, abs=0.001)
        assert len(result.supporting_observations) == 2
        assert len(result.conflicting_observations) == 1
        assert result.has_conflict is True

    def test_provenance_retention_across_sources_and_evidence(self) -> None:
        obs1 = _make_obs(
            value="dark_brown",
            confidence=0.90,
            source="qwen-vl-72b",
            obs_id="obs-1",
            ref_id="ref-100",
            evidence={"bbox": [10, 20, 30, 40]},
        )
        obs2 = _make_obs(
            value="black",
            confidence=0.50,
            source="insightface-v3",
            obs_id="obs-2",
            ref_id="ref-200",
            evidence={"detection_score": 0.98},
        )

        result = self.strategy.reconcile(TraitName("hair.color"), [obs1, obs2])

        # Verify all metadata and source IDs survived intact
        assert result.supporting_observations[0].id.value == "obs-1"
        assert result.supporting_observations[0].reference_id.value == "ref-100"
        assert result.supporting_observations[0].source == "qwen-vl-72b"
        assert result.supporting_observations[0].evidence == {"bbox": [10, 20, 30, 40]}

        assert result.conflicting_observations[0].id.value == "obs-2"
        assert result.conflicting_observations[0].reference_id.value == "ref-200"
        assert result.conflicting_observations[0].source == "insightface-v3"
        assert result.conflicting_observations[0].evidence == {"detection_score": 0.98}

    def test_determinism_irrespective_of_input_order(self) -> None:
        obs1 = _make_obs(trait="facial.eye_color", value="hazel", confidence=0.70, obs_id="obs-1")
        obs2 = _make_obs(trait="facial.eye_color", value="green", confidence=0.70, obs_id="obs-2")
        obs3 = _make_obs(trait="facial.eye_color", value="brown", confidence=0.80, obs_id="obs-3")

        result_a = self.strategy.reconcile(TraitName("facial.eye_color"), [obs1, obs2, obs3])
        result_b = self.strategy.reconcile(TraitName("facial.eye_color"), [obs3, obs1, obs2])
        result_c = self.strategy.reconcile(TraitName("facial.eye_color"), [obs2, obs3, obs1])

        assert result_a.selected_value == result_b.selected_value == result_c.selected_value
        assert result_a.confidence == result_b.confidence == result_c.confidence
        assert (
            result_a.supporting_observations
            == result_b.supporting_observations
            == result_c.supporting_observations
        )
        assert (
            result_a.conflicting_observations
            == result_b.conflicting_observations
            == result_c.conflicting_observations
        )
