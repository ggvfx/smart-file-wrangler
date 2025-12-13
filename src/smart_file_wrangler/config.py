"""
config.py
Holds default settings and shared configuration structures.
"""

Defaults = {
    "recurse_subfolders": True,
    "file_types": ["mp4", "png", "wav", "jpg"],
    "generate_thumbnails": False,
    "thumb_images": True,
    "thumb_videos": True,
    "thumb_size": 512,
    "thumb_suffix": "_thumb",
    "thumb_folder_name": "thumbnails",
    "move_files": False,
    "verbose": False,
    "expand_log": False,
    "output_csv": True,
    "output_json": False,
    "output_text": False,
    "metadata_sort_by": "name",
    "include_media_types": {
        "image": True,
        "video": True,
        "audio": True,
        "other": True
    },
    "metadata_fields": [
        "file_path",
        "file_size_bytes",
        "media_type",
        "extension",
        "resolution_px",
        "duration_seconds",
        "mode",
        "format",
    ],
    # Organiser-specific defaults
    "organiser_mode": "media_type",  # Options: "media_type", "extension", "filename_rule"
    "filename_rules": [              # Only used if organiser_mode == "filename_rule"
    # Example: {"type": "contains", "value": "SEF"}
    ],
    "default_unsorted_folder": "unsorted",  # Folder for unmatched files

}
