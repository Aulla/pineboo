"""
Module for MYISAM2 driver.
"""


from pineboolib import logging


from . import flmysql_myisam


from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.application.metadata import pntablemetadata  # noqa: F401

LOGGER = logging.get_logger(__name__)


class FLMYSQL_MYISAM2(flmysql_myisam.FLMYSQL_MYISAM):
    """MYISAM2 Driver class."""

    def __init__(self):
        """Create empty driver."""
        super().__init__()
        self.name_ = "FLMYSQL_MyISAM2"
        self.alias_ = "MySQL MyISAM (PyMySQL)"
        self.mobile_ = True
        self.pure_python_ = True
        self._safe_load = {"pymysql": "PyMySQL", "sqlalchemy": "sqlAlchemy"}
        self._default_charset = "DEFAULT CHARACTER SET = UTF8MB3 COLLATE = UTF8MB3_BIN"

    def getEngine(self, name: str, host: str, port: int, usern: str, passw_: str) -> Any:
        """Return sqlAlchemy connection."""
        from sqlalchemy import create_engine  # type: ignore

        return create_engine("mysql+pymysql://%s:%s@%s:%s/%s" % (usern, passw_, host, port, name))

    def getConn(self, name: str, host: str, port: int, usern: str, passw_: str) -> Any:
        """Return connection."""

        import pymysql  # type: ignore

        conn_ = None
        try:
            conn_ = pymysql.connect(
                host=host, user=usern, password=passw_, db=name, charset="UTF8MB4", autocommit=True
            )
        except pymysql.Error as error:
            self.setLastError(str(error), "CONNECT")

        return conn_

    def getAlternativeConn(self, name: str, host: str, port: int, usern: str, passw_: str) -> Any:
        """Return connection."""

        import pymysql  # type: ignore

        conn_ = None
        try:
            conn_ = pymysql.connect(
                host=host, user=usern, password=passw_, charset="UTF8MB4", autocommit=True
            )
        except pymysql.Error as error:
            self.setLastError(str(error), "CONNECT")

        return conn_

    def loadSpecialConfig(self) -> None:
        """Set special config."""

        pass

    def dict_cursor(self) -> Any:
        """Return dict cursor."""

        from pymysql.cursors import DictCursor  # type: ignore

        return DictCursor

    def normalizeValue(self, text: str) -> str:
        """Escape values, suitable to prevent sql injection."""
        import pymysql

        return pymysql.escape_string(text)
