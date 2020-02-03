"""Qtexstream module."""

from PyQt5 import QtCore


class QTextStream(QtCore.QTextStream):
    """QTextStream class."""

    def opIn(self, text_):
        """Set value to QTextStream."""
        self.device().write(text_.encode())

    def read(self, max_len: int = 0) -> str:
        """Read datas from QTextStream."""

        if max_len > 0:
            return super().read(max_len)
        else:
            return super().readAll()
