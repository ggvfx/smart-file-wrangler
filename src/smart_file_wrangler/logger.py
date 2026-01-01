"""
logger.py

Central logging utility for Smart File Wrangler.

This module provides a simple, deterministic logging interface used across the project.
It is intentionally lightweight and beginner-readable.

Responsibilities:
- Unified `log()` entry point for terminal and UI log sinks
- Multiple log levels (INFO, WARNING, ERROR, DEBUG)
- Optional file logging when a file sink is configured
- No external telemetry, no remote services, no structured logging backends
"""

# ----------------------------------------------------------------------
# Standard library imports
# ----------------------------------------------------------------------

from pathlib import Path
from typing import Optional

# ----------------------------------------------------------------------
# Log level labels (enum-like, for consistency)
# ----------------------------------------------------------------------
class LogLevel:
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"

# ----------------------------------------------------------------------
# Internal singleton logger + central verbosity + optional file sink
# ----------------------------------------------------------------------
_logger: Optional["Logger"] = None
_verbose: bool = False
_file_sink: Optional[str] = None  # file sink path (string form)

# ----------------------------------------------------------------------
# Logger class
# ----------------------------------------------------------------------
class Logger:
    def __init__(self, ui_callback=None):
        """
        Parameters:
            ui_callback (callable | None): Optional sink to forward logs to a GUI or UI.
        """
        self.ui_callback = ui_callback

    def log(self, message: str, level: str = LogLevel.INFO):
        """
        Log a message with a severity label.

        Parameters:
            message (str): The log message.
            level (str): One of LogLevel.* labels. Does not filter or change behavior.
        """
        # Terminal sink (legacy behavior preserved, controlled centrally by _verbose)
        if _verbose:
            print(f"[{level.upper()}] {message}")

        # UI sink if provided
        if self.ui_callback:
            self.ui_callback(f"[{level.upper()}] {message}")

        # Optional file sink (non-print sink)
        if _file_sink:
            with open(_file_sink, "a", encoding="utf-8") as f:
                f.write(f"[{level.upper()}] {message}\n")

# ----------------------------------------------------------------------
# Public initializer (call once from an entry point, sets central flags)
# ----------------------------------------------------------------------
def init_logger(verbose: bool = False, ui_callback=None):
    """
    Initialize the global logger singleton. Call once from CLI or GUI entry point.

    Parameters:
        verbose (bool): Enable verbose terminal logging globally.
        ui_callback (callable | None): Optional UI sink for GUI forwarding.
    """
    global _logger, _verbose
    _verbose = verbose  # central verbosity control
    _logger = Logger(ui_callback)

# ----------------------------------------------------------------------
# Optional: set a file sink path (safe to call once, no other modules touched)
# ----------------------------------------------------------------------
def set_file_sink(path: Path | str):
    """
    Set a file path to receive log messages.

    Parameters:
        path (Path | str): Filesystem path to a log file.
    """
    global _file_sink
    _file_sink = str(path)

# ----------------------------------------------------------------------
# Global log wrapper (safe to call anywhere, preserves legacy fallback)
# ----------------------------------------------------------------------
def log(message: str, *, level: str = LogLevel.INFO):
    """
    Log a message via the global logger, preserving legacy print fallback.

    Parameters:
        message (str): Log message.
        level (str): Severity label (LogLevel.*). For labeling only.
    """
    if _logger:
        _logger.log(message, level=level)
    else:
        # Legacy fallback terminal sink (behavior preserved)
        print(f"[{level.upper()}] {message}")
