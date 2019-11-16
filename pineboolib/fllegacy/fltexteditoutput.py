"""Fltexteditoutput module."""
# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
import sys
from typing import Union, Any

from pineboolib import logging

logger = logging.getLogger("FLTextEditOputput")


class FLTextEditOutput(QtWidgets.QPlainTextEdit):
    """FLTextEditOutput class."""

    oldStdout: Any
    oldStderr: Any

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        """Inicialize."""
        super().__init__(parent)

        self.oldStdout = sys.stdout
        self.oldStderr = sys.stderr
        sys.stdout = self  # type: ignore [assignment] # noqa F821
        sys.stderr = self  # type: ignore [assignment] # noqa F821

    def write(self, txt: Union[bytearray, bytes, str]) -> None:
        """Set text."""
        txt = str(txt)
        if self.oldStdout:
            self.oldStdout.write(txt)
        self.appendPlainText(txt)

    def flush(self):
        """Flush data."""

        pass

    def close(self) -> bool:
        """Control close."""
        if self.oldStdout:
            sys.stdout = self.oldStdout
        if self.oldStderr:
            sys.stderr = self.oldStderr
        return super().close()
