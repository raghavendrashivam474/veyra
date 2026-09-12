"""Local filesystem asset store implementation."""

import hashlib
from pathlib import Path


class LocalAssetStore:
    """Handles storage and retrieval of raw binary assets on the local filesystem."""

    def __init__(self, base_path: Path) -> None:
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_bytes(self, key: str, data: bytes) -> dict[str, str | int]:
        """Save raw bytes to asset key and return asset metadata."""
        target_file = self.base_path / key
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_bytes(data)

        sha256_hash = hashlib.sha256(data).hexdigest()
        return {
            "key": key,
            "path": str(target_file),
            "size_bytes": len(data),
            "sha256": sha256_hash,
        }

    def read_bytes(self, key: str) -> bytes:
        """Read asset bytes by key."""
        target_file = self.base_path / key
        if not target_file.exists():
            raise FileNotFoundError(f"Asset not found: {key}")
        return target_file.read_bytes()

    def exists(self, key: str) -> bool:
        """Check if an asset exists."""
        return (self.base_path / key).exists()

    def delete(self, key: str) -> bool:
        """Delete an asset if present."""
        target_file = self.base_path / key
        if target_file.exists():
            target_file.unlink()
            return True
        return False
