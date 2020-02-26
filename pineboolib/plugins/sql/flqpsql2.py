"""Flqpsql2 module."""
from pineboolib import logging
from pineboolib.application.utils.check_dependencies import check_dependencies

from pineboolib.core import settings

from PyQt5 import QtWidgets

from pineboolib.plugins.sql.flqpsql import FLQPSQL
from typing import Any, cast

LOGGER = logging.getLogger(__name__)


class FLQPSQL2(FLQPSQL):
    """FLQPSQL2 class."""

    def __init__(self) -> None:
        """Inicialize."""
        super().__init__()
        self.name_ = "FLQPSQL2"
        self.alias_ = "PostgreSQL"
        self.mobile_ = True
        self.pure_python_ = True

    def safe_load(self) -> bool:
        """Return if the driver can loads dependencies safely."""
        return check_dependencies({"pg8000": "pg8000", "sqlalchemy": "sqlAlchemy"}, False)

    def connect(
        self, db_name: str, db_host: str, db_port: int, db_userName: str, db_password: str
    ) -> Any:
        """Connecto to database."""
        self._dbname = db_name
        check_dependencies({"pg8000": "pg8000", "sqlalchemy": "sqlAlchemy"})
        import pg8000  # type: ignore
        import traceback

        # conninfostr = "dbname=%s host=%s port=%s user=%s password=%s connect_timeout=5"
        #                % (db_name, db_host, db_port, db_userName, db_password)

        try:
            self.conn_ = pg8000.connect(
                user=db_userName,
                host=db_host,
                port=int(db_port),
                database=db_name,
                password=db_password,
                timeout=5,
            )

            if settings.config.value("ebcomportamiento/orm_enabled", False):
                from sqlalchemy import create_engine  # type: ignore

                self.engine_ = create_engine(
                    "postgresql+pg8000://%s:%s@%s:%s/%s"
                    % (db_userName, db_password, db_host, db_port, db_name)
                )
        except Exception as e:
            LOGGER.warning(e)
            from pineboolib import application

            if not application.PROJECT.DGI.localDesktop():
                if repr(traceback.format_exc()).find("the database system is starting up") > -1:
                    raise

                return False

            if application.PROJECT._splash:
                application.PROJECT._splash.hide()
            if repr(traceback.format_exc()).find("does not exist") > -1:
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
                        tmpConn = pg8000.connect(
                            user="postgres",
                            host=db_host,
                            port=int(db_port),
                            password=db_password,
                            timeout=5,
                        )
                        tmpConn.autocommit = True

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

        # self.conn_.autocommit = True #Posiblemente tengamos que ponerlo a
        # false para que las transacciones funcionen
        # self.conn_.set_isolation_level(
        #    pg8000.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

        self.conn_.autocommit = True

        try:
            cursor = self.conn_.cursor()
            cursor.execute("SET CLIENT_ENCODING TO 'UTF8'")
        except Exception:
            LOGGER.warning(traceback.format_exc())

        return self.conn_
