"""Tests for Veyra domain identifiers."""

import pytest

from veyra.domain.ids import CharacterId, ObservationId, ReferenceId


class TestCharacterId:
    def test_generate_creates_unique_ids(self):
        a = CharacterId.generate()
        b = CharacterId.generate()
        assert a != b
        assert a.value

    def test_explicit_value(self):
        cid = CharacterId(value="char-001")
        assert str(cid) == "char-001"

    def test_rejects_empty_string(self):
        with pytest.raises(ValueError, match="non-empty"):
            CharacterId(value="")

    def test_rejects_whitespace_only(self):
        with pytest.raises(ValueError, match="non-empty"):
            CharacterId(value="   ")

    def test_equality(self):
        a = CharacterId(value="same")
        b = CharacterId(value="same")
        assert a == b

    def test_frozen(self):
        cid = CharacterId.generate()
        with pytest.raises(AttributeError):
            cid.value = "nope"  # type: ignore[misc]


class TestReferenceId:
    def test_generate(self):
        rid = ReferenceId.generate()
        assert rid.value

    def test_rejects_empty(self):
        with pytest.raises(ValueError, match="non-empty"):
            ReferenceId(value="")


class TestObservationId:
    def test_generate(self):
        oid = ObservationId.generate()
        assert oid.value

    def test_rejects_empty(self):
        with pytest.raises(ValueError, match="non-empty"):
            ObservationId(value="")
