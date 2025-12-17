
"""
cli.py
Command-line interface for Smart File Wrangler.

This CLI is a thin wrapper around pipeline.run_pipeline().
It only:
- parses command line flags
- overrides config.Defaults
- runs the pipeline

(So organiser/thumbnail/report logic stays in their own modules.)
"""

import argparse
from pathlib import Path

from .config import Defaults
from .pipeline import run_pipeline
from .logger import init_logger


def parse_args():
    parser = argparse.ArgumentParser(
        description="Smart File Wrangler - Modular media automation tool."
    )

    parser.add_argument("-i", "--input", required=True, help="Input folder")
    parser.add_argument("-o", "--output", default=None, help="Output folder for reports (default: input folder)")

    parser.add_argument("--organise", action="store_true", help="Organise files (copy unless --move is set)")

    parser.add_argument("--subfolders", action="store_true", help="Include subfolders")
    parser.add_argument("--move", action="store_true", help="Move files instead of copying (enables organiser)")

    parser.add_argument("--report-format", choices=["csv", "json", "excel", "all", "none"], default="csv")
    parser.add_argument("--folder-tree", action="store_true", help="Output text folder tree")

    parser.add_argument("--thumbnails", action="store_true", help="Generate thumbnails")
    parser.add_argument("--thumb-size", type=int, default=512, help="Thumbnail size in pixels")

    parser.add_argument("--verbose", action="store_true", help="Verbose logging")

    # Modular shortcuts
    parser.add_argument("--report-only", action="store_true", help="Run only report generation")
    parser.add_argument("--thumbnails-only", action="store_true", help="Run only thumbnails generation")

    return parser.parse_args()


def run_cli():
    init_logger(verbose=Defaults["verbose"])
    args = parse_args()

    input_folder = Path(args.input)
    if not input_folder.exists() or not input_folder.is_dir():
        raise ValueError(f"Input folder not found: {input_folder}")

    # ---- override Defaults from CLI flags ----
    Defaults["verbose"] = bool(args.verbose)
    Defaults["recurse_subfolders"] = bool(args.subfolders)

    # organiser
    Defaults["enable_organiser"] = bool(args.organise or args.move)
    Defaults["move_files"] = bool(args.move)


    # thumbnails
    Defaults["generate_thumbnails"] = bool(args.thumbnails)
    Defaults["thumb_size"] = int(args.thumb_size)

    # reports (defaults)
    Defaults["output_csv"] = False
    Defaults["output_json"] = False
    Defaults["output_excel"] = False
    Defaults["output_tree"] = False

    # report format flag
    if args.report_format == "csv":
        Defaults["output_csv"] = True
    elif args.report_format == "json":
        Defaults["output_json"] = True
    elif args.report_format == "excel":
        Defaults["output_excel"] = True
    elif args.report_format == "all":
        Defaults["output_csv"] = True
        Defaults["output_json"] = True
        Defaults["output_excel"] = True
    elif args.report_format == "none":
        pass

    # folder tree is separate toggle
    Defaults["output_tree"] = bool(args.folder_tree)

    # report output directory (None means “use input folder”)
    Defaults["report_output_dir"] = str(Path(args.output)) if args.output else None

    if args.report_only and args.thumbnails_only:
        raise ValueError("Choose only one: --report-only OR --thumbnails-only")

    # modular shortcuts
    if args.report_only:
        Defaults["enable_organiser"] = False
        Defaults["generate_thumbnails"] = False

    if args.thumbnails_only:
        Defaults["enable_organiser"] = False

        Defaults["generate_thumbnails"] = True

        Defaults["output_csv"] = False
        Defaults["output_json"] = False
        Defaults["output_excel"] = False
        Defaults["output_tree"] = False

    # ---- run ----
    print("Running Smart File Wrangler...")
    run_pipeline(input_folder)
    print("Done.")


if __name__ == "__main__":
    run_cli()

