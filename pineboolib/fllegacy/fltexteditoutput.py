"""Fltexteditoutput module."""
# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets  # type: ignore
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
        super(FLTextEditOutput, self).__init__(parent)

        self.oldStdout = sys.stdout
        self.oldStderr = sys.stderr
        sys.stdout = self
        sys.stderr = self

    def write(self, txt: Union[bytearray, bytes, str]) -> None:
        """Set text."""
        txt = str(txt)
        if self.oldStdout:
            self.oldStdout.write(txt)
        self.appendPlainText(txt)

    def flush(self):
        pass

    def close(self) -> bool:
        """Control close."""
        if self.oldStdout:
            sys.stdout = self.oldStdout
        if self.oldStderr:
            sys.stderr = self.oldStderr
        return super().close()
