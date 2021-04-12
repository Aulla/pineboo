"""Aqssproject module."""

from PyQt6 import QtCore  # type: ignore[import]

from pineboolib import application


class AQSSProject(QtCore.QObject):
    """AQSSProject class."""

    New = 0
    Changed = 1
    UnChanged = 2

    def callEntryFunction(self):
        """Call entry function."""
        application.PROJECT.aq_app.callScriptEntryFunction()

    def get_entry_function(self) -> str:
        """Return entry function."""
        return application.PROJECT.aq_app.script_entry_function_

    def set_entry_function(self, entry_fun_: str) -> None:
        """Set entry function."""
        application.PROJECT.aq_app.script_entry_function_ = entry_fun_

    entryFunction = property(get_entry_function, set_entry_function)
