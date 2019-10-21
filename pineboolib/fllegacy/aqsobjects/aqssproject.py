"""Aqssproject module."""

from PyQt5 import QtCore
from pineboolib.fllegacy import flapplication

from typing import Optional


class AQSSProject(QtCore.QObject):
    """AQSSProject class."""

    New = 0
    Changed = 1
    UnChanged = 2

    def callEntryFunction(self):
        """Call entry function."""
        flapplication.aqApp.callScriptEntryFunction()

    def get_entry_function(self) -> Optional[str]:
        """Return entry function."""
        return flapplication.aqApp.script_entry_function_

    def set_entry_function(self, entry_fun_: str) -> None:
        """Set entry function."""
        flapplication.aqApp.script_entry_function_ = entry_fun_

    entryFunction = property(get_entry_function, set_entry_function)
