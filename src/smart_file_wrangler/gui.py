"""
gui.py

This module provides the graphical interface for the Smart File Wrangler tool.
The UI was built using Qt Designer (`main_window.ui`) and loaded at runtime.

Responsibilities:
- Let the user select a folder and organiser, thumbnail and report settings
- Run the pipeline without blocking the UI thread
- Display logs and progress updates
- Trigger FFmpeg installation when requested (restart required on Windows)

Constraints:
- Contains no media-processing business logic (handled by pipeline and subsystems)
- Does not modify features or behavior, only coordinates UI actions
"""

# ----------------------------------------------------------------------
# Standard library imports
# ----------------------------------------------------------------------
import sys
import subprocess
import io
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr

from PySide6.QtWidgets import QWidget, QMainWindow, QFileDialog, QApplication
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QThread, Signal, QObject, QPoint, QTimer, QFile, QIODevice

# ----------------------------------------------------------------------
# Local imports
# ----------------------------------------------------------------------

from smart_file_wrangler.config import Config
from smart_file_wrangler.pipeline import run_pipeline

# -----------------------------
# Build helper
# -----------------------------
def ui_resource_path(filename: str) -> Path:
    """
    Return the path to a bundled UI resource.

    - In dev:   <this_package_dir>/<filename>
    - Frozen:   <_MEIPASS>/smart_file_wrangler/<filename>
    """
    if hasattr(sys, "_MEIPASS"):  # PyInstaller
        return Path(sys._MEIPASS) / "smart_file_wrangler" / filename
    return Path(__file__).resolve().parent / filename

