"""Qlabel module."""

# -*- coding: utf-8 -*-

from PyQt6 import QtWidgets, QtGui  # type: ignore[import]
from typing import Any, Union, Optional

from pineboolib.core import decorators


class QLabel(QtWidgets.QLabel):
    """QLabel class."""

    def __init__(
        self,
        text_or_parent: Union[str, QtWidgets.QWidget],
        parent: Optional[QtWidgets.QWidget] = None,
        name: Optional[str] = None,
    ):
        """Inititalize."""

        super().__init__(text_or_parent)

        if parent is not None:
            self.setParent(parent)

        if name is not None:
            self.setObjectName(name)

    def get_text(self) -> str:
        """Return text label."""

        return super().text()

    def setText(self, text: Union[str, int]) -> None:
        """Set text label."""

        if not isinstance(text, str):
            text = str(text)
        super().setText(text)

    def setPixmap(self, pix: Union[QtGui.QIcon, QtGui.QPixmap]) -> None:
        """Set pixmap."""

        if isinstance(pix, QtGui.QIcon):
            pix = pix.pixmap(32, 32)
        super(QLabel, self).setPixmap(pix)

    @decorators.pyqt_slot(bool)
    def setShown(self, visible: bool):
        """Set visible."""

        self.setVisible(visible)

    def getAlign(self) -> Any:
        """Return Alignment."""

        return super().alignment()

    def setAlign(self, alignment_: Any) -> None:
        """Set alignment."""

        self.setAlignment(alignment_)

    def get_palette_fore_ground(self) -> QtGui.QColor:
        """Return palette foreground color."""

        return self.palette().text().color()

    def set_palette_fore_ground(self, color: QtGui.QColor) -> None:
        """Set palette foreground color."""
        pal = self.palette()
        pal.setColor(pal.ColorRole.WindowText, color)
        self.setPalette(pal)

    alignment = property(getAlign, setAlign)  # type: ignore
    text = property(get_text, setText)  # type: ignore
    paletteForegroundColor = property(get_palette_fore_ground, set_palette_fore_ground)
