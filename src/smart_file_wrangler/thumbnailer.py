"""
thumbnailer.py
Generates thumbnails for images and videos.

Supports:
- Running standalone on a list of files
- Maintaining aspect ratio
- Custom sizes (256, 512, 1024px, etc.)
- Can process all files in a folder (optionally including subfolders)
- Maintains aspect ratio
- Stores thumbnails in a 'thumbnails' subfolder
- Adds '_thumb' suffix to thumbnail filenames
- Video thumbnails require ffmpeg. If unavailable, only image thumbnails are generated.
"""

from pathlib import Path
from PIL import Image
from .utils import is_ffmpeg_available, image_extensions, video_extensions, get_thumbnail_path
from .config import Defaults
from .file_scanner import scan_folder
import subprocess
import re
from .logger import log

frame_pattern = re.compile(r".+[._-]\d+(\.[^.]+)$")

def create_thumbnail(file_path, out_path=None, size=None, codec="mp4"):
    """
    Detect file type and call the appropriate thumbnail function.

    Parameters:
        file_path (Path): Input file path
        out_path (Path): Output thumbnail path
        size (int): Maximum dimension in pixels (preserves aspect ratio)
        frame_number (int): Frame number to capture for video thumbnails
        codec (str): Video output codec if applicable
    """
    file_path = Path(file_path)
    if size is None:
        size = Defaults["thumb_size"]
    if out_path is None:
        out_path = get_thumbnail_path(file_path, thumb_folder_name=Defaults["thumb_folder_name"], thumb_suffix=Defaults["thumb_suffix"])

    if not file_path.is_file():
        raise ValueError(f"{file_path} is not a valid file")

    extension = file_path.suffix.lower()

    # Check if the file is an image
    if extension in image_extensions:
        if Defaults["thumb_images"]:
            create_image_thumbnail(file_path, out_path, size)
    # Check if the file is a video
    elif extension in video_extensions:
        if Defaults["thumb_videos"]:
            if is_ffmpeg_available():
                create_video_thumbnail(file_path, out_path, size, codec)
            else:
                print(f"Skipping video thumbnail for {file_path.name}: ffmpeg not available")
    else:
        if Defaults.get("verbose"):
            log(f"Skipping {file_path.name}: unsupported file type")


def create_image_thumbnail(file_path, out_path, size):
    """Create a thumbnail from an image file while maintaining aspect ratio."""
    try:
        with Image.open(file_path) as img:
            original_width, original_height = img.size

            # determine scaling factor based on max dimension
            scale_factor = size / max(original_width, original_height)
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)

            # resize image
            img_resized = img.resize((new_width, new_height), Image.LANCZOS)

            #Make dir
            out_path.parent.mkdir(parents=True, exist_ok=True)

            img_resized.save(out_path)
            print(f"Image thumbnail created: {out_path}")

    except Exception as exc:
        print(f"Failed to create image thumbnail for {file_path}: {exc}")


def create_video_thumbnail(file_path, out_path, size, codec):
    """Create a thumbnail from a video file using ffmpeg."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        # ffmpeg command: picks a representative frame and scales it
        command = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel", "error",
            "-i", str(file_path),
            "-vf", f"thumbnail,scale={size}:-1",
            "-frames:v", "1",
            str(out_path)
        ]
        subprocess.run(command, check=True)
        print(f"Video thumbnail created: {out_path}")
    except Exception as exc:
        print(f"Failed to create video thumbnail for {file_path}: {exc}")


def generate_thumbnails_for_folder(folder_path, size=None, codec="mp4"):
    """
    Generate thumbnails for all supported files in a folder (and optionally subfolders).

    Thumbnails are stored in a 'thumbnails' folder within each directory,
    and filenames use the '_thumb' suffix.
    """
    folder_path = Path(folder_path)
    if not folder_path.is_dir():
        raise ValueError(f"{folder_path} is not a valid directory")
    
    # scan folder using config defaults (includes recurse_subfolders)
    files = scan_folder(folder_path)

    for file_path in files:
        # Skip frame sequence members
        if frame_pattern.match(file_path.name):
            continue

        ext = file_path.suffix.lower()
        # skip if not enabled in Defaults
        if ext in image_extensions and not Defaults["thumb_images"]:
            continue
        if ext in video_extensions and not Defaults["thumb_videos"]:
            continue

        thumb_path = get_thumbnail_path(
            file_path,
            thumb_folder_name=Defaults["thumb_folder_name"],
            thumb_suffix=Defaults["thumb_suffix"]
        )
        create_thumbnail(file_path, out_path=thumb_path, size=Defaults["thumb_size"], codec=codec)

def generate_thumbnail_for_sequence(sequence_dict):
    from .utils import get_thumbnail_path

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


# quick test
if __name__ == "__main__":
    # Get the path to the sample media folder
    current_directory = Path(__file__).resolve().parent
    sample_media_folder = current_directory.parent.parent / "assets" / "sample_media"

    print("\n--- Thumbnail generation test ---")

    # Generate thumbnails for all supported files in the folder
    # This will respect Defaults["recurse_subfolders"]
    generate_thumbnails_for_folder(sample_media_folder)

    print("\nThumbnail generation completed.")

