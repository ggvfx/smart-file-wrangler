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
from .metadata_reader import extract_metadata
from .report_writer import generate_reports



def run_pipeline(folder_path):
    folder_path = Path(folder_path)

    #Organiser
    if Defaults.get("enable_organiser", True):
        organise_files(folder_path)

    #Thumbnails
    if Defaults.get("generate_thumbnails", False):

        files = scan_folder(folder_path, include_subfolders=Defaults["recurse_subfolders"])

        if Defaults.get("combine_frame_seq", True):
            items = group_frame_sequences(files)
        else:
            items = files

        for item in items:
            # frame sequence → single thumbnail
            if isinstance(item, dict) and "frames" in item:
                generate_thumbnail_for_sequence(item)

            # normal file → normal thumbnail
            else:
                create_thumbnail(item)


    #Reports
    if Defaults.get("output_csv") or Defaults.get("output_json") or Defaults.get("output_tree"):

        files = scan_folder(folder_path, include_subfolders=Defaults["recurse_subfolders"])

        if Defaults.get("combine_frame_seq", True):
            report_items = group_frame_sequences(files)
        else:
            report_items = files

        metadata = []
        for item in report_items:
            metadata.append(extract_metadata(item))

        output_dir = Defaults["report_output_dir"] or folder_path

        generate_reports(
            metadata=metadata,
            input_folder=folder_path,
            output_dir=output_dir,
            fields=Defaults["metadata_fields"],
            sort_by=Defaults.get("metadata_sort_by"),
            reverse=Defaults.get("metadata_sort_reverse", False),
            csv_enabled=Defaults.get("output_csv"),
            json_enabled=Defaults.get("output_json"),
            tree_enabled=Defaults.get("output_tree"),
        )




if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m smart_file_wrangler.pipeline <folder_path>")
        sys.exit(1)

    run_pipeline(sys.argv[1])

