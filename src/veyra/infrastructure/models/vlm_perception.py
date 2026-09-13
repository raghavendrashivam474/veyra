"""Concrete VLM-based perception engine implementation for S1 research."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from veyra.application.ports.perception import PerceptionEngine
from veyra.domain.ids import ObservationId
from veyra.domain.observations import Observation
from veyra.domain.reference import Reference
from veyra.domain.traits import Confidence, TraitName, TraitValue

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RawPerceptionResult:
    """Raw model output structure before translation to Domain Observations.

    This remains an infrastructure concern. No domain layer imports it.
    """

    model_name: str
    raw_traits: list[dict[str, Any]]
    metadata: dict[str, Any] = field(default_factory=dict)


class VLMPerceptionEngine(PerceptionEngine):
    """Concrete PerceptionEngine designed for experimental character observation."""

    def __init__(self, model_name: str = "experimental-vlm-s1") -> None:
        self._model_name = model_name

    def observe(
        self,
        reference: Reference,
        traits: list[TraitName],
    ) -> list[Observation]:
        """Analyze a reference and produce observations for the requested traits."""
        logger.info(
            "Analyzing reference %s (asset: %s) with model %s",
            reference.id,
            reference.asset_id,
            self._model_name,
        )
        trait_filter = [str(t) for t in traits] if traits else None
        raw_result = self._run_model(str(reference.asset_id), trait_filter)
        return self._convert_to_observations(reference, raw_result)

    def _run_model(
        self,
        asset_id: str,
        requested_traits: list[str] | None,
    ) -> RawPerceptionResult:
        """Runs the vision model inference logic (mocked baseline for S1)."""
        simulated_traits = [
            {
                "trait": "identity.facial_structure",
                "value": "oval",
                "confidence": 0.89,
                "evidence": {"raw_label": "oval face"},
            },
            {
                "trait": "appearance.hair_color",
                "value": "dark brown",
                "confidence": 0.94,
                "evidence": {"raw_label": "deep dark brown"},
            },
            {
                "trait": "appearance.hair_length",
                "value": "shoulder-length",
                "confidence": 0.88,
                "evidence": {"raw_label": "medium-long shoulder length"},
            },
            {
                "trait": "clothing.garment_type",
                "value": "jacket",
                "confidence": 0.96,
                "evidence": {"raw_label": "leather jacket"},
            },
            {
                "trait": "state.expression",
                "value": "neutral",
                "confidence": 0.75,
                "evidence": {"raw_label": "expressionless"},
            },
        ]

        if requested_traits:
            simulated_traits = [t for t in simulated_traits if t["trait"] in requested_traits]

        return RawPerceptionResult(
            model_name=self._model_name,
            raw_traits=simulated_traits,
            metadata={"status": "simulated", "asset_id": asset_id},
        )

    def _convert_to_observations(
        self,
        reference: Reference,
        raw_result: RawPerceptionResult,
    ) -> list[Observation]:
        """Converts raw infrastructure-level results into domain Observations."""
        observations: list[Observation] = []

        for item in raw_result.raw_traits:
            try:
                trait_name = TraitName(item["trait"])
                trait_value = TraitValue(item["value"])
                confidence = Confidence(float(item.get("confidence", 0.0)))

                evidence = {
                    "model": raw_result.model_name,
                    "raw_label": item.get("evidence", {}).get("raw_label", item["value"]),
                    "timestamp": datetime.now(UTC).isoformat(),
                }

                obs = Observation(
                    id=ObservationId.generate(),
                    reference_id=reference.id,
                    trait=trait_name,
                    value=trait_value,
                    confidence=confidence,
                    source=raw_result.model_name,
                    evidence=evidence,
                    created_at=datetime.now(UTC),
                )
                observations.append(obs)
            except (KeyError, ValueError, TypeError) as exc:
                logger.warning("Skipped invalid trait item %s: %s", item, exc)

        return observations
