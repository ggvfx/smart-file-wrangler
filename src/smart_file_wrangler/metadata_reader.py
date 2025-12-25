"""
metadata_reader.py

Extracts raw metadata from files and frame sequences.

This module is responsible only for reading metadata from files.
It does not format, filter, sort, or output metadata for reports.
"""

from pathlib import Path
import subprocess
import json

from PIL import Image

from .utils import (
    is_ffmpeg_available,
    image_extensions,
    video_extensions,
    audio_extensions,
)
from .file_scanner import scan_folder
from .config import Config
from .media_item import MediaItem


# ----------------------------------------------------------------------
# Internal helpers
# ----------------------------------------------------------------------

def _populate_ffprobe_metadata(file_path, metadata):
    """
    Populate metadata fields using ffprobe for audio/video files.

    This helper mutates the metadata dictionary in place.
    If ffprobe fails for any reason, metadata is left unchanged.

    Fields that may be populated:
        - resolution_px
        - duration_seconds
        - sample_rate_hz
    """
    command = [
        "ffprobe",
        "-v", "error",
        "-print_format", "json",
        "-show_streams",
        "-show_format",
        str(file_path),
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
    except Exception:
        # Fail silently and leave metadata unchanged
        return

    for stream in data.get("streams", []):
        if "width" in stream and "height" in stream:
            try:
                width = int(stream["width"])
                height = int(stream["height"])
                metadata["resolution_px"] = f"{width}x{height}"
            except Exception:
                pass

        if "duration" in stream and metadata["duration_seconds"] is None:
            try:
                metadata["duration_seconds"] = float(stream["duration"])
            except Exception:
                pass

        if "sample_rate" in stream and metadata["sample_rate_hz"] is None:
            try:
                metadata["sample_rate_hz"] = int(stream["sample_rate"])
            except Exception:
                pass


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------

def extract_metadata(file_path):
    """
    Extract raw metadata for a single file or frame sequence.

    Args:
        file_path (Path | dict | MediaItem):
            - Path: a normal file on disk
            - dict: a frame sequence dictionary produced by utils.detect_frame_sequences
            - MediaItem: internal wrapper for either a file or sequence
    ...
    """

    # --- MediaItem unwrapping (behavior-safe) ---
    if isinstance(file_path, MediaItem):
        if file_path.kind == "sequence":
            file_path = file_path.sequence_info
        else:
            file_path = file_path.path

    # ------------------------------------------------------------------
    # 1) FRAME SEQUENCES
    # ------------------------------------------------------------------
    # Frame sequences are passed in as dictionaries with frame information.
    # These are treated as a single logical media item.
    if isinstance(file_path, dict) and "frames" in file_path:

        frames = file_path["frames"]
        folder = file_path["folder"]
        basename = file_path["basename"]
        extension = file_path["ext"]
        separator = file_path.get("separator", ".")

        total_bytes = 0

        for frame in frames:
            frame_path = folder / f"{basename}{separator}{frame}{extension}"
            if frame_path.exists():
                total_bytes += frame_path.stat().st_size

        start_frame = frames[0]
        end_frame = frames[-1]
        middle_frame = frames[len(frames) // 2]

        resolution_px = None
        middle_frame_path = folder / f"{basename}{separator}{middle_frame}{extension}"

        if middle_frame_path.exists():
            try:
                with Image.open(middle_frame_path) as image:
                    resolution_px = f"{image.width}x{image.height}"
            except Exception:
                pass

        # Construct a display-style sequence name once
        sequence_name = f"{basename}.[{start_frame}-{end_frame}]{extension}"
        sequence_path = folder / sequence_name

        metadata = {
            "filename": sequence_name,
            "file_path": str(sequence_path),
            "file_size_bytes": total_bytes,
            "media_type": "video",
            "extension": extension,
            "resolution_px": resolution_px,
            "duration_seconds": None,
            "sample_rate_hz": None,
            "mode": None,
            "format": None,
            "frame_count": len(frames),
            "middle_frame_number": middle_frame,
            "start_frame": start_frame,
            "end_frame": end_frame,
        }

        return metadata

    # ------------------------------------------------------------------
    # 2) NORMAL FILES
    # ------------------------------------------------------------------

    file_path = Path(file_path)

    if not file_path.exists():
        # Create minimal legacy metadata safely for "other" files
        return {
            "file_path": str(file_path),
            "file_size_bytes": file_path.stat().st_size if file_path.is_file() else None,
            "media_type": "other",
            "extension": file_path.suffix.lower(),
            "resolution_px": None,
            "duration_seconds": None,
            "sample_rate_hz": None,
            "mode": None,
            "format": None,
        }


    file_size_bytes = file_path.stat().st_size
    extension = file_path.suffix.lower()

    # Base metadata shared by all file types
    metadata = {
        "file_path": str(file_path),
        "file_size_bytes": file_size_bytes,
        "media_type": "other",
        "extension": extension,
        "resolution_px": None,
        "duration_seconds": None,
        "sample_rate_hz": None,
        "mode": None,
        "format": None,
    }

    # ------------------------------------------------------------------
    # IMAGE FILES
    # ------------------------------------------------------------------
    if extension in image_extensions:
        metadata["media_type"] = "image"
        try:
            with Image.open(file_path) as image:
                metadata["resolution_px"] = f"{image.width}x{image.height}"
                metadata["format"] = image.format
                metadata["mode"] = image.mode
        except Exception:
            # Some image formats may not be readable by Pillow
            pass

    # ------------------------------------------------------------------
    # VIDEO FILES
    # ------------------------------------------------------------------
    elif extension in video_extensions:
        metadata["media_type"] = "video"
        if is_ffmpeg_available():
            _populate_ffprobe_metadata(file_path, metadata)

    # ------------------------------------------------------------------
    # AUDIO FILES
    # ------------------------------------------------------------------
    elif extension in audio_extensions:
        metadata["media_type"] = "audio"
        if is_ffmpeg_available():
            _populate_ffprobe_metadata(file_path, metadata)

    return metadata


def extract_metadata_for_folder(folder_path, config=None):
    """
    Extract metadata for all supported files in a folder.

    Note:
        This function is not used by the main pipeline, which performs
        scanning and orchestration itself. It exists for standalone use
        and manual testing.

    This function:
        - Scans the folder using scan_folder()
        - Extracts raw metadata for each file
        - Applies media-type inclusion rules from config
        - Filters metadata fields based on config.metadata_fields


    Args:
        folder_path (str | Path): Folder to scan.

    Returns:
        list[dict]: List of filtered metadata dictionaries.
    """

    if config is None:
        raise ValueError(
            "extract_metadata_for_folder() now requires a Config object. "
            "Pipeline must pass config explicitly."
        )

    folder_path = Path(folder_path)

    if not folder_path.is_dir():
        raise ValueError(f"{folder_path} is not a valid directory")

    files = scan_folder(
        folder_path,
        include_subfolders=config.recurse_subfolders,
        file_types=None,
        config=config,
    )

    all_file_metadata = []

    for current_file in files:
        file_metadata = extract_metadata(current_file)

        media_type = file_metadata["media_type"]
        if not config.include_media_types.get(media_type, False):
            continue


        # Filter metadata fields based on user configuration
        filtered_metadata = {}
        for key, value in file_metadata.items():
            if key in config.metadata_fields:
                filtered_metadata[key] = value


        all_file_metadata.append(filtered_metadata)

    return all_file_metadata


# ----------------------------------------------------------------------
# Manual testing (isolated, behavior-safe, uses Config defaults directly)
# ----------------------------------------------------------------------

if __name__ == "__main__":
    from .config import Config
    from .utils import scan_folder, group_frame_sequences
    from .thumbnailer import generate_thumbnail_for_sequence  # only used in sequence test print
    from .metadata_reader import extract_metadata, extract_metadata_for_folder

    here = Path(__file__).resolve().parent
    sample_folder = here.parent.parent / "assets" / "sample_media"

    print("\n--- Single file metadata test ---")
    for current_file in sample_folder.iterdir():
        if current_file.is_file():
            print(f"\nTesting file: {current_file.name}")
            file_meta = extract_metadata(current_file)
            for key, value in file_meta.items():
                print(f"{key} : {value}")

    print("\n--- Folder metadata extraction test ---")
    # Build test Config using literal defaults (no Defaults dict)
    test_config = Config(
        recurse_subfolders=True,
        file_types=[".png", ".jpg", ".jpeg", ".mp4", ".mov", ".wav", ".xls", ".xlsx", ".epub", ".txt", ".zip", ".md", ".ods", ".odt", ".pdf", ".rtf"],
        combine_frame_seq=True,
        ignore_thumbnail_folders=True,
        generate_thumbnails=False,
        thumb_images=False,
        thumb_videos=False,
        thumb_size=(400, 300),
        thumb_suffix="_thumb",
        thumb_folder_name="thumbnails",
        include_media_types={"image": True, "video": True, "audio": True, "other": True},
        metadata_fields=["file_path", "file_size_bytes", "media_type", "extension", "resolution_px", "duration_seconds", "sample_rate_hz", "mode", "format"],
        metadata_sort_by="file_size_bytes",
        metadata_sort_reverse=False,
        enable_organiser=False,
        organiser_mode="copy",
        default_unsorted_folder="other",
        verbose=True,
    )

    folder_meta = extract_metadata_for_folder(sample_folder, config=test_config)
    for file_metadata in folder_meta:
        print(file_metadata)

    print("\n--- Frame sequence metadata test ---")
    files = scan_folder(sample_folder, include_subfolders=True)
    items = group_frame_sequences(files)

    for item in items:
        if isinstance(item, dict):
            meta = extract_metadata(item)
            print(meta)
