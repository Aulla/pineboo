"""
Manage form sizes.
"""

from pineboolib.core import settings
from pineboolib import application

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PyQt5.QtCore import QSize  # type: ignore # pragma: no cover


def save_geometry_form(name: str, geo: "QSize") -> None:
    """
    Save the geometry of a window.

    @param name, window name.
    @param geo, QSize with window values.
    """

    if application.PROJECT.conn_manager is None:
        raise Exception("Project is not connected yet")

    name = "geo/%s/%s" % (application.PROJECT.conn_manager.mainConn().DBName(), name)
    settings.SETTINGS.set_value(name, geo)


def load_geometry_form(name: str) -> "QSize":
    """
    Load the geometry of a window.

    @param name, window name
    @return QSize with the saved window geometry data.
    """
    if application.PROJECT.conn_manager is None:
        raise Exception("Project is not connected yet")

    name = "geo/%s/%s" % (application.PROJECT.conn_manager.mainConn().DBName(), name)
    return settings.SETTINGS.value(name, None)
