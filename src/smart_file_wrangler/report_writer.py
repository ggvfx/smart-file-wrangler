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
    Build a friendly filename for frame sequences like:
    sample-frameSeq.[1000-1005].png
    """
    frame_count = metadata.get("frame_count")
    middle_frame = metadata.get("middle_frame_number")
    ext = metadata.get("extension", "")
    start_frame = metadata.get("start_frame")
    end_frame = metadata.get("end_frame")
    base_name = Path(metadata.get("file_path", "")).name

    if start_frame is not None and end_frame is not None:
        return f"{base_name}.[{start_frame}-{end_frame}]{ext}"


    # If we don't have sequence info, fall back to the basename of file_path
    file_path = metadata.get("file_path", "")
    base_name = Path(file_path).name if file_path else "sequence"

    # If we have frame_count and middle_frame, try to infer range from file_path if possible
    # (Better: later we can pass frames start/end explicitly)
    # For now: keep it simple and readable.
    if frame_count and middle_frame:
        return f"{base_name}.[seq]{ext}"

    return f"{base_name}{ext}"


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
    from .config import Defaults

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

            output_row = {k: output_row.get(k) for k in header}
            writer.writerow(output_row)

    # Helpful success message
    print(f'CSV report written: "{output_path}" ({len(data)} rows)')


def write_json_report(data, output_path, fields):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    filtered = [
        {field: item.get(field) for field in fields}
        for item in data
    ]

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(filtered, f, indent=2)


def write_folder_tree(root_path, output_path):
    root_path = Path(root_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = []

    for path in sorted(root_path.rglob("*")):
        indent = "│   " * (len(path.relative_to(root_path).parts) - 1)
        prefix = "├─ "
        lines.append(f"{indent}{prefix}{path.name}")

    with output_path.open("w", encoding="utf-8") as file:
        file.write("\n".join(lines))


def sort_report_items(data, root_folder):
    def sort_key(item):
        # relative path
        rel_path = Path(item["file_path"])

        # folder depth (top-level first)
        depth = len(rel_path.parts) - 1

        # parent folder name
        parent = rel_path.parent.as_posix()

        # filename
        filename = item.get("filename", "")

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
            fields
        )

    if tree_enabled:
        write_folder_tree(
            input_folder,
            Path(output_dir) / "folder_tree.txt"
        )




