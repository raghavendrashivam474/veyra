"""Veyra S0.3 Domain Model Showcase.

Demonstrates the complete domain vocabulary working independently
of any infrastructure, ML model, or database.

Run: uv run python scripts/s0.3_showcase.py
"""

from veyra.domain import (
    Character,
    CharacterId,
    CharacterRepresentation,
    Confidence,
    Observation,
    ObservationId,
    Reference,
    ReferenceId,
    ReferenceSourceType,
    TraitName,
    TraitValue,
)


def main() -> None:
    print("=" * 60)
    print("  VEYRA S0.3 - Domain Model Showcase")
    print("=" * 60)

    # 1. Create a character
    char = Character(
        id=CharacterId.generate(),
        name="veyra-character-001",
        description="Initial prototype character for S0.3 validation",
    )
    print(f"\nCharacter: {char.name}")
    print(f"  ID: {char.id}")

    # 2. Create references (source material)
    ref_a = Reference(
        id=ReferenceId.generate(),
        asset_id="asset-front-portrait.jpg",
        source_type=ReferenceSourceType.IMAGE_FILE,
    )
    ref_b = Reference(
        id=ReferenceId.generate(),
        asset_id="asset-side-profile.jpg",
        source_type=ReferenceSourceType.IMAGE_FILE,
    )
    print(f"\nReferences: {ref_a.asset_id}, {ref_b.asset_id}")

    # 3. Simulate perception observations
    observations_data = [
        ("facial.eye_shape", "almond", 0.91, ref_a.id),
        ("hair.texture", "wavy", 0.84, ref_a.id),
        ("facial.jaw_structure", "angular", 0.76, ref_b.id),
        ("silhouette.shoulder_width", "medium", 0.72, ref_b.id),
        ("appearance.skin_tone", "warm-ivory", 0.88, ref_a.id),
    ]

    obs_list = []
    for trait, value, conf, ref_id in observations_data:
        obs = Observation(
            id=ObservationId.generate(),
            reference_id=ref_id,
            trait=TraitName(trait),
            value=TraitValue(value),
            confidence=Confidence(conf),
            source="simulated-perception-v0",
        )
        obs_list.append(obs)

    # 4. Build representation
    rep = CharacterRepresentation(character_id=char.id)
    for obs in obs_list:
        rep.add_observation(obs)

    print(f"\nRepresentation v{rep.version}")
    print(f"  Observations: {len(rep.observations)}")
    print(f"  Distinct traits: {rep.trait_names}")
    print()

    for obs in rep.observations:
        print(f"  {obs.trait.value}")
        print(f"      value: {obs.value}")
        print(f"      confidence: {obs.confidence}")
        print()

    print("=" * 60)
    print("  Domain model works independently of infrastructure.")
    print("  No database, no ML model, no API required.")
    print("=" * 60)


if __name__ == "__main__":
    main()
