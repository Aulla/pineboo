"""Qtoolbutton module."""
# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets  # type: ignore
from pineboolib.core import decorators


from .qframe import QFrame
from .qgroupbox import QGroupBox
from .qwidget import QWidget
from typing import Union, Optional


class QToolButton(QtWidgets.QToolButton):
    """QToolButton class."""

    groupId: Optional[int]

    def __init__(
        self, parent: Union[QWidget, QGroupBox, QFrame], name: Optional[str] = None
    ) -> None:
        """Inicialize."""
        super().__init__(parent)

        if name is not None:
            self.setObjectName(name)

        self.groupId = None

    def setToggleButton(self, value: bool) -> None:
        """Set toggled button."""

        self.setDown(value)

    @decorators.Deprecated
    def setUsesBigPixmap(self, value: bool):
        """Set uses big pixmap."""

        pass

    def toggleButton(self) -> bool:
        """Return button is toggled."""
        return self.isDown()

    def getOn(self) -> bool:
        """Return button is checked."""
        return self.isChecked()

    def setOn(self, value: bool) -> None:
        """Set checked."""
        self.setChecked(value)

    @decorators.Deprecated
    def setUsesTextLabel(self, value: bool):
        """Set uses text label."""
        pass

    def buttonGroupId(self) -> Optional[int]:
        """Return button group id."""
        return self.groupId

    def setButtonGroupId(self, id: int) -> None:
        """Set button group id."""
        self.groupId = id

    on = property(getOn, setOn)
