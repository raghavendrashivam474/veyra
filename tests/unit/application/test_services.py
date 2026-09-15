"""Unit tests for Veyra application services."""

from __future__ import annotations

import pytest

from tests.fixtures.fakes import (
    FakePerceptionEngine,
    InMemoryCharacterRepository,
    InMemoryObservationRepository,
    InMemoryReferenceRepository,
)
from veyra.application.services.character_service import CharacterService
from veyra.application.services.perception_service import PerceptionService
from veyra.application.services.representation_service import RepresentationService
from veyra.domain.ids import CharacterId, ObservationId, ReferenceId
from veyra.domain.observations import Observation
from veyra.domain.reconciliation import HighestConfidenceStrategy
from veyra.domain.reference import Reference, ReferenceSourceType
from veyra.domain.traits import Confidence, TraitName, TraitValue


def _make_obs(
    trait: str,
    value: str,
    confidence: float = 0.85,
    source: str = "mock-vlm",
) -> Observation:
    return Observation(
        id=ObservationId.generate(),
        reference_id=ReferenceId.generate(),
        trait=TraitName(trait),
        value=TraitValue(value),
        confidence=Confidence(confidence),
        source=source,
    )


class TestCharacterService:
    """Tests for CharacterService orchestrations."""

    def test_create_and_persist_character(self) -> None:
        repo = InMemoryCharacterRepository()
        service = CharacterService(character_repo=repo)

        character = service.create_character(name="Aethelgard", description="Ancient wanderer.")

        assert character.name == "Aethelgard"
        assert character.description == "Ancient wanderer."

        retrieved = service.get_character(character.id)
        assert retrieved is not None
        assert retrieved.name == "Aethelgard"

    def test_get_character_returns_none_if_missing(self) -> None:
        repo = InMemoryCharacterRepository()
        service = CharacterService(character_repo=repo)

        assert service.get_character(CharacterId("nonexistent")) is None

    def test_create_character_rejects_empty_name(self) -> None:
        repo = InMemoryCharacterRepository()
        service = CharacterService(character_repo=repo)

        with pytest.raises(ValueError, match=r"Character name must be non-empty\."):
            service.create_character(name="   ")


class TestPerceptionService:
    """Tests for PerceptionService orchestrations."""

    def test_perceive_orchestrates_engine_and_repository(self) -> None:
        engine = FakePerceptionEngine(
            preset_values={"facial.eye_color": "amber", "hair.length": "long"}
        )
        obs_repo = InMemoryObservationRepository()
        service = PerceptionService(perception_engine=engine, observation_repo=obs_repo)

        ref = Reference(
            id=ReferenceId("ref-test"),
            asset_id="asset-1",
            source_type=ReferenceSourceType.IMAGE_FILE,
        )

        target_traits = [TraitName("facial.eye_color"), TraitName("hair.length")]
        observations = service.perceive(ref, target_traits)

        assert len(observations) == 2
        persisted = obs_repo.get_by_reference(ref.id)
        assert len(persisted) == 2

    def test_perceive_with_empty_traits(self) -> None:
        engine = FakePerceptionEngine()
        obs_repo = InMemoryObservationRepository()
        service = PerceptionService(perception_engine=engine, observation_repo=obs_repo)

        ref = Reference(
            id=ReferenceId("ref-empty"),
            asset_id="asset-1",
            source_type=ReferenceSourceType.IMAGE_FILE,
        )

        observations = service.perceive(ref, [])
        assert observations == []


