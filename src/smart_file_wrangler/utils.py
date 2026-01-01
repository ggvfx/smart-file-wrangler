"""
utils.py

Shared helper functions for Smart File Wrangler.

This module contains reusable helper functions used across the project.
It provides deterministic, dependency-free utilities for media pipelines.

Responsibilities:
- OS and environment detection (e.g., FFmpeg availability)
- File path helpers (naming, safe folder resolution)
- Small pure functions shared by CLI, GUI, and pipeline
- Contains no feature logic, business rules, or external services
"""

# ----------------------------------------------------------------------
# Standard library imports
# ----------------------------------------------------------------------

from pathlib import Path
import subprocess
import re
from collections import defaultdict

# ----------------------------------------------------------------------
# Local imports
# ----------------------------------------------------------------------

from .config import Config as WranglerConfig


# ----------------------------------------------------------------------
# Media file extension groups
# ----------------------------------------------------------------------
# These lists define known media extensions and are used for basic
# classification and filtering. They are not intended to be exhaustive.

image_extensions = [
    ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".gif",
    ".exr", ".dpx", ".cin", ".tga", ".hdr", ".sgi", ".rgb"
]

video_extensions = [
    ".mp4", ".mov", ".avi", ".mkv", ".flv", ".webm"
]

audio_extensions = [
    ".wav", ".mp3", ".aac", ".flac"
]


# ----------------------------------------------------------------------
# Filesystem helpers
# ----------------------------------------------------------------------

def ensure_directory(path):
    """
    Ensure that a directory exists.

    Args:
        path (str or Path): Directory path to create if it does not exist.

    This function is safe to call multiple times. If the directory already
    exists, no action is taken.
    """
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def get_thumbnail_path(file_path: Path, thumb_folder_name="thumbnails", thumb_suffix="_thumb", thumb_ext=".png") -> Path:
    """
    Generate the output path for a thumbnail corresponding to a media file.

    Args:
        file_path (Path): Path to the original media file.
        thumb_folder_name (str): Folder name where thumbnails are stored.
        thumb_suffix (str): Suffix appended to the original filename stem.
        thumb_ext (str): Extension used for thumbnail files.

    Returns:
        Path: Full path to the thumbnail file.

    Notes:
        - If thumb_folder_name or thumb_suffix is None, values are read from
          config.Defaults.
        - This creates an implicit dependency on Defaults, which is intentional
          but should be kept in mind when reusing this function.
    """
    if thumb_folder_name is None:
        thumb_folder_name = WranglerConfig().include_media_types.get("thumb_folder_name", "thumbnails")
    if thumb_suffix is None:
        thumb_suffix = WranglerConfig().include_media_types.get("thumb_suffix", "_thumb")


    thumb_dir = file_path.parent / thumb_folder_name
    thumb_name = f"{file_path.stem}{thumb_suffix}{thumb_ext}"

    return thumb_dir / thumb_name


# ----------------------------------------------------------------------
# Environment and dependency checks
# ----------------------------------------------------------------------

def is_ffmpeg_available():
    """
    Check whether ffmpeg or ffprobe is available on the system.

    Returns:
        bool: True if either ffmpeg or ffprobe can be executed, False otherwise.

    This function attempts to run 'ffmpeg -version' and 'ffprobe -version'.
    If either command succeeds, the function returns True.

    Any exceptions raised by subprocess execution are caught internally,
    and the function fails safely by returning False.
    """
    for command in ("ffmpeg", "ffprobe"):
        try:
            subprocess.run(
                [command, "-version"],
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except Exception:
            continue

    return False


# ----------------------------------------------------------------------
# Metadata helpers
# ----------------------------------------------------------------------

def filter_metadata(metadata: dict, fields: list = None) -> dict:
    """
    Filter a metadata dictionary to include only specified fields.

    Args:
        metadata (dict): Full metadata dictionary.
        fields (list, optional): List of keys to retain. If None, defaults
            to `Config.metadata_fields` via WranglerConfig().

    Returns:
        dict: Filtered metadata dictionary containing only requested keys.

    Notes:
        - Missing keys are silently ignored.
        - No validation of field names is performed.
        - If fields is None, this function implicitly depends on Defaults.
    """
    if fields is None:
        fields = WranglerConfig().metadata_fields

    return {key: value for key, value in metadata.items() if key in fields}


# ----------------------------------------------------------------------
# Frame sequence detection
# ----------------------------------------------------------------------

def detect_frame_sequences(files, min_sequence_length=2):
    """
    Detect frame sequences in a list of file paths.
    physical discovery + sequence grouping, returns legacy types for pipeline


    Args:
        files (list[Path or str]): List of file paths to analyse.
        min_sequence_length (int): Minimum number of frames required to
            consider a group a sequence.

    Returns:
        list: A mixed list containing:
            - dicts describing detected frame sequences (logical media units)
            - Path objects for standalone files

    Sequence dictionary format:
        {
            "basename": str,
            "frames": list[int],
            "ext": str,
            "folder": Path,
            "separator": str
        }

    Notes:
        - Files that do not match a frame pattern are returned as Path objects.
        - Short sequences (below min_sequence_length) are flattened back into
          standalone files.
        - This function performs grouping, validation, and output assembly
          in one pass for simplicity.
    """
    sequences = defaultdict(lambda: {
        "frames": [],
        "ext": None,
        "folder": None,
        "separator": None,
    })

    standalone_files = []

    # Regex captures:
    #   base name, frame number, extension
    # Allows separators like '.', '_', or '-'
    pattern = re.compile(r"(.+?)[._-](\d+)(\.[^.]+)$")

    for file_path in files:
        path = Path(file_path)
        match = pattern.match(path.name)

        if match:
            base, frame_str, ext = match.groups()
            separator = path.name[len(base)]
            frame_num = int(frame_str)

            key = (path.parent, base, ext)
            sequences[key]["frames"].append(frame_num)
            sequences[key]["ext"] = ext
            sequences[key]["folder"] = path.parent
            sequences[key]["separator"] = separator
        else:
            standalone_files.append(path)

    result = []

    for (folder, base, ext), seq in sequences.items():
        frames = sorted(seq["frames"])

        if len(frames) >= min_sequence_length:
            result.append({
                "basename": base,
                "frames": frames,
                "ext": ext,
                "folder": folder,
                "separator": seq.get("separator", "."),
            })
        else:
            # Treat short sequences as individual files
            for frame in frames:
                sep_match = re.search(
                    r"(.+?)([._-])\d+(\.[^.]+)$",
                    str(folder / f"{base}{ext}")
                )

                if sep_match:
                    separator = sep_match.group(2)
                else:
                    separator = "."
                    # NOTE: This print is intentionally left as-is.
                    # It should eventually be replaced by logger.py.
                    print(
                        f"Warning: could not detect separator for frame sequence "
                        f"'{base}' in folder '{folder}', defaulting to '{separator}'."
                    )

                filename = folder / f"{base}{separator}{frame}{ext}"
                standalone_files.append(filename)

    return result + standalone_files


def group_frame_sequences(files, min_sequence_length=2):
    """
    Alias for detect_frame_sequences.

    This wrapper exists to preserve naming compatibility with organiser.py
    and other modules that expect this function name.
    """
    return detect_frame_sequences(
        files,
        min_sequence_length=min_sequence_length
    )
