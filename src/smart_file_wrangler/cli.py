"""
cli.py
Command-line interface for Smart File Wrangler.
Parses arguments and delegates tasks to core modules.
"""

import argparse
from smart_file_wrangler import main, file_scanner, organiser, report_writer, logger, thumbnailer

def parse_args():
    """Define and parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Smart File Wrangler - Organize your media files easily."
    )
    
    parser.add_argument(
        "-i", "--input",
        type=str,
        required=True,
        help="Path to the input folder containing media files."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="output",
        help="Path to the output folder where files will be organized."
    )
    parser.add_argument(
        "--subfolders",
        action="store_true",
        help="Include subfolders in scanning."
    )
    parser.add_argument(
        "--move",
        action="store_true",
        help="Move files instead of copying them."
    )
    parser.add_argument(
        "--thumbnails",
        action="store_true",
        help="Generate thumbnails for images and videos."
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging."
    )
    parser.add_argument(
        "--report-format",
        choices=["csv", "json", "both"],
        default="csv",
        help="Output format for report files."
    )

    return parser.parse_args()


def run_cli():
    """Main CLI runner."""
    args = parse_args()
    
    # Initialize logger
    log = logger.Logger(verbose=args.verbose)
    log.log("Starting Smart File Wrangler in CLI mode...")
    
    # TODO: Implement workflow
    # Example:
    # files = file_scanner.scan_folder(args.input, include_subfolders=args.subfolders)
    # organiser.organise_files(files, args.output, move_files=args.move)
    # if args.thumbnails:
    #     thumbnailer.create_thumbnail(...) 
    # report_writer.write_csv_report(...) or write_json_report(...)

    log.log("Processing complete.")


if __name__ == "__main__":
    run_cli()
