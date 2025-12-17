"""
file_scanner.py
Scans folders, handles subfolder recursion, and filters files by type.
Supports recursive scanning for use in organising subfolders.
"""

from pathlib import Path
from .config import Defaults  # import config to get global recurse setting
from .utils import detect_frame_sequences

def scan_folder(root_path, include_subfolders=None, file_types=None, ignore_thumbnails=False):
    """
    Return a list of file paths that match the given file types.

    Parameters:
        root_path (str | Path): Directory to scan.
        include_subfolders (bool): Whether to recurse into subdirectories.
        file_types (list[str] | None): Extensions to include, e.g. ["mp4", "png"]. Case-insensitive.
                                        If None, all files are returned.

    Returns:
        list[Path]: List of matching file paths.
    """
    root_path = Path(root_path)
    
    # Check that the path exists and is a directory
    if not root_path.is_dir():
        raise ValueError(f"{root_path} is not a valid directory")
    
    # Use default from config if not explicitly provided
    if include_subfolders is None:
        include_subfolders = Defaults["recurse_subfolders"]

    # Normalize file extensions to lower case, remove leading dots
    if file_types:
        file_types = [ext.lower().lstrip(".") for ext in file_types]

    # Choose iterator based on whether to include subfolders
    if include_subfolders:
        files_iterator = root_path.rglob("*")  # Recursive search
    else:
        files_iterator = root_path.glob("*")   # Top-level only

    # Collect matching files
    matched_files = []
    for file_path in files_iterator:
        if not file_path.is_file():
            continue  # Skip directories

        # Skip thumbnails folder if requested
        if ignore_thumbnails and Defaults["thumb_folder_name"] in file_path.parts:
            continue

        # Check file type
        if file_types is None or file_path.suffix.lower().lstrip(".") in file_types:
            matched_files.append(file_path)

    return matched_files


def scan_files(folder_path, include_subfolders=None, file_types=None, combine_frame_seq=True):
    """
    Return a list of file paths or frame sequences that match the given file types.

    Parameters:
        folder_path (str | Path): Folder to scan.
        include_subfolders (bool | None): Whether to include subfolders.
        file_types (list[str] | None): Optional filter by file extension.
        combine_frame_seq (bool): If True, consecutive frame sequences are treated as one item.

    Returns:
        list[Path | dict]: List of file paths or frame sequence dictionaries.
        Frame sequence dict contains keys:
            "folder"  -> Path to sequence folder
            "basename"-> Base name of sequence (without frame number)
            "ext"     -> File extension (including dot)
            "frames"  -> Sorted list of frame numbers in the sequence
    """
    # Scan files in the folder (recursively if requested)
    files = scan_folder(folder_path, include_subfolders=include_subfolders, file_types=file_types)

    if combine_frame_seq:
        # Detect and group consecutive frame sequences
        items = detect_frame_sequences(files)
    else:
        items = files

    return items


# Example usage for testing
if __name__ == "__main__":
    from pprint import pprint

    # Path to your test media folder
    test_folder = Path(r"D:\_repos\smart-file-wrangler\assets\sample_media")

    print("\nScanning files (with frame sequence detection enabled):\n")

    # Run the scan
    scanned_items = scan_files(test_folder)

    # Print results in a readable way
    for item in scanned_items:
        if isinstance(item, dict):
            print("Frame sequence found:")
            print(f"  folder   : {item['folder']}")
            print(f"  basename : {item['basename']}")
            print(f"  ext      : {item['ext']}")
            print(f"  frames   : {item['frames']}")
            print(f"  count    : {len(item['frames'])}")
            print()
        else:
            print(f"Single file: {item}")

