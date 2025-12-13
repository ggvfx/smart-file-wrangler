from pathlib import Path
from PIL import Image
import subprocess
import json
from .utils import is_ffmpeg_available  # import the helper


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
            metadata["resolution"] = (int(stream["width"]), int(stream["height"]))
        if "duration" in stream and metadata["duration"] is None:
            try:
                metadata["duration"] = float(stream["duration"])
            except ValueError:
                pass
        if "sample_rate" in stream and metadata["sample_rate"] is None:
            try:
                metadata["sample_rate"] = int(stream["sample_rate"])
            except ValueError:
                pass


#Main function
def extract_metadata(file_path):
    """
    Return a dictionary of metadata for the given file.

    Video and audio metadata is only extracted if ffmpeg/ffprobe is available.
    """
    file_path = Path(file_path)
    if not file_path.is_file():
        raise ValueError(f"{file_path} is not a valid file")

    #Default metadata
    metadata = {
        "file_size": file_path.stat().st_size,
        "type": "other",          # default type
        "extension": extension,   # store the file extension
        "resolution": None,
        "format": None,
        "mode": None,
        "duration": None,
        "sample_rate": None,
    }

    extension = file_path.suffix.lower()

    image_extensions = [
        ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".gif",
        ".exr", ".dpx", ".cin", ".tga", ".hdr", ".sgi", ".rgb"
    ]
    video_extensions = [".mp4", ".mov", ".avi", ".mkv"]
    audio_extensions = [".wav", ".mp3", ".aac", ".flac"]

    #Images
    if extension in image_extensions:
        metadata["type"] = "image"
        try:
            with Image.open(file_path) as image:
                metadata["resolution"] = (image.width, image.height)
                metadata["format"] = image.format
                metadata["mode"] = image.mode
        except Exception:
            pass  # some formats may not be readable by Pillow

    #Videos
    elif extension in video_extensions:
        metadata["type"] = "video"
        # only call ffprobe if it is available
        if is_ffmpeg_available():
            _populate_ffprobe_metadata(file_path, metadata)

    #Audio
    elif extension in audio_extensions:
        metadata["type"] = "audio"
        if is_ffmpeg_available():
            _populate_ffprobe_metadata(file_path, metadata)

    # other file types will still have file_size and extension
    return metadata

# quick test
if __name__ == "__main__":
    test_file = Path("../assets/sample_media/video1.mp4")
    m = extract_metadata(test_file)
    for k, v in m.items():
        print(k, ":", v)

