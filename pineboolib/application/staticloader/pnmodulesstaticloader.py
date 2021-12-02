# -*- coding: utf-8 -*-
"""
Static loader emulating Eneboo.

Performs load of scripts from disk instead of database.
"""


from PyQt6 import QtWidgets, QtCore

from pineboolib.core import settings, decorators
from pineboolib.core.utils import logging, utils_base

from pineboolib import application

import os
from typing import List, Optional, cast, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.interfaces import iconnection  # pragma: no cover

LOGGER = logging.get_logger(__name__)

SHOW_REINIT_MESSAGE = True


class AQStaticDirInfo(object):
    """Store information about a filesystem folder."""

    active_: bool
    path_: str

    def __init__(self, *args) -> None:
        """Inicialize."""

        self.active_ = str(args[0]) == "True"
        self.path_ = "" if len(args) == 1 else args[1]


class AQStaticBdInfo(object):
    """Get or set settings on database related to staticloader."""

    enabled_: bool
    dirs_: List[AQStaticDirInfo]
    key_: str

    def __init__(self, database: "iconnection.IConnection") -> None:
        """Create new AQStaticBdInfo."""
        self.db_ = database.DBName()
        self.dirs_ = []
        self.key_ = "StaticLoader/%s/" % self.db_
        self.enabled_ = settings.CONFIG.value("%senabled" % self.key_, False)

    def findPath(self, path: str) -> Optional[AQStaticDirInfo]:
        """Find if path "path" is managed in this class."""
        for info in self.dirs_:
            if info.path_ == path:
                return info

        return None

    def readSettings(self) -> None:
        """Read settings for staticloader."""
        self.enabled_ = settings.CONFIG.value("%senabled" % self.key_, False)
        self.dirs_.clear()
        dirs = settings.CONFIG.value("%sdirs" % self.key_, [])
        i = 0

        while i < len(dirs):
            active_ = dirs[i]
            i += 1
            path_ = dirs[i]
            i += 1
            self.dirs_.append(AQStaticDirInfo(active_, path_))

    def writeSettings(self) -> None:
        """Write settings for staticloader."""
        settings.CONFIG.set_value("%senabled" % self.key_, self.enabled_)
        dirs: List[Union[bool, str]] = []
        active_dirs = []

        for info in self.dirs_:
            dirs.append(info.active_)
            dirs.append(info.path_)
            if info.active_:
                active_dirs.append(info.path_)

        settings.CONFIG.set_value("%sdirs" % self.key_, dirs)
        settings.CONFIG.set_value("%sactiveDirs" % self.key_, ",".join(active_dirs))

    def msg_static_changed(self, event) -> None:
        """Show reinit msg."""

        global SHOW_REINIT_MESSAGE
        if not isinstance(event.src_path, str) or not event.src_path.find(".") > -1:
            return

        if event.src_path.upper().find("__PYCACHE__") > -1:
            return

        if not SHOW_REINIT_MESSAGE:
            return

        SHOW_REINIT_MESSAGE = False

        if utils_base.is_library():
            LOGGER.warning(
                "STATIC LOADER:  %s HAS BEEN %s. REINIT!",
                event.src_path.upper(),
                event.event_type.upper(),
            )

            while application.PROJECT.aq_app._inicializing:
                QtWidgets.QApplication.processEvents()

            application.PROJECT.aq_app.reinit()
        else:
            LOGGER.warning(
                "STATIC LOADER:  %s HAS BEEN %s.", event.src_path.upper(), event.event_type.upper()
            )


class FLStaticLoaderWarning(QtCore.QObject):
    """Create warning about static loading."""

    warns_: List[str]
    paths_: List[str]

    def __init__(self) -> None:
        """Create a new FLStaticLoaderWarning."""
        super().__init__()
        self.warns_ = []
        self.paths_ = []

    def popupWarnings(self) -> None:
        """Show a popup if there are any warnings."""
        if not self.warns_:
            return

        msg = '<p><img source="about.png" align="right"><b><u>CARGA ESTATICA ACTIVADA</u></b><br><br><font face="Monospace">'
        for item in self.warns_:
            msg += "%s<br>" % (item)

        msg += "</font><br></p>"
        self.warns_.clear()

        application.PROJECT.aq_app.popupWarn(msg)


WARN_: Optional[FLStaticLoaderWarning] = None


