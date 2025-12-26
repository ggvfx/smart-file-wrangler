"""
gui.py
UI layer for Smart File Wrangler.
"""
import sys
import shutil
from pathlib import Path

from .config import Config
from .pipeline import run_pipeline

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton,
    QFileDialog, QTextEdit, QLabel, QProgressBar
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart File Wrangler")
        self.resize(500, 340)

        # 1) Construct Config once (public contract for GUI → backend)
        self.config = Config()

        # 2) Detect FFmpeg once on UI construction
        self.ffmpeg_exists = shutil.which("ffmpeg") is not None

        # --- UI widgets (will later be replaced by Designer .ui) ---

        # Folder picker
        self.pick_btn = QPushButton("Pick Folder", self)
        self.pick_btn.move(20, 20)
        self.pick_btn.clicked.connect(self.pick_folder)

        # Run pipeline button
        self.run_btn = QPushButton("Run Pipeline", self)
        self.run_btn.move(20, 60)
        self.run_btn.clicked.connect(self.on_run)

        # Cancel button (disabled until backend cancel is implemented)
        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.move(140, 60)
        self.cancel_btn.setEnabled(False)

        # FFmpeg status label
        self.ffmpeg_label = QLabel(self, text="")
        self.ffmpeg_label.move(20, 100)
        self.update_ffmpeg_label()

        # Install FFmpeg button (only enabled if missing)
        self.ffmpeg_install_btn = QPushButton("Install FFmpeg", self)
        self.ffmpeg_install_btn.move(20, 130)
        self.ffmpeg_install_btn.setEnabled(not self.ffmpeg_exists)
        self.ffmpeg_install_btn.clicked.connect(self.install_ffmpeg)

        # Progress bar (indeterminate for now)
        self.progress = QProgressBar(self)
        self.progress.move(20, 180)
        self.progress.resize(460, 20)
        self.progress.setRange(0, 0)  # spinning bar mode

        # Log box (read-only, expandable)
        self.log_box = QTextEdit(self)
        self.log_box.move(20, 220)
        self.log_box.resize(460, 100)
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumHeight(0)  # start hidden

        self.folder = None

    # ------------------------------------------------------------
    # GUI callbacks
    # ------------------------------------------------------------

    def update_ffmpeg_label(self):
        status = "Installed" if self.ffmpeg_exists else "Not Found"
        self.ffmpeg_label.setText(f"FFmpeg: {status}")

    def update_ffmpeg_label(self):
        self.ffmpeg_label.setText(
            "FFmpeg: Installed" if self.ffmpeg_exists else "FFmpeg: Not Found"
        )

    def pick_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Process")
        if folder:
            self.folder = folder
            self.log_box.append(f"Folder selected: {folder}")

    def on_run(self):
        if not self.folder:
            self.log_box.append("No folder selected!")
            return

        # Apply expand_log flag from Config
        if self.config.expand_log:
            self.log_box.setMaximumHeight(160)
        else:
            self.log_box.setMaximumHeight(0)

        self.log_box.append("Running pipeline...")

        # Call backend entrypoint (GUI owns no core logic)
        try:
            run_pipeline(folder_path=self.folder, config=self.config)
            self.log_box.append("Pipeline executed!")
        except Exception as e:
            self.log_box.append(f"Error: {e}")

    def install_ffmpeg(self):
        # Beginner-friendly: open official download page
        import webbrowser
        webbrowser.open("https://ffmpeg.org/download.html")
        self.log_box.append("Opened FFmpeg download page.")

    # Optional: GUI can update Config fields from UI later
    # (checkboxes, dropdowns etc will connect here after Designer)


class SmartFileWranglerGUI:
    """Launch the PySide6 GUI."""

    def launch_gui(self):
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())


def launch_gui():
    """Manual launch entrypoint for GUI."""
    SmartFileWranglerGUI().launch_gui()

if __name__ == "__main__":
    launch_gui()


