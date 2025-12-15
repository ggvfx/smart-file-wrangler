"""
organiser.py
Moves or copies files into structured folders.
Supports:
- Organising by media type (image, video, audio, other)
- Organising by file extension
- Organising by user-defined string rules ("contains", "starts_with")
- Recursive subfolder creation
- Handling files not matching any rule (put in "unsorted")
- Optional verbose logging with summary
"""

from pathlib import Path
from shutil import copy2, move
from .file_scanner import scan_folder
from .metadata_reader import extract_metadata
from .config import Defaults
from .utils import group_frame_sequences


def organise_files(folder_path, output_dir=None, move_files=None, mode="extension", rules=None, default_folder="unsorted"):
    """
    Process files in a folder into structured subfolders.

    Parameters:
        folder_path (Path | str): Base folder to scan files from.
        output_dir (Path | str | None): Base output directory. Defaults to the input folder.
        move_files (bool | None): Move instead of copy. Defaults to Defaults["move_files"].
        mode (str): How to organise files: "media_type", "extension", "string_rule".
        rules (list[dict] | None): User-defined rules for string_rule mode.
        default_folder (str): Folder for files that don't match any rule or have no extension.
    """

    if not Defaults.get("enable_organiser", True):
        if Defaults.get("verbose", True):
            print("Organiser disabled — skipping file moves/copies")
        return

    folder_path = Path(folder_path)
    if not folder_path.is_dir():
        raise ValueError(f"{folder_path} is not a valid directory")

    if output_dir is None:
        output_dir = folder_path
    output_dir = Path(output_dir)

    if move_files is None:
        move_files = Defaults["move_files"]

    #Scan all files in folder (recursively if enabled)
    file_list = scan_folder(folder_path, include_subfolders=Defaults["recurse_subfolders"])

    #Optionally combine frame sequences into single items
    if Defaults.get("combine_frame_seq", True):
        # group_frame_sequences returns a list where each item is either:
        # - Path object (regular file)
        # - dict {"basename": ..., "ext": ..., "frames": [...]}
        file_list = group_frame_sequences(file_list)

    created_folders = set()
    processed_files = 0

    #Process each item (frame sequence or regular file)
    for item in file_list:
        matched_rule = None  # used for logging string_rule matches

        # Handle frame sequences
        if isinstance(item, dict) and "frames" in item:
            seq_name = f"{item['basename']}.{item['frames'][0]}-{item['frames'][-1]}{item['ext']}"

            # REPLACE HERE: dynamically use extension as folder name
            ext_folder_name = item['ext'].lstrip(".").lower()
            dest_folder = item["folder"] / ext_folder_name

            # Create destination folder if it doesn't exist
            if not dest_folder.exists():
                dest_folder.mkdir(parents=True, exist_ok=True)
                created_folders.add(dest_folder.name)
                if Defaults["verbose"]:
                    print(f'created folder: "{dest_folder}"')

            # Copy/move each frame individually
            frames_copied = 0
            for frame_number in item["frames"]:
                separator = item.get("separator", ".")
                frame_file_name = f"{item['basename']}{separator}{frame_number}{item['ext']}"
                src_file = item["folder"] / frame_file_name
                dst_file = dest_folder / frame_file_name

                if not src_file.exists():
                    if Defaults["verbose"]:
                        print(f"skipping missing frame: {src_file}")
                    continue

                if move_files:
                    move(src_file, dst_file)
                    action = "moved"
                else:
                    copy2(src_file, dst_file)
                    action = "copied"

                frames_copied += 1
                if Defaults["verbose"]:
                    print(f'{action} "{src_file}" → folder "{dest_folder.name}"')


            if frames_copied > 0:
                processed_files += 1
                if Defaults["verbose"]:
                    print(f'processed frame sequence: "{seq_name}" ({frames_copied} frames) → folder "{dest_folder.name}"')


        #Handle regular files
        else:
            file_path = item
            file_path_to_move = file_path
            destination_folder = None
            file_name_lower = file_path.name.lower()

            # Determine folder based on string rules if enabled
            if mode == "string_rule" and rules:
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
                if not destination_folder:
                    destination_folder = default_folder

            # Determine folder based on file extension
            elif mode == "extension":
                if file_path.suffix:
                    destination_folder = file_path.suffix.lower().lstrip(".")
                else:
                    destination_folder = default_folder

            # Determine folder based on media type metadata
            elif mode == "media_type":
                metadata = extract_metadata(file_path)
                destination_folder = metadata.get("media_type", "other")
                if destination_folder not in ["image", "video", "audio", "other"]:
                    destination_folder = "other"

            else:
                raise ValueError(f"unknown organise mode: {mode}")

            # Determine parent folder based on recurse setting
            parent_for_file = file_path.parent if Defaults["recurse_subfolders"] else output_dir
            final_folder_path = parent_for_file / destination_folder

            # Create folder if it doesn’t exist
            if not final_folder_path.exists():
                final_folder_path.mkdir(parents=True, exist_ok=True)
                created_folders.add(destination_folder)
                if Defaults["verbose"]:
                    print(f'created folder: "{final_folder_path}"')

            # Full destination path for copy/move
            destination_file_path = final_folder_path / file_path.name

            # Move or copy the file
            if move_files and file_path_to_move:
                move(file_path_to_move, destination_file_path)
                action = "moved"
            elif file_path_to_move:
                copy2(file_path_to_move, destination_file_path)
                action = "copied"

            processed_files += 1

            # Verbose logging
            if Defaults["verbose"]:
                if matched_rule:
                    print(f'{action} "{file_path}" → folder "{destination_folder}" (matched rule: {matched_rule})')
                else:
                    print(f'{action} "{file_path}" → folder "{destination_folder}"')

    # Print summary
    print(f"\nmove/copy complete")
    print(f"total files processed: {processed_files}")
    print(f"folders created: {len(created_folders)} -> {', '.join(sorted(created_folders))}")