class PNStaticLoader(QtCore.QObject):
    """Perform static loading of scripts from filesystem."""

    def __init__(self, info: "AQStaticBdInfo", dialog: QtWidgets.QDialog) -> None:
        """Create a new FLStaticLoader."""

        super(PNStaticLoader, self).__init__()

        self._dialog = dialog
        self._info = info
        self._dialog.pixOn.setVisible(  # type: ignore[attr-defined] # noqa: F821
            self._info.enabled_
        )
        self._dialog.pixOff.setVisible(  # type: ignore[attr-defined] # noqa: F821
            not self._info.enabled_
        )

        tbl_dir = self._dialog.tblDirs  # type: ignore[attr-defined] # noqa: F821
        tbl_dir.show()
        cast(QtWidgets.QTableWidget, tbl_dir).verticalHeader().setVisible(True)
        cast(QtWidgets.QTableWidget, tbl_dir).horizontalHeader().setVisible(True)

        tbl_dir.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        tbl_dir.setAlternatingRowColors(True)
        tbl_dir.setColumnCount(2)
        tbl_dir.setHorizontalHeaderLabels([self.tr("Carpeta"), self.tr("Activo")])

        horizontal_header = tbl_dir.horizontalHeader()
        horizontal_header.setSectionsClickable(False)
        horizontal_header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)

        horizontal_header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        horizontal_header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

        self.load()
        cast(
            QtWidgets.QToolButton, self._dialog.pbAddDir  # type: ignore[attr-defined] # noqa: F821
        ).clicked.connect(self.addDir)
        cast(
            QtWidgets.QToolButton, self._dialog.pbModDir  # type: ignore[attr-defined] # noqa: F821
        ).clicked.connect(self.modDir)
        cast(
            QtWidgets.QToolButton, self._dialog.pbDelDir  # type: ignore[attr-defined] # noqa: F821
        ).clicked.connect(self.delDir)
        cast(
            QtWidgets.QToolButton, self._dialog.pbNo  # type: ignore[attr-defined] # noqa: F821
        ).clicked.connect(self._dialog.reject)
        cast(
            QtWidgets.QToolButton, self._dialog.pbOk  # type: ignore[attr-defined] # noqa: F821
        ).clicked.connect(self._dialog.accept)
        cast(
            QtWidgets.QCheckBox, self.chkEnabled
        ).toggled.connect(  # type: ignore [attr-defined] # noqa: F821
            self.setEnabled
        )

    @decorators.pyqt_slot()
    def load(self) -> None:
        """Load and initialize the object."""
        info = self._info
        info.readSettings()
        cast(
            QtWidgets.QLabel, self._dialog.lblBdTop  # type: ignore[attr-defined] # noqa: F821
        ).setText(info.db_)
        cast(
            QtWidgets.QCheckBox, self._dialog.chkEnabled  # type: ignore[attr-defined] # noqa: F821
        ).setChecked(info.enabled_)
        tbl_dir = cast(
            QtWidgets.QTableWidget, self._dialog.tblDirs  # type: ignore[attr-defined] # noqa: F821
        )
        if info.dirs_:
            n_rows = tbl_dir.rowCount()
            if n_rows > 0:
                tbl_dir.clear()

            n_rows = len(info.dirs_)
            tbl_dir.setRowCount(n_rows)

            for row, info_dir in enumerate(info.dirs_):
                item = QtWidgets.QTableWidgetItem(info_dir.path_)
                item.setTextAlignment(
                    QtCore.Qt.AlignmentFlag.AlignVCenter + QtCore.Qt.AlignmentFlag.AlignLeft
                )
                tbl_dir.setItem(row, 0, item)
                chk = QtWidgets.QCheckBox(tbl_dir)
                chk.setChecked(info_dir.active_)
                chk.toggled.connect(self.setChecked)  # type: ignore [attr-defined] # noqa: F821
                tbl_dir.setCellWidget(row, 1, chk)

            tbl_dir.setCurrentCell(n_rows, 0)

    @decorators.pyqt_slot(bool)
    def addDir(self) -> None:
        """Ask user for adding a new folder for static loading."""

        tbl_dir = cast(
            QtWidgets.QTableWidget, self._dialog.tblDirs  # type: ignore[attr-defined] # noqa: F821
        )
        cur_row = tbl_dir.currentRow()
        dir_init = tbl_dir.item(cur_row, 0).text() if cur_row > -1 else ""

        dir = QtWidgets.QFileDialog.getExistingDirectory(
            None, self.tr("Selecciones el directorio a insertar"), dir_init
        )

        if dir:

            n_rows = tbl_dir.rowCount()
            tbl_dir.setRowCount(n_rows + 1)

            item = QtWidgets.QTableWidgetItem(str(dir))
            item.setTextAlignment(
                QtCore.Qt.AlignmentFlag.AlignVCenter + QtCore.Qt.AlignmentFlag.AlignLeft
            )
            tbl_dir.setItem(n_rows, 0, item)

            chk = QtWidgets.QCheckBox(tbl_dir)
            chk.setChecked(True)
            chk.toggled.connect(self.setChecked)  # type: ignore [attr-defined] # noqa: F821

            tbl_dir.setCellWidget(n_rows, 1, chk)
            tbl_dir.setCurrentCell(n_rows, 0)

            self._info.dirs_.append(AQStaticDirInfo(True, dir))

    @decorators.pyqt_slot()
    def modDir(self) -> None:
        """Ask user for a folder to change."""

        tbl_dir = cast(QtWidgets.QTableWidget, self.tblDirs)
        cur_row = tbl_dir.currentRow()
        if cur_row == -1:
            return

        actual_dir = tbl_dir.item(cur_row, 0).text() if cur_row > -1 else ""

        new_dir = QtWidgets.QFileDialog.getExistingDirectory(
            None, self.tr("Selecciones el directorio a modificar"), actual_dir
        )

        if new_dir:
            info = self._info.findPath(actual_dir)
            if info:
                info.path_ = new_dir

            item = QtWidgets.QTableWidgetItem(str(new_dir))
            item.setTextAlignment(
                QtCore.Qt.AlignmentFlag.AlignVCenter + QtCore.Qt.AlignmentFlag.AlignLeft
            )
            tbl_dir.setItem(cur_row, 0, item)

    @decorators.pyqt_slot()
    def delDir(self) -> None:
        """Ask user for folder to delete."""

        tbl_dir = cast(QtWidgets.QTableWidget, self.tblDirs)
        cur_row = tbl_dir.currentRow()
        if cur_row == -1:
            return

        if QtWidgets.QMessageBox.StandardButton.No == QtWidgets.QMessageBox.warning(
            QtWidgets.QWidget(),
            self.tr("Borrar registro"),
            self.tr("El registro activo será borrado. ¿ Está seguro ?"),
            QtWidgets.QMessageBox.StandardButton.Ok,
            QtWidgets.QMessageBox.StandardButton.No,
        ):
            return

        info = self._info.findPath(tbl_dir.item(cur_row, 0).text())
        if info:
            self._info.dirs_.remove(info)

        tbl_dir.removeRow(cur_row)

    @decorators.pyqt_slot(bool)
    def setEnabled(self, state: bool) -> None:
        """Enable or disable this object."""
        self._info.enabled_ = state
        self._dialog.pixOn.setVisible(state)  # type: ignore[attr-defined] # noqa: F821
        self._dialog.pixOff.setVisible(not state)  # type: ignore[attr-defined] # noqa: F821

    @decorators.pyqt_slot(bool)
    def setChecked(self, state: bool) -> None:
        """Set checked this object."""

        tbl_dir = cast(QtWidgets.QTableWidget, self.tblDirs)
        chk = self.sender()
        if not chk:
            return

        for row in range(tbl_dir.rowCount()):
            if tbl_dir.cellWidget(row, 1) is chk:
                info = self._info.findPath(tbl_dir.item(row, 0).text())
                if info:
                    info.active_ = state

    @staticmethod
    def setup(info: "AQStaticBdInfo", dialog: QtWidgets.QDialog) -> None:
        """Configure user interface from given widget."""

        diag_setup = PNStaticLoader(info, dialog)
        if QtWidgets.QDialog.DialogCode.Accepted == diag_setup._dialog.exec():
            info.writeSettings()

    @staticmethod
    def content(name: str, info: "AQStaticBdInfo", only_path: bool = False) -> str:
        """Get content from given path."""
        global WARN_
        info.readSettings()
        candidates: List[List[str]] = []

        if not info.dirs_:
            LOGGER.info(
                "STATIC LOAD: No folders found searching %s. Please disable static load or add folders",
                name,
            )
            return ""

        for info_item in info.dirs_:
            content_path_candidate = os.path.join(info_item.path_, name)
            if info_item.path_ not in content_path_candidate:
                continue
            if info_item.active_ and os.path.exists(
                content_path_candidate
            ):  # Buscamos todos los candidatos
                if content_path_candidate in [
                    path_candidate for name, path_candidate in candidates
                ]:
                    continue
                candidates.append([info_item.path_, content_path_candidate])

        if candidates:
            if not WARN_:
                WARN_ = FLStaticLoaderWarning()

            file_path, content_path = candidates[0]
            msg = "%s -> ...%s" % (name, file_path[0:40])

            if msg not in WARN_.warns_:
                if len(candidates) > 1:  # Si hay mas de un candidato muestra warning
                    LOGGER.warning(
                        "STATIC LOAD: MULTIPLES CANIDATES FOUND FOR %s. USING FIRST:", name.upper()
                    )
                    for num, candidate in enumerate(candidates):
                        LOGGER.warning("    %s) - %s/%s", num + 1, candidate[0], name)

                WARN_.warns_.append(msg)
                WARN_.paths_.append("%s:%s" % (name, file_path))
                if settings.CONFIG.value("ebcomportamiento/SLConsola", False):
                    LOGGER.warning("STATIC LOAD: ACTIVATED %s -> %s", name, file_path)
                if settings.CONFIG.value("ebcomportamiento/SLGUI", False):
                    QtCore.QTimer.singleShot(500, WARN_.popupWarnings)

            if only_path:
                return content_path
            else:

                return application.PROJECT.conn_manager.managerModules().contentFS(
                    os.path.join(file_path, name)
                )

        return ""

    def __getattr__(self, name: str) -> QtWidgets.QWidget:
        """Emulate child properties as if they were inserted into the object."""
        return cast(QtWidgets.QWidget, self._dialog.findChild(QtWidgets.QWidget, name))
