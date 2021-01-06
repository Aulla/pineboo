"""QDir module."""
# -*- coding: utf-8 -*-

from PyQt6 import QtCore


class QDir(QtCore.QDir):
    """QDir class."""

    def absPath(self):
        """Return absolute path."""
        return self.absolutePath()
