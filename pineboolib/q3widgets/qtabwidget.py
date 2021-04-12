"""Qtabwidget module."""
# -*- coding: utf-8 -*-
from PyQt6 import QtWidgets  # type: ignore[import]
from pineboolib import logging
from typing import Optional, Union

logger = logging.get_logger(__name__)


class QTabWidget(QtWidgets.QTabWidget):
    """QTabWidget class."""

    Top = QtWidgets.QTabWidget.TabPosition.North
    Bottom = QtWidgets.QTabWidget.TabPosition.South
    Left = QtWidgets.QTabWidget.TabPosition.West
    Right = QtWidgets.QTabWidget.TabPosition.East

    def setTabEnabled(self, tab: str, enabled: bool) -> None:  # type: ignore [override]
        """Set a tab enabled."""
        idx = self.indexByName(tab)
        if idx is None:
            return None

        QtWidgets.QTabWidget.setTabEnabled(self, idx, enabled)

    def showPage(self, tab: str) -> None:
        """Show a tab specified by name."""
        idx = self.indexByName(tab)
        if idx is None:
            return None

        QtWidgets.QTabWidget.setCurrentIndex(self, idx)

    def indexByName(self, tab: Union[str, int]) -> Optional[int]:
        """Return a index tab from a name or number."""
        if isinstance(tab, int):
            return tab
        elif not isinstance(tab, str):
            logger.error("ERROR: Unknown type tab name or index:: QTabWidget %r", tab)
            return None

        try:
            for num in range(self.count()):
                if self.widget(num).objectName() == tab.lower():
                    return num
        except ValueError:
            logger.error("ERROR: Tab not found:: QTabWidget, tab name = %r", tab)
        return None

    def removePage(self, idx) -> None:
        """Remove a page specified by name."""

        if isinstance(idx, int):
            self.removeTab(idx)
