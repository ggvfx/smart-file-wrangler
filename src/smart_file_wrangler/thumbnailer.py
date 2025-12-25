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
from .config import Config
from .file_scanner import scan_folder
from .logger import log
from .media_item import MediaItem



# ----------------------------------------------------------------------
# Constants and patterns
# ----------------------------------------------------------------------

# Matches filenames that look like individual frame sequence members,
# e.g. shot_001.exr, render.1001.png
frame_pattern = re.compile(r".+[._-]\d+(\.[^.]+)$")


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------

def create_thumbnail(file_path, out_path=None, size=None, codec="mp4", config=None):
    """
    Create a thumbnail for a single file.

    This function detects the file type and delegates to the appropriate
    image or video thumbnail function.

    Args:
        file_path (Path): Input media file.
        out_path (Path | None): Output thumbnail path.
            If None, the path is derived using get_thumbnail_path().
        size (int | None): Maximum thumbnail dimension in pixels.
            If None, config.thumb_size is used.
        codec (str): Video output codec (currently unused, preserved for API stability).
    """
    if config is None:
        raise ValueError(
            "create_thumbnail() now requires a Config object. "
            "Pipeline must pass config explicitly."
        )
    
    if isinstance(file_path, MediaItem):
        file_path = file_path.sequence_info if file_path.kind == "sequence" else file_path.path


    if size is None:
        size = config.thumb_size

    verbose = config.verbose

    file_path = Path(file_path)

    if out_path is None:
        out_path = get_thumbnail_path(
            file_path,
            thumb_folder_name=config.thumb_folder_name,
            thumb_suffix=config.thumb_suffix,
        )

    if not file_path.is_file():
        raise ValueError(f"{file_path} is not a valid file")

    extension = file_path.suffix.lower()

    # ------------------------------------------------------------------
    # IMAGE FILES
    # ------------------------------------------------------------------
    if extension in image_extensions:
        if config.thumb_images:
            _create_image_thumbnail(file_path, out_path, size)

    # ------------------------------------------------------------------
    # VIDEO FILES
    # ------------------------------------------------------------------
    elif extension in video_extensions:
        if config.thumb_videos:
            if is_ffmpeg_available():
                _create_video_thumbnail(file_path, out_path, size, codec)
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
        if verbose:
            log(f"Skipping {file_path.name}: unsupported file type")


# ----------------------------------------------------------------------
# Image thumbnail generation
# ----------------------------------------------------------------------

def _create_image_thumbnail(file_path, out_path, size):
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

def _create_video_thumbnail(file_path, out_path, size, codec):
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

def generate_thumbnail_for_sequence(sequence_dict, config=None):
    if isinstance(sequence_dict, MediaItem):
        sequence_dict = sequence_dict.sequence_info

    """
    Generate a thumbnail for a frame sequence.

    The middle frame of the sequence is used as the thumbnail source.
    """
    # unwrap MediaItem safely (behavior preserved)
    if isinstance(sequence_dict, MediaItem):
        sequence_dict = sequence_dict.sequence_info

    if config is None:
        raise ValueError(
            "thumbnailer functions now require a Config object. "
            "Pipeline must pass config explicitly."
        )

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

    thumb_path = get_thumbnail_path(
        frame_path,
        thumb_folder_name=config.thumb_folder_name,
        thumb_suffix=config.thumb_suffix,
    )

    create_thumbnail(frame_path, out_path=thumb_path, config=config)

    if config.verbose:
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

    test_config = Config(
        recurse_subfolders=Defaults["recurse_subfolders"],
        file_types=Defaults["file_types"],
        combine_frame_seq=Defaults["combine_frame_seq"],
        ignore_thumbnail_folders=Defaults["ignore_thumbnail_folders"],

        generate_thumbnails=True,
        thumb_images=Defaults["thumb_images"],
        thumb_videos=Defaults["thumb_videos"],
        thumb_size=Defaults["thumb_size"],
        thumb_suffix=Defaults["thumb_suffix"],
        thumb_folder_name=Defaults["thumb_folder_name"],

        include_media_types=Defaults["include_media_types"],
        metadata_fields=Defaults["metadata_fields"],
        metadata_sort_by=Defaults["metadata_sort_by"],
        metadata_sort_reverse=Defaults["metadata_sort_reverse"],

        enable_organiser=False,
        organiser_mode=Defaults["organiser_mode"],
        filename_rules=Defaults["filename_rules"],
        default_unsorted_folder=Defaults["default_unsorted_folder"],
        move_files=False,

        output_csv=False,
        output_json=False,
        output_excel=False,
        output_tree=False,
        report_output_dir=None,

        verbose=True,
        expand_log=Defaults["expand_log"],
    )

    print("\n--- Thumbnail generation test ---")

    from .utils import group_frame_sequences

    files = scan_folder(
        sample_media_folder,
        include_subfolders=test_config.recurse_subfolders,
    )

    items = (
        group_frame_sequences(files)
        if test_config.combine_frame_seq
        else files
    )

    for item in items:
        if isinstance(item, dict) and "frames" in item:
            generate_thumbnail_for_sequence(item, config=test_config)
        else:
            create_thumbnail(item, config=test_config)


    print("\nThumbnail generation completed.")
