"""
file_scanner.py

Filesystem discovery for Smart File Wrangler.

Purpose:
- Scans folders to discover files on disk
- Returns physical filesystem entries (Path objects)
- Delegates sequence grouping to utils
- Wraps results into internal MediaItem objects later
Internal wrapping into `MediaItem` happens **only** in:
   - `_items_to_media_items()`
   - `scan_media_items()`
 `scan_folder()` and `scan_files()` return legacy types (`Path | dict`) unchanged.

Terminology:
- files = physical filesystem entries on disk
- sequences = grouped frame sequences (dict objects from utils)
- media items = internal wrapped objects for clarity only (MediaItem)

This module contains no filtering or business logic — it only discovers files
and hands them off to other subsystems.
"""

# ----------------------------------------------------------------------
# Standard library imports
# ----------------------------------------------------------------------

from pathlib import Path

# ----------------------------------------------------------------------
# Local imports
# ----------------------------------------------------------------------

from .config import Config
from .utils import detect_frame_sequences
from .media_item import MediaItem


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------

def scan_folder(root_path, include_subfolders=None, file_types=None, ignore_thumbnails=False, config=None):
    """
    Scan a folder and return all discovered files.

    Args:
        root_path (str | Path): Folder to scan.
        include_subfolders (bool): Whether to recurse into subfolders
        config (Config | None): Optional config used only for default recursion flag

    Returns:
        List[Path]: All discovered files on disk as physical filesystem entries

    Notes:
        - This function preserves legacy behavior and makes no assumptions about MediaItem.
        - No filtering is performed here.
    """

    root_path = Path(root_path)

    # Validate input path early
    if not root_path.is_dir():
        raise ValueError(f"{root_path} is not a valid directory")
    
    # Resolve runtime configuration
    if config is not None:
        include_subfolders = config.recurse_subfolders
        ignore_thumbnails = config.ignore_thumbnail_folders
        thumb_folder_name = config.thumb_folder_name
    else:
        thumb_folder_name = None

    # Resolve recursion behavior
    # If not explicitly specified, fall back to global Defaults
    if include_subfolders is None:
        raise ValueError(
        "include_subfolders was not resolved from Config or arguments"
    )

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
        if ignore_thumbnails and thumb_folder_name in file_path.parts:
            continue

        # Check extension filter
        #
        # If file_types is None, all files are accepted.
        # Otherwise, only files with matching extensions are included.
        if file_types is None or file_path.suffix.lower().lstrip(".") in file_types:
            matched_files.append(file_path)

    return matched_files


def scan_files(folder_path, include_subfolders=None, file_types=None, combine_frame_seq=True, config=None):
    """
    Scan a folder and return files or grouped frame sequences.

    This is a higher-level convenience wrapper around scan_folder().

    Args:
        folder_path (str | Path): Folder to scan.
        include_subfolders (bool | None): Whether to recurse into subfolders.
            If None, the value must be provided via Config or arguments.
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
    if config is not None:
        include_subfolders = config.recurse_subfolders
        file_types = file_types or config.file_types
        combine_frame_seq = config.combine_frame_seq

    #guard
    if combine_frame_seq is None:
        raise ValueError(
            "combine_frame_seq was not resolved from Config or arguments"
        )


    # First perform raw file discovery
    files = scan_folder(folder_path, include_subfolders=include_subfolders, file_types=file_types, config=config)

    # Optionally detect and group frame sequences
    #
    # When enabled, this replaces individual frame files with
    # structured sequence dictionaries.
    if combine_frame_seq:
        items = detect_frame_sequences(files)
    else:
        items = files

    return items


def _items_to_media_items(items):
    """
    Convert legacy scan output (Path | dict) into MediaItem objects.
    Behavior-safe: does not change scan logic, only wraps results.
    """
    media_items = []

    for item in items:
        if isinstance(item, dict):
            media_items.append(
                MediaItem(kind="sequence", path=None, sequence_info=item)
            )
        else:
            media_items.append(
                MediaItem(kind="file", path=item, sequence_info=None)
            )

    return media_items

def scan_media_items(folder_path, include_subfolders=None, file_types=None, combine_frame_seq=True, config=None):
    """
    Scan a folder and return internal media units for pipeline orchestration.

    Args:
        folder (Path): Folder to scan
        include_subfolders (bool): Whether to recurse into subfolders
        config (Config | None): Optional config used only for default recursion flag

    Returns:
        List[MediaItem]: Wrapped media objects (file or sequence) for internal clarity

    Notes:
        - Unconditionally wraps sequences (dict) and files (Path) into MediaItem objects.
        - This is internal only and does not change behavior of the pipeline.
        - No filtering or business logic is added here.
    """

    items = scan_files(folder_path, include_subfolders=include_subfolders, file_types=file_types, combine_frame_seq=combine_frame_seq, config=config)

    return _items_to_media_items(items)



# ----------------------------------------------------------------------
# Manual test harness
# ----------------------------------------------------------------------
# This block is intended for ad-hoc testing and debugging only.
# It is not used by the pipeline or CLI.

if __name__ == "__main__":
    from pprint import pprint

    test_folder = Path(r"D:\_repos\smart-file-wrangler\assets\sample_media")

    print("\nScanning files (with frame sequence detection enabled):\n")

    from .config import Config

    test_config = Config(
        recurse_subfolders=True,
        combine_frame_seq=True,
        generate_thumbnails=False,
        thumb_images=False,
        thumb_videos=False,
        enable_organiser=False,
        move_files=False,
        output_csv=False,
        output_json=False,
        output_excel=False,
        output_tree=False,
        report_output_dir=None,
        verbose=True,
    )


    scanned_items = scan_files(test_folder, config=test_config)

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
