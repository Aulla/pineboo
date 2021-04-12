"""conn_dialog module."""

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from PyQt6 import QtWidgets  # type: ignore[import] # pragma: no cover
    from pineboolib.loader.projectconfig import ProjectConfig  # pragma: no cover


def show_connection_dialog(app: "QtWidgets.QApplication") -> Optional["ProjectConfig"]:
    """Show the connection dialog, and configure the project accordingly."""
    from . import dlgconnect

    connection_window = dlgconnect.DlgConnect()
    connection_window.load()
    connection_window.show()
    app.exec()  # FIXME: App should be started before this function
    connection_window.close()
    return connection_window.selected_project_config
