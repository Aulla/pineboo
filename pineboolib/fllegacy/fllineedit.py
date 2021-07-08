# -*- coding: utf-8 -*-
"""Fllineedit module."""

from PyQt6 import QtCore, QtWidgets, QtGui  # type: ignore[import]
from pineboolib import logging

LOGGER = logging.get_logger(__name__)


class FLLineEdit(QtWidgets.QLineEdit):
    """FLLineEdit class."""

    _tipo: str
    _part_decimal: int
    _part_integer: int
    _max_value: int
    _auto_select: bool
    _name: str
    _longitud_max: int
    _parent: QtWidgets.QWidget
    _last_text: str
    _formating: bool
    _field_name: str

    lostFocus = QtCore.pyqtSignal()

    def __init__(self, parent: QtWidgets.QWidget, name: str = "") -> None:
        """Inicialize."""
        super().__init__(parent)
        self._name = name
        field_name = getattr(parent, "_field_name", None)
        if field_name is not None:
            self._field_name = field_name
            cursor = getattr(parent, "cursor_", None)
            if cursor is not None:
                mtd = cursor.metadata()
                if mtd is None:
                    raise Exception("mtd is Empty!")

                self._tipo = mtd.field(self._field_name).type()
                self._part_decimal = 0
                self._auto_select = True
                self._formating = False
                self._part_integer = mtd.field(self._field_name).partInteger()

                self._parent = parent

                if self._tipo == "string":
                    self._longitud_max = mtd.field(self._field_name).length()
                    self.setMaxLength(self._longitud_max)

                elif self._tipo in ("int", "uint", "double"):
                    self.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

    def setText(self, text_: str, check_focus: bool = True) -> None:
        """Set text to control."""

        text_ = str(text_)
        # if not project.DGI.localDesktop():
        #    project.DGI._par.addQueque("%s_setText" % self._parent.objectName(), text_)
        # else:
        if check_focus:

            if text_ in ("", None) or self.hasFocus():
                super().setText(text_)
                return

        ok_ = False

        minus = False

        if self._tipo == "double":
            if text_[0] == "-":
                minus = True
                text_ = text_[1:]

            val, ok_ = QtCore.QLocale.system().toDouble(text_.replace(".", ","))

            if ok_:
                text_ = QtCore.QLocale.system().toString(float(text_), "f", self._part_decimal)
            if minus:
                text_ = "-%s" % text_

        elif self._tipo in ("int"):
            val, ok_ = QtCore.QLocale.system().toInt(text_)
            if ok_:
                text_ = QtCore.QLocale.system().toString(val)

        elif self._tipo in ("uint"):
            val, ok_ = QtCore.QLocale.system().toUInt(text_)
            if ok_:
                text_ = QtCore.QLocale.system().toString(val)

        super().setText(str(text_))

    def text(self) -> str:
        """Return text from control."""

        text_ = super().text()
        if text_ == "":
            return text_

        ok_ = False
        minus = False

        if self._tipo == "double":
            if text_[0] == "-":
                minus = True
                text_ = text_[1:]

            val, ok_ = QtCore.QLocale.system().toDouble(text_)
            if ok_:
                text_ = str(val)

            if minus:
                text_ = "-%s" % text_

            if text_ == ",":
                text_ = ""

        elif self._tipo == "uint":
            val, ok_ = QtCore.QLocale.system().toUInt(text_)
            if ok_:
                text_ = str(val)

        elif self._tipo == "int":
            val, ok_ = QtCore.QLocale.system().toInt(text_)

            if ok_:
                text_ = str(val)

        return text_

    def setMaxValue(self, max_value: int) -> None:
        """Set max value for numeric types."""

        self._max_value = max_value

    def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
        """Focus out event."""

        if self._tipo in ("double", "int", "uint"):
            text_ = super().text()

            if self._tipo == "double":

                val, ok_ = QtCore.QLocale.system().toDouble(text_)

                if ok_:
                    text_ = QtCore.QLocale.system().toString(val, "f", self._part_decimal)
                super().setText(text_)
            else:

                self.setText(text_)
        super().focusOutEvent(event)

    def focusInEvent(self, event: QtGui.QFocusEvent) -> None:
        """Focus in event."""

        if self.isReadOnly():
            return

        if self._tipo in ("double", "int", "uint"):
            self.blockSignals(True)
            s_orig = self.text()
            text_ = s_orig
            if self._tipo == "double":
                if s_orig != "":
                    text_ = QtCore.QLocale.system().toString(float(s_orig), "f", self._part_decimal)

                if QtCore.QLocale.system().toString(1.1, "f", 1)[1] == ",":
                    text_ = text_.replace(".", "")
                else:
                    text_ = text_.replace(",", "")

            validator = self.validator()
            if validator:
                pos = 0
                validator.validate(text_, pos)

            super().setText(text_)
            self.blockSignals(False)

        if self._auto_select and not self.selectedText() and not self.isReadOnly():
            self.selectAll()

        super().focusInEvent(event)
