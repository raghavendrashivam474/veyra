import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture(scope="session", autouse=True)
def test_env_isolation():
    """
    Enforces total test isolation. All data storage, assets, and database
    writes are redirected to a temporary environment.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Define overrides
        overrides = {
            "VEYRA_ENVIRONMENT": "testing",
            "VEYRA_DEBUG": "true",
            "VEYRA_DATA_DIR": str(tmp_path / "data"),
            "VEYRA_SQLITE_PATH": str(tmp_path / "data" / "database" / "veyra_test.db"),
            "VEYRA_ASSET_DIR": str(tmp_path / "data" / "assets"),
            "VEYRA_EMBEDDING_DIR": str(tmp_path / "data" / "embeddings"),
        }

        # Save old values to restore after test run
        old_env = {key: os.environ.get(key) for key in overrides}

        # Set new overrides
        for key, val in overrides.items():
            os.environ[key] = val

        # Ensure targeted mock directories exist
        (tmp_path / "data" / "database").mkdir(parents=True, exist_ok=True)
        (tmp_path / "data" / "assets").mkdir(parents=True, exist_ok=True)
        (tmp_path / "data" / "embeddings").mkdir(parents=True, exist_ok=True)

        yield

        # Restore environment variables
        for key, old_val in old_env.items():
            if old_val is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old_val
