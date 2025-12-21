"""
thumbnailer.py

Generates thumbnails for images, videos, and frame sequences.

This module:
- Creates image thumbnails using Pillow
- Creates video thumbnails using ffmpeg (if available)
- Preserves aspect ratio
- Stores thumbnails in a 'thumbnails' subfolder
- Appends a '_thumb' suffix to thumbnail filenames

This module performs thumbnail generation only.
It does not scan for metadata or organise files.
"""

from pathlib import Path
import subprocess
import re

from PIL import Image

from .utils import (
    is_ffmpeg_available,
    image_extensions,
    video_extensions,
    get_thumbnail_path,
)
from .config import Defaults
from .file_scanner import scan_folder
from .logger import log


# ----------------------------------------------------------------------
# Constants and patterns
# ----------------------------------------------------------------------

# Matches filenames that look like individual frame sequence members,
# e.g. shot_001.exr, render.1001.png
frame_pattern = re.compile(r".+[._-]\d+(\.[^.]+)$")


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------

def create_thumbnail(file_path, out_path=None, size=None, codec="mp4"):
    """
    Create a thumbnail for a single file.

    This function detects the file type and delegates to the appropriate
    image or video thumbnail function.

    Args:
        file_path (Path): Input media file.
        out_path (Path | None): Output thumbnail path.
            If None, the path is derived using get_thumbnail_path().
        size (int | None): Maximum thumbnail dimension in pixels.
            If None, Defaults["thumb_size"] is used.
        codec (str): Video output codec (currently unused, preserved for API stability).
    """
    file_path = Path(file_path)

    if size is None:
        size = Defaults["thumb_size"]

    if out_path is None:
        out_path = get_thumbnail_path(
            file_path,
            thumb_folder_name=Defaults["thumb_folder_name"],
            thumb_suffix=Defaults["thumb_suffix"],
        )

    if not file_path.is_file():
        raise ValueError(f"{file_path} is not a valid file")

    extension = file_path.suffix.lower()

    # ------------------------------------------------------------------
    # IMAGE FILES
    # ------------------------------------------------------------------
    if extension in image_extensions:
        if Defaults["thumb_images"]:
            create_image_thumbnail(file_path, out_path, size)

    # ------------------------------------------------------------------
    # VIDEO FILES
    # ------------------------------------------------------------------
    elif extension in video_extensions:
        if Defaults["thumb_videos"]:
            if is_ffmpeg_available():
                create_video_thumbnail(file_path, out_path, size, codec)
            else:
                # External dependency missing; skip safely
                print(
                    f"Skipping video thumbnail for {file_path.name}: "
                    f"ffmpeg not available"
                )

    # ------------------------------------------------------------------
    # UNSUPPORTED FILE TYPES
    # ------------------------------------------------------------------
    else:
        if Defaults.get("verbose"):
            log(f"Skipping {file_path.name}: unsupported file type")


# ----------------------------------------------------------------------
# Image thumbnail generation
# ----------------------------------------------------------------------

def create_image_thumbnail(file_path, out_path, size):
    """
    Create a thumbnail for an image file using Pillow.

    The image is resized while maintaining aspect ratio, using the
    largest dimension as the scaling reference.
    """
    try:
        # Pillow is used here to open and resize image files
        with Image.open(file_path) as img:
            original_width, original_height = img.size

            # Scale so that the largest dimension matches `size`
            scale_factor = size / max(original_width, original_height)
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)

            img_resized = img.resize(
                (new_width, new_height),
                Image.LANCZOS
            )

            # Ensure output directory exists
            out_path.parent.mkdir(parents=True, exist_ok=True)

            img_resized.save(out_path)
            print(f"Image thumbnail created: {out_path}")

    except Exception as exc:
        # Fail safely; thumbnail generation should not halt the pipeline
        print(f"Failed to create image thumbnail for {file_path}: {exc}")


# ----------------------------------------------------------------------
# Video thumbnail generation
# ----------------------------------------------------------------------

def create_video_thumbnail(file_path, out_path, size, codec):
    """
    Create a thumbnail for a video file using ffmpeg.

    This function relies on the external ffmpeg tool to:
    - Select a representative frame
    - Scale it while preserving aspect ratio
    - Output a single thumbnail image
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # External tool: ffmpeg
        #
        # - 'thumbnail' filter selects a representative frame
        # - 'scale' resizes the frame to the requested size
        command = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel", "error",
            "-i", str(file_path),
            "-vf", f"thumbnail,scale={size}:-1",
            "-frames:v", "1",
            str(out_path),
        ]

        subprocess.run(command, check=True)
        print(f"Video thumbnail created: {out_path}")

    except Exception as exc:
        # Fail safely; missing codecs or corrupt files should not stop execution
        print(f"Failed to create video thumbnail for {file_path}: {exc}")


# ----------------------------------------------------------------------
# Folder-level helpers
# ----------------------------------------------------------------------

def generate_thumbnails_for_folder(folder_path, size=None, codec="mp4"):
    """
    Generate thumbnails for all supported files in a folder.

    This function:
    - Scans the folder using scan_folder()
    - Respects recursion settings from Defaults
    - Skips individual frame sequence members
    - Respects Defaults["thumb_images"] and Defaults["thumb_videos"]
    """
    folder_path = Path(folder_path)

    if not folder_path.is_dir():
        raise ValueError(f"{folder_path} is not a valid directory")

    # Scan folder using configuration defaults
    files = scan_folder(folder_path)

    for file_path in files:
        # Skip individual frame sequence members
        if frame_pattern.match(file_path.name):
            continue

        ext = file_path.suffix.lower()

        # Respect thumbnail enable flags
        if ext in image_extensions and not Defaults["thumb_images"]:
            continue
        if ext in video_extensions and not Defaults["thumb_videos"]:
            continue

        thumb_path = get_thumbnail_path(
            file_path,
            thumb_folder_name=Defaults["thumb_folder_name"],
            thumb_suffix=Defaults["thumb_suffix"],
        )

        create_thumbnail(
            file_path,
            out_path=thumb_path,
            size=Defaults["thumb_size"],
            codec=codec,
        )


def generate_thumbnail_for_sequence(sequence_dict):
    """
    Generate a thumbnail for a frame sequence.

    The middle frame of the sequence is used as the thumbnail source.
    """
    frames = sequence_dict["frames"]
    folder = sequence_dict["folder"]
    basename = sequence_dict["basename"]
    ext = sequence_dict["ext"]
    separator = sequence_dict.get("separator", ".")

    if not frames:
        return None

    middle_index = len(frames) // 2
    middle_frame_number = frames[middle_index]

    frame_path = folder / f"{basename}{separator}{middle_frame_number}{ext}"

    if not frame_path.exists():
        print(f"Warning: middle frame missing: {frame_path}")
        return None

    thumb_path = get_thumbnail_path(frame_path)
    create_thumbnail(frame_path, out_path=thumb_path)

    if Defaults.get("verbose", True):
        print(
            f"Thumbnail created for sequence '{basename}' "
            f"(frame {middle_frame_number}) -> {thumb_path}"
        )

    return thumb_path


# ----------------------------------------------------------------------
# Manual testing
# ----------------------------------------------------------------------

if __name__ == "__main__":
    current_directory = Path(__file__).resolve().parent
    sample_media_folder = current_directory.parent.parent / "assets" / "sample_media"

    print("\n--- Thumbnail generation test ---")

    generate_thumbnails_for_folder(sample_media_folder)

    print("\nThumbnail generation completed.")
