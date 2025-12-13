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
    ]
}
