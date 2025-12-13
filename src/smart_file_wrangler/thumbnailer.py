"""
thumbnailer.py
Generates thumbnails for images and videos.
Supports:
- Running standalone on a list of files
- Maintaining aspect ratio
- Custom or preset sizes (256, 512, 1024px, etc.)
- Orientation selection (horizontal/vertical)
- Selecting specific video frame for videos (default 24th)
- Supports .mp4 and .mov output with selectable codecs
“Video thumbnails require ffmpeg. If unavailable, only image thumbnails are generated.”
"""

def create_thumbnail(path, out_path, size=256, orientation="horizontal", frame_number=24, codec="mp4"):
    """
    Wrapper function to create a thumbnail based on file type.

    Parameters:
        path (Path): Input file.
        out_path (Path): Output thumbnail path.
        size (int or tuple): Pixel size (preserves aspect ratio).
        orientation (str): 'horizontal' or 'vertical'.
        frame_number (int): Frame number to capture for videos.
        codec (str): Output video codec if applicable.
    """
    # TODO: detect file type and call image/video handler
    pass

def create_image_thumbnail(path, out_path, size, orientation):
    """Create a thumbnail from an image file, preserving aspect ratio."""
    pass

def create_video_thumbnail(path, out_path, size, orientation, frame_number, codec):
    """Create a thumbnail from a video file with frame selection and codec support."""
    pass
