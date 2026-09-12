"""Unit tests for Local Asset Store."""

from veyra.infrastructure.assets.local import LocalAssetStore


def test_asset_store_lifecycle(tmp_path):
    store = LocalAssetStore(tmp_path)
    sample_data = b"sample visual asset payload"
    key = "samples/test_image.png"

    # Save
    meta = store.save_bytes(key, sample_data)
    assert meta["key"] == key
    assert meta["size_bytes"] == len(sample_data)
    assert "sha256" in meta

    # Exists & Read
    assert store.exists(key) is True
    read_data = store.read_bytes(key)
    assert read_data == sample_data

    # Delete
    assert store.delete(key) is True
    assert store.exists(key) is False
