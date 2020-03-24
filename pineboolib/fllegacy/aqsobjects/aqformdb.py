"""Aqformdb module."""

from pineboolib import application

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.fllegacy.flformdb import FLFormDB
    from PyQt5 import QtWidgets


def AQFormDB(action_name: str, parent: "QtWidgets.QWidget") -> "FLFormDB":
    """Return a FLFormDB instance."""

    if application.PROJECT.conn_manager is None:
        raise Exception("Project is not connected yet")

    ac_xml = application.PROJECT.actions[action_name]
    ac_xml.load_master_form()
    if ac_xml._master_widget is None:
        raise Exception("mainform_widget is emtpy!")

    return ac_xml._master_widget.form
