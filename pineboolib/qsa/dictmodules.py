"""dictmodules module."""

from pineboolib import application
from pineboolib.application import qsadictmodules
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from . import formdbwidget
    from pineboolib.application.database.orm import basemodel


def from_project(scriptname: str) -> Any:
    """Get script from project."""

    return qsadictmodules.QSADictModules.from_project(scriptname)


def orm_(action_name: str = "") -> Any:
    """Get Orm from project."""

    table_name = (
        application.PROJECT.actions[action_name]._table
        if action_name in application.PROJECT.actions.keys()
        else action_name
    )

    return qsadictmodules.QSADictModules.orm_(table_name)


class Application:
    """
    Emulate QS Application class.

    The "Data" module uses "Application.formRecorddat_processes" to read the module.
    """

    def __getattr__(self, name: str) -> Any:
        """Emulate any method and retrieve application action module specified."""

        return qsadictmodules.QSADictModules.from_project(name)
