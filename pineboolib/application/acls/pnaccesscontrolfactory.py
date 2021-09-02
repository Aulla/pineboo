# -*- coding: utf-8 -*-
"""
PNAccessControlFactory Module.

Manage ACLs between different application objects.
"""

from PyQt6 import QtWidgets, QtGui  # type: ignore[import]

from pineboolib.application.metadata import pntablemetadata
from . import pnaccesscontrol


from typing import Dict, Union, cast, List

from pineboolib import logging

LOGGER: "logging.Logger" = logging.get_logger(__name__)


class PNAccessControlMainWindow(pnaccesscontrol.PNAccessControl):
    """PNAccessControlMainWindow Class."""

    def type(self) -> str:
        """Return target type."""

        return "mainwindow"

    def processObject(  # type: ignore [override]
        self, main_window: "QtWidgets.QMainWindow"
    ) -> None:
        """Process the object."""

        if self._perm:
            for action in main_window.findChildren(QtGui.QAction):
                action_name = action.objectName()
                perms_value = (
                    self._acos_perms[action_name]
                    if action_name in self._acos_perms.keys()
                    else self._perm
                )
                if perms_value in ("-w", "--"):
                    cast(QtWidgets.QWidget, action).setVisible(False)


class PNAccessControlForm(pnaccesscontrol.PNAccessControl):
    """PNAccessControlForm Class."""

    def __init__(self) -> None:
        """Inicialize."""

        super().__init__()

        self.pal = QtGui.QPalette()
        palette_ = QtWidgets.QApplication.palette()  # type: ignore[misc] # noqa: F821
        background_color = palette_.color(
            QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Base
        )
        # FIXMEPYQT6
        # self.pal.setColor(QtGui.QPalette.Foreground, background_color)
        self.pal.setColor(QtGui.QPalette.ColorRole.Text, background_color)
        self.pal.setColor(QtGui.QPalette.ColorRole.ButtonText, background_color)
        self.pal.setColor(QtGui.QPalette.ColorRole.Base, background_color)
        # self.pal.setColor(QtGui.QPalette.Background, background_color)

    def type(self) -> str:
        """Return target type."""
        return "form"

    def processObject(self, widget: "QtWidgets.QWidget") -> None:  # type: ignore [override]
        """
        Process objects that are of the FLFormDB class.

        Only control the children of the object that are of the QWidget class, and only
        allows to make them not visible or not editable. Actually do them
        not visible means that they are not editable and modifying the palette to
        that the entire region of the component be shown in black. The permits
        which accepts are:

        - "-w" or "--" (no_read / write or no_read / no_write) -> not visible
        - "r-" (read / no_write) -> not editable

        This allows any component of an AbanQ form (FLFormDB,
        FLFormRecordDB and FLFormSearchDB) can be made not visible or not editable for convenience.
        """

        not_found_widgets: List[str] = list(self._acos_perms.keys())

        for child_object in widget.findChildren(QtWidgets.QWidget):
            child_widget = cast(QtWidgets.QWidget, child_object)
            widget_name = child_widget.objectName()
            perms = self._perm
            if widget_name in self._acos_perms.keys():
                perms = self._acos_perms[widget_name]
                not_found_widgets.remove(widget_name)

            if perms == "":
                continue

            elif perms in ("-w", "--"):
                child_widget.setPalette(self.pal)
                child_widget.setDisabled(True)
                child_widget.hide()

            elif perms == "r-":
                child_widget.setDisabled(True)

        for not_found_widget_name in not_found_widgets:
            LOGGER.warning(
                "PNAccessControlFactory: No se encuentra el control %s para procesar ACLS.",
                not_found_widget_name,
            )


class PNAccessControlTable(pnaccesscontrol.PNAccessControl):
    """PNAccessControlTable Class."""

    def __init__(self) -> None:
        """Inicialize."""

        super().__init__()
        self._acos_perms: Dict[str, str] = {}

    def type(self) -> str:
        """Return target type."""

        return "table"

    def processObject(  # type: ignore [override]
        self, table_metadata: "pntablemetadata.PNTableMetaData"
    ) -> None:
        """Process pntablemetadata.PNTableMetaData belonging to a table."""
        mask_perm = 0
        has_acos = True if self._acos_perms else False

        if self._perm:
            if self._perm[0] == "r":
                mask_perm += 2
            if self._perm[1] == "w":
                mask_perm += 1
        elif has_acos:
            mask_perm = 3
        else:
            return

        for field in table_metadata.fieldList():

            mask_field_perm = mask_perm  # por defecto valores de self._perm

            if has_acos and (
                field.name() in self._acos_perms.keys()
            ):  # si hay acos_perm especifico sobrecargo
                field_perm = self._acos_perms[field.name()]
                mask_field_perm = 0
                if field_perm[0] == "r":
                    mask_field_perm += 2

                if field_perm[1] == "w":
                    mask_field_perm += 1

            if mask_field_perm == 0:
                field.setVisible(False)
                field.setEditable(False)
            elif mask_field_perm == 1:
                if not field.visible():
                    continue
                else:
                    field.setVisible(True)
                field.setEditable(False)
            elif mask_field_perm == 2:
                field.setVisible(True)
                field.setEditable(False)
            elif mask_field_perm == 3:
                field.setVisible(True)
                field.setEditable(True)

    def setFromObject(self, table_mtd: "pntablemetadata.PNTableMetaData") -> None:
        """Apply permissions from a pntablemetadata.PNTableMetaData."""

        self._acos_perms.clear()

        for field in table_mtd.fieldList():
            perm_read = "r" if field.visible() else "-"
            perm_write = "w" if field.editable() else "-"
            self._acos_perms[field.name()] = "%s%s" % (perm_read, perm_write)


class PNAccessControlFactory(object):
    """PNAccessControlFactory Class."""

    def create(self, type_: str = "") -> "pnaccesscontrol.PNAccessControl":
        """Create a control instance according to the type that we pass."""

        if not type_:
            raise ValueError("type_ must be set")

        if type_ == "mainwindow":
            return PNAccessControlMainWindow()
        elif type_ == "form":
            return PNAccessControlForm()
        elif type_ == "table":
            return PNAccessControlTable()

        raise ValueError("type_ %r unknown" % type_)

    def type(
        self,
        obj: Union["QtWidgets.QWidget", "pntablemetadata.PNTableMetaData", "QtWidgets.QMainWindow"],
    ) -> str:
        """Return the type of instance target."""

        ret_: str = ""

        if isinstance(obj, QtWidgets.QMainWindow):
            ret_ = "mainwindow"
        elif isinstance(obj, pntablemetadata.PNTableMetaData):
            ret_ = "table"
        elif isinstance(obj, QtWidgets.QDialog):
            ret_ = "form"

        return ret_
