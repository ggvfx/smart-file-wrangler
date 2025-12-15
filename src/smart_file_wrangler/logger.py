"""
logger.py
Handles verbose output and UI-integrated logging.
"""

def log(message):
    print(message)

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
        """Log a message to console or GUI."""
        if self.verbose:
            print(message)
        if self.ui_callback:
            self.ui_callback(message)
