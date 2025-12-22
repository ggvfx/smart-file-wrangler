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

from .config import Config
from .file_scanner import scan_folder
from .utils import group_frame_sequences
from .thumbnailer import (
    generate_thumbnail_for_sequence,
    create_thumbnail,
)
from .organiser import organise_files
from .metadata_reader import extract_metadata
from .report_writer import generate_reports


def run_pipeline(folder_path, config=None):
    """
    Run the Smart File Wrangler pipeline on a folder.

    This function executes enabled subsystems in a fixed order:
        1) Thumbnail generation (optional)
        2) File organisation (optional)
        3) Report generation (optional)

    Args:
        folder_path (str | Path): Folder to process.
    """
    # --------------------------------------------------------------
    # Build a config if one not provided
    # --------------------------------------------------------------
    if config is None:
        config = Config(
            recurse_subfolders=Defaults["recurse_subfolders"],
            file_types=Defaults["file_types"],
            combine_frame_seq=Defaults["combine_frame_seq"],
            ignore_thumbnail_folders=Defaults["ignore_thumbnail_folders"],

            generate_thumbnails=Defaults["generate_thumbnails"],
            thumb_images=Defaults["thumb_images"],
            thumb_videos=Defaults["thumb_videos"],
            thumb_size=Defaults["thumb_size"],
            thumb_suffix=Defaults["thumb_suffix"],
            thumb_folder_name=Defaults["thumb_folder_name"],

            include_media_types=Defaults["include_media_types"],
            metadata_fields=Defaults["metadata_fields"],
            metadata_sort_by=Defaults["metadata_sort_by"],
            metadata_sort_reverse=Defaults["metadata_sort_reverse"],

            enable_organiser=Defaults["enable_organiser"],
            organiser_mode=Defaults["organiser_mode"],
            filename_rules=Defaults["filename_rules"],
            default_unsorted_folder=Defaults["default_unsorted_folder"],
            move_files=Defaults["move_files"],

            output_csv=Defaults["output_csv"],
            output_json=Defaults["output_json"],
            output_excel=Defaults["output_excel"],
            output_tree=Defaults["output_tree"],
            report_output_dir=Defaults["report_output_dir"],

            verbose=Defaults["verbose"],
            expand_log=Defaults["expand_log"],
        )


    folder_path = Path(folder_path)

    # --------------------------------------------------------------
    # Resolve shared pipeline flags
    # --------------------------------------------------------------
    # If organiser runs, subfolder scanning must also be enabled
    organiser_enabled = config.enable_organiser
    scan_subfolders = config.recurse_subfolders or organiser_enabled

    ignore_thumbnails = config.ignore_thumbnail_folders

    # --------------------------------------------------------------
    # 1) Thumbnail generation
    # --------------------------------------------------------------
    if config.generate_thumbnails:

        # Discover files for thumbnail generation
        files = scan_folder(
            folder_path,
            include_subfolders=scan_subfolders,
            ignore_thumbnails=ignore_thumbnails,
        )

        # Optionally group frame sequences
        if config.combine_frame_seq:
            items = group_frame_sequences(files)
        else:
            items = files

        # Generate thumbnails
        for item in items:
            # Frame sequence → single representative thumbnail
            if isinstance(item, dict) and "frames" in item:
                generate_thumbnail_for_sequence(item, config=config)
            # Normal file → standard thumbnail
            else:
                create_thumbnail(item, config=config)

    # --------------------------------------------------------------
    # 2) File organisation
    # --------------------------------------------------------------
    if config.enable_organiser:
        organise_files(
            folder_path,
            move_files=config.move_files,
            ignore_thumbnails=config.ignore_thumbnail_folders,
            config=config,
        )



    # --------------------------------------------------------------
    # 3) Report generation
    # --------------------------------------------------------------
    if (
        config.output_csv
        or config.output_json
        or config.output_tree
        or config.output_excel
    ):
        # Discover files for reporting
        files = scan_folder(
            folder_path,
            include_subfolders=scan_subfolders,
            ignore_thumbnails=ignore_thumbnails,
        )

        # Optionally group frame sequences
        if config.combine_frame_seq:
            report_items = group_frame_sequences(files)
        else:
            report_items = files

        # Extract metadata for each item
        metadata = []
        for item in report_items:
            metadata.append(extract_metadata(item))

        # Resolve report output directory
        output_dir = config.report_output_dir or folder_path

        generate_reports(
            metadata=metadata,
            input_folder=folder_path,
            output_dir=output_dir,
            fields=config.metadata_fields,
            sort_by=config.metadata_sort_by,
            reverse=config.metadata_sort_reverse,
            csv_enabled=config.output_csv,
            json_enabled=config.output_json,
            excel_enabled=config.output_excel,
            tree_enabled=config.output_tree,
            config=config,
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
