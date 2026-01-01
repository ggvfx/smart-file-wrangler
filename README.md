# smart-file-wrangler  
Python Automation for Media Pipelines

Smart File Wrangler is a learning-friendly, modular Python project that automates common media-folder cleanup tasks used in film, VFX, and office productivity pipelines.

It processes one folder at a time and runs subsystems in a safe, fixed order:

1. **Filesystem scan** (done once per stage)
2. **Frame-sequence detection and grouping**
3. **MediaItem wrapping** (internal clarity refactor, no behavior change)
4. **Thumbnail generation** (optional, supports images, video, and frame sequences)
5. **File organisation** (optional, copy or move into media type folders)
6. **Report generation** (CSV, JSON, Excel, or folder-tree view)

> The pipeline contains **no business logic** — it only controls execution order and subsystem activation.

---

Smart File Wrangler works **without any external dependencies**.  
All core functionality (scanning, recursion, grouping, organising, reporting) runs using only the Python standard library.

---

## Optional ffmpeg support

`ffmpeg` is **not required** to run the tool.

If `ffmpeg` *is available on the system*, Smart File Wrangler can also:

- Extract extra **video/audio metadata** (duration, resolution, sample rate)
- Generate **video thumbnails**
- Generate **one thumbnail for frame sequences** (e.g. `sequence.[1000-1005].png`)

If `ffmpeg` is *not installed*:

- These features are skipped automatically ✔
- No errors or crashes occur ✔
- The pipeline continues normally ✔
- Terminal output falls back to simple `print()` logging intentionally ✔

Option included for installing ffmpeg (automatically if deoendencies met, otherwise will open webpage for manual install).
###Smart File Wrangler must be restarted after ffmpeg install

---

## Internal data model: `MediaItem`

The project now uses a minimal internal data class called `MediaItem` to remove ambiguity between raw filesystem paths and sequence metadata:

```python
class MediaItem:
    kind: "file" | "sequence"
    path: Path | None
    sequence_info: dict | None
