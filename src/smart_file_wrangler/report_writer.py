"""
report_writer.py
Generates CSV/JSON reports or folder tree output.
Can be used independently (report-only workflow).
“Fields may be empty if metadata could not be extracted.”
"""

import csv
import json
from pathlib import Path
from .config import Defaults
from collections import defaultdict

media_type_order = {
    "video": 0,
    "image": 1,
    "audio": 2,
    "other": 3,
}


def make_relative_path(path_string, root_folder):
    """
    Convert an absolute path string to a path relative to root_folder.
    If conversion fails, fall back to the original string.
    """
    if not path_string:
        return ""

    try:
        return str(Path(path_string).resolve().relative_to(Path(root_folder).resolve()))
    except Exception:
        return path_string
    

def make_sequence_filename(metadata):
    """
    Return the filename for reporting.

    For frame sequences, the filename is already fully constructed
    in metadata_reader.py and stored in metadata["filename"].

    For normal files, this is just the filename.
    """
    return metadata.get("filename", "")



def sort_metadata(data, sort_by=None, reverse=False):
    if not sort_by:
        return data
    return sorted(
        data,
        key=lambda item: item.get(sort_by) or "",
        reverse=reverse
    )


def write_csv_report(data, output_path, root_folder):
    """
    Write report data to a CSV file.

    - Adds a 'filename' column first
    - Converts file_path to a relative path from root_folder
    - Uses Defaults["metadata_fields"] to decide what fields to include (except filename)
    """

    output_path = Path(output_path)

    # Decide CSV column order
    # filename always first, then file_path, then the rest
    selected_fields = list(Defaults.get("metadata_fields", []))

    # Ensure file_path exists in selected fields (you want it)
    if "file_path" not in selected_fields:
        selected_fields.insert(0, "file_path")

    # Build final header order
    header = ["filename"] + [f for f in selected_fields if f != "filename"]

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()

        for row in data:
            # Convert absolute file_path to relative
            original_path = row.get("file_path", "")
            relative_path = make_relative_path(original_path, root_folder)

            # Build filename
            # If it's a sequence row, you marked media_type="video" and include frame_count/middle_frame_number
            if row.get("frame_count"):
                filename = make_sequence_filename(row)
            else:
                filename = Path(original_path).name if original_path else ""

            output_row = dict(row)
            output_row["file_path"] = relative_path
            output_row["filename"] = filename

            # Convert file size to human-readable form
            size_bytes = row.get("file_size_bytes")
            if size_bytes is not None:
                output_row["file_size"] = format_file_size(size_bytes) if size_bytes is not None else ""
            else:
                output_row["file_size"] = ""

            output_row = {k: output_row.get(k, "") for k in header}
            writer.writerow(output_row)

    # Helpful success message
    print(f'CSV report written: "{output_path}" ({len(data)} rows)')


def write_json_report(data, output_path, root_folder):
    """
    Write report data to a JSON file.

    Matches CSV output:
    - filename field
    - relative file_path
    - human-readable file_size
    """

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_rows = []

    for row in data:
        original_path = row.get("file_path", "")
        relative_path = make_relative_path(original_path, root_folder)

        # filename
        if row.get("frame_count"):
            filename = make_sequence_filename(row)
        else:
            filename = Path(original_path).name if original_path else ""

        output_row = dict(row)

        # replace fields for output
        output_row["filename"] = filename
        output_row["file_path"] = relative_path

        # format size
        size_bytes = row.get("file_size_bytes")
        output_row["file_size"] = format_file_size(size_bytes)

        # remove raw bytes (JSON should be clean)
        output_row.pop("file_size_bytes", None)

        # filter fields according to config
        filtered = {
            k: output_row.get(k)
            for k in ["filename"] + Defaults["metadata_fields"]
            if k in output_row
        }

        output_rows.append(filtered)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(output_rows, f, indent=2)

    print(f'JSON report written: "{output_path}" ({len(output_rows)} items)')


def build_tree(items):
    """
    Build a nested dict representing folder structure.
    """
    tree = defaultdict(dict)

    for item in items:
        path = Path(item["file_path"])
        parts = path.parts

        current = tree
        for part in parts[:-1]:
            current = current.setdefault(part, {})

        # file or sequence filename
        current[parts[-1]] = None

    return tree

def write_tree_lines(tree, indent=""):
    lines = []

    entries = sorted(tree.items())

    for i, (name, subtree) in enumerate(entries):
        is_last = i == len(entries) - 1
        branch = "└─ " if is_last else "├─ "
        lines.append(f"{indent}{branch}{name}")

        if isinstance(subtree, dict):
            extension = "   " if is_last else "│  "
            lines.extend(write_tree_lines(subtree, indent + extension))

    return lines


def write_folder_tree(items, output_path, root_folder):

    """
    Write a text-based folder tree.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    root_folder = Path(root_folder)
    root_name = root_folder.name


    relative_items = []
    for item in items:
        new_item = dict(item)
        new_item["file_path"] = str(
            Path(item["file_path"]).relative_to(root_folder)
        )
        relative_items.append(new_item)

    tree = build_tree(relative_items)
    lines = write_tree_lines(tree)
    lines = [root_name] + lines


    with output_path.open("w", encoding="utf-8") as tree_file:
        for line in lines:
            tree_file.write(line + "\n")

    print(f'Folder tree written: "{output_path}"')


def sort_report_items(data, root_folder):
    def sort_key(item):
        # relative path
        rel_path = Path(make_relative_path(item.get("file_path", ""), root_folder))

        # folder depth (top-level first)
        depth = len(rel_path.parts) - 1

        # parent folder name
        parent = rel_path.parent.as_posix()

        # filename
        if item.get("frame_count"):
            filename = make_sequence_filename(item)
        else:
            filename = Path(item.get("file_path", "")).name


        # media type order
        media_type = item.get("media_type", "other")
        media_order = media_type_order.get(media_type, 99)

        # extension
        extension = item.get("extension", "")

        return (
            depth,
            parent,
            filename.lower(),
            media_order,
            extension.lower(),
        )

    return sorted(data, key=sort_key)




def generate_reports(
    metadata,
    input_folder,
    output_dir,
    fields,
    sort_by=None,
    reverse=False,
    csv_enabled=False,
    json_enabled=False,
    tree_enabled=False,
):
    #sorted_data = sort_metadata(metadata, sort_by, reverse)
    sorted_data = sort_report_items(metadata, input_folder)
    

    if csv_enabled:
        write_csv_report(
            sorted_data,
            Path(output_dir) / "report.csv",
            root_folder=input_folder
        )

    if json_enabled:
        write_json_report(
            sorted_data,
            Path(output_dir) / "report.json",
            root_folder=input_folder
        )

    if tree_enabled:
        write_folder_tree(
            sorted_data,
            Path(output_dir) / "folder_tree.txt",
            root_folder=input_folder
        )




def format_file_size(bytes_value):

    if bytes_value is None:
        return ""
    
    bytes_value = int(bytes_value)

    if bytes_value < 1024:
        return f"{bytes_value} B"

    kb = bytes_value / 1024
    if kb < 1024:
        return f"{kb:.1f} KB"

    mb = kb / 1024
    if mb < 1024:
        return f"{mb:.2f} MB"

    gb = mb / 1024
    return f"{gb:.2f} GB"





