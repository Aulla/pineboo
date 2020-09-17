"""Flsqls module."""


from pineboolib.core import decorators

from pineboolib.application.metadata import pntablemetadata
from pineboolib import logging

from pineboolib.fllegacy import flutil
from . import flpymssql

from typing import Optional, Union, List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.engine import base, result  # type: ignore [import] # noqa: F401, F821
    from sqlalchemy.orm import session as orm_session  # noqa: F401


LOGGER = logging.get_logger(__name__)


class FLPYODBC(flpymssql.FLPYMSSQL):
    """FLPYODBC class."""

    def __init__(self):
        """Inicialize."""
        super().__init__()
        self.name_ = "FLPYODBC"
        self.alias_ = "SQL Server (PYODBC)"
        self._safe_load = {"pyodbc": "pyodbc", "sqlalchemy": "sqlAlchemy"}
        self._database_not_found_keywords = ["4060"]
        self._sqlalchemy_name = "mssql+pyodbc"

    def loadConnectionString(self, name: str, host: str, port: int, usern: str, passw_: str) -> str:
        """Set special config."""

        return (
            super().loadConnectionString(name, host, port, usern, passw_)
            + "?driver=ODBC+Driver+17+for+SQL+Server"
        )
