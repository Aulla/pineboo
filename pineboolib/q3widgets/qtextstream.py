"""Qtexstream module."""

from PyQt5 import QtCore


class QTextStream(QtCore.QTextStream):
    """QTextStream class."""

    def opIn(self, text_):
        """Set value to QTextStream."""
        self.device().write(text_.encode())
