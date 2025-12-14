"""
utils.py
Shared helper functions for Smart File Wrangler.
"""

from pathlib import Path
import subprocess
from .config import Defaults
import re
from collections import defaultdict

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
    if thumb_folder_name is None:
        thumb_folder_name = Defaults["thumb_folder_name"]
    if thumb_suffix is None:
        thumb_suffix = Defaults["thumb_suffix"]
    thumb_dir = file_path.parent / thumb_folder_name
    thumb_dir.mkdir(parents=True, exist_ok=True)
    thumb_name = f"{file_path.stem}{thumb_suffix}{thumb_ext}"
    return thumb_dir / thumb_name


def filter_metadata(metadata: dict, fields: list = None) -> dict:
    """Return only the keys specified in fields. If fields=None, return all."""
    if fields is None:
        fields = Defaults["metadata_fields"]
    return {k: v for k, v in metadata.items() if k in fields}


def detect_frame_sequences(files, min_sequence_length=2):
    """
    Detects frame sequences in a list of files.

    Args:
        files (list[Path or str]): List of file paths.
        min_sequence_length (int): Minimum number of frames to consider a sequence.

    Returns:
        list: Sequence dicts and standalone files.
        Example:
        [
            {"basename": "shot01", "frames": [1001,1002,1003], "ext": ".exr", "folder": Path(...)},
            Path("standalone_file.txt")
        ]
    """
    sequences = defaultdict(lambda: {"frames": [], "ext": None, "folder": None})
    standalone_files = []

    # Regex to capture frame numbers with flexible separators before the number
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

    # Build final list, filter sequences by min length
    result = []
    for (folder, base, ext), seq in sequences.items():
        frames = sorted(seq["frames"])
        if len(frames) >= min_sequence_length:
            result.append({
                "basename": base,
                "frames": frames,
                "ext": ext,
                "folder": folder,
                "separator": seq.get("separator", ".")
            })
        else:
            # Treat short sequences as individual files
            for frame in frames:
                # Attempt to detect the original separator before the frame number
                sep_match = re.search(r"(.+?)([._-])\d+(\.[^.]+)$", str(folder / f"{base}{ext}"))
    
                if sep_match:
                    separator = sep_match.group(2)
                else:
                    separator = "."
                    print(f"Warning: could not detect separator for frame sequence '{base}' in folder '{folder}', defaulting to '{separator}'.")

                filename = folder / f"{base}{separator}{frame}{ext}"
                standalone_files.append(filename)

    # Combine sequences + standalone files
    return result + standalone_files

def group_frame_sequences(files, min_sequence_length=2):
    """Wrapper to match organiser.py naming."""
    return detect_frame_sequences(files, min_sequence_length=min_sequence_length)

def generate_thumbnail_for_sequence(sequence_dict):
    """
    Generate a single thumbnail for a frame sequence using the middle frame.
    
    Parameters:
        sequence_dict (dict): {"basename": ..., "frames": [...], "ext": ..., "folder": Path(...)}
    
    Returns:
        Path to the generated thumbnail (optional)
    """
    frames = sequence_dict["frames"]
    folder = sequence_dict["folder"]
    basename = sequence_dict["basename"]
    ext = sequence_dict["ext"]

    if not frames:
        # No frames available, skip
        if Defaults.get("verbose", True):
            print(f"No frames found for sequence: {basename}")
        return None

    # Pick the middle frame
    middle_index = len(frames) // 2
    middle_frame_number = frames[middle_index]

    # Construct the full path to the middle frame
    middle_frame_file = folder / f"{basename}.{str(middle_frame_number).zfill(len(str(frames[-1])))}{ext}"

    # Generate the thumbnail path (using the helper function from utils.py)
    thumbnail_path = get_thumbnail_path(middle_frame_file)

    # TODO: implement actual thumbnail generation if needed
    # For now, just print debug info
    if Defaults.get("verbose", True):
        print(f"Generating thumbnail for sequence '{basename}': using frame {middle_frame_number} -> {thumbnail_path}")

    return thumbnail_path

