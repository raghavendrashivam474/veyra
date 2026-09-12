"""Core configuration management for Veyra."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Veyra runtime configuration."""

    model_config = SettingsConfigDict(
        env_prefix="VEYRA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: Literal["development", "testing", "production"] = Field(
        default="development",
        description="Execution environment mode",
    )
    debug: bool = Field(
        default=True,
        description="Debug mode toggle",
    )

    # Base paths
    base_dir: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent.parent
    )
    data_dir: Path = Field(default_factory=lambda: Path("data"))
    database_url: str = Field(default="sqlite:///data/database/veyra.db")
    asset_storage_dir: Path = Field(default_factory=lambda: Path("data/assets"))
    embedding_storage_dir: Path = Field(default_factory=lambda: Path("data/experiments/embeddings"))

    def resolved_data_dir(self) -> Path:
        """Return the absolute path for data directory."""
        if self.data_dir.is_absolute():
            return self.data_dir
        return self.base_dir / self.data_dir

    def resolved_asset_dir(self) -> Path:
        """Return the absolute path for asset storage."""
        if self.asset_storage_dir.is_absolute():
            return self.asset_storage_dir
        return self.base_dir / self.asset_storage_dir

    def resolved_database_path(self) -> Path:
        """Extract filesystem path if using SQLite."""
        prefix = "sqlite:///"
        if self.database_url.startswith(prefix):
            raw_path = self.database_url[len(prefix) :]
            path = Path(raw_path)
            if path.is_absolute():
                return path
            return self.base_dir / path
        raise ValueError(f"Non-sqlite database URL provided: {self.database_url}")


@lru_cache
def get_settings() -> Settings:
    """Provide cached settings instance."""
    return Settings()
