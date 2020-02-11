"""Filedialog module."""
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QFileDialog, QApplication
import os
from typing import Optional, Any, List


class FileDialog(object):
    """FileDialog class."""

    @staticmethod
    def getOpenFileName(path: str = "", *args: Any) -> Optional[str]:
        """Show a dialog to choose a file."""

        obj = QFileDialog.getOpenFileName(QApplication.activeWindow(), path, *args)
        return obj[0] if obj is not None else None

    @staticmethod
    def getOpenFileNames(path: str = "", *args: Any) -> List[str]:
        """Show a dialog to choose a file."""
        obj = QFileDialog.getOpenFileNames(QApplication.activeWindow(), path, *args)
        return obj[0] if obj is not None else []

    @staticmethod
    def getSaveFileName(filter: str = "*", title: str = "Pineboo") -> Optional[str]:
        """Show a dialog to save a file."""
        ret = QFileDialog.getSaveFileName(
            QApplication.activeWindow(), title, os.getenv("HOME") or ".", filter
        )
        return ret[0] if ret else None

    @staticmethod
    def getExistingDirectory(
        basedir: Optional[str] = None, title: str = "Pineboo"
    ) -> Optional[str]:
        """Show a dialog to choose a directory."""

        dir_ = basedir if basedir and os.path.exists(basedir) else "%s/" % os.getenv("HOME")
        ret = QFileDialog.getExistingDirectory(
            QApplication.activeWindow(), title, dir_, QFileDialog.ShowDirsOnly
        )
        return "%s/" % ret if ret else ret
