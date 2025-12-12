"""
cli.py
Command-line interface for Smart File Wrangler.
Now supports:
- Recursive subfolder processing
- Organising by type or user string rules
- Optional CSV/JSON report only
- Optional text output of folder tree
- Thumbnail options (size, orientation, frame selection, codec)
Supports modular workflows:
- Full workflow: scan → organise → report → thumbnails
- Report only (CSV/JSON/folder tree)
- Thumbnails only (images and/or videos)
"""

import argparse
from smart_file_wrangler import file_scanner, organiser, report_writer, thumbnailer, logger

def parse_args():
    parser = argparse.ArgumentParser(description="Smart File Wrangler - Modular media automation tool.")
    
    parser.add_argument("-i", "--input", type=str, required=True, help="Input folder")
    parser.add_argument("-o", "--output", type=str, default="output", help="Output folder")
    parser.add_argument("--subfolders", action="store_true", help="Include subfolders")
    parser.add_argument("--move", action="store_true", help="Move files instead of copying")
    parser.add_argument("--report-format", choices=["csv", "json", "both"], default="csv", help="Report format")
    parser.add_argument("--folder-tree", action="store_true", help="Output text folder tree")
    parser.add_argument("--thumbnails", action="store_true", help="Generate thumbnails")
    parser.add_argument("--thumb-size", type=int, default=256, help="Thumbnail size in pixels")
    parser.add_argument("--thumb-orientation", choices=["horizontal", "vertical"], default="horizontal")
    parser.add_argument("--video-frame", type=int, default=24, help="Video frame number for thumbnail")
    parser.add_argument("--video-codec", choices=["mp4", "mov"], default="mp4")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    # Optional modular flags
    parser.add_argument("--report-only", action="store_true", help="Run only report generation")
    parser.add_argument("--thumbnails-only", action="store_true", help="Run only thumbnails generation")
    
    # TODO: add arguments for user-defined sorting rules
    
    return parser.parse_args()

def run_cli():
    args = parse_args()
    log = logger.Logger(verbose=args.verbose)
    log.log("Starting Smart File Wrangler CLI")

    # Modular workflow
    if args.thumbnails_only:
        log.log("Running thumbnails only")
        # TODO: call thumbnailer on input folder
    elif args.report_only:
        log.log("Running report only")
        # TODO: call report_writer functions on input folder
    else:
        log.log("Running full workflow")
        # TODO: scan → organise → report → thumbnails


    log.log("Processing complete.")


if __name__ == "__main__":
    run_cli()
