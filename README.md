# Smart File Wrangler ![Smart File Wrangler icon](assets/smart-file-wrangler32.png)
Python Automation for Media Pipelines - Windows and Mac installers available for download in the installer directory of this repo.

**Smart File Wrangler** is a modular Python automation utility designed to solve the "manual data-wrangling" bottleneck in high-volume media pipelines. Built for VFX and Post-Production, it provides a standardized execution layer to identify, sequence-group, and metadata-tag thousands of assets automatically. By integrating automated reporting and thumbnail generation, it ensures data transparency and pipeline health across cross-departmental handoffs.

![Smart File Wrangler UI2](assets/smartFileWranlgerUI2.Png)
*Professional media organization at the click of a button.*

---

## 🚀 The Concept
Media pipelines often involve thousands of loose files, complex image sequences, and scattered video assets that require manual sorting before ingestion into a pipeline. Standard file managers do not understand frame sequences (e.g., `shot_01.[1001-1050].exr`), leading to broken paths and lost metadata. Smart File Wrangler eliminates this risk by treating sequences as single "Media Items," ensuring that organization and reporting remain technically accurate and human-readable.

---

## ✨ Key Features

* **Sequence-Aware Intelligence:** Automatically detects and groups frame-based image sequences, treating them as a single "Media Item" for organization and technical reporting.
* **Logic-Driven Organization:** Implements "Safe-Fixed" execution modes (Move/Copy) based on media type, file extension, or naming conventions (Starts With/Contains) to enforce pipeline standards.
* **Automated Metadata Reporting:** Generates a "state of play" for any directory, exporting technical audits to CSV, JSON, Excel or simple file tree for easy integration into production tracking software.
* **Democratized Media Access (Automated Thumbnails):** Generates lightweight previews for images, videos, and complex frame sequences at user-defined resolutions (56px to 4096px). This enables non-technical stakeholders to perform visual health checks and populate production databases or reports without requiring specialized VFX software to open files.
* **Fail-Safe Error Handling:** Any asset not meeting active filter criteria is routed to an `unsorted` directory, ensuring no data is lost during the automation process.
* **FFmpeg Extension Layer:** Dynamically unlocks advanced metadata extraction (bitrate, sample rate, resolution) when FFmpeg is detected, while maintaining a lightweight, zero-dependency core.

---

## 📖 Quick Start Guide

1.  **Select Folder:** Click **Select Folder** to set your target directory.
2.  **Configure Tasks:** Toggle the **Organize**, **Thumbnails**, and **Reports** modules as needed.
3.  **Refine Filters:** If using Filename organization, type your criteria into the text box that appears.
4.  **Run:** Hit the **Run** button. A scrolling progress bar will indicate activity while the **Output Log** provides real-time updates.
5.  **Review:** Your organized files and a `thumbnails` folder will be created directly within the source directory.

---

## 🛠 UI Overview

| Feature | Function |
| :--- | :--- |
| **Recurse Subfolders** | Processes all nested directories instead of just the top level. |
| **Expand Log** | Expands the window to reveal the full Output Log for feedback. |
| **Thumbnail Size** | Dropdown to select horizontal resolution (128, 256, 512, 1024, 2048). |
| **Thumbnail Suffix** | Defines a custom string (e.g., `_thumb`) for generated preview files. |
| **Verbose Toggle** | Provides deep, technical CLI-style data in the Output Log. |
| **FFmpeg Status** | Visual indicator (Green/Red) showing if media libraries are detected. |

---

## 🎥 FFmpeg Integration

`ffmpeg` is **not required** to run the tool, but its presence unlocks advanced capabilities.

### If FFmpeg is installed:
* Extract extra **video/audio metadata** (duration, resolution, sample rate).
* Generate **video thumbnails**.
* Generate **one thumbnail for frame sequences** (e.g., `sequence.[1000-1005].png`).

### If FFmpeg is NOT installed:
* These features are skipped automatically without errors or crashes.
* The pipeline continues normally using simple `print()` logging.
* An **Install FFmpeg** button appears in the UI (Red status text).

### Manual Installation Paths
The tool automatically scans the following locations for `ffmpeg.exe`:

* **Windows:**
    * `C:\ffmpeg\bin\ffmpeg.exe`
    * `C:\Program Files\ffmpeg\bin\ffmpeg.exe`
    * `C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe`
* **Mac:**
    * `/Applications/ffmpeg`
    * `/usr/local/bin/ffmpeg`

> [!IMPORTANT]  
> The program must be **restarted** after a manual FFmpeg installation to recognize the changes.

---

## 📦 Installation

Smart File Wrangler includes standalone installers for desktop use:

1.  Navigate to the `installer` folder in this repository.
2.  **Windows:** Run the `.exe` installer.
3.  **Mac:** Run the `.dmg` installer.

---

## 🤝 Contributing
Smart File Wrangler was built to streamline media production workflows. If you have ideas for new organization modes, report formats, or find a bug, please open an issue or submit a pull request!
