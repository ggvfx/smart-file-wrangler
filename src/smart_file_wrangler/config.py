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


from dataclasses import dataclass
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
    recurse_subfolders: bool

    # File extensions to include when scanning (without leading dots)
    file_types: List[str]

    # Whether to group frame sequences into logical units
    combine_frame_seq: bool

    # Ignore generated thumbnail folders during scanning
    ignore_thumbnail_folders: bool


    # ------------------------------------------------------------------
    # Thumbnail generation
    # ------------------------------------------------------------------

    # Master switch for thumbnail generation
    generate_thumbnails: bool

    # Enable thumbnails for specific media types
    thumb_images: bool
    thumb_videos: bool

    # Thumbnail output settings
    thumb_size: int
    thumb_suffix: str
    thumb_folder_name: str


    # ------------------------------------------------------------------
    # Metadata extraction
    # ------------------------------------------------------------------

    # Media categories to include during metadata processing
    include_media_types: Dict[str, bool]

    # Metadata fields to extract and include in reports
    metadata_fields: List[str]

    # Metadata sorting options
    # Options: "file_path", "extension", "media_type"
    metadata_sort_by: str
    metadata_sort_reverse: bool


    # ------------------------------------------------------------------
    # Organiser behavior
    # ------------------------------------------------------------------

    # Enable or disable the organiser subsystem entirely
    enable_organiser: bool

    # Organiser mode selection
    # Options: "media_type", "extension", "filename_rule"
    organiser_mode: str

    # Filename-based organiser rules
    # Only used if organiser_mode == "filename_rule"
    # Example rule: {"type": "contains", "value": "SEF"}
    filename_rules: List[Dict]

    # Folder name for files that do not match organiser rules
    default_unsorted_folder: str

    # Whether files should be moved (True) or copied (False)
    move_files: bool


    # ------------------------------------------------------------------
    # Reporting outputs
    # ------------------------------------------------------------------

    # Enable or disable specific report formats
    output_csv: bool
    output_json: bool
    output_excel: bool
    output_tree: bool

    # Output directory for reports
    # None = same folder as input
    report_output_dir: Optional[str]


    # ------------------------------------------------------------------
    # Logging and verbosity
    # ------------------------------------------------------------------

    # Enable verbose console output
    verbose: bool

    # Expand logging output with additional detail
    expand_log: bool
