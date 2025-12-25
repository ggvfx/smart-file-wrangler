"""
media_item.py

Internal data object representing a discovered filesystem entry.

Purpose:
- Provides a single, unambiguous container for media discovery results
- Replaces raw `Path` and `dict` primitives incrementally across the project
- Preserves behavior by carrying legacy values without adding logic

Fields:
- kind (Literal["file", "sequence"]): Whether this item is a single file or a frame sequence
- path (Path | None): Path to a single file (None if sequence)
- sequence_info (dict | None): Sequence metadata row (None if single file)

Notes:
- This is a pure data container with no methods or behavior assumptions
- It is not coupled to pipeline logic or other modules
- It does not filter, transform, or scan the filesystem
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

@dataclass
class MediaItem:
    kind: Literal["file", "sequence"]
    path: Path | None = None
    sequence_info: dict | None = None
