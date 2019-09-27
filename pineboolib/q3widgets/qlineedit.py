"""Qlineedit module."""

# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets  # type: ignore
from pineboolib.core import decorators


from typing import Union, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .qframe import QFrame  # noqa: F401
    from .qgroupbox import QGroupBox  # noqa: F401
    from .qwidget import QWidget  # noqa: F401


class QLineEdit(QtWidgets.QLineEdit):
    """QLineEdit class."""

    _parent = None
    WindowOrigin = 0

    def __init__(
        self,
        parent: Optional[Union["QGroupBox", "QWidget", "QFrame"]] = None,
        name: Optional[str] = None,
    ) -> None:
        """Inicialize."""

        super(QLineEdit, self).__init__(parent)
        self._parent = parent

        if name:
            self.setObjectName(name)

        self.setMaximumHeight(22)

    def getText(self) -> str:
        """Return the text of the field."""

        return super().text()

    def setText(self, v: Any) -> None:
        """Set the text of the field."""

        if not isinstance(v, str):
            v = str(v)

        super().setText(v)

    text = property(getText, setText)  # type: ignore

    @decorators.NotImplementedWarn
    def setBackgroundOrigin(self, bgo: Any):
        """Not implemented."""
        pass

    @decorators.NotImplementedWarn
    def setLineWidth(self, w: int):
        """Not implemented."""
        pass

    @decorators.NotImplementedWarn
    def setFrameShape(self, f: int):
        """Not implemented."""
        pass

    @decorators.NotImplementedWarn
    def setFrameShadow(self, f: int):
        """Not implemented."""
        pass
