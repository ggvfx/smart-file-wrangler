"""
config.py
Holds default settings and shared configuration structures.
"""

Defaults = {
    "recurse_subfolders": True,
    "file_types": ["mp4", "png", "wav", "jpg"],
    "combine_frame_seq" : True,
    "generate_thumbnails": False,
    "enable_organiser": False,
    "thumb_images": True,
    "thumb_videos": True,
    "thumb_size": 512,
    "thumb_suffix": "_thumb",
    "thumb_folder_name": "thumbnails",
    "move_files": False,
    "verbose": True,
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
        "file_size_mb",
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
    # Organiser-specific defaults
    "organiser_mode": "media_type",  # Options: "media_type", "extension", "filename_rule"
    "filename_rules": [              # Only used if organiser_mode == "filename_rule"
    # Example: {"type": "contains", "value": "SEF"}
    ],
    "default_unsorted_folder": "unsorted",  # Folder for unmatched files
    # Reporting
    "output_csv": True,
    "output_json": False,
    "output_tree": False,

    "report_output_dir": None,  # None = same folder as input

    # Sorting
    "metadata_sort_by": "file_path",   # options: file_path, extension, media_type
    "metadata_sort_reverse": False,

}
