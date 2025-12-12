"""
file_scanner.py
Scans folders, handles subfolder recursion, and filters files by type.
Supports recursive scanning for use in organising subfolders.
"""

from pathlib import Path

def scan_folder(root_path, include_subfolders=True, file_types=None):
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
    if not root_path.is_dir():
        raise ValueError(f"{root_path} is not a valid directory")

    if file_types:
        file_types = [ext.lower().lstrip(".") for ext in file_types]

    files_iter = root_path.rglob("*") if include_subfolders else root_path.glob("*")
    matched_files = [f for f in files_iter if f.is_file() and (not file_types or f.suffix.lower().lstrip(".") in file_types)]
    return matched_files



# Example usage (for testing)
if __name__ == "__main__":
    files = scan_folder("sample_media", include_subfolders=True, file_types=["mp4", "png"])
    for f in files:
        print(f)

