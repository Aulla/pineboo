"""Qdialog module."""

# -*- coding: utf-8 -*-

from PyQt6 import QtWidgets  # type: ignore[import]
from typing import Any, Optional, cast
from pineboolib.core import decorators


class QDialog(QtWidgets.QDialog):
    """QDialog class."""

    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        name: Optional[str] = None,
        other: Any = None,
    ) -> None:
        """Inicialize."""

        if isinstance(parent, int):
            parent = None

        super().__init__(parent)
        if name:
            self.setTitle(name)
        self.setModal(True)

    def child(self, name: str) -> QtWidgets.QWidget:
        """Return an child specified by name."""

        return cast(QtWidgets.QWidget, self.findChild(QtWidgets.QWidget, name))

    def getTitle(self) -> str:
        """Return dialog title."""

        return self.windowTitle()

    def setTitle(self, title: str) -> None:
        """Set dialog title."""

        self.setWindowTitle(title)

    def getEnabled(self) -> bool:
        """Return if dialog is enabled."""

        return self.isEnabled()

    def setEnable_(self, enable_: bool) -> None:
        """Set if dialog is enabled."""

        self.setEnabled(enable_)

    @decorators.pyqt_slot()
    def accept(self) -> None:
        """Call accept."""
        super().accept()

    @decorators.pyqt_slot()
    def reject(self) -> None:
        """Call reject."""
        super().reject()

    @decorators.pyqt_slot()
    def close(self) -> bool:
        """Call close."""
        return super().close()

    caption = property(getTitle, setTitle)
    enable = property(getEnabled, setEnable_)
