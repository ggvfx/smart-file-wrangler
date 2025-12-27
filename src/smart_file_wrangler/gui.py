import sys
import shutil
import subprocess
from pathlib import Path

from .config import Config
from .pipeline import run_pipeline

from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QWidget
from PySide6.QtUiTools import QUiLoader

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.config = Config()
        self.folder = None
        self.ffmpeg_exists = shutil.which("ffmpeg") is not None

        # Load UI
        loader = QUiLoader()
        ui_file = Path(__file__).parent / "main_window.ui"
        self.ui = loader.load(str(ui_file))
        self.setCentralWidget(self.ui)

        # Make window match UI size
        self.resize(self.ui.size())

        # FFmpeg status + install button visibility
        if self.ffmpeg_exists:
            self.ui.ffmpeg_label.setText("FFmpeg installed")
        else:
            self.ui.ffmpeg_label.setText("FFmpeg not installed")

        self.ui.ffmpeg_label.setVisible(True)
        self.ui.ffmpeg_btn.setVisible(not self.ffmpeg_exists)
        self.ui.ffmpeg_btn.setEnabled(True)
        self.ui.ffmpeg_btn.clicked.connect(self.install_ffmpeg)

        # Log section collapsed on start
        self.ui.log_widget.setVisible(False)
        self.ui.expand_log_check.toggled.connect(self.on_toggle_log)
        self.ui.organise_mode_combo.currentTextChanged.connect(self.on_mode_changed)
        self.ui.select_folder_btn.clicked.connect(self.pick_folder)
        self.ui.run_btn.clicked.connect(self.on_run)

    def pick_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder = folder
            self.ui.select_folder_label.setText(folder)

    def on_toggle_log(self, checked):
        self.config.expand_log = checked
        self.ui.log_widget.setVisible(checked)

    def on_mode_changed(self, text):
        name_rule = text.lower() == "name rule"
        self.ui.organise_string_combo.setVisible(name_rule)
        self.ui.organise_string_lineedit.setVisible(name_rule)

    def on_run(self):
        if not self.folder:
            self.ui.log_box.append("No folder selected!")
            return
        
        # Run CLI and capture terminal output
        result = subprocess.run(
            ["python", "-m", "smart_file_wrangler.cli", "-i", self.folder],
            capture_output=True,
            text=True
        )

        # Send captured CLI output into UI log box
        self.ui.log_box.append(result.stdout)

        # --- READ UI VALUES INTO CONFIG (this is the wiring you were missing) ---
        self.config.recurse_subfolders = self.ui.recurse_subfolders_check.isChecked()
        self.config.expand_log = self.ui.expand_log_check.isChecked()

        self.config.enable_organiser = self.ui.organise_enable_check.isChecked()
        self.config.organise_mode = self.ui.organise_mode_combo.currentText()
        self.config.organise_action = "copy" if self.ui.organise_copy_radio.isChecked() else "move"

        self.config.organise_string_mode = self.ui.organise_string_combo.currentText()
        self.config.organise_string = self.ui.organise_string_lineedit.text()

        self.config.generate_thumbnails = self.ui.thumbnails_enable_check.isChecked()
        self.config.thumbnail_for_videos = self.ui.thumbnails_videos_check.isChecked()
        self.config.thumbnail_for_images = self.ui.thumbnails_images_check.isChecked()
        self.config.thumbnail_size = self.ui.thumbnails_size_combo.currentText()
        self.config.thumbnail_suffix = self.ui.thumbnails_suffix_lineedit.text()

        self.config.report_csv = self.ui.reports_csv_check.isChecked()
        self.config.report_json = self.ui.reports_json_check.isChecked()
        self.config.report_excel = self.ui.reports_excel_check.isChecked()
        self.config.report_tree = self.ui.reports_tree_check.isChecked()

        self.config.log_verbose = self.ui.log_verbose_check.isChecked()
        # --------------------------------------------------------------

        # Now run pipeline with updated Config
        run_pipeline(self.folder, self.config)
        self.ui.log_box.append("Pipeline executed!")


    def install_ffmpeg(self):
        import webbrowser
        webbrowser.open("https://ffmpeg.org/download.html")
        self.ui.log_box.append("Opened FFmpeg download page.")

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
