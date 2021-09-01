"""Qdateedit module."""
# -*- coding: utf-8 -*-

from PyQt6 import QtWidgets, QtCore  # type: ignore[import]
from pineboolib.core import decorators
from typing import Any, Union


class QDateEdit(QtWidgets.QDateEdit):
    """QDateEdit class."""

    _parent: QtWidgets.QWidget
    _date: str
    separator_ = "-"

    def __init__(self, parent=None, name=None) -> None:
        """Inicialize."""

        super().__init__(parent)
        super().setDisplayFormat("dd-MM-yyyy")
        if name:
            self.setObjectName(name)
        self.setSeparator("-")
        self._parent = parent
        self.date_ = super().date().toString(QtCore.Qt.DateFormat.ISODate)
        # if not project.DGI.localDesktop():
        #    project.DGI._par.addQueque("%s_CreateWidget" % self._parent.objectName(), "QDateEdit")

    def getDate(self) -> str:
        """Return string date."""
        ret = super().date().toString(QtCore.Qt.DateFormat.ISODate)
        if ret != "2000-01-01":
            return ret
        else:
            return ""

    def setDate(self, value: Union[str, Any]) -> None:
        """Set date."""

        if not isinstance(value, str):
            if hasattr(value, "toString"):
                value = value.toString("yyyy%sMM%sdd" % (self.separator(), self.separator()))

            value = str(value)

        date = QtCore.QDate.fromString(value[:10], "yyyy-MM-dd")
        super().setDate(date)
        # if not project.DGI.localDesktop():
        #    project.DGI._par.addQueque("%s_setDate" % self._parent.objectName(), "QDateEdit")

    date: str = property(getDate, setDate)  # type: ignore[assignment] # noqa : F821

    @decorators.not_implemented_warn
    def setAutoAdvance(self, value: bool) -> None:
        """Set auto advance."""
        pass

    def setSeparator(self, value: str) -> None:
        """Set separator."""

        self.separator_ = value
        self.setDisplayFormat("dd%sMM%syyyy" % (self.separator(), self.separator()))

    def separator(self) -> str:
        """Return separator."""

        return self.separator_

    # def __getattr__(self, name) -> Any:
    #    """Return attribute."""
    #
    #    if name == "date":
    #        return super(QDateEdit, self).date().toString(QtCore.Qt.ISODate)
