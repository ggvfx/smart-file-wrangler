"""
cli.py

Command-line interface for Smart File Wrangler.

This CLI is intentionally thin. It is responsible only for:
- Parsing command-line arguments
- Constructing a Config object from defaults and CLI overrides
- Invoking the pipeline

All business logic remains in pipeline and subsystem modules.
"""

import argparse
from pathlib import Path

from .config import Config
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
    parser.add_argument(
        "--organise-by",
        choices=["media_type", "extension", "string_rule"],
        default=None,
        help="Organisation mode: media_type, extension, or string_rule"
    )
    parser.add_argument(
        "--contains",
        action="append",
        default=[],
        help="Organise files whose names contain this string (can be repeated)"
    )

    parser.add_argument(
        "--starts-with",
        action="append",
        default=[],
        help="Organise files whose names start with this string (can be repeated)"
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
    Command-line entry point for Smart File Wrangler.

    Responsibilities (thin orchestration only):
    - Parses command line arguments
    - Constructs a Config object using its internal defaults
    - Applies CLI overrides into Config
    - Invokes the pipeline exactly once

    Notes:
        - The legacy `Defaults` dictionary has been removed from runtime use.
        - This module does not contain business logic.
        - Public pipeline behavior is preserved.
    """
    args = parse_args()

    # Initialise logging early
    init_logger(verbose=args.verbose)

    input_folder = Path(args.input)
    if not input_folder.exists() or not input_folder.is_dir():
        raise ValueError(f"Input folder not found: {input_folder}")

    # --------------------------------------------------------------
    # Construct Config instance (internal defaults only, no Defaults dict)
    # --------------------------------------------------------------
    config = Config()

    # Core scanning
    config.recurse_subfolders = args.subfolders

    # Logging
    config.verbose = args.verbose

    # Organiser
    config.enable_organiser = args.organise or args.move
    config.move_files = args.move
    # --------------------------------------------------------------
    # Organiser configuration
    # --------------------------------------------------------------
    if args.organise_by:
        config.organiser_mode = args.organise_by

    # Build filename rules only if needed
    rules = []

    for value in args.contains:
        rules.append({
            "type": "contains",
            "value": value,
        })

    for value in args.starts_with:
        rules.append({
            "type": "starts_with",
            "value": value,
        })

    if rules:
        config.filename_rules = rules

    # Thumbnails
    config.generate_thumbnails = args.thumbnails
    config.thumb_size = args.thumb_size

    # Reporting
    config.output_csv = False
    config.output_json = False
    config.output_excel = False
    config.output_tree = args.folder_tree

    if args.report_format == "csv":
        config.output_csv = True
    elif args.report_format == "json":
        config.output_json = True
    elif args.report_format == "excel":
        config.output_excel = True
    elif args.report_format == "all":
        config.output_csv = True
        config.output_json = True
        config.output_excel = True

    config.report_output_dir = (
        str(Path(args.output)) if args.output else None
    )

    # --------------------------------------------------------------
    # Workflow shortcuts (mutually exclusive)
    # --------------------------------------------------------------
    if args.report_only and args.thumbnails_only:
        raise ValueError(
            "Choose only one: --report-only OR --thumbnails-only"
        )

    if args.report_only:
        config.enable_organiser = False
        config.generate_thumbnails = False

    if args.thumbnails_only:
        config.enable_organiser = False
        config.generate_thumbnails = True

        config.output_csv = False
        config.output_json = False
        config.output_excel = False
        config.output_tree = False

    # --------------------------------------------------------------
    # Run pipeline
    # --------------------------------------------------------------
    print("Running Smart File Wrangler...")
    run_pipeline(input_folder, config)
    print("Done.")


if __name__ == "__main__":
    run_cli()
