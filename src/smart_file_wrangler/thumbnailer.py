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
        size = Defaults["thumbnail_size"]
    if out_path is None:
        out_path = get_thumbnail_path(file_path)

    if not file_path.is_file():
        raise ValueError(f"{file_path} is not a valid file")

    extension = file_path.suffix.lower()

    # Check if the file is an image
    if extension in image_extensions:
        create_image_thumbnail(file_path, out_path, size)
    # Check if the file is a video
    elif extension in video_extensions:
        if is_ffmpeg_available():
            create_video_thumbnail(file_path, out_path, size, codec)
        else:
            print(f"Skipping video thumbnail for {file_path.name}: ffmpeg not available")
    else:
        print(f"Skipping {file_path.name}: unsupported file type")


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
    
    if size is None:
        size = Defaults["thumbnail_size"]

    # Decide whether to recurse based on config
    files = scan_folder(
        folder_path,
        file_types=image_extensions + video_extensions
    )

    for file_path in files:
        thumb_path = get_thumbnail_path(file_path)
        create_thumbnail(file_path, out_path=thumb_path, size=size, codec=codec)


# example usage for testing
if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    sample_folder = here.parent.parent / "assets" / "sample_media"

    generate_thumbnails_for_folder(sample_folder)
