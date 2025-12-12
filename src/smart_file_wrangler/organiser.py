"""
organiser.py
Moves or copies files into structured folders.
Can be called independently for selective workflow.
Supports:
- Organising by file type
- Organising by user-defined string rules ("contains", "starts with")
- Recursive subfolder creation
- Handling files not matching any rule (put in "unsorted")
"""

from pathlib import Path
from shutil import copy2, move

def organise_files(file_list, output_dir, move_files=False, rules=None, default_folder="unsorted"):
    """
    Process files into structured folders.

    Parameters:
        file_list (list[Path]): Files to organise.
        output_dir (Path): Base output directory.
        move_files (bool): Move instead of copy.
        rules (list[dict] | None): List of user-defined rules, e.g.:
            [{"type": "contains", "value": "holiday"}, {"type": "starts_with", "value": "IMG"}]
        default_folder (str): Folder for files that don't match any rule.
    """
    # TODO: implement sorting logic according to rules and type
    # TODO: create subfolders recursively if needed
    pass
