"""Unit tests for Veyra configuration."""

from pathlib import Path

from veyra.core.config import Settings


def test_default_settings():
    settings = Settings()
    assert settings.env == "development"
    assert settings.debug is True
    assert isinstance(settings.resolved_data_dir(), Path)
    assert isinstance(settings.resolved_asset_dir(), Path)
    assert isinstance(settings.resolved_database_path(), Path)


def test_custom_settings():
    settings = Settings(
        env="testing",
        debug=False,
        database_url="sqlite:///custom/path.db",
    )
    assert settings.env == "testing"
    assert settings.debug is False
    assert settings.resolved_database_path().name == "path.db"
