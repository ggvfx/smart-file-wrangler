"""
pipeline.py

Coordinates high-level Smart File Wrangler workflows.

This module acts as the orchestration layer. It decides which
subsystems run, and in what order, based on configuration flags
defined in config.Defaults.

Responsibilities:
- Optional thumbnail generation
- Optional file organisation (move/copy)
- Optional report generation
- Ensuring subsystems remain decoupled

The pipeline contains no business logic. It only controls
execution order and feature activation.
"""

from pathlib import Path

from .config import Defaults
from .file_scanner import scan_folder
from .utils import group_frame_sequences
from .thumbnailer import (
    generate_thumbnail_for_sequence,
    create_thumbnail,
)
from .organiser import organise_files
from .metadata_reader import extract_metadata
from .report_writer import generate_reports


def run_pipeline(folder_path):
    """
    Run the Smart File Wrangler pipeline on a folder.

    This function executes enabled subsystems in a fixed order:
        1) Thumbnail generation (optional)
        2) File organisation (optional)
        3) Report generation (optional)

    Args:
        folder_path (str | Path): Folder to process.
    """
    folder_path = Path(folder_path)

    # --------------------------------------------------------------
    # Resolve shared pipeline flags
    # --------------------------------------------------------------
    # If organiser runs, subfolder scanning must also be enabled
    organiser_enabled = Defaults.get("enable_organiser", True)
    scan_subfolders = Defaults["recurse_subfolders"] or organiser_enabled

    ignore_thumbnails = Defaults.get("ignore_thumbnail_folders", True)

    # --------------------------------------------------------------
    # 1) Thumbnail generation
    # --------------------------------------------------------------
    if Defaults.get("generate_thumbnails", False):

        # Discover files for thumbnail generation
        files = scan_folder(
            folder_path,
            include_subfolders=scan_subfolders,
            ignore_thumbnails=ignore_thumbnails,
        )

        # Optionally group frame sequences
        if Defaults.get("combine_frame_seq", True):
            items = group_frame_sequences(files)
        else:
            items = files

        # Generate thumbnails
        for item in items:
            # Frame sequence → single representative thumbnail
            if isinstance(item, dict) and "frames" in item:
                generate_thumbnail_for_sequence(item)
            # Normal file → standard thumbnail
            else:
                create_thumbnail(item)

    # --------------------------------------------------------------
    # 2) File organisation
    # --------------------------------------------------------------
    if organiser_enabled:
        organise_files(
            folder_path,
            ignore_thumbnails=ignore_thumbnails,
        )

    # --------------------------------------------------------------
    # 3) Report generation
    # --------------------------------------------------------------
    if (
        Defaults.get("output_csv")
        or Defaults.get("output_json")
        or Defaults.get("output_tree")
        or Defaults.get("output_excel")
    ):
        # Discover files for reporting
        files = scan_folder(
            folder_path,
            include_subfolders=scan_subfolders,
            ignore_thumbnails=ignore_thumbnails,
        )

        # Optionally group frame sequences
        if Defaults.get("combine_frame_seq", True):
            report_items = group_frame_sequences(files)
        else:
            report_items = files

        # Extract metadata for each item
        metadata = []
        for item in report_items:
            metadata.append(extract_metadata(item))

        # Resolve report output directory
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
            excel_enabled=Defaults.get("output_excel"),
            tree_enabled=Defaults.get("output_tree"),
        )


# ----------------------------------------------------------------------
# Manual invocation
# ----------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m smart_file_wrangler.pipeline <folder_path>")
        sys.exit(1)

    run_pipeline(sys.argv[1])
