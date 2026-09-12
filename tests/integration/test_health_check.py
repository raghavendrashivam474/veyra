"""Integration tests for Veyra health check."""

import veyra
from veyra.api.cli import run_health_check


def test_health_check_execution(tmp_path, monkeypatch):
    monkeypatch.setenv("VEYRA_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("VEYRA_DATABASE_URL", f"sqlite:///{tmp_path}/data/test.db")
    monkeypatch.setenv("VEYRA_ASSET_STORAGE_DIR", str(tmp_path / "data" / "assets"))
    monkeypatch.setenv("VEYRA_EMBEDDING_STORAGE_DIR", str(tmp_path / "data" / "embeddings"))

    code = run_health_check()
    assert code == 0


def test_version():
    assert veyra.__version__ == "0.1.0a0"
