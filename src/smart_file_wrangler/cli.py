"""
cli.py

Command-line interface for Smart File Wrangler.

This CLI is intentionally thin. It is responsible only for:
- Parsing command-line arguments
- Overriding config.Defaults
- Invoking the pipeline

All business logic remains in pipeline and subsystem modules.
"""

import argparse
from pathlib import Path

from .config import Config, Defaults
from .pipeline import run_pipeline
from .logger import init_logger


# ----------------------------------------------------------------------
# Argument parsing
# ----------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Smart File Wrangler - Modular media automation tool."
    )

    # --------------------------------------------------------------
    # Core paths
    # --------------------------------------------------------------
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Input folder to process"
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output folder for reports (default: input folder)"
    )

    # --------------------------------------------------------------
    # Organiser options
    # --------------------------------------------------------------
    parser.add_argument(
        "--organise",
        action="store_true",
        help="Organise files (copy unless --move is set)"
    )
    parser.add_argument(
        "--move",
        action="store_true",
        help="Move files instead of copying (implies --organise)"
    )

    # --------------------------------------------------------------
    # Scanning options
    # --------------------------------------------------------------
    parser.add_argument(
        "--subfolders",
        action="store_true",
        help="Include subfolders when scanning"
    )

    # --------------------------------------------------------------
    # Reporting options
    # --------------------------------------------------------------
    parser.add_argument(
        "--report-format",
        choices=["csv", "json", "excel", "all", "none"],
        default="csv",
        help="Report output format"
    )
    parser.add_argument(
        "--folder-tree",
        action="store_true",
        help="Output a text-based folder tree"
    )

    # --------------------------------------------------------------
    # Thumbnail options
    # --------------------------------------------------------------
    parser.add_argument(
        "--thumbnails",
        action="store_true",
        help="Generate thumbnails"
    )
    parser.add_argument(
        "--thumb-size",
        type=int,
        default=512,
        help="Thumbnail size in pixels"
    )

    # --------------------------------------------------------------
    # Logging
    # --------------------------------------------------------------
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose logging"
    )

    # --------------------------------------------------------------
    # Workflow shortcuts
    # --------------------------------------------------------------
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Run only report generation"
    )
    parser.add_argument(
        "--thumbnails-only",
        action="store_true",
        help="Run only thumbnail generation"
    )

    return parser.parse_args()


# ----------------------------------------------------------------------
# CLI execution
# ----------------------------------------------------------------------

def run_cli():
    """
    Entry point for the Smart File Wrangler CLI.

    This function:
    - Validates arguments
    - Overrides config.Defaults
    - Runs the pipeline
    """
    args = parse_args()

    # Initialise logging early
    init_logger(verbose=Defaults["verbose"])

    input_folder = Path(args.input)
    if not input_folder.exists() or not input_folder.is_dir():
        raise ValueError(f"Input folder not found: {input_folder}")

    # --------------------------------------------------------------
    # Apply CLI overrides to Defaults
    # --------------------------------------------------------------

    # Logging and scanning
    verbose = bool(args.verbose)
    recurse_subfolders = bool(args.subfolders)

    # --------------------------------------------------------------
    # Organiser settings
    # --------------------------------------------------------------
    enable_organiser = bool(args.organise or args.move)
    move_files = bool(args.move)

    # --------------------------------------------------------------
    # Thumbnail settings
    # --------------------------------------------------------------
    generate_thumbnails = bool(args.thumbnails)

    # --------------------------------------------------------------
    # Report settings (reset first)
    # --------------------------------------------------------------
    output_csv = False
    output_json = False
    output_excel = False
    output_tree = False


    if args.report_format == "csv":
        output_csv = True
    elif args.report_format == "json":
        output_json = True
    elif args.report_format == "excel":
        output_excel = True
    elif args.report_format == "all":
        output_csv = True
        output_json = True
        output_excel = True
    elif args.report_format == "none":
        pass

    output_tree = bool(args.folder_tree)

    # Report output directory (None means input folder)
    report_output_dir=str(Path(args.output)) if args.output else None

    # --------------------------------------------------------------
    # Workflow shortcuts (mutually exclusive)
    # --------------------------------------------------------------
    if args.report_only and args.thumbnails_only:
        raise ValueError(
            "Choose only one: --report-only OR --thumbnails-only"
        )

    if args.report_only:
        enable_organiser = False
        generate_thumbnails = False

    if args.thumbnails_only:
        enable_organiser = False
        generate_thumbnails = True

        output_csv = False
        output_json = False
        output_excel = False
        output_tree = False

    # --------------------------------------------------------------
    # Create Config instance
    # --------------------------------------------------------------
    config = Config(

    recurse_subfolders=bool(args.subfolders),
    file_types=Defaults["file_types"],
    combine_frame_seq=Defaults["combine_frame_seq"],
    ignore_thumbnail_folders=Defaults["ignore_thumbnail_folders"],

    generate_thumbnails=generate_thumbnails,
    thumb_images=Defaults["thumb_images"],
    thumb_videos=Defaults["thumb_videos"],
    thumb_size=int(args.thumb_size),
    thumb_suffix=Defaults["thumb_suffix"],
    thumb_folder_name=Defaults["thumb_folder_name"],

    include_media_types=Defaults["include_media_types"],
    metadata_fields=Defaults["metadata_fields"],
    metadata_sort_by=Defaults["metadata_sort_by"],
    metadata_sort_reverse=Defaults["metadata_sort_reverse"],

    enable_organiser=enable_organiser,
    organiser_mode=Defaults["organiser_mode"],
    filename_rules=Defaults["filename_rules"],
    default_unsorted_folder=Defaults["default_unsorted_folder"],
    move_files=move_files,

    output_csv=output_csv,
    output_json=output_json,
    output_excel=output_excel,
    output_tree=output_tree,
    report_output_dir=str(Path(args.output)) if args.output else None,

    verbose=bool(args.verbose),
    expand_log=Defaults["expand_log"],
)


    # --------------------------------------------------------------
    # Run pipeline
    # --------------------------------------------------------------
    print("Running Smart File Wrangler...")
    run_pipeline(input_folder, config)
    print("Done.")


if __name__ == "__main__":
    run_cli()
