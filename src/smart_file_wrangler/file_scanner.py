"""
file_scanner.py
Scans folders, handles subfolder logic, and filters by file type.
"""

from pathlib import Path

def scan_folder(root_path, include_subfolders=True, file_types=None):
    """
    Return a list of paths that match the given file types.
    
    Parameters:
        root_path (str|Path): Directory to scan.
        include_subfolders (bool): Whether to recurse into subdirectories.
        file_types (list[str]): Extensions to include, e.g. ["mp4", "png"].
    """
    # TODO: implement scanning logic
    return []
