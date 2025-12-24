from dataclasses import dataclass
from pathlib import Path
from typing import Literal

@dataclass
class MediaItem:
    kind: Literal["file", "sequence"]
    path: Path | None = None
    sequence_info: dict | None = None
