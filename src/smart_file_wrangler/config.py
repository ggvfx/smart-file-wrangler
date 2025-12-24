"""
config.py

Holds default settings and shared configuration values for Smart File Wrangler.

These defaults define baseline behavior for scanning, metadata extraction,
organisation, thumbnail generation, and reporting.

Values here are intended to be overridden by CLI arguments or future GUI input.
This module contains configuration only — no runtime logic.
"""

Defaults = {

    # ------------------------------------------------------------------
    # Scanning and file discovery
    # ------------------------------------------------------------------

    # Whether to recurse into subfolders when scanning input directories
    "recurse_subfolders": True,

    # File extensions to include when scanning (without leading dots)
    "file_types": ["mp4", "png", "wav", "jpg"],

    # Whether to group frame sequences into logical units
    "combine_frame_seq": True,

    # Ignore generated thumbnail folders during scanning
    "ignore_thumbnail_folders": True,


    # ------------------------------------------------------------------
    # Thumbnail generation
    # ------------------------------------------------------------------

    # Master switch for thumbnail generation
    "generate_thumbnails": False,

    # Enable thumbnails for specific media types
    "thumb_images": True,
    "thumb_videos": True,

    # Thumbnail output settings
    "thumb_size": 512,
    "thumb_suffix": "_thumb",
    "thumb_folder_name": "thumbnails",


    # ------------------------------------------------------------------
    # Metadata extraction
    # ------------------------------------------------------------------

    # Media categories to include during metadata processing
    "include_media_types": {
        "image": True,
        "video": True,
        "audio": True,
        "other": True,
    },

    # Metadata fields to extract and include in reports
    "metadata_fields": [
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
    ],

    # Metadata sorting options
    # Options: "file_path", "extension", "media_type"
    "metadata_sort_by": "file_path",
    "metadata_sort_reverse": False,


    # ------------------------------------------------------------------
    # Organiser behavior
    # ------------------------------------------------------------------

    # Enable or disable the organiser subsystem entirely
    "enable_organiser": False,

    # Organiser mode selection
    # Options: "media_type", "extension", "filename_rule"
    "organiser_mode": "media_type",

    # Filename-based organiser rules
    # Only used if organiser_mode == "filename_rule"
    # Example rule: {"type": "contains", "value": "SEF"}
    "filename_rules": [],

    # Folder name for files that do not match organiser rules
    "default_unsorted_folder": "unsorted",

    # Whether files should be moved (True) or copied (False)
    "move_files": False,


    # ------------------------------------------------------------------
    # Reporting outputs
    # ------------------------------------------------------------------

    # Enable or disable specific report formats
    "output_csv": True,
    "output_json": True,
    "output_excel": True,
    "output_tree": True,

    # Output directory for reports
    # None = same folder as input
    "report_output_dir": None,


    # ------------------------------------------------------------------
    # Logging and verbosity
    # ------------------------------------------------------------------

    # Enable verbose console output
    "verbose": True,

    # Expand logging output with additional detail
    "expand_log": False,
}


from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Config:
    """
    Runtime configuration for a single Smart File Wrangler run.

    This dataclass mirrors the Defaults dictionary exactly.
    It exists to replace global mutable Defaults at runtime,
    while preserving identical behavior and meaning.
    """

    # ------------------------------------------------------------------
    # Scanning and file discovery
    # ------------------------------------------------------------------

    # Whether to recurse into subfolders when scanning input directories
    recurse_subfolders: bool = Defaults["recurse_subfolders"]

    # File extensions to include when scanning (without leading dots)
    file_types: List[str] = field(default_factory=lambda: Defaults["file_types"])

    # Whether to group frame sequences into logical units
    combine_frame_seq: bool = Defaults["combine_frame_seq"]

    # Ignore generated thumbnail folders during scanning
    ignore_thumbnail_folders: bool = Defaults["ignore_thumbnail_folders"]


    # ------------------------------------------------------------------
    # Thumbnail generation
    # ------------------------------------------------------------------

    # Master switch for thumbnail generation
    generate_thumbnails: bool = Defaults["generate_thumbnails"]

    # Enable thumbnails for specific media types
    thumb_images: bool = Defaults["thumb_images"]
    thumb_videos: bool = Defaults["thumb_videos"]

    # Thumbnail output settings
    thumb_size: int = Defaults["thumb_size"]
    thumb_suffix: str = Defaults["thumb_suffix"]
    thumb_folder_name: str = Defaults["thumb_folder_name"]


    # ------------------------------------------------------------------
    # Metadata extraction
    # ------------------------------------------------------------------

    # Media categories to include during metadata processing
    include_media_types: Dict[str, bool] = field(default_factory=lambda: Defaults["include_media_types"])

    # Metadata fields to extract and include in reports
    metadata_fields: List[str] = field(default_factory=lambda: Defaults["metadata_fields"])

    # Metadata sorting options
    # Options: "file_path", "extension", "media_type"
    metadata_sort_by: str = Defaults["metadata_sort_by"]
    metadata_sort_reverse: bool = Defaults["metadata_sort_reverse"]


    # ------------------------------------------------------------------
    # Organiser behavior
    # ------------------------------------------------------------------

    # Enable or disable the organiser subsystem entirely
    enable_organiser: bool = Defaults["enable_organiser"]

    # Organiser mode selection
    # Options: "media_type", "extension", "filename_rule"
    organiser_mode: str = Defaults["organiser_mode"]

    # Filename-based organiser rules
    # Only used if organiser_mode == "filename_rule"
    # Example rule: {"type": "contains", "value": "SEF"}
    filename_rules: List[Dict] = field(default_factory=lambda: Defaults["filename_rules"])

    # Folder name for files that do not match organiser rules
    default_unsorted_folder: str = Defaults["default_unsorted_folder"]

    # Whether files should be moved (True) or copied (False)
    move_files: bool = Defaults["move_files"]


    # ------------------------------------------------------------------
    # Reporting outputs
    # ------------------------------------------------------------------

    # Enable or disable specific report formats
    output_csv: bool = Defaults["output_csv"]
    output_json: bool = Defaults["output_json"]
    output_excel: bool = Defaults["output_excel"]
    output_tree: bool = Defaults["output_tree"]

    # Output directory for reports
    # None = same folder as input
    report_output_dir: Optional[str] = None


    # ------------------------------------------------------------------
    # Logging and verbosity
    # ------------------------------------------------------------------

    # Enable verbose console output
    verbose: bool = Defaults["verbose"]

    # Expand logging output with additional detail
    expand_log: bool = Defaults["expand_log"]
