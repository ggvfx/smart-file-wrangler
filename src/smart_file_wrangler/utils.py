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
        subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
        return True  # if this succeeds, ffmpeg is available
    
    except Exception:
        # if ffmpeg fails, try ffprobe
        try:
            subprocess.run(["ffprobe", "-version"], capture_output=True, text=True, check=True)
            return True  # ffprobe available
        except Exception:
            # neither ffmpeg nor ffprobe could be run
            return False
        

# lists of supported file extensions
image_extensions = [".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".gif",".exr", ".dpx", ".cin", ".tga", ".hdr", ".sgi", ".rgb"]

video_extensions = [".mp4", ".mov", ".avi", ".mkv"]

audio_extensions = [".wav", ".mp3", ".aac", ".flac"]


def get_thumbnail_path(file_path: Path, thumb_folder_name="thumbnails", thumb_suffix="_thumb", thumb_ext=".png") -> Path:
    """
    Generate the path for a thumbnail based on the original file.

    Parameters:
        file_path (Path): Original file path
        thumb_folder_name (str): Folder name where thumbnails will be stored
        thumb_suffix (str): Suffix to append to the file stem
        thumb_ext (str): Extension for the thumbnail file

    Returns:
        Path: Full path to the thumbnail
    """
    thumb_dir = file_path.parent / thumb_folder_name
    thumb_dir.mkdir(parents=True, exist_ok=True)
    thumb_name = f"{file_path.stem}{thumb_suffix}{thumb_ext}"
    return thumb_dir / thumb_name
