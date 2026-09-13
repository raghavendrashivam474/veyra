"""Unit tests for the experimental VLM perception engine."""

from __future__ import annotations

import pytest
from veyra.domain.ids import ReferenceId
from veyra.domain.reference import Reference, ReferenceSourceType
from veyra.domain.traits import TraitName
from veyra.infrastructure.models.vlm_perception import (
    RawPerceptionResult,
    VLMPerceptionEngine,
)


@pytest.fixture
def engine() -> VLMPerceptionEngine:
    return VLMPerceptionEngine(model_name="test-vlm-model")


@pytest.fixture
def reference() -> Reference:
    source_type = next(iter(ReferenceSourceType))
    return Reference(
        id=ReferenceId.generate(),
        asset_id="asset-test-001",
        source_type=source_type,
    )


def test_converts_raw_results_to_domain_observations(
    engine: VLMPerceptionEngine, reference: Reference
) -> None:
    raw = RawPerceptionResult(
        model_name="test-vlm-model",
        raw_traits=[
            {
                "trait": "appearance.hair_color",
                "value": "dark brown",
                "confidence": 0.94,
            }
        ],
    )
    observations = engine._convert_to_observations(reference, raw)

    assert len(observations) == 1
    obs = observations[0]
    assert str(obs.trait) == "appearance.hair_color"
    assert str(obs.value) == "dark brown"
    assert obs.confidence.score == pytest.approx(0.94)
    assert obs.source == "test-vlm-model"
    assert obs.reference_id == reference.id


def test_skips_malformed_traits(engine: VLMPerceptionEngine, reference: Reference) -> None:
    raw = RawPerceptionResult(
        model_name="test-vlm-model",
        raw_traits=[
            {"trait": "appearance.hair_color", "value": "black"},
            {"value": "missing-trait"},
            {"trait": "invalid-namespace-format", "value": "red"},
        ],
    )
    observations = engine._convert_to_observations(reference, raw)
    assert len(observations) == 1
    assert str(observations[0].trait) == "appearance.hair_color"


def test_observe_orchestrates_entire_mock_flow(
    engine: VLMPerceptionEngine, reference: Reference
) -> None:
    traits = [TraitName("appearance.hair_color")]
    observations = engine.observe(reference, traits)
    assert len(observations) == 1
    assert str(observations[0].trait) == "appearance.hair_color"
