"""Filedialog module."""
# -*- coding: utf-8 -*-
from PyQt6 import QtWidgets  # type: ignore[import]

from pineboolib.core import system as core_system
import os
from typing import List


class FileDialog(object):
    """FileDialog class."""

    @staticmethod
    def getOpenFileName(filter: str = "*", caption: str = "Pineboo") -> str:
        """Show a dialog to choose a file."""

        folder = core_system.System.getenv("HOME")

        file_list = QtWidgets.QFileDialog.getOpenFileName(None, caption, folder, filter)
        return file_list[0] if file_list else ""

    @staticmethod
    def getOpenFileNames(
        folder: str = ".", filter: str = "*", caption: str = "Pineboo"
    ) -> List[str]:
        """Show a dialog to choose a file."""

        obj = QtWidgets.QFileDialog.getOpenFileNames(None, caption, folder, filter)
        return obj[0] if obj else []

    @staticmethod
    def getSaveFileName(filter: str = "*", caption: str = "Pineboo") -> str:
        """Show a dialog to save a file."""

        folder = core_system.System.getenv("HOME")

        ret = QtWidgets.QFileDialog.getSaveFileName(None, caption, folder, filter)
        return ret[0] if ret else ""

    @staticmethod
    def getExistingDirectory(folder: str = "", caption: str = "Pineboo") -> str:
        """Show a dialog to choose a directory."""

        if not os.path.exists(folder):
            folder = "%s/" % core_system.System.getenv("HOME")

        ret = QtWidgets.QFileDialog.getExistingDirectory(
            None, caption, folder, QtWidgets.QFileDialog.Option.ShowDirsOnly
        )
        return "%s/" % ret if ret else ""