# -----------------------------
# Worker to run pipeline off the UI thread
# -----------------------------
class PipelineWorker(QObject):
    output = Signal(str)
    finished = Signal()
    failed = Signal(str)

    def __init__(self, folder: str, config: Config):
        super().__init__()
        self.folder = folder
        self.config = config

    def run(self):
        try:
            buf = io.StringIO()
            # Capture anything printed/logged to stdout/stderr during the run
            with redirect_stdout(buf), redirect_stderr(buf):
                run_pipeline(self.folder, self.config)

            text = buf.getvalue().strip()
            if text:
                self.output.emit(text)

            self.finished.emit()
        except Exception as e:
            self.failed.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.config = Config()
        self.folder = None
        # re-detect ffmpeg and sync to config
        try:
            subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            self.config.ffmpeg_available = True
        except Exception:
            self.config.ffmpeg_available = False


        # Load UI
        loader = QUiLoader()

        ui_path = ui_resource_path("main_window.ui")
        ui_file = QFile(str(ui_path))

        if not ui_file.open(QIODevice.ReadOnly):
            raise RuntimeError(f"Unable to open/read ui device: {ui_path}")

        self.ui = loader.load(ui_file)
        ui_file.close()

        if self.ui is None:
            raise RuntimeError(f"Failed to load UI file: {ui_path}")

        self.setCentralWidget(self.ui)
        self.ui.log_box.setMinimumHeight(120)

        #self.debug_tree()

        # Wire signals
        self.ui.select_folder_btn.clicked.connect(self.pick_folder)
        self.ui.run_btn.clicked.connect(self.on_run_clicked)
        self.ui.organise_mode_combo.currentTextChanged.connect(self.on_mode_changed)
        self.ui.expand_log_check.toggled.connect(self.on_toggle_log)

        # Initial UI state
        self.ui.ffmpeg_btn.clicked.connect(self.install_ffmpeg)
        self.apply_ffmpeg_status()
        self.on_mode_changed(self.ui.organise_mode_combo.currentText())
        self.on_toggle_log(self.ui.expand_log_check.isChecked())

        # Progress bar initial (not running)
        self.ui.progressBar.setRange(0, 1)
        self.ui.progressBar.setValue(0)

        # Thread handles
        self._thread = None
        self._worker = None

        self.show()
        self.on_toggle_log(self.ui.expand_log_check.isChecked())
        QTimer.singleShot(0, lambda: self._resize_to_widget_bottom(self.ui.progressBar))



    def _resize_to_widget_bottom(self, widget, padding=24):
        # bottom-left of widget in MainWindow coordinate space
        bottom_left = widget.mapTo(self, QPoint(0, widget.height()))
        self.resize(self.width(), bottom_left.y() + padding)



    # -----------------------------
    # UI helpers
    # -----------------------------
    def apply_ffmpeg_status(self):
        if self.config.ffmpeg_available:
            self.ui.ffmpeg_label.setText("FFmpeg installed")
            self.ui.ffmpeg_label.setStyleSheet("color: green;")
            self.ui.ffmpeg_btn.setEnabled(False)
            self.ui.ffmpeg_btn.setVisible(False)
        else:
            self.ui.ffmpeg_label.setText("FFmpeg not installed")
            self.ui.ffmpeg_label.setStyleSheet("color: red;")
            self.ui.ffmpeg_btn.setEnabled(True)
            self.ui.ffmpeg_btn.setVisible(True)

    def on_mode_changed(self, text: str):
        # Combo items are: "media type", "file extension", "name rule"
        is_name_rule = text.strip().lower() == "name rule"
        self.ui.organise_string_combo.setVisible(is_name_rule)
        self.ui.organise_string_lineedit.setVisible(is_name_rule)

    def on_toggle_log(self, checked: bool):
        self.config.expand_log = checked

        if checked:
            self.ui.log_widget.setVisible(True)
            self.ui.log_widget.setFixedHeight(240)  # was setMaximumHeight(240)
            #QTimer.singleShot(0, lambda: self._resize_to_widget_bottom(self.ui.log_widget))
            QTimer.singleShot(0, lambda: self.resize(self.width(), 800))
            self.ui.log_widget.raise_()

        else:
            self.ui.log_widget.setFixedHeight(0)    # was setMaximumHeight(0)
            self.ui.log_widget.setVisible(False)
            QTimer.singleShot(0, lambda: self._resize_to_widget_bottom(self.ui.progressBar))

    def debug_tree(self, widget=None, indent=0):
        if widget is None:
            widget = self.ui
        print("  " * indent + f"- {widget.objectName()} ({type(widget).__name__})")
        for child in widget.children():
            if isinstance(child, QWidget):
                self.debug_tree(child, indent + 1)



    def pick_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder = folder
            self.ui.select_folder_label.setText(folder)
            self.ui.select_folder_label.setVisible(True)

    def install_ffmpeg(self):
        import platform
        import subprocess
        import webbrowser

        system = platform.system()

        try:
            if system == "Windows":
                subprocess.run(["winget", "install", "-e", "--id", "Gyan.FFmpeg"], check=True)

            elif system == "Darwin":  # macOS
                subprocess.run(["brew", "install", "ffmpeg"], check=True)

            elif system == "Linux":
                subprocess.run(["apt", "update"], check=True)
                subprocess.run(["apt", "install", "-y", "ffmpeg"], check=True)

            else:
                raise RuntimeError("Unsupported OS for automatic FFmpeg install")

            # expand log and disable Run button to force restart after install
            self.ui.expand_log_check.setChecked(True)
            self.ui.run_btn.setEnabled(False)  # Run stays disabled until restart
            self.ui.log_box.append(f"FFmpeg installed successfully on {system}. Please restart the app to continue.")

        except Exception:
            webbrowser.open("https://ffmpeg.org/download.html")
            self.ui.expand_log_check.setChecked(True)
            self.ui.log_box.append("Please install FFmpeg manually, then restart the app.")


    # -----------------------------
    # Config wiring (UI -> Config)
    # -----------------------------
    def read_ui_into_config(self):
        c = self.config

        # scanning
        c.recurse_subfolders = self.ui.recurse_subfolders_check.isChecked()

        # logging
        c.expand_log = self.ui.expand_log_check.isChecked()
        c.verbose = self.ui.log_verbose_check.isChecked()

        # organiser
        c.enable_organiser = self.ui.organise_enable_check.isChecked()
        
        # map dropdown text to backend organiser_mode
        mode = self.ui.organise_mode_combo.currentText().strip().lower()
        if mode == "media type":
            c.organiser_mode = "media_type"
        elif mode == "file extension":
            c.organiser_mode = "extension"
        elif mode == "name rule":
            c.organiser_mode = "string_rule"

        # Capture rule string from UI when in string_rule mode
        if c.organiser_mode == "string_rule":
            rule_text = self.ui.organise_string_lineedit.text().strip().lower()
            if rule_text:
                c.filename_rules = [{"type": self.ui.organise_string_combo.currentText().strip().lower(), "value": rule_text}]
            else:
                c.filename_rules = []  

        c.move_files = self.ui.organise_move_radio.isChecked()

        # thumbnails
        c.generate_thumbnails = self.ui.thumbnails_enable_check.isChecked()
        c.thumb_images = self.ui.thumbnails_images_check.isChecked()
        c.thumb_videos = self.ui.thumbnails_videos_check.isChecked()
        c.thumb_suffix = self.ui.thumbnails_suffix_lineedit.text().strip() or c.thumb_suffix

        # thumb size from combo (strings like "512")
        try:
            c.thumb_size = int(self.ui.thumbnails_size_combo.currentText())
        except ValueError:
            pass  # keep existing default

        # reports
        reports_enabled = self.ui.reports_enable_check.isChecked()
        if reports_enabled:
            c.output_csv = self.ui.reports_csv_check.isChecked()
            c.output_json = self.ui.reports_json_check.isChecked()
            c.output_excel = self.ui.reports_excel_check.isChecked()
            c.output_tree = self.ui.reports_tree_check.isChecked()
        else:
            c.output_csv = False
            c.output_json = False
            c.output_excel = False
            c.output_tree = False

    # -----------------------------
    # Run handling
    # -----------------------------
    def on_run_clicked(self):
        if not self.folder:
            self.ui.log_box.append("No folder selected!")
            return

        # Update Config from UI
        self.read_ui_into_config()

        # Clear log for new run
        self.ui.log_box.clear()

        # Start progress animation
        self.ui.progressBar.setRange(0, 0)  # indeterminate/spinning

        # Disable run button while running
        self.ui.run_btn.setEnabled(False)

        # Start worker thread
        self._thread = QThread()
        self._worker = PipelineWorker(self.folder, self.config)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.output.connect(self.append_log)
        self._worker.failed.connect(self.on_failed)
        self._worker.finished.connect(self.on_finished)

        # Cleanup
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(self._cleanup_worker)

        self._thread.start()

    def append_log(self, text: str):
        # Preserve formatting
        self.ui.log_box.append(text)

    def on_failed(self, msg: str):
        self.ui.log_box.append(f"ERROR: {msg}")
        self.on_finished()

    def on_finished(self):
        # Stop progress animation
        self.ui.progressBar.setRange(0, 1)
        self.ui.progressBar.setValue(1)
        self.ui.run_btn.setEnabled(True)

    def _cleanup_worker(self):
        self._worker = None
        self._thread = None


class SmartFileWranglerGUI:
    def launch_gui(self):
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())


def launch_gui():
    SmartFileWranglerGUI().launch_gui()


if __name__ == "__main__":
    launch_gui()
