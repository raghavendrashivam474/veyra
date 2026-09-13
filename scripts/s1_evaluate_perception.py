"""S1 Research Evaluation Script — Assess perception repeatability and quality."""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

from veyra.domain.ids import ReferenceId  # noqa: E402
from veyra.domain.reference import Reference, ReferenceSourceType  # noqa: E402
from veyra.domain.traits import TraitName  # noqa: E402
from veyra.infrastructure.models.vlm_perception import VLMPerceptionEngine  # noqa: E402


def evaluate_perception(runs: int = 3) -> dict[str, float]:
    """Runs repeated perception checks to evaluate observation consistency."""
    engine = VLMPerceptionEngine(model_name="experimental-vlm-s1")
    ref = Reference(
        id=ReferenceId.generate(),
        asset_id="ref_eval_001.jpg",
        source_type=ReferenceSourceType.IMAGE_FILE,
    )
    requested_traits = [
        TraitName("identity.facial_structure"),
        TraitName("appearance.hair_color"),
        TraitName("appearance.hair_length"),
        TraitName("clothing.garment_type"),
    ]

    all_runs = []
    for _ in range(runs):
        obs = engine.observe(ref, requested_traits)
        all_runs.append({str(o.trait): str(o.value) for o in obs})

    # Assert consistency across runs
    first_run = all_runs[0]
    identical_count = sum(1 for r in all_runs if r == first_run)
    repeatability = identical_count / runs

    print("=== Perception Evaluation Report ===")
    print(f"Evaluated Runs: {runs}")
    print(f"Repeatability Score: {repeatability * 100:.1f}%")
    print(f"Observed Traits per Run: {len(first_run)}")
    return {"repeatability": repeatability, "trait_count": float(len(first_run))}


if __name__ == "__main__":
    evaluate_perception()
