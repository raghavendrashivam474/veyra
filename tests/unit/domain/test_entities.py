"""Tests for Veyra domain entities and aggregates."""

import pytest
from veyra.domain.character import Character
from veyra.domain.ids import CharacterId, ObservationId, ReferenceId
from veyra.domain.observations import Observation
from veyra.domain.reference import Reference, ReferenceSourceType
from veyra.domain.representation import CharacterRepresentation
from veyra.domain.traits import Confidence, TraitName, TraitValue


class TestReference:
    def test_valid_creation(self):
        ref = Reference(
            id=ReferenceId.generate(),
            asset_id="asset-001",
            source_type=ReferenceSourceType.IMAGE_FILE,
        )
        assert ref.source_type == ReferenceSourceType.IMAGE_FILE
        assert ref.asset_id == "asset-001"
        assert ref.created_at is not None

    def test_rejects_empty_asset_id(self):
        with pytest.raises(ValueError, match="non-empty"):
            Reference(
                id=ReferenceId.generate(),
                asset_id="",
                source_type=ReferenceSourceType.IMAGE_FILE,
            )

    def test_metadata_default_empty(self):
        ref = Reference(
            id=ReferenceId.generate(),
            asset_id="a",
            source_type=ReferenceSourceType.UNKNOWN,
        )
        assert ref.metadata == {}


class TestCharacter:
    def test_valid_creation(self):
        char = Character(
            id=CharacterId.generate(),
            name="Test Character",
        )
        assert char.name == "Test Character"
        assert char.description == ""

    def test_rejects_empty_name(self):
        with pytest.raises(ValueError, match="non-empty"):
            Character(id=CharacterId.generate(), name="")

    def test_mutable_description(self):
        char = Character(id=CharacterId.generate(), name="X")
        char.description = "Updated"
        assert char.description == "Updated"


class TestObservation:
    def _make_obs(self, **overrides) -> Observation:
        defaults = dict(
            id=ObservationId.generate(),
            reference_id=ReferenceId.generate(),
            trait=TraitName("facial.eye_shape"),
            value=TraitValue("almond"),
            confidence=Confidence(0.85),
            source="test-model",
        )
        defaults.update(overrides)
        return Observation(**defaults)

    def test_valid_creation(self):
        obs = self._make_obs()
        assert obs.trait.value == "facial.eye_shape"
        assert obs.confidence.score == 0.85

    def test_rejects_empty_source(self):
        with pytest.raises(ValueError, match="non-empty"):
            self._make_obs(source="")

    def test_frozen(self):
        obs = self._make_obs()
        with pytest.raises(AttributeError):
            obs.confidence = Confidence(0.5)  # type: ignore[misc]


class TestCharacterRepresentation:
    def _make_rep(self) -> CharacterRepresentation:
        return CharacterRepresentation(
            character_id=CharacterId.generate(),
        )

    def test_empty_representation(self):
        rep = self._make_rep()
        assert rep.version == "0.1"
        assert rep.observations == []
        assert rep.trait_names == set()

    def test_add_observation(self):
        rep = self._make_rep()
        obs = Observation(
            id=ObservationId.generate(),
            reference_id=ReferenceId.generate(),
            trait=TraitName("hair.texture"),
            value=TraitValue("wavy"),
            confidence=Confidence(0.84),
            source="test",
        )
        rep.add_observation(obs)
        assert len(rep.observations) == 1
        assert "hair.texture" in rep.trait_names

    def test_observations_for_trait(self):
        rep = self._make_rep()
        ref_id = ReferenceId.generate()
        for val in ["almond", "round"]:
            rep.add_observation(
                Observation(
                    id=ObservationId.generate(),
                    reference_id=ref_id,
                    trait=TraitName("facial.eye_shape"),
                    value=TraitValue(val),
                    confidence=Confidence(0.8),
                    source="test",
                )
            )
        rep.add_observation(
            Observation(
                id=ObservationId.generate(),
                reference_id=ref_id,
                trait=TraitName("hair.texture"),
                value=TraitValue("straight"),
                confidence=Confidence(0.7),
                source="test",
            )
        )
        eye_obs = rep.observations_for_trait("facial.eye_shape")
        assert len(eye_obs) == 2
        assert len(rep.observations_for_trait("hair.texture")) == 1
