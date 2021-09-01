"""Qtoolbutton module."""
# -*- coding: utf-8 -*-
from PyQt6 import QtWidgets  # type: ignore[import]
from pineboolib.core import decorators


from .qframe import QFrame
from .qgroupbox import QGroupBox
from .qwidget import QWidget
from .qiconset import QIconSet

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

        self.groupId = None  # pylint: disable=invalid-name

    def setToggleButton(self, value: bool) -> None:
        """Set toggled button."""

        self.setDown(value)

    @decorators.deprecated
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

    @decorators.deprecated
    def setUsesTextLabel(self, value: bool):
        """Set uses text label."""
        pass

    def buttonGroupId(self) -> Optional[int]:
        """Return button group id."""
        return self.groupId

    def setButtonGroupId(self, id_: int) -> None:
        """Set button group id."""
        self.groupId = id_

    def getEnabled(self) -> bool:
        """Return if is enabled."""

        return super().isEnabled()

    def setIconSet(self, icon_set: "QIconSet") -> None:
        """Set iconset."""

        self.setIcon(icon_set)

    def setEnabled(self, value: bool) -> None:
        """Set if enabled."""

        super().setEnabled(value)

    def animateClick(self, num: int) -> None:  # type: ignore [override] # noqa: F821
        """Animateclick Bound method."""

        super().animateClick()

    on = property(getOn, setOn)
    enabled = property(getEnabled, setEnabled)
