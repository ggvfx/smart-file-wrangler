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
from .file_scanner import scan_folder
from .config import Defaults

def organise_files(folder_path, output_dir=None, move_files=False, rules=None, default_folder="unsorted"):
    """
    Process files in a folder into structured subfolders.

    Parameters:
        folder_path (Path): Base folder to scan files from.
        output_dir (Path | None): Base output directory. Defaults to the input folder.
        move_files (bool): Move instead of copy.
        rules (list[dict] | None): User-defined rules for naming folders.
        default_folder (str): Folder for files that don't match any rule.
    """
    folder_path = Path(folder_path)
    if output_dir is None:
        output_dir = folder_path
    output_dir = Path(output_dir)

    # Get all files according to config's recurse setting
    file_list = scan_folder(folder_path, include_subfolders=Defaults["recurse_subfolders"])

    for file_path in file_list:
        destination_folder = None

        # Check user-defined rules first
        if rules:
            for rule in rules:
                rule_type = rule.get("type")
                rule_value = rule.get("value", "").lower()
                file_name_lower = file_path.name.lower()
                
                if rule_type == "contains" and rule_value in file_name_lower:
                    destination_folder = rule_value
                    break
                elif rule_type == "starts_with" and file_name_lower.startswith(rule_value):
                    destination_folder = rule_value
                    break

        # If no rule matched, organise by file type
        if not destination_folder:
            if file_path.suffix:
                destination_folder = file_path.suffix.lower().lstrip(".")
            else:
                destination_folder = default_folder

        # Ensure the destination folder exists
        final_folder_path = output_dir / destination_folder
        final_folder_path.mkdir(parents=True, exist_ok=True)

        # Determine full destination file path
        destination_file_path = final_folder_path / file_path.name

        # Move or copy file
        if move_files:
            move(file_path, destination_file_path)
        else:
            copy2(file_path, destination_file_path)
