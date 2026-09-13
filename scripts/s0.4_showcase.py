"""Veyra S0.4 Showcase.

Demonstrates the application service orchestration layer interacting with
domain objects and abstract ports, simulated via in-memory adapters.
"""

import sys
from pathlib import Path

# Ensure repository root is on sys.path for standalone script execution
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from veyra.application.services.character_service import CharacterService  # noqa: E402
from veyra.application.services.perception_service import PerceptionService  # noqa: E402
from veyra.application.services.representation_service import (  # noqa: E402
    RepresentationService,
)
from veyra.domain.ids import ReferenceId  # noqa: E402
from veyra.domain.reference import Reference, ReferenceSourceType  # noqa: E402
from veyra.domain.traits import TraitName  # noqa: E402

from tests.fixtures.fakes import (  # noqa: E402
    FakePerceptionEngine,
    InMemoryCharacterRepository,
    InMemoryObservationRepository,
    InMemoryReferenceRepository,
)


def main() -> int:
    print("======================================================================")
    print("                    VEYRA S0.4 ARCHITECTURE SHOWCASE                  ")
    print("======================================================================")
    print("Demonstrating thin application orchestration and dependency boundaries.")
    print()

    # 1. Initialize Adapters (Simulating Infrastructure)
    char_repo = InMemoryCharacterRepository()
    ref_repo = InMemoryReferenceRepository()
    obs_repo = InMemoryObservationRepository()

    # Pre-configure preset observation values on our fake perception engine
    perception_engine = FakePerceptionEngine(
        default_confidence=0.92,
        source="mock-qwen-vl-72b",
        preset_values={
            "facial.eye_color": "almond-shaped hazel",
            "hair.texture": "curly with gold accents",
            "style.clothing": "cyberpunk trench coat",
        },
    )

    # 2. Instantiate Application Services
    char_service = CharacterService(character_repo=char_repo)
    perception_service = PerceptionService(
        perception_engine=perception_engine, observation_repo=obs_repo
    )
    rep_service = RepresentationService()

    print("[Step 1] Initializing Application Services and In-Memory Ports... OK")

    # 3. Create a Fictional Character identity via CharacterService
    character = char_service.create_character(
        name="Kaelen",
        description="A quiet archivist seeking lost technology.",
    )
    print(f" -> Created Character: ID={character.id} | Name={character.name}")

    # 4. Ingest and Save a Reference
    reference = Reference(
        id=ReferenceId.generate(),
        asset_id="asset_kaelen_concept_art_01",
        source_type=ReferenceSourceType.IMAGE_FILE,
        metadata={"filename": "kaelen_profile.png", "resolution": "1024x1024"},
    )
    ref_repo.save(reference)
    print(f" -> Ingested Reference: ID={reference.id} | Asset ID={reference.asset_id}")

    # 5. Perform Perception Orchestraction via PerceptionService
    traits_to_query = [
        TraitName("facial.eye_color"),
        TraitName("hair.texture"),
        TraitName("style.clothing"),
    ]
    print(f" -> Requesting perception on traits: {[str(t) for t in traits_to_query]}...")

    observations = perception_service.perceive(reference=reference, traits=traits_to_query)
    print(f" -> Generated {len(observations)} Observations via {perception_engine.source}")

    for idx, obs in enumerate(observations, 1):
        print(f"    ({idx}) Trait: {obs.trait} | Value: {obs.value} | Confidence: {obs.confidence}")

    # 6. Aggregate Observations to Character Representation
    representation = rep_service.create_representation(
        character_id=character.id, observations=observations
    )

    print()
    print("======================== FINAL AGGREGATE STATE ========================")
    print(f"Character: {character.name} (ID: {character.id})")
    print(f"Description: {character.description}")
    print(f"Representation Version: {representation.version}")
    print(f"Total Observations Tracked: {len(representation.observations)}")
    print(f"Distinct Observed Traits: {representation.trait_names}")
    print(f"Last Updated: {representation.updated_at.isoformat()}")
    print("======================================================================")
    print("Showcase run completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
