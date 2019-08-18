"""Eneboo_mdi module."""

# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMainWindow  # type: ignore

from pineboolib import logging

logger = logging.getLogger("mainForm_%s" % __name__)


class MainForm(QMainWindow):
    """MainForm class."""

    is_closing_: bool
    mdi_enable_: bool

    def __init__(self) -> None:
        """Inicialize."""
        super().__init__()
        from pineboolib import application

        application.aqApp.main_widget_ = self
        self.is_closing_ = False
        self.mdi_enable_ = True

    @classmethod
    def setDebugLevel(self, q: int) -> None:
        """Set a new debug level."""
        MainForm.debugLevel = q

    def initScript(self) -> None:
        """Inicialize main script."""
        from pineboolib.core.utils.utils_base import filedir

        mw = self
        mw.createUi(filedir("plugins/mainform/eneboo_mdi/mainform.ui"))
        from pineboolib.fllegacy.flapplication import aqApp

        aqApp.container_ = mw
        aqApp.init()

    def createUi(self, ui_file: str) -> None:
        """Create UI from a file."""
        from pineboolib.application import project

        mng = project.conn.managerModules()
        self.w_ = mng.createUI(ui_file, None, self)
        self.w_.setObjectName("container")


mainWindow: MainForm
# mainWindow = MainForm()
