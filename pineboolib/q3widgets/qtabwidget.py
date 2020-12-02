"""Qtabwidget module."""
# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets  # type: ignore
from pineboolib import logging
from typing import Optional, Union

logger = logging.get_logger(__name__)


class QTabWidget(QtWidgets.QTabWidget):
    """QTabWidget class."""

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        """Inicialize."""
        super().__init__(parent)

        self.Top = self.North
        self.Bottom = self.South
        self.Left = self.West
        self.Right = self.East

    def setTabEnabled(self, tab: str, enabled: bool) -> None:  # type: ignore
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
