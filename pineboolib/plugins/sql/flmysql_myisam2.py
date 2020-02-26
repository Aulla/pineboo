"""
Module for MYISAM2 driver.
"""
from PyQt5 import QtWidgets

from pineboolib.application.utils import check_dependencies
from pineboolib import application, logging

from pineboolib.core import settings

from . import flmysql_myisam

import traceback

from typing import Any, Dict, cast, List, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.application.metadata import pntablemetadata  # noqa: F401

LOGGER = logging.getLogger(__name__)


class FLMYSQL_MYISAM2(flmysql_myisam.FLMYSQL_MYISAM):
    """MYISAM2 Driver class."""

    cursorsArray_: Dict[str, Any]  # IApiCursor
    rowsFetched: Dict[str, List]

    def __init__(self):
        """Create empty driver."""
        super().__init__()
        self.name_ = "FLMYSQL_MyISAM2"
        self.alias_ = "MySQL MyISAM (PyMySQL)"
        self.cursorsArray_ = {}
        self.mobile_ = True
        self.pure_python_ = True
        self.rowsFetched = {}

    def safe_load(self) -> bool:
        """Return if the driver can loads dependencies safely."""
        return check_dependencies.check_dependencies(
            {"pymysql": "PyMySQL", "sqlalchemy": "sqlAlchemy"}, False
        )

    def connect(
        self, db_name: str, db_host: str, db_port: int, db_userName: str, db_password: str
    ) -> Any:
        """Connect to a database."""
        self._dbname = db_name
        check_dependencies.check_dependencies({"pymysql": "PyMySQL", "sqlalchemy": "sqlAlchemy"})
        import pymysql

        try:
            self.conn_ = pymysql.connect(
                host=db_host,
                user=db_userName,
                password=db_password,
                db=db_name,
                charset="utf8",
                autocommit=True,
            )

            if settings.config.value("ebcomportamiento/orm_enabled", False):
                from sqlalchemy import create_engine  # type: ignore

                self.engine_ = create_engine(
                    "mysql+pymysql://%s:%s@%s:%s/%s"
                    % (db_userName, db_password, db_host, db_port, db_name)
                )
        except pymysql.Error as e:
            LOGGER.warning(e)
            if application.PROJECT._splash:
                application.PROJECT._splash.hide()
            if "Unknown database" in str(e):
                if not application.PROJECT.DGI.localDesktop():
                    return False

                ret = QtWidgets.QMessageBox.warning(
                    QtWidgets.QWidget(),
                    "Pineboo",
                    "La base de datos %s no existe.\n¿Desea crearla?" % db_name,
                    cast(
                        QtWidgets.QMessageBox.StandardButtons,
                        QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.No,
                    ),
                )
                if ret == QtWidgets.QMessageBox.No:
                    return False
                else:
                    try:
                        tmpConn = pymysql.connect(
                            host=db_host,
                            user=db_userName,
                            password=db_password,
                            charset="utf8",
                            autocommit=True,
                        )
                        cursor = tmpConn.cursor()
                        try:
                            cursor.execute("CREATE DATABASE %s" % db_name)
                        except Exception:
                            LOGGER.warning(traceback.format_exc())
                            cursor.execute("ROLLBACK")
                            cursor.close()
                            return False
                        cursor.close()
                        return self.connect(db_name, db_host, db_port, db_userName, db_password)
                    except Exception:
                        LOGGER.warning(traceback.format_exc())
                        QtWidgets.QMessageBox.information(
                            QtWidgets.QWidget(),
                            "Pineboo",
                            "ERROR: No se ha podido crear la Base de Datos %s" % db_name,
                            QtWidgets.QMessageBox.Ok,
                        )
                        print("ERROR: No se ha podido crear la Base de Datos %s" % db_name)
                        return False

            else:
                QtWidgets.QMessageBox.information(
                    QtWidgets.QWidget(),
                    "Pineboo",
                    "Error de conexión\n%s" % str(e),
                    QtWidgets.QMessageBox.Ok,
                )
                return False

        if self.conn_:
            self.open_ = True
        # self.conn_.autocommit(True)
        # self.conn_.set_character_set('utf8')

        return self.conn_

    def dict_cursor(self) -> Any:
        """Return dict cursor."""

        from pymysql.cursors import DictCursor  # type: ignore

        return DictCursor

    def normalizeValue(self, text: str) -> str:
        """Escape values, suitable to prevent sql injection."""
        import pymysql

        return pymysql.escape_string(text)
