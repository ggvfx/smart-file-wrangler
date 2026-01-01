"""
main.py

Entry point for Smart File Wrangler.

Determines whether to run CLI or GUI, and manages modular workflows:
- Full workflow
- Report only
- Thumbnails only
"""

from smart_file_wrangler import cli, gui
import sys

def main():
    """
    If CLI arguments are provided, run the terminal workflow.
    Otherwise, start the PySide GUI application.
    """
    if len(sys.argv) > 1:
        # CLI mode
        cli.run_cli()
    else:
        # GUI mode
        gui.run_gui()

if __name__ == "__main__":
    main()
