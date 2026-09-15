"""Tests for Veyra domain trait value objects."""

import pytest

from veyra.domain.traits import Confidence, TraitName, TraitValue


class TestTraitName:
    def test_valid_names(self):
        assert TraitName("facial.eye_shape").value == "facial.eye_shape"
        assert TraitName("hair.texture").namespace == "hair"
        assert TraitName("hair.texture").name == "texture"
        assert TraitName("silhouette.shoulder_width").namespace == "silhouette"

    def test_rejects_no_namespace(self):
        with pytest.raises(ValueError, match=r"namespace\.name"):
            TraitName("eye_shape")

    def test_rejects_uppercase(self):
        with pytest.raises(ValueError):
            TraitName("Facial.EyeShape")

    def test_rejects_spaces(self):
        with pytest.raises(ValueError):
            TraitName("facial.eye shape")

    def test_rejects_empty(self):
        with pytest.raises(ValueError):
            TraitName("")

    def test_equality(self):
        assert TraitName("a.b") == TraitName("a.b")
        assert TraitName("a.b") != TraitName("a.c")

    def test_frozen(self):
        t = TraitName("a.b")
        with pytest.raises(AttributeError):
            t.value = "x.y"  # type: ignore[misc]


class TestTraitValue:
    def test_string_value(self):
        v = TraitValue("almond")
        assert str(v) == "almond"

    def test_numeric_value(self):
        v = TraitValue(0.73)
        assert str(v) == "0.73"

    def test_int_value(self):
        v = TraitValue(42)
        assert str(v) == "42"

    def test_rejects_empty_string(self):
        with pytest.raises(ValueError, match="non-empty"):
            TraitValue("")


class TestConfidence:
    def test_valid_range(self):
        assert Confidence(0.0).score == 0.0
        assert Confidence(0.5).score == 0.5
        assert Confidence(1.0).score == 1.0

    def test_rejects_above_one(self):
        with pytest.raises(ValueError, match=r"\[0\.0, 1\.0\]"):
            Confidence(1.01)

    def test_rejects_negative(self):
        with pytest.raises(ValueError, match=r"\[0\.0, 1\.0\]"):
            Confidence(-0.1)

    def test_str_format(self):
        assert str(Confidence(0.91)) == "0.91"

    def test_frozen(self):
        c = Confidence(0.5)
        with pytest.raises(AttributeError):
            c.score = 0.9  # type: ignore[misc]
