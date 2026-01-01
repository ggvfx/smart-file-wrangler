"""
media_item.py

Internal data object representing a discovered filesystem entry.

This class is part of a modular media-processing pipeline. It provides
a single, unambiguous container to wrap either:

- A real filesystem file (`Path` object`), OR
- A detected frame sequence (`dict` record containing sequence metadata)

It intentionally contains **no methods or logic** — it only stores data
to keep other modules simple and clear.
"""

# ----------------------------------------------------------------------
# Standard library imports
# ----------------------------------------------------------------------

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


# ----------------------------------------------------------------------
# Dataclass
# ----------------------------------------------------------------------
@dataclass
class MediaItem:
    """
    A simple container representing one discovered media item.

    Attributes:
        kind (Literal["file", "sequence"]):
            - "file" → this item represents a single real file on disk
            - "sequence" → this item represents a frame sequence pattern

        path (Path | None):
            - Stores the filesystem path if `kind == "file"`
            - Must be `None` if `kind == "sequence"`

        sequence_info (dict | None):
            - Stores sequence metadata if `kind == "sequence"`
            - Must be `None` if `kind == "file"`

    Example:
        MediaItem(kind="file", path=Path("/tmp/video.mp4"))
        MediaItem(kind="sequence", sequence_info={"start": 1001, "end": 1050})
    """
    kind: Literal["file", "sequence"]
    path: Path | None = None
    sequence_info: dict | None = None

