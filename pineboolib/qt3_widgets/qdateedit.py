"""Qdateedit module."""
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, QtCore  # type: ignore
from pineboolib.core import decorators
from typing import Any, Union, Optional


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
        self.date_ = super(QDateEdit, self).date().toString(QtCore.Qt.ISODate)
        # if not project.DGI.localDesktop():
        #    project.DGI._par.addQueque("%s_CreateWidget" % self._parent.objectName(), "QDateEdit")

    def getDate(self) -> Optional[str]:
        """Return string date."""
        ret = super(QDateEdit, self).date().toString(QtCore.Qt.ISODate)
        if ret != "2000-01-01":
            return ret
        else:
            return None

    def setDate(self, v: Union[str, Any]) -> None:
        """Set date."""

        if not isinstance(v, str):
            if hasattr(v, "toString"):
                v = v.toString("yyyy%sMM%sdd" % (self.separator(), self.separator()))
            else:
                v = str(v)

        date = QtCore.QDate.fromString(v[:10], "yyyy-MM-dd")
        super(QDateEdit, self).setDate(date)
        # if not project.DGI.localDesktop():
        #    project.DGI._par.addQueque("%s_setDate" % self._parent.objectName(), "QDateEdit")

    date = property(getDate, setDate)  # type: ignore

    @decorators.NotImplementedWarn
    def setAutoAdvance(self, b: bool) -> None:
        """Set auto advance."""
        pass

    def setSeparator(self, c: str) -> None:
        """Set separator."""

        self.separator_ = c
        self.setDisplayFormat("dd%sMM%syyyy" % (self.separator(), self.separator()))

    def separator(self) -> str:
        """Return separator."""

        return self.separator_

    def __getattr__(self, name) -> Any:
        """Return attribute."""

        if name == "date":
            return super(QDateEdit, self).date().toString(QtCore.Qt.ISODate)
