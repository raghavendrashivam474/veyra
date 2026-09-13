"""Unit tests for Veyra application services."""

import pytest
from veyra.application.services.character_service import CharacterService
from veyra.application.services.perception_service import PerceptionService
from veyra.application.services.representation_service import RepresentationService
from veyra.domain.ids import CharacterId, ReferenceId
from veyra.domain.reference import Reference, ReferenceSourceType
from veyra.domain.traits import TraitName

from tests.fixtures.fakes import (
    FakePerceptionEngine,
    InMemoryCharacterRepository,
    InMemoryObservationRepository,
    InMemoryReferenceRepository,
)


class TestCharacterService:
    """Tests for CharacterService orchestration."""

    def test_create_and_persist_character(self) -> None:
        repo = InMemoryCharacterRepository()
        service = CharacterService(character_repo=repo)

        char = service.create_character(name="Aria", description="A wandering researcher")

        assert char.name == "Aria"
        assert char.description == "A wandering researcher"
        assert isinstance(char.id, CharacterId)

        # Confirm persisted in repo
        persisted = repo.get(char.id)
        assert persisted is not None
        assert persisted.id == char.id
        assert persisted.name == "Aria"

    def test_get_character_returns_none_if_missing(self) -> None:
        repo = InMemoryCharacterRepository()
        service = CharacterService(character_repo=repo)

        missing_id = CharacterId.generate()
        result = service.get_character(missing_id)
        assert result is None

    def test_create_character_rejects_empty_name(self) -> None:
        repo = InMemoryCharacterRepository()
        service = CharacterService(character_repo=repo)

        with pytest.raises(ValueError):
            service.create_character(name="   ")


class TestPerceptionService:
    """Tests for PerceptionService orchestration."""

    def test_perceive_orchestrates_engine_and_repository(self) -> None:
        obs_repo = InMemoryObservationRepository()
        engine = FakePerceptionEngine(
            default_confidence=0.85,
            source="fake-vlm",
            preset_values={"facial.eye_color": "amber", "hair.color": "silver"},
        )
        service = PerceptionService(perception_engine=engine, observation_repo=obs_repo)

        ref = Reference(
            id=ReferenceId.generate(),
            asset_id="asset-12345",
            source_type=ReferenceSourceType.IMAGE_FILE,
        )
        traits = [TraitName("facial.eye_color"), TraitName("hair.color")]

        observations = service.perceive(reference=ref, traits=traits)

        assert len(observations) == 2
        assert observations[0].reference_id == ref.id
        assert str(observations[0].trait) == "facial.eye_color"
        assert str(observations[0].value) == "amber"
        assert observations[0].confidence.score == 0.85

        assert str(observations[1].trait) == "hair.color"
        assert str(observations[1].value) == "silver"

        # Check repository persistence
        persisted_obs = obs_repo.get_by_reference(ref.id)
        assert len(persisted_obs) == 2
        assert {o.id for o in persisted_obs} == {o.id for o in observations}

    def test_perceive_with_empty_traits(self) -> None:
        obs_repo = InMemoryObservationRepository()
        engine = FakePerceptionEngine()
        service = PerceptionService(perception_engine=engine, observation_repo=obs_repo)

        ref = Reference(
            id=ReferenceId.generate(),
            asset_id="asset-999",
            source_type=ReferenceSourceType.GENERATED,
        )

        observations = service.perceive(reference=ref, traits=[])
        assert observations == []
        assert obs_repo.get_by_reference(ref.id) == []


class TestRepresentationService:
    """Tests for RepresentationService orchestration."""

    def test_create_representation_from_observations(self) -> None:
        rep_service = RepresentationService()
        char_id = CharacterId.generate()
        ref_id = ReferenceId.generate()

        engine = FakePerceptionEngine(
            preset_values={"facial.eye_color": "green", "hair.texture": "wavy"}
        )
        traits = [TraitName("facial.eye_color"), TraitName("hair.texture")]
        ref = Reference(
            id=ref_id,
            asset_id="asset-001",
            source_type=ReferenceSourceType.IMAGE_FILE,
        )
        observations = engine.observe(ref, traits)

        rep = rep_service.create_representation(character_id=char_id, observations=observations)

        assert rep.character_id == char_id
        assert len(rep.observations) == 2
        assert rep.trait_names == {"facial.eye_color", "hair.texture"}
        assert len(rep.observations_for_trait("facial.eye_color")) == 1
        assert str(rep.observations_for_trait("facial.eye_color")[0].value) == "green"

    def test_create_representation_with_empty_observations(self) -> None:
        rep_service = RepresentationService()
        char_id = CharacterId.generate()

        rep = rep_service.create_representation(character_id=char_id, observations=[])

        assert rep.character_id == char_id
        assert len(rep.observations) == 0
        assert rep.trait_names == set()


class TestApplicationWorkflowIntegration:
    """Integration test checking end-to-end orchestration without infrastructure."""

    def test_end_to_end_orchestration_flow(self) -> None:
        # Repositories & Engine
        char_repo = InMemoryCharacterRepository()
        ref_repo = InMemoryReferenceRepository()
        obs_repo = InMemoryObservationRepository()
        perception_engine = FakePerceptionEngine(
            preset_values={
                "facial.eye_color": "hazel",
                "hair.length": "shoulder",
            }
        )

        # Services
        char_service = CharacterService(character_repo=char_repo)
        perception_service = PerceptionService(
            perception_engine=perception_engine, observation_repo=obs_repo
        )
        rep_service = RepresentationService()

        # Step 1: Create Character
        character = char_service.create_character(name="Lyra", description="Protagonist")

        # Step 2: Store reference
        reference = Reference(
            id=ReferenceId.generate(),
            asset_id="local-disk-file-01",
            source_type=ReferenceSourceType.IMAGE_FILE,
        )
        ref_repo.save(reference)

        # Step 3: Perceive traits from reference
        traits_to_extract = [
            TraitName("facial.eye_color"),
            TraitName("hair.length"),
        ]
        observations = perception_service.perceive(reference=reference, traits=traits_to_extract)
        assert len(observations) == 2

        # Step 4: Construct character representation
        representation = rep_service.create_representation(
            character_id=character.id, observations=observations
        )

        # Assert final aggregate state
        assert representation.character_id == character.id
        assert len(representation.observations) == 2
        assert "facial.eye_color" in representation.trait_names
        assert "hair.length" in representation.trait_names
        assert char_repo.get(character.id) is not None
        assert ref_repo.get(reference.id) is not None
        assert len(obs_repo.get_by_reference(reference.id)) == 2
