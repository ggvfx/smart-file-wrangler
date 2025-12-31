"""
pipeline.py

Coordinates high-level Smart File Wrangler workflows.

This module acts as the orchestration layer. It decides which
subsystems run, and in what order, based on configuration flags
defined in the Config object.

Responsibilities:
- Optional thumbnail generation
- Optional file organisation (move/copy)
- Optional report generation
- Ensuring subsystems remain decoupled

The pipeline contains no business logic. It only controls
execution order and feature activation.
"""

from pathlib import Path

from .file_scanner import scan_folder
from .utils import group_frame_sequences
from .thumbnailer import (generate_thumbnail_for_sequence, create_thumbnail)
from .organiser import organise_files
from .metadata_reader import extract_metadata
from .report_writer import generate_reports
from .logger import log


# Internal helper: scans once for a stage, then list is reused by caller. No filtering or behavior assumptions.
def _scan_once(folder_path, config, ignore_thumbnails):
    files = scan_folder(
        folder_path,
        include_subfolders=config.recurse_subfolders,
        file_types=None,
        ignore_thumbnails=ignore_thumbnails,
        config=config,
    )
    return files


def run_pipeline(folder_path, config=None):
    """
    Run the Smart File Wrangler pipeline on a folder.

    Args:
        folder_path (str | Path): Folder to process.
        config (Config): Config object passed by CLI.

    Notes:
        - `folder_path` is converted to a Path internally.
        - `config` must be passed by CLI, not constructed here.
    """

    # --------------------------------------------------------------
    # Validate config
    # --------------------------------------------------------------
    if config is None:
        raise ValueError(
            "run_pipeline() requires a Config object. "
            "CLI must construct and pass Config explicitly."
        )

    folder_path = Path(folder_path)

    # files = physical filesystem entries discovered from disk (Path or sequence dict)
    # items = logical media units created by grouping passes (then optionally wrapped into MediaItem)

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
        log("Starting Thumbnails", level="INFO")
        files = _scan_once(folder_path, config, ignore_thumbnails)
        items = group_frame_sequences(files)

        for item in items:
            if isinstance(item, dict):
                generate_thumbnail_for_sequence(item, config=config)
            else:
                create_thumbnail(item, config=config)

        log("Thumbnails Complete", level="INFO")


    # --------------------------------------------------------------
    # 2) File organisation
    # --------------------------------------------------------------
    if config.enable_organiser:
        log("Starting Organiser", level="INFO")
        # reuse existing items if already scanned, otherwise scan once
        if 'items' not in locals():
            files = _scan_once(folder_path, config, ignore_thumbnails)
            items = group_frame_sequences(files)

        organise_files(folder_path, move_files=config.move_files, ignore_thumbnails=config.ignore_thumbnail_folders, config=config)

        log("Organiser Complete", level="INFO")


    # --------------------------------------------------------------
    # 3) Report generation
    # --------------------------------------------------------------
    if (config.output_csv or config.output_json or config.output_tree or config.output_excel):
        log("Starting Reports", level="INFO")
        # Re-scan AFTER organiser has run so reports see new file locations (behavior preserved)
        files = scan_folder(
            folder_path,
            include_subfolders=scan_subfolders,
            file_types=None,
            ignore_thumbnails=ignore_thumbnails,
            config=config,
        )

        items = group_frame_sequences(files)  # one grouping pass

        # Extract metadata for each item
        metadata = []
        for item in items:
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

        log("Reports Complete", level="INFO")


# ----------------------------------------------------------------------
# Manual invocation
# ----------------------------------------------------------------------

if __name__ == "__main__":
    raise RuntimeError(
        "Manual pipeline invocation is disabled. "
        "Use the CLI to construct and pass a Config object."
    )

