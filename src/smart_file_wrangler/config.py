"""
config.py

Holds default settings and shared configuration values for Smart File Wrangler.

These defaults define baseline behavior for scanning, metadata extraction,
organisation, thumbnail generation, and reporting.

Values here are intended to be overridden by CLI arguments or future GUI input.
This module contains configuration only — no runtime logic.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class Config:
    """
    Runtime configuration for a single Smart File Wrangler run.

    This dataclass holds settings for **one folder processing run**.
    The legacy global `Defaults` dictionary was removed from runtime use.
    `Config` contains no media logic — it is only a passive container.
    """

    # ------------------------------------------------------------------
    # Scanning and file discovery
    # ------------------------------------------------------------------

    # Whether to recurse into subfolders when scanning input directories
    recurse_subfolders: bool = True

    # File extensions to include when scanning (without leading dots)
    file_types: List[str] = field(default_factory=lambda: ["mp4", "png", "wav", "jpg"])

    # Whether to group frame sequences into logical units
    combine_frame_seq: bool = True

    # Ignore generated thumbnail folders during scanning
    ignore_thumbnail_folders: bool = True

    # ------------------------------------------------------------------
    # Thumbnail generation
    # ------------------------------------------------------------------

    # Master switch for thumbnail generation
    generate_thumbnails: bool = False

    # Enable thumbnails for specific media types
    thumb_images: bool = True
    thumb_videos: bool = True

    # Thumbnail output settings (size is longest edge in pixels)
    thumb_size: int = 512
    thumb_suffix: str = "_thumb"
    thumb_folder_name: str = "thumbnails"

    # ------------------------------------------------------------------
    # Metadata extraction
    # ------------------------------------------------------------------

    # Media categories to include during metadata processing
    include_media_types: Dict[str, bool] = field(default_factory=lambda: {
        "image": True,
        "video": True,
        "audio": True,
        "other": True,
    })

    # Metadata fields to extract and include in reports
    metadata_fields: List[str] = field(default_factory=lambda: [
        "file_path",
        "file_size",
        "media_type",
        "extension",
        "resolution_px",
        "duration_seconds",
        "sample_rate_hz",
        "mode",
        "format",
        "frame_count",
        "middle_frame_number",
        "start_frame",
        "end_frame",
    ])

    # Metadata sorting options
    # Options: "file_path", "extension", "media_type"
    metadata_sort_by: str = "file_path"
    metadata_sort_reverse: bool = False

    # ------------------------------------------------------------------
    # Organiser behavior
    # ------------------------------------------------------------------

    # Enable or disable the organiser subsystem entirely
    enable_organiser: bool = False

    # Organiser mode selection
    # Options: "media_type", "extension", "filename_rule"
    organiser_mode: str = "media_type"

    # Filename-based organiser rules
    # Only used if organiser_mode == "string_rule"
    # Example rule: {"type": "contains", "value": "SEF"}
    filename_rules: List[Dict] = field(default_factory=lambda: [])

    # Folder name for files that do not match organiser rules
    default_unsorted_folder: str = "unsorted"

    # Whether files should be moved (True) or copied (False)
    move_files: bool = False

    # ------------------------------------------------------------------
    # Reporting outputs
    # ------------------------------------------------------------------

    # Enable or disable specific report formats
    output_csv: bool = True
    output_json: bool = True
    output_excel: bool = True
    output_tree: bool = True

    # Output directory for reports
    # None = same folder as input
    report_output_dir: Optional[str] = None

    # ------------------------------------------------------------------
    # Logging and verbosity
    # ------------------------------------------------------------------

    # Enable verbose console output
    verbose: bool = True

    # Expand logging output with additional detail
    expand_log: bool = False
