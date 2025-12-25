"""
logger.py
Handles verbose output and UI-integrated logging.
"""

from pathlib import Path

_logger = None  # internal singleton instance


class Logger:
    def __init__(self, verbose=False, ui_callback=None):
        """
        Parameters:
            verbose (bool): Show detailed logs to terminal.
            ui_callback (callable | None): Optional sink to forward logs to a GUI or UI.
        """
        self.verbose = verbose
        self.ui_callback = ui_callback

    def log(self, message, level="info"):
        """
        Log a message with an optional severity level.

        Parameters:
            message (str): The log message.
            level (str): Severity tag: "info", "warning", "error", "debug".
                         This does not change behavior, it only labels output.
        """
        # terminal sink (legacy behavior preserved)
        if self.verbose:
            print(f"[{level.upper()}] {message}")

        # UI sink if provided
        if self.ui_callback:
            self.ui_callback(f"[{level.upper()}] {message}")


def init_logger(verbose=False, ui_callback=None):
    """
    Initialize the global logger singleton once from an entry point (CLI or GUI).

    Parameters:
        verbose (bool): Enable verbose terminal logging.
        ui_callback (callable | None): Optional UI sink.
    """
    global _logger
    _logger = Logger(verbose=verbose, ui_callback=ui_callback)


def log(message, *, level="info"):
    """
    Log a message through the global logger singleton, preserving legacy print fallback.

    Parameters:
        message (str): Log message.
        level (str): Severity tag for labeling only — does not filter or change behavior.
    """
    if _logger:
        _logger.log(message, level)
    else:
        # legacy fallback terminal sink (behavior preserved)
        print(f"[{level.upper()}] {message}")




