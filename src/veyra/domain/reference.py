"""Veyra domain Reference entity.

A Reference represents source material used for visual identity analysis.
It is NOT a Character - it is input that may eventually contribute
to a CharacterRepresentation.

    Reference A -+
    Reference B -+--> CharacterRepresentation
    Reference C -+

The actual image bytes are NOT stored here. The asset remains
managed by the asset-storage infrastructure boundary.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from veyra.domain.ids import ReferenceId


class ReferenceSourceType(StrEnum):
    """How the reference material was provided.

    Kept minimal for S0.3. Extend as S1 research demands.
    """

    IMAGE_FILE = "image_file"
    IMAGE_URL = "image_url"
    VIDEO_FRAME = "video_frame"
    GENERATED = "generated"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class Reference:
    """Source material for visual identity analysis.

    Attributes:
        id: Unique domain identifier.
        asset_id: Opaque handle to the actual asset in storage.
                  The domain does not know or care about file paths,
                  S3 keys, or database BLOBs.
        source_type: How this reference was provided.
        created_at: When Veyra ingested this reference.
        metadata: Arbitrary domain-level metadata. Not for
                  infrastructure concerns.
    """

    id: ReferenceId
    asset_id: str
    source_type: ReferenceSourceType
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.asset_id or not self.asset_id.strip():
            raise ValueError("Reference asset_id must be non-empty.")
