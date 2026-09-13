"""S1 Research Script — Execute Perception Experiments on Target Assets."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add project root to path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

from veyra.domain.ids import ReferenceId  # noqa: E402
from veyra.domain.reference import Reference, ReferenceSourceType  # noqa: E402
from veyra.domain.traits import TraitName  # noqa: E402
from veyra.infrastructure.models.vlm_perception import VLMPerceptionEngine  # noqa: E402


def run_experiment(asset_id: str, model_name: str) -> None:
    """Executes a structured perception check against a local asset."""
    engine = VLMPerceptionEngine(model_name=model_name)
    source_type = next(iter(ReferenceSourceType))
    reference = Reference(
        id=ReferenceId.generate(),
        asset_id=asset_id,
        source_type=source_type,
    )

    print("=== Running S1 Perception Experiment ===")
    print(f"Model ID:     {model_name}")
    print(f"Reference ID: {reference.id}")
    print(f"Asset ID:     {reference.asset_id}\n")

    requested_traits = [
        TraitName("identity.facial_structure"),
        TraitName("appearance.hair_color"),
        TraitName("appearance.hair_length"),
        TraitName("clothing.garment_type"),
    ]

    observations = engine.observe(reference, requested_traits)

    print(f"Observations Extracted ({len(observations)}):")
    print("-" * 60)
    for obs in observations:
        print(
            f"Trait: {obs.trait!s:<30} | "
            f"Value: {obs.value!s:<15} | "
            f"Confidence: {obs.confidence.score:.2f}"
        )
    print("-" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--asset-id", default="reference_001.jpg")
    parser.add_argument("--model", default="experimental-vlm-s1")
    args = parser.parse_args()

    run_experiment(args.asset_id, args.model)
