"""Qtextedit module."""

# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore
from pineboolib.core import decorators
from typing import Optional


class QTextEdit(QtWidgets.QTextEdit):
    """QTextEdit class."""

    LogText: int = 0
    RichText: int = 1

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        """Inicialize."""
        super().__init__(parent)
        self.LogText = 0
        self.RichText = 1

    def setText(self, text: str) -> None:
        """Set text."""

        super(QTextEdit, self).setText(text)
        # if not project.DGI.localDesktop():
        #    project.DGI._par.addQueque("%s_setText" % self._parent.objectName(), text)

    def getText(self) -> str:
        """Return text."""
        return super().toPlainText()

    @decorators.NotImplementedWarn
    def getTextFormat(self) -> int:
        """Return text format."""
        return -1

    @decorators.Incomplete
    def setTextFormat(self, value: int) -> None:
        """Set text format."""
        if value == 0:  # LogText
            self.setReadOnly(True)
            self.setAcceptRichText(False)
        elif value == 1:
            self.setReadOnly(False)
            self.setAcceptRichText(True)

    def setShown(self, value: bool) -> None:
        """Set visible."""
        self.setVisible(value)
        # if value:
        #    super().show()
        # else:
        #    super().hide()

    def get_alignment(self) -> QtCore.Qt.Alignment:
        return super().alignment()

    def set_alignment(self, flags: Union[QtCore.Qt.Alignment, QtCore.Qt.AlignmentFlag]) -> None:
        super().setAlignment(flags)

    def getPlainText(self) -> str:
        """Return text in plain text format."""
        return super(QTextEdit, self).toPlainText()

    def setAutoFormatting(self, value=QtWidgets.QTextEdit.AutoAll) -> None:
        """Set auto formating mode."""

        super().setAutoFormatting(QtWidgets.QTextEdit.AutoAll)

    textFormat = property(getTextFormat, setTextFormat)
    text = property(getText, setText)
    PlainText = property(getPlainText, setText)
    aligment: QtCore.Qt.Alignment = property(  # type: ignore [assignment] # noqa F821
        get_alignment, set_aligment
    )