class TestRepresentationService:
    """Tests for RepresentationService orchestrations."""

    def test_create_representation_from_observations(self) -> None:
        service = RepresentationService()
        char_id = CharacterId("char-rep-1")
        obs1 = _make_obs("hair.color", "dark_brown")
        obs2 = _make_obs("facial.eye_shape", "almond")

        rep = service.create_representation(char_id, [obs1, obs2])

        assert rep.character_id == char_id
        assert len(rep.observations) == 2
        assert rep.trait_names == {"hair.color", "facial.eye_shape"}

    def test_create_representation_with_empty_observations(self) -> None:
        service = RepresentationService()
        char_id = CharacterId("char-rep-2")
        rep = service.create_representation(char_id, [])

        assert rep.character_id == char_id
        assert len(rep.observations) == 0

    def test_reconcile_observations_groups_and_reconciles_traits(self) -> None:
        service = RepresentationService()
        obs1 = _make_obs("hair.color", "dark_brown", 0.90)
        obs2 = _make_obs("hair.color", "dark_brown", 0.80)
        obs3 = _make_obs("hair.color", "black", 0.50)
        obs4 = _make_obs("facial.eye_shape", "almond", 0.75)

        reconciled_map = service.reconcile_observations([obs1, obs2, obs3, obs4])

        assert len(reconciled_map) == 2
        assert TraitName("hair.color") in reconciled_map
        assert TraitName("facial.eye_shape") in reconciled_map

        hair_recon = reconciled_map[TraitName("hair.color")]
        assert hair_recon.selected_value == TraitValue("dark_brown")
        assert hair_recon.total_observations == 3
        assert hair_recon.has_conflict is True

        eye_recon = reconciled_map[TraitName("facial.eye_shape")]
        assert eye_recon.selected_value == TraitValue("almond")
        assert eye_recon.total_observations == 1
        assert eye_recon.has_conflict is False

    def test_reconcile_observations_empty_list_returns_empty_dict(self) -> None:
        service = RepresentationService()
        assert service.reconcile_observations([]) == {}

    def test_reconcile_traits_from_character_representation(self) -> None:
        service = RepresentationService()
        char_id = CharacterId("char-rep-3")
        obs1 = _make_obs("hair.color", "silver", 0.95)
        obs2 = _make_obs("hair.color", "silver", 0.90)
        rep = service.create_representation(char_id, [obs1, obs2])

        reconciled = service.reconcile_traits(rep)

        assert TraitName("hair.color") in reconciled
        assert reconciled[TraitName("hair.color")].selected_value == TraitValue("silver")
        assert reconciled[TraitName("hair.color")].confidence == Confidence(0.95)

    def test_reconcile_with_custom_strategy_injection(self) -> None:
        service = RepresentationService(default_strategy=HighestConfidenceStrategy())
        obs1 = _make_obs("hair.color", "black", 0.95)
        obs2 = _make_obs("hair.color", "dark_brown", 0.90)
        obs3 = _make_obs("hair.color", "dark_brown", 0.90)

        # HighestConfidenceStrategy chooses 'black' (0.95 vs 0.90)
        # while ConfidenceWeightedStrategy would choose 'dark_brown' (1.80 vs 0.95)
        reconciled = service.reconcile_observations([obs1, obs2, obs3])

        assert reconciled[TraitName("hair.color")].selected_value == TraitValue("black")
        assert reconciled[TraitName("hair.color")].confidence == Confidence(0.95)


class TestApplicationWorkflowIntegration:
    """End-to-end orchestration tests across application services."""

    def test_end_to_end_orchestration_flow(self) -> None:
        char_repo = InMemoryCharacterRepository()
        ref_repo = InMemoryReferenceRepository()
        obs_repo = InMemoryObservationRepository()

        char_service = CharacterService(character_repo=char_repo)
        engine = FakePerceptionEngine(
            preset_values={
                "facial.eye_color": "hazel",
                "hair.color": "chestnut",
            }
        )
        perceive_service = PerceptionService(perception_engine=engine, observation_repo=obs_repo)
        rep_service = RepresentationService()

        # 1. Create character
        char = char_service.create_character("Veyra Protagonist")

        # 2. Add reference
        ref = Reference(
            id=ReferenceId.generate(),
            asset_id="asset-ref-1",
            source_type=ReferenceSourceType.IMAGE_FILE,
        )
        ref_repo.save(ref)

        # 3. Perceive
        traits = [TraitName("facial.eye_color"), TraitName("hair.color")]
        observations = perceive_service.perceive(ref, traits)

        # 4. Form representation & reconcile
        rep = rep_service.create_representation(char.id, observations)
        reconciled = rep_service.reconcile_traits(rep)

        assert len(rep.observations) == 2
        assert len(reconciled) == 2
        assert reconciled[TraitName("facial.eye_color")].selected_value == TraitValue("hazel")
        assert reconciled[TraitName("hair.color")].selected_value == TraitValue("chestnut")
