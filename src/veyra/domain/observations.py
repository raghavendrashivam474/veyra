"""Veyra domain Observation model.

An Observation captures what a perception system noticed about
a reference. This is fundamentally different from a ground-truth fact.

    "What Veyra observed"  !=  "What the character ultimately is"

This distinction becomes critical when multiple references and
multiple models produce conflicting observations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from veyra.domain.ids import ObservationId, ReferenceId
from veyra.domain.traits import Confidence, TraitName, TraitValue


@dataclass(frozen=True, slots=True)
class Observation:
    """A single perception observation about a reference.

    Attributes:
        id: Unique observation identifier.
        reference_id: Which reference this observation came from.
        trait: What visual characteristic was observed.
        value: What the perception system reported.
        confidence: How confident the system was (0.0-1.0).
        source: Identifier for the perception model/method
                (e.g. 'qwen-vl-72b', 'insightface-v3').
                Kept as a plain string to avoid coupling.
        evidence: Optional structured evidence supporting
                  this observation (e.g. bounding box coords,
                  attention weights). Domain-agnostic.
        created_at: When this observation was produced.
    """

    id: ObservationId
    reference_id: ReferenceId
    trait: TraitName
    value: TraitValue
    confidence: Confidence
    source: str
    evidence: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.source or not self.source.strip():
            raise ValueError("Observation source must be non-empty.")
