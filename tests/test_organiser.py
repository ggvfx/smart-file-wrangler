"""
test_organiser.py
Quick test script for organiser.py
Tests all three modes: extension, media_type, string_rule
"""

import sys
from pathlib import Path

# add src folder to the module search path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pathlib import Path
from smart_file_wrangler.organiser import organise_files
from smart_file_wrangler.config import Defaults

# Enable verbose logging for testing
Defaults["verbose"] = True

# Sample folder containing files and subfolders
sample_folder = Path(__file__).parent.parent / "assets" / "sample_media"

# # 1. Test organising by extension
# print("\n--- Test: organise by extension ---")
# organise_files(
#     folder_path=sample_folder,
#     move_files=False,   # set True to move instead of copy
#     mode="extension"
# )

# # 2. Test organising by media_type
# print("\n--- Test: organise by media_type ---")
# organise_files(
#     folder_path=sample_folder,
#     move_files=False,
#     mode="media_type"
# )

# 3. Test organising by string rules
print("\n--- Test: organise by string_rule ---")
string_rules = [
    {"type": "starts_with", "value": "sample-"},
    {"type": "contains", "value": "video"}
]
organise_files(
    folder_path=sample_folder,
    move_files=False,
    mode="string_rule",
    rules=string_rules
)

print("\nTest complete. Check the sample_media folder for organised output.")
