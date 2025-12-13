"""
organiser.py
Moves or copies files into structured folders.
Supports:
- Organising by file type
- Organising by user-defined string rules ("contains", "starts with")
- Recursive subfolder creation
- Handling files not matching any rule (put in "unsorted")
- Optional verbose logging with summary
"""

from pathlib import Path
from shutil import copy2, move
from .file_scanner import scan_folder
from .config import Defaults

def organise_files(folder_path, output_dir=None, move_files=None, rules=None, default_folder="unsorted"):
    """
    Process files in a folder into structured subfolders.

    Parameters:
        folder_path (Path | str): Base folder to scan files from.
        output_dir (Path | str | None): Base output directory. Defaults to the input folder.
        move_files (bool | None): Move instead of copy. Defaults to Defaults["move_files"].
        rules (list[dict] | None): User-defined rules for naming folders.
        default_folder (str): Folder for files that don't match any rule.
    """
    folder_path = Path(folder_path)
    if not folder_path.is_dir():
        raise ValueError(f"{folder_path} is not a valid directory")

    if output_dir is None:
        output_dir = folder_path
    output_dir = Path(output_dir)

    if move_files is None:
        move_files = Defaults["move_files"]

    # Scan folder using recurse_subfolders from Defaults
    file_list = scan_folder(
        folder_path, 
        include_subfolders=Defaults["recurse_subfolders"]
    )

    # Track created folders and processed files for summary
    created_folders = set()
    processed_files = 0

    for file_path in file_list:
        destination_folder = None
        file_name_lower = file_path.name.lower()
        matched_rule = None

        # Check user-defined rules first
        if rules:
            for rule in rules:
                rule_type = rule.get("type")
                rule_value = rule.get("value", "").lower()
                
                if rule_type == "contains" and rule_value in file_name_lower:
                    destination_folder = rule_value
                    matched_rule = f'contains "{rule_value}"'
                    break
                elif rule_type == "starts_with" and file_name_lower.startswith(rule_value):
                    destination_folder = rule_value
                    matched_rule = f'starts_with "{rule_value}"'
                    break

        # If no rule matched, organise by file extension
        if not destination_folder:
            if file_path.suffix:
                destination_folder = file_path.suffix.lower().lstrip(".")
            else:
                destination_folder = default_folder

        # Ensure the destination folder exists
        final_folder_path = output_dir / destination_folder
        if not final_folder_path.exists():
            final_folder_path.mkdir(parents=True, exist_ok=True)
            created_folders.add(destination_folder)
            if Defaults["verbose"]:
                print(f'created folder: "{final_folder_path}"')

        # Determine full destination file path
        destination_file_path = final_folder_path / file_path.name

        # Move or copy file
        if move_files:
            move(file_path, destination_file_path)
            action = "moved"
        else:
            copy2(file_path, destination_file_path)
            action = "copied"

        processed_files += 1

        # Verbose logging
        if Defaults["verbose"]:
            if matched_rule:
                print(f'{action} "{file_path}" → folder "{destination_folder}" (matched rule: {matched_rule})')
            else:
                print(f'{action} "{file_path}" → folder "{destination_folder}"')

    # Summary
    print(f"\nmove/copy complete")
    print(f"total files processed: {processed_files}")
    print(f"folders created: {len(created_folders)} -> {', '.join(sorted(created_folders))}")
