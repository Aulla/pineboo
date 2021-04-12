# -*- coding: utf-8 -*-
"""About_pineboo module."""

from PyQt6 import QtWidgets, QtCore  # type: ignore[import]

from pineboolib.core.utils import check_dependencies

import platform

from typing import Any


class AboutPineboo(QtWidgets.QDialog):
    """AboutPineboo class."""

    def __init__(self) -> None:
        """Inicialize."""

        super().__init__()
        self.load()

    def load(self) -> None:
        """Load widget and show."""

        from pineboolib import application
        from pineboolib.core.utils.utils_base import filedir

        dlg_ = filedir("plugins/dgi/dgi_qt/dgi_objects/dlg_about/about_pineboo.ui")
        version_ = application.PROJECT.load_version()
        self.ui_: Any = application.PROJECT.conn_manager.managerModules().createUI(dlg_, None, self)
        if self.ui_ is None:
            raise Exception("Error creating UI About Dialog")

        self.ui_.lbl_version.setText("Pineboo %s" % str(version_))
        self.ui_.btn_close.clicked.connect(self.ui_.close)
        self.ui_.btn_clipboard.clicked.connect(self.to_clipboard)
        self.ui_.show()

        self.ui_.lbl_librerias.setText(self.load_components())

    def load_components(self) -> str:
        """Resume libraries loaded."""

        components = "Versiones de componentes:\n\n"
        components += "S.O.: %s %s %s\n" % (
            platform.system(),
            platform.release(),
            platform.version(),
        )

        if "PyQt6.QtCore" not in check_dependencies.DEPENDENCIES_CHECKED.keys():
            components += "PyQt6.QtCore: %s\n" % QtCore.QT_VERSION_STR

        for k in check_dependencies.DEPENDENCIES_CHECKED.keys():
            components += "%s: %s\n" % (k, check_dependencies.DEPENDENCIES_CHECKED[k])

        return components

    def to_clipboard(self) -> None:
        """Copy resume libraries loaded into clipboard."""

        clip_board = QtWidgets.QApplication.clipboard()
        clip_board.clear()
        clip_board.setText(self.load_components())
