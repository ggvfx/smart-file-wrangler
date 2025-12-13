"""
utils.py
Shared helper functions for Smart File Wrangler.
"""

from pathlib import Path
import os
import subprocess

def ensure_directory(path):
    """Create the directory if it doesn't exist."""
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

def is_ffmpeg_available():
    """
    Check if ffmpeg or ffprobe is available on the system.

    Returns:
        bool: True if ffmpeg or ffprobe can be run, False otherwise.

    This function tries to run 'ffmpeg -version' and 'ffprobe -version'.
    If either command succeeds, we assume ffmpeg is installed.
    """
    # try ffmpeg first
    try:
        # subprocess.run tries to execute the command
        # capture_output=True prevents it from printing to the console
        # text=True returns output as string
        # check=True raises an error if the command fails
        subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            check=True
        )
        return True  # if this succeeds, ffmpeg is available
    except Exception:
        # if ffmpeg fails, try ffprobe
        try:
            subprocess.run(
                ["ffprobe", "-version"],
                capture_output=True,
                text=True,
                check=True
            )
            return True  # ffprobe available
        except Exception:
            # neither ffmpeg nor ffprobe could be run
            return False
