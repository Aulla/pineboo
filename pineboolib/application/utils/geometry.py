"""
Manage form sizes.
"""

from pineboolib.core.settings import settings
from pineboolib import application

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PyQt5.QtCore import QSize  # type: ignore


def saveGeometryForm(name: str, geo: "QSize") -> None:
    """
    Save the geometry of a window.

    @param name, window name.
    @param geo, QSize with window values.
    """

    if application.PROJECT.conn_manager is None:
        raise Exception("Project is not connected yet")

    name = "geo/%s/%s" % (application.PROJECT.conn_manager.mainConn().DBName(), name)
    settings.set_value(name, geo)


def loadGeometryForm(name: str) -> "QSize":
    """
    Load the geometry of a window.

    @param name, window name
    @return QSize with the saved window geometry data.
    """
    if application.PROJECT.conn_manager is None:
        raise Exception("Project is not connected yet")

    name = "geo/%s/%s" % (application.PROJECT.conn_manager.mainConn().DBName(), name)
    return settings.value(name, None)
