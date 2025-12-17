"""
logger.py
Handles verbose output and UI-integrated logging.
"""

from .config import Defaults

_logger = None  # internal singleton


class Logger:
    def __init__(self, verbose=False, ui_callback=None):
        """
        Parameters:
            verbose (bool): Show detailed logs.
            ui_callback (callable): Optional function to push logs to GUI window.
        """
        self.verbose = verbose
        self.ui_callback = ui_callback

    def log(self, message):
        if self.verbose:
            print(message)
        if self.ui_callback:
            self.ui_callback(message)


def init_logger(verbose=False, ui_callback=None):
    """
    Initialize the global logger.
    Call this once (CLI or GUI entry point).
    """
    global _logger
    _logger = Logger(verbose=verbose, ui_callback=ui_callback)


def log(message):
    """
    Log a message using the global logger.
    Safe to call anywhere.
    """
    if _logger:
        _logger.log(message)
    else:
        # fallback if logger not initialized
        print(message)

