"""dictmodules module."""

from pineboolib import application

from typing import Any


def from_project(scriptname: str) -> Any:
    """Get script from project."""
    from pineboolib.application.qsadictmodules import QSADictModules

    return QSADictModules.from_project(scriptname)


# def class_(object_name: str) -> Any:
#    """Get class from project."""

#    from pineboolib.application.qsadictmodules import QSADictModules

#    return QSADictModules.class_(object_name)


def orm_(action_name: str = "") -> Any:
    """Get Orm from project."""

    table_name = action_name

    if action_name in application.PROJECT.actions.keys():
        table_name = application.PROJECT.actions[action_name]._table
    orm = None
    if table_name:
        from pineboolib.application.qsadictmodules import QSADictModules

        orm = QSADictModules.orm_(table_name)

    return orm


class Application:
    """
    Emulate QS Application class.

    The "Data" module uses "Application.formRecorddat_processes" to read the module.
    """

    def __getattr__(self, name: str) -> Any:
        """Emulate any method and retrieve application action module specified."""
        from pineboolib.application.qsadictmodules import QSADictModules

        return QSADictModules.from_project(name)
