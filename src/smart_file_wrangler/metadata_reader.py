"""
metadata_reader.py
Extracts metadata such as duration, resolution, file size, etc.
"""

from pathlib import Path
from PIL import Image
import subprocess
import json
from .utils import is_ffmpeg_available, image_extensions, video_extensions, audio_extensions
from .file_scanner import scan_folder
from .config import Defaults


# helper for video/audio files if ffmpeg is available
def _populate_ffprobe_metadata(file_path, metadata):
    # build ffprobe command
    command = ["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(file_path)]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
    except Exception:
        return  # leave metadata as None if ffprobe fails

    for stream in data.get("streams", []):
        if "width" in stream and "height" in stream:
            width = int(stream["width"])
            height = int(stream["height"])
            metadata["resolution_px"] = f"{width}x{height}"

        if "duration" in stream and metadata["duration_seconds"] is None:
            try:
                metadata["duration_seconds"] = float(stream["duration"])
            except ValueError:
                pass
        if "sample_rate" in stream and metadata["sample_rate_hz"] is None:
            try:
                metadata["sample_rate_hz"] = int(stream["sample_rate"])
            except ValueError:
                pass


#Main function
def extract_metadata(file_path):
    """
    Return a dictionary of metadata for the given file.

    Video and audio metadata is only extracted if ffmpeg/ffprobe is available.
    """

    # 1) FRAME SEQUENCES FIRST
    if isinstance(file_path, dict) and "frames" in file_path:
        frames = file_path["frames"]

        metadata = {
            "file_path": f"{file_path['basename']}.[{frames[0]}-{frames[-1]}]{file_path['ext']}",
            "file_size_mb": None,
            "media_type": "video",
            "extension": file_path["ext"],
            "resolution_px": None,
            "duration_seconds": None,
            "sample_rate_hz": None,
            "mode": None,
            "format": None,
            "frame_count": len(frames),
            "middle_frame_number": frames[len(frames) // 2],
            "start_frame": frames[0],
            "end_frame": frames[-1],
        }
        return metadata


    # 2) NORMAL FILES
    file_path = Path(file_path)

    if not file_path.is_file():
        raise ValueError(f"{file_path} is not a valid file")

    file_size_bytes = file_path.stat().st_size
    file_size_mb = round(file_size_bytes / (1024 * 1024), 2)

    
    # DEBUG: confirm whether ffmpeg is visible to Python
    #print("ffmpeg available:", is_ffmpeg_available())
    
    extension = file_path.suffix.lower()



    #Default metadata
    metadata = {
        "file_path": str(file_path),
        "file_size_mb": file_size_mb,
        "media_type": "other",
        "extension": file_path.suffix.lower(),
        "resolution_px": None,
        "duration_seconds": None,
        "sample_rate_hz": None,
        "mode": None,
        "format": None,
    }

    #Images
    if extension in image_extensions:
        metadata["media_type"] = "image"
        try:
            with Image.open(file_path) as image:
                metadata["resolution_px"] = f"{image.width}x{image.height}"
                metadata["format"] = image.format
                metadata["mode"] = image.mode
        except Exception:
            pass  # some formats may not be readable by Pillow

    #Videos
    elif extension in video_extensions:
        metadata["media_type"] = "video"
        # only call ffprobe if it is available
        if is_ffmpeg_available():
            _populate_ffprobe_metadata(file_path, metadata)

    #Audio
    elif extension in audio_extensions:
        metadata["media_type"] = "audio"
        if is_ffmpeg_available():
            _populate_ffprobe_metadata(file_path, metadata)

    # other file types will still have file_size and extension
    return metadata

# Extract metadata for all files in a folder
def extract_metadata_for_folder(folder_path):
    """
    Generate metadata dictionaries for all supported files in a folder
    (and optionally subfolders based on Defaults["recurse_subfolders"]).

    Returns:
        list[dict]: List of metadata dictionaries.
    """
    folder_path = Path(folder_path)
    if not folder_path.is_dir():
        raise ValueError(f"{folder_path} is not a valid directory")

    # Use scan_folder to respect config for recursion
    files = scan_folder(
        folder_path,
        include_subfolders=Defaults["recurse_subfolders"],
        file_types=None
    )

    all_file_metadata = []  # This will store metadata for every file

    for current_file in files:
        # Extract full metadata for this file
        file_metadata = extract_metadata(current_file)

        media_type = file_metadata["media_type"]
        if not Defaults["include_media_types"].get(media_type, False):
            continue  # skip this file entirely

        # Keep only the metadata fields that the user wants (from Defaults)
        filtered_metadata = {}
        for key, value in file_metadata.items():
            if key in Defaults["metadata_fields"]:
                filtered_metadata[key] = value

        #DEBUG
        #filtered_metadata["file_path"] = str(current_file)

        # Add the filtered metadata for this file to the main list
        all_file_metadata.append(filtered_metadata)

    # Return the list containing metadata for all files
    return all_file_metadata

# quick test
if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    sample_folder = here.parent.parent / "assets" / "sample_media"

    # Test metadata extraction for individual files
    print("\n--- Single file metadata test ---")
    for current_file in sample_folder.iterdir():
        if current_file.is_file():
            print(f"\nTesting file: {current_file.name}")
            current_file_metadata = extract_metadata(current_file)
            for key, value in current_file_metadata.items():
                print(f"{key} : {value}")

    # Test metadata extraction for the whole folder
    print("\n--- Folder metadata extraction test ---")
    all_files_metadata = extract_metadata_for_folder(sample_folder)
    for file_metadata in all_files_metadata:
        print(file_metadata)

    #Metadata for frame sequences
    from .utils import group_frame_sequences

    print("\n--- Frame sequence metadata test ---")
    files = scan_folder(sample_folder, include_subfolders=True)
    items = group_frame_sequences(files)

    for item in items:
        if isinstance(item, dict):
            meta = extract_metadata(item)
            print(meta)
