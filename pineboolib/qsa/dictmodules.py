"""dictmodules module."""

from typing import Any


def from_project(scriptname: str) -> Any:
    """Get script from project."""
    from pineboolib.application.qsadictmodules import QSADictModules

    return QSADictModules.from_project(scriptname)


def class_(object_name: str) -> Any:
    """Get class from project."""

    from pineboolib.application.qsadictmodules import QSADictModules

    return QSADictModules.class_(object_name)


class Application:
    """
    Emulate QS Application class.

    The "Data" module uses "Application.formRecorddat_processes" to read the module.
    """

    def __getattr__(self, name: str) -> Any:
        """Emulate any method and retrieve application action module specified."""
        from pineboolib.application.qsadictmodules import QSADictModules

        return QSADictModules.from_project(name)
