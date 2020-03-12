"""Flqpsql2 module."""
from pineboolib import logging

from pineboolib.plugins.sql.flqpsql import FLQPSQL
from typing import Any

LOGGER = logging.get_logger(__name__)


class FLQPSQL2(FLQPSQL):
    """FLQPSQL2 class."""

    def __init__(self) -> None:
        """Inicialize."""
        super().__init__()
        self.name_ = "FLQPSQL2"
        self.alias_ = "PostgreSQL"
        self.mobile_ = True
        self.pure_python_ = True
        self._safe_load = {"pg8000": "pg8000", "sqlalchemy": "sqlAlchemy"}

    def getEngine(self, name: str, host: str, port: int, usern: str, passw_: str) -> Any:
        """Return sqlAlchemy connection."""
        from sqlalchemy import create_engine  # type: ignore

        return create_engine(
            "postgresql+pg8000://%s:%s@%s:%s/%s" % (usern, passw_, host, port, name)
        )

    def getConn(self, name: str, host: str, port: int, usern: str, passw_: str) -> Any:
        """Return connection."""

        import pg8000  # type: ignore

        conn_ = None

        try:
            conn_ = pg8000.connect(
                user=usern, host=host, port=port, database=name, password=passw_, timeout=5
            )
        except Exception as error:
            self.setLastError(str(error), "CONNECT")

        return conn_

    def loadSpecialConfig(self) -> None:
        """Set special config."""

        self.conn_.autocommit = True
        cursor = self.conn_.cursor()
        cursor.execute("SET CLIENT_ENCODING TO 'UTF8'")

    def getAlternativeConn(self, name: str, host: str, port: int, usern: str, passw_: str) -> Any:
        """Return connection."""

        conn_ = self.getConn("postgres", host, port, usern, passw_)
        if conn_ is not None:
            conn_.autocommit = True

        return conn_
