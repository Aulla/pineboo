"""Aqformdb module."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.fllegacy.flformdb import FLFormDB
    from PyQt5 import QtWidgets


def AQFormDB(action_name: str, parent: "QtWidgets.QWidget") -> "FLFormDB":
    """Return a FLFormDB instance."""

    from pineboolib.application.utils import convert_flaction
    from pineboolib import application

    if application.PROJECT.conn_manager is None:
        raise Exception("Project is not connected yet")

    ac_flaction = application.PROJECT.conn_manager.manager().action(action_name)
    ac_xml = convert_flaction.convert_from_flaction(ac_flaction)
    ac_xml.load_master_form()
    if ac_xml._master_widget is None:
        raise Exception("mainform_widget is emtpy!")

    ret_ = ac_xml._master_widget.form

    return ret_
