"""
file_scanner.py

Scans folders to discover files for processing.

This module is responsible for:
- Traversing a directory (optionally recursively)
- Filtering files by extension
- Excluding generated artifacts such as thumbnails
- Optionally grouping frame sequences into logical units

This module performs discovery only. It does not read metadata,
move files, or generate outputs.
"""

from pathlib import Path

from .config import Defaults
from .utils import detect_frame_sequences


def scan_folder(
    root_path,
    include_subfolders=None,
    file_types=None,
    ignore_thumbnails=False
):
    """
    Scan a folder and return matching file paths.

    Args:
        root_path (str | Path): Directory to scan.
        include_subfolders (bool | None): Whether to recurse into subdirectories.
            If None, the default value from config.Defaults is used.
        file_types (list[str] | None): List of file extensions to include
            (e.g. ["mp4", "png"]). Case-insensitive, without leading dots.
            If None, all file types are included.
        ignore_thumbnails (bool): If True, files located inside the thumbnail
            output folder are excluded.

    Returns:
        list[Path]: List of matching file paths.

    Raises:
        ValueError: If root_path does not exist or is not a directory.
    """
    root_path = Path(root_path)

    # Validate input path early
    if not root_path.is_dir():
        raise ValueError(f"{root_path} is not a valid directory")

    # Resolve recursion behavior
    # If not explicitly specified, fall back to global Defaults
    if include_subfolders is None:
        include_subfolders = Defaults["recurse_subfolders"]

    # Normalize file extensions for comparison
    # Convert to lowercase and strip leading dots
    if file_types:
        file_types = [ext.lower().lstrip(".") for ext in file_types]

    # Choose traversal method based on recursion setting
    #
    # rglob("*") walks all subdirectories recursively
    # glob("*") only scans the top-level directory
    if include_subfolders:
        files_iterator = root_path.rglob("*")
    else:
        files_iterator = root_path.glob("*")

    matched_files = []

    for file_path in files_iterator:
        # Skip directories; only files are returned
        if not file_path.is_file():
            continue

        # Optionally exclude thumbnail folders
        #
        # This check looks for the thumbnail folder name anywhere in the path
        # parts to ensure generated thumbnails are not reprocessed.
        if ignore_thumbnails and Defaults["thumb_folder_name"] in file_path.parts:
            continue

        # Check extension filter
        #
        # If file_types is None, all files are accepted.
        # Otherwise, only files with matching extensions are included.
        if file_types is None or file_path.suffix.lower().lstrip(".") in file_types:
            matched_files.append(file_path)

    return matched_files


def scan_files(
    folder_path,
    include_subfolders=None,
    file_types=None,
    combine_frame_seq=True
):
    """
    Scan a folder and return files or grouped frame sequences.

    This is a higher-level convenience wrapper around scan_folder().

    Args:
        folder_path (str | Path): Folder to scan.
        include_subfolders (bool | None): Whether to recurse into subfolders.
            If None, the default from config.Defaults is used.
        file_types (list[str] | None): Optional extension filter.
        combine_frame_seq (bool): If True, consecutive frame sequences
            are grouped into a single logical item.

    Returns:
        list[Path | dict]: A list containing either:
            - Path objects for standalone files
            - dict objects describing detected frame sequences

        Frame sequence dictionaries contain:
            {
                "folder": Path,
                "basename": str,
                "ext": str,
                "frames": list[int]
            }
    """
    # First perform raw file discovery
    files = scan_folder(
        folder_path,
        include_subfolders=include_subfolders,
        file_types=file_types
    )

    # Optionally detect and group frame sequences
    #
    # When enabled, this replaces individual frame files with
    # structured sequence dictionaries.
    if combine_frame_seq:
        items = detect_frame_sequences(files)
    else:
        items = files

    return items


# ----------------------------------------------------------------------
# Manual test harness
# ----------------------------------------------------------------------
# This block is intended for ad-hoc testing and debugging only.
# It is not used by the pipeline or CLI.

if __name__ == "__main__":
    from pprint import pprint

    test_folder = Path(r"D:\_repos\smart-file-wrangler\assets\sample_media")

    print("\nScanning files (with frame sequence detection enabled):\n")

    scanned_items = scan_files(test_folder)

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
