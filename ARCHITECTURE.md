# Architecture Overview — Smart File Wrangler

**Design principle:**  
Each subsystem is decoupled. The pipeline only coordinates execution order.

**Data flow (high level):**  

Physical discovery → grouping → internal MediaItem wrapping → optional thumbs → optional organise → reports

**Stage details:**
1. **Physical discovery**
   - Scans the filesystem for files and frame-sequence patterns
   - Produces a list of `Path` objects and/or sequence `dict` records
   - This scan is reused where possible to avoid duplicate work

2. **Grouping**
   - `group_frame_sequences()` converts frame lists into logical `"sequence"` units
   - Other files pass through unchanged

3. **MediaItem wrapping**
   - `MediaItem` is an internal data class used to remove ambiguity between `Path` and `dict`
   - No module depends on its behavior — it is a passive container only

4. **Optional thumbnail stage**
   - Uses the grouped list
   - Enhances output if `ffmpeg` is available
   - Falls back safely when it is not

5. **Optional organise stage**
   - Copies or moves files into media-type folders (`audio/`, `image/`, `video/`, `other/`)
   - Does not affect upstream scanning or thumbnail logic
   - Sorting rules can include:
     - **By media type** → file suffix determines media category (e.g., `.mp4` → `video/`)
     - **By extension** → file suffix determines folder (e.g., `.mp4` → `mp4/`)
     - **By string matching**:
       - **starts with** → filename prefix decides category (`sample_video` → `sample/`)
       - **contains** → substring decides category (`abc_river_wide` → `river/`)
   - If no rule matches, files go into the `other/` folder by default
   - All sorting options are local and deterministic — no external services are used


6. **Report stage**
   - May scan again if folder state changed (e.g., after organisation)
   - Writes output in enabled formats (CSV, JSON, Excel, or folder tree)

---

**Beginner key terms:**
- `files` = real disk entries
- `items` = grouped logical media units
- `MediaItem` = internal clarity container

---

**Extension points later (GUI-safe, not implemented yet):**
- UI log sink via `ui_callback`
- File log sink via `set_file_sink()`

