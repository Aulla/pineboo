"""
Manage form sizes.
"""

from PyQt6 import QtCore  # type: ignore

from pineboolib.core import settings
from pineboolib import application


def save_geometry_form(name: str, geo: "QtCore.QSize") -> None:
    """
    Save the geometry of a window.

    @param name, window name.
    @param geo, QSize with window values.
    """

    if application.PROJECT.conn_manager is None:
        raise Exception("Project is not connected yet")

    name = "geo/%s/%s" % (application.PROJECT.conn_manager.mainConn().DBName(), name)
    settings.SETTINGS.set_value(name, geo)


def load_geometry_form(name: str) -> "QtCore.QSize":
    """
    Load the geometry of a window.

    @param name, window name
    @return QSize with the saved window geometry data.
    """
    if application.PROJECT.conn_manager is None:
        raise Exception("Project is not connected yet")

    name = "geo/%s/%s" % (application.PROJECT.conn_manager.mainConn().DBName(), name)
    value = settings.SETTINGS.value(name, None)
    if isinstance(value, dict):
        value = QtCore.QSize(int(value["width"]), int(value["height"]))
    return value
