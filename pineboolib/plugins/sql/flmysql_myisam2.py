"""
Module for MYISAM2 driver.
"""
from PyQt5.Qt import qWarning  # type: ignore


from PyQt5.QtWidgets import QMessageBox, QWidget  # type: ignore
from pineboolib.application.utils.check_dependencies import check_dependencies

from pineboolib.application import project


from pineboolib import logging

from . import flmysql_myisam

import traceback

from typing import Any, Dict, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.application.metadata import pntablemetadata  # noqa: F401
    from pineboolib.application.database import pnsqlcursor  # noqa: F401

logger = logging.getLogger(__name__)


class FLMYSQL_MYISAM2(flmysql_myisam.FLMYSQL_MYISAM):
    """MYISAM2 Driver class."""

    cursorsArray_: Dict[str, Any]  # IApiCursor

    def __init__(self):
        """Create empty driver."""
        super().__init__()
        self.version_ = "0.8"
        self.conn_ = None
        self.name_ = "FLMYSQL_MyISAM2"
        self.open_ = False
        self.alias_ = "MySQL MyISAM (PyMySQL)"
        self.cursorsArray_ = {}
        self.noInnoDB = True
        self.mobile_ = True
        self.pure_python_ = True
        self.defaultPort_ = 3306
        self.rowsFetched: Dict[str, int] = {}
        self.active_create_index = True
        self.db_ = None
        self.engine_ = None
        self.session_ = None
        self.declarative_base_ = None
        self.lastError_ = None

    def safe_load(self) -> bool:
        """Return if the driver can loads dependencies safely."""
        return check_dependencies({"pymysql": "PyMySQL", "sqlalchemy": "sqlAlchemy"}, False)

    def connect(
        self, db_name: str, db_host: str, db_port: int, db_userName: str, db_password: str
    ) -> Any:
        """Connect to a database."""
        self._dbname = db_name
        check_dependencies({"pymysql": "PyMySQL", "sqlalchemy": "sqlAlchemy"})
        from sqlalchemy import create_engine  # type: ignore
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
            self.engine_ = create_engine(
                "mysql+pymysql://%s:%s@%s:%s/%s"
                % (db_userName, db_password, db_host, db_port, db_name)
            )
        except pymysql.Error as e:
            if project._splash:
                project._splash.hide()
            if "Unknown database" in str(e):
                if project._DGI and not project.DGI.localDesktop():
                    return False

                ret = QMessageBox.warning(
                    QWidget(),
                    "Pineboo",
                    "La base de datos %s no existe.\n¿Desea crearla?" % db_name,
                    cast(QMessageBox, QMessageBox.Ok | QMessageBox.No),
                )
                if ret == QMessageBox.No:
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
                            print("ERROR: FLMYSQL2.connect", traceback.format_exc())
                            cursor.execute("ROLLBACK")
                            cursor.close()
                            return False
                        cursor.close()
                        return self.connect(db_name, db_host, db_port, db_userName, db_password)
                    except Exception:
                        qWarning(traceback.format_exc())
                        QMessageBox.information(
                            QWidget(),
                            "Pineboo",
                            "ERROR: No se ha podido crear la Base de Datos %s" % db_name,
                            QMessageBox.Ok,
                        )
                        print("ERROR: No se ha podido crear la Base de Datos %s" % db_name)
                        return False

            else:
                QMessageBox.information(
                    QWidget(), "Pineboo", "Error de conexión\n%s" % str(e), QMessageBox.Ok
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
