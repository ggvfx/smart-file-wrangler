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
    
    # Check that the path exists and is a directory
    if not root_path.is_dir():
        raise ValueError(f"{root_path} is not a valid directory")

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

        # Check if the file matches the requested types (or include all if None)
        if file_types is None or file_path.suffix.lower().lstrip(".") in file_types:
            matched_files.append(file_path)

    return matched_files


# Example usage (for testing)
if __name__ == "__main__":
    # Update this path relative to your current working directory
    sample_folder_path = Path(__file__).parent / "../../assets/sample_media"

    # Scan all files in the folder and subfolders
    files_found = scan_folder(sample_folder_path, include_subfolders=True)

    # Print results
    print("Files found:")
    for file_path in files_found:
        print(file_path)
