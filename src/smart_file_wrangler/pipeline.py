"""
pipeline.py
Coordinates high-level Smart File Wrangler workflows.

This module acts as the orchestration layer that decides which
subsystems run, based on configuration flags in config.Defaults.

Responsibilities:
- Runs the organiser (file moving/copying) when enabled
- Runs thumbnail generation when enabled
- Ensures organiser, thumbnailer, and reporting systems remain
  fully decoupled and modular
- Provides a single entry point for end-to-end processing

The pipeline itself contains no business logic; it only controls
execution order and feature activation.
"""


from pathlib import Path
from .config import Defaults
from .organiser import organise_files
from .file_scanner import scan_folder
from .utils import group_frame_sequences
from .thumbnailer import generate_thumbnail_for_sequence, create_thumbnail


def run_pipeline(folder_path):
    folder_path = Path(folder_path)

    #Organiser
    if Defaults.get("enable_organiser", True):
        organise_files(folder_path)

    # Thumbnails
    if Defaults.get("generate_thumbnails", False):

        files = scan_folder(folder_path, include_subfolders=Defaults["recurse_subfolders"])

        sequence_items = []
        sequence_files = set()

        if Defaults.get("combine_frame_seq", True):
            items = group_frame_sequences(files)

            for item in items:
                if isinstance(item, dict) and "frames" in item:
                    sequence_items.append(item)

                    separator = item.get("separator", ".")
                    for frame in item["frames"]:
                        frame_file = item["folder"] / f"{item['basename']}{separator}{frame}{item['ext']}"
                        sequence_files.add(frame_file.resolve())

        # thumbnail regular files (excluding sequence frames)
        for file_path in files:
            if file_path.resolve() in sequence_files:
                continue
            create_thumbnail(file_path)

        # thumbnail frame sequences (single middle frame only)
        for sequence in sequence_items:
            generate_thumbnail_for_sequence(sequence)



if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m smart_file_wrangler.pipeline <folder_path>")
        sys.exit(1)

    run_pipeline(sys.argv[1])

