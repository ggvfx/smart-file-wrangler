"""
organiser.py

Moves or copies files into structured folders.

Supports:
- Organising by media type (image, video, audio, other)
- Organising by file extension
- Organising by user-defined string rules ("contains", "starts_with")
- Recursive subfolder creation
- Handling unmatched files (placed in a default folder)
- Optional verbose logging with summary output
"""

from pathlib import Path
from shutil import copy2, move

from .file_scanner import scan_folder
from .metadata_reader import extract_metadata
from .config import Defaults, Config
from .utils import group_frame_sequences
from .logger import init_logger


def organise_files(
    folder_path,
    output_dir=None,
    move_files=None,
    mode=None,
    rules=None,
    default_folder=None,
    ignore_thumbnails=False,
    config=None,
):
    """
    Organise files in a folder into structured subfolders.

    Args:
        folder_path (Path | str): Base folder to scan.
        output_dir (Path | str | None): Output directory. Defaults to input folder.
        move_files (bool | None): Move files instead of copying.
            Must be resolved from Config or passed explicitly.
        mode (str): Organisation mode:
            - "media_type"
            - "extension"
            - "string_rule"
        rules (list[dict] | None): String-matching rules for "string_rule" mode.
        default_folder (str): Folder name for files that match no rule.
        ignore_thumbnails (bool): Whether to skip thumbnail folders when scanning.
    """

    # Resolve values from config if provided
    if config is not None:
        if move_files is None:
            move_files = config.move_files
        if mode is None:
            mode = config.organiser_mode
        if rules is None:
            rules = config.filename_rules
        if default_folder is None:
            default_folder = config.default_unsorted_folder

    if config is None:
        raise ValueError(
            "organise_files() now requires a Config object. "
            "Pipeline must pass config explicitly."
        )

    # --------------------------------------------------------------
    # Early exit if organiser is disabled
    # --------------------------------------------------------------

    folder_path = Path(folder_path)
    if not folder_path.is_dir():
        raise ValueError(f"{folder_path} is not a valid directory")

    # Resolve output directory
    if output_dir is None:
        output_dir = folder_path
    output_dir = Path(output_dir)

    # Resolve move vs copy behavior
    if move_files is None:
        raise ValueError(
            "move_files was not resolved from config or arguments"
    )


    # --------------------------------------------------------------
    # Scan files from input folder
    # --------------------------------------------------------------
    # Uses global recursion and thumbnail ignore rules
    file_list = scan_folder(
        folder_path,
        include_subfolders=config.recurse_subfolders,
        ignore_thumbnails=ignore_thumbnails,
    )

    # Optionally group frame sequences into logical items
    if config.combine_frame_seq:
        # Each item is either:
        # - Path (regular file)
        # - dict describing a frame sequence
        file_list = group_frame_sequences(file_list)

    created_folders = set()
    processed_files = 0

    # --------------------------------------------------------------
    # Process each item
    # --------------------------------------------------------------
    for item in file_list:
        matched_rule = None  # used only for logging string-rule matches

        # ----------------------------------------------------------
        # Skip files inside thumbnail folders
        # ----------------------------------------------------------
        if isinstance(item, dict) and "frames" in item:
            # Use the first frame to determine sequence location
            item_path = Path(item["folder"])
        else:
            item_path = Path(item)

        if config.ignore_thumbnail_folders:
            if config.thumb_folder_name in item_path.parts:
                if config.verbose:
                    print(f'skipping thumbnail item: "{item_path}"')
                continue

        # ==========================================================
        # FRAME SEQUENCES
        # ==========================================================
        # Handle frame sequences
        if isinstance(item, dict) and "frames" in item:
            frames = item["frames"]
            folder = item["folder"]
            basename = item["basename"]
            extension = item["ext"]
            separator = item.get("separator", ".")

            seq_name = f"{basename}.{frames[0]}-{frames[-1]}{extension}"
            seq_name_lower = seq_name.lower()

            destination_folder = None
            matched_rule = None

            # Determine folder based on string rules if enabled
            if mode == "string_rule" and rules:
                for rule in rules:
                    rule_type = rule.get("type")
                    rule_value = rule.get("value", "").lower()

                    if rule_type == "contains" and rule_value in seq_name_lower:
                        destination_folder = rule_value
                        matched_rule = f'contains "{rule_value}"'
                        break
                    elif rule_type == "starts_with" and seq_name_lower.startswith(rule_value):
                        destination_folder = rule_value
                        matched_rule = f'starts_with "{rule_value}"'
                        break

                if not destination_folder:
                    destination_folder = default_folder

            # Determine folder based on file extension
            elif mode == "extension":
                if extension:
                    destination_folder = extension.lstrip(".").lower()
                else:
                    destination_folder = default_folder

            # Determine folder based on media type metadata
            elif mode == "media_type":
                metadata = extract_metadata(item)
                destination_folder = metadata.get("media_type", "other")
                if destination_folder not in ["image", "video", "audio", "other"]:
                    destination_folder = "other"

            else:
                raise ValueError(f"unknown organise mode: {mode}")

            # Determine parent folder based on recurse setting
            parent_for_item = folder if config.recurse_subfolders else output_dir
            dest_folder = parent_for_item / destination_folder

            # Create destination folder if it doesn't exist
            if not dest_folder.exists():
                dest_folder.mkdir(parents=True, exist_ok=True)
                created_folders.add(dest_folder.name)
                if config.verbose:
                    print(f'created folder: "{dest_folder}"')

            # Copy/move each frame individually
            frames_copied = 0
            for frame_number in frames:
                frame_file_name = f"{basename}{separator}{frame_number}{extension}"
                src_file = folder / frame_file_name
                dst_file = dest_folder / frame_file_name

                if not src_file.exists():
                    if config.verbose:
                        print(f"skipping missing frame: {src_file}")
                    continue

                if move_files:
                    move(src_file, dst_file)
                    action = "moved"
                else:
                    copy2(src_file, dst_file)
                    action = "copied"

                frames_copied += 1
                if config.verbose:
                    if matched_rule:
                        print(
                            f'{action} "{src_file}" → folder "{dest_folder.name}" '
                            f"(matched rule: {matched_rule})"
                        )
                    else:
                        print(f'{action} "{src_file}" → folder "{dest_folder.name}"')

            if frames_copied > 0:
                processed_files += 1
                if config.verbose:
                    if matched_rule:
                        print(
                            f'processed frame sequence: "{seq_name}" ({frames_copied} frames) '
                            f'→ folder "{dest_folder.name}" (matched rule: {matched_rule})'
                        )
                    else:
                        print(
                            f'processed frame sequence: "{seq_name}" ({frames_copied} frames) '
                            f'→ folder "{dest_folder.name}"'
                        )


        # ==========================================================
        # REGULAR FILES
        # ==========================================================
        else:
            file_path = item
            file_name_lower = file_path.name.lower()
            destination_folder = None

            # ------------------------------------------------------
            # String rule mode
            # ------------------------------------------------------
            if mode == "string_rule" and rules:
                for rule in rules:
                    rule_type = rule.get("type")
                    rule_value = rule.get("value", "").lower()

                    if rule_type == "contains" and rule_value in file_name_lower:
                        destination_folder = rule_value
                        matched_rule = f'contains "{rule_value}"'
                        break

                    elif (
                        rule_type == "starts_with"
                        and file_name_lower.startswith(rule_value)
                    ):
                        destination_folder = rule_value
                        matched_rule = f'starts_with "{rule_value}"'
                        break

                if not destination_folder:
                    destination_folder = default_folder

            # ------------------------------------------------------
            # Extension-based mode
            # ------------------------------------------------------
            elif mode == "extension":
                if file_path.suffix:
                    destination_folder = file_path.suffix.lower().lstrip(".")
                else:
                    destination_folder = default_folder

            # ------------------------------------------------------
            # Media-type-based mode
            # ------------------------------------------------------
            elif mode == "media_type":
                metadata = extract_metadata(file_path)
                destination_folder = metadata.get("media_type", "other")

                if destination_folder not in ["image", "video", "audio", "other"]:
                    destination_folder = "other"

            else:
                raise ValueError(f"unknown organise mode: {mode}")

            # ------------------------------------------------------
            # Determine final destination folder
            # ------------------------------------------------------
            parent_for_file = (
                file_path.parent
                if config.recurse_subfolders
                else output_dir
            )
            final_folder_path = parent_for_file / destination_folder

            if not final_folder_path.exists():
                final_folder_path.mkdir(parents=True, exist_ok=True)
                created_folders.add(destination_folder)
                if config.verbose:
                    print(f'created folder: "{final_folder_path}"')

            destination_file_path = final_folder_path / file_path.name

            # Move or copy the file
            if move_files:
                move(file_path, destination_file_path)
                action = "moved"
            else:
                copy2(file_path, destination_file_path)
                action = "copied"

            processed_files += 1

            if config.verbose:
                if matched_rule:
                    print(
                        f'{action} "{file_path}" → folder "{destination_folder}" '
                        f"(matched rule: {matched_rule})"
                    )
                else:
                    print(
                        f'{action} "{file_path}" → folder "{destination_folder}"'
                    )

    # --------------------------------------------------------------
    # Summary
    # --------------------------------------------------------------
    print("\nmove/copy complete")
    print(f"total files processed: {processed_files}")
    print(
        f"folders created: {len(created_folders)} -> "
        f"{', '.join(sorted(created_folders))}"
    )
