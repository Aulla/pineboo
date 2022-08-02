# -*- coding: utf-8 -*-
"""
Defines the PNConnection class.
"""

from pineboolib.interfaces.isqlcursor import ISqlCursor
from PyQt6 import QtCore, QtWidgets  # type: ignore[import]

from pineboolib.core import settings, decorators
from pineboolib.core.utils import utils_base
from pineboolib.interfaces import iconnection
from pineboolib import application
from pineboolib.application.database.orm import alembic_tools

from typing import List, Optional, Any, Union, TYPE_CHECKING


if TYPE_CHECKING:
    from pineboolib.interfaces import isqlcursor, isqldriver, isession  # pragma: no cover
    from pineboolib.application.metadata import pntablemetadata  # pragma: no cover
    from sqlalchemy.engine import base, result  # pragma: no cover

    from . import pnconnectionmanager  # pragma: no cover

LOGGER = utils_base.logging.get_logger(__name__)


class PNConnection(QtCore.QObject, iconnection.IConnection):
    """Wrapper for database cursors which are used to emulate FLSqlCursor."""

    def __init__(
        self,
        db_name: str,
        db_host: str = "",
        db_port: int = 0,
        db_user_name: str = "",
        db_password: str = "",
        driver_alias: str = "",
    ) -> None:
        """Database connection through a sql driver."""

        super().__init__()
        self.conn = None
        self._transaction_level = 0
        self._driver = None
        self._db_name = db_name
        self._session_legacy = None
        self._session_atomic = None

        conn_manager = application.PROJECT.conn_manager
        self._conn_manager = conn_manager
        if conn_manager is None:
            raise Exception("conn_manager is not Initialized!")

        if "main_conn" in conn_manager.connections_dict.keys():
            main_conn_ = conn_manager.connections_dict["main_conn"]
            if main_conn_._db_name == self._db_name and not db_host:
                db_host = main_conn_._db_host
                db_port = main_conn_._db_port
                db_user_name = main_conn_._db_user_name
                db_password = main_conn_._db_password
                driver_alias = main_conn_.driverAlias()

        self._db_host = db_host
        self._db_port = db_port
        self._db_user_name = db_user_name
        self._db_password = db_password

        self._driver_name = conn_manager._drivers_sql_manager.aliasToName(driver_alias)

        if application.USE_INTERACTIVE_GUI:
            self._interactive_gui = "Pineboo" if not utils_base.is_library() else "Pinebooapi"
        else:
            self._interactive_gui = ""

        self._last_active_cursor = None
        self._last_error = ""
        self._is_open = False

    def connManager(self) -> "pnconnectionmanager.PNConnectionManager":
        """Return connection manager."""
        return self._conn_manager

    def database(self) -> "iconnection.IConnection":
        """Return self."""
        return self

    def db(self) -> "iconnection.IConnection":
        """Return self."""

        return self

    def connectionName(self) -> str:
        """Get the current connection name for this cursor."""
        return self._name

    def connection(self) -> "base.Connection":
        """Return base connection."""

        return self.driver().connection()

    def isOpen(self) -> bool:
        """Indicate if a connection is open."""

        return self._is_open and self.driver().is_open()

    def tables(self, tables_type: Union[str, int] = "") -> List[str]:
        """Return a list of available tables in the database, according to a given filter."""

        types = ["", "Tables", "SystemTables", "Views"]

        if isinstance(tables_type, int):
            item = ""
            if tables_type < len(types):
                item = types[tables_type]
        else:
            item = tables_type

        return self.driver().tables(item)

    def DBName(self) -> str:
        """Return the database name."""
        return self.driver().DBName()

    def driver(self) -> "isqldriver.ISqlDriver":
        """Return the instance of the driver that is using the connection."""
        if self._driver is None:
            self._driver = self._conn_manager._drivers_sql_manager.driver()

        return self._driver

    def session(self, raise_error: bool = True) -> "isession.PinebooSession":
        """
        Sqlalchemy session.

        When using the ORM option this function returns the session for sqlAlchemy.
        """
        if self._name == "main_conn":
            raise Exception("main_conn no es valido para session")
        mng = self.connManager()

        returned_session = (
            self._session_legacy if self._session_atomic is None else self._session_atomic
        )

        if not mng.is_valid_session(returned_session, raise_error):
            if returned_session is not None:
                mng.remove_session(returned_session)

            returned_session = self.driver().session()

            if self._session_atomic is not None:
                # self._session_atomic = returned_session
                raise Exception("la transacción atómica no es válida")
            else:
                LOGGER.debug("Nueva sesión %s --> %s" % (self._name, returned_session))
                self._session_legacy = returned_session

        if not returned_session:
            raise ValueError("Invalid session!")

        return returned_session

    def engine(self) -> "base.Engine":
        """Sqlalchemy connection."""

        return self.driver().engine()

    def conectar(
        self,
        db_name: str,
        db_host: str = "",
        db_port: int = 0,
        db_user_name: str = "",
        db_password: str = "",
    ) -> Union["base.Connection", bool]:
        """Request a connection to the database."""

        self._db_name = db_name
        self._db_host = db_host
        self._db_port = db_port
        self._db_user_name = db_user_name
        self._db_password = db_password
        # if self._db_name:
        #    self.driver().alias_ = self.driverName() + ":" + self._name
        self.driver().db_ = self
        LOGGER.debug("")
        result: Union["base.Connection", bool] = self.driver().connect(
            db_name, db_host, db_port, db_user_name, db_password
        )
        LOGGER.debug(
            " NEW CONNECTION NAME: %s, HOST: %s, PORT: %s, DB NAME: %s, USER NAME: %s, STATUS: %s",
            self._name,
            db_host,
            db_port,
            db_name,
            db_user_name,
            "FAILURE" if not result else "ESTABLISHED",
        )

        return result

    def driverName(self) -> str:
        """Return sql driver name."""

        return self.driver().driverName()

    def driverAlias(self) -> str:
        """Return sql driver alias."""
        return self.driver().alias_

    def driverNameToDriverAlias(self, name: str) -> str:
        """Return the alias from the name of a sql driver."""

        return self._conn_manager._drivers_sql_manager.nameToAlias(name)

    def lastError(self) -> str:
        """Return the last error reported by the sql driver."""

        return self.driver().last_error()

    def host(self) -> str:
        """Return the name of the database host."""

        return self._db_host

    def port(self) -> int:
        """Return the port used by the database."""

        return self._db_port

    def user(self) -> str:
        """Return the user name used by the database."""

        return self._db_user_name

    def returnword(self) -> str:
        """Return the password used by the database."""

        return self._db_password

    @decorators.deprecated
    def password(self) -> str:
        """Return the password used by the database."""

        return self._db_password

    def setInteractiveGUI(self, gui_name: str) -> None:
        """Set if it is an interactive GUI."""
        if application.USE_INTERACTIVE_GUI:
            self._interactive_gui = gui_name

    def formatValue(self, type_: str, value: Any, upper: bool) -> Any:
        """Return a correctly formatted value to be assigned as a where filter."""

        return self.driver().formatValue(type_, value, upper)

    def formatValueLike(self, type_: str, value: Any, upper: bool) -> str:
        """Return a correctly formatted value to be assigned as a WHERE LIKE filter."""

        return self.driver().formatValueLike(type_, value, upper)

    def lastActiveCursor(self) -> Optional["ISqlCursor"]:
        """Return the last active cursor in the sql driver."""

        return self._last_active_cursor

    def doTransaction(self, cursor: "isqlcursor.ISqlCursor") -> bool:
        """Make a transaction or savePoint according to transaction level."""

        if settings.CONFIG.value("application/isDebuggerMode", False):
            text_ = (
                "Creando punto de salvaguarda %s:%s" % (self._name, self._transaction_level)
                if self._transaction_level
                else "Iniciando Transacción... %s" % self._transaction_level
            )
            application.PROJECT.message_manager().send("status_help_msg", "send", [text_])

        # LOGGER.warning(
        #    "Creando transaccion/savePoint número:%s, cursor:%s, tabla:%s",
        #    self._transaction_level,
        #    cursor.curName(),
        #    cursor.table(),
        # )
        if not self.transaction():
            return False
        if not self._transaction_level:
            self._last_active_cursor = cursor
            application.PROJECT.aq_app.emitTransactionBegin(cursor)

        self._transaction_level += 1
        cursor.private_cursor._transactions_opened.insert(0, self._transaction_level)
        return True

    def transactionLevel(self) -> int:
        """Indicate the level of transaction."""

        return self._transaction_level

    def doRollback(self, cur: "isqlcursor.ISqlCursor") -> bool:
        """Drop a transaction or savepoint depending on the transaction level."""

        cancel = False
        if (
            cur.modeAccess() in (cur.Insert, cur.Edit)
            and cur.isModifiedBuffer()
            and cur.private_cursor._ask_for_cancel_changes
        ):

            msg_box = getattr(application.PROJECT.DGI, "msgBoxQuestion", None)
            if msg_box is not None:
                res = msg_box(
                    "Todos los cambios se cancelarán.¿Está seguro?", None, "Cancelar Cambios"
                )

                if res is not None:
                    if res == QtWidgets.QMessageBox.StandardButton.No:
                        return False

            cancel = True

        if self._transaction_level:
            if cur.private_cursor._transactions_opened:
                trans = cur.private_cursor._transactions_opened.pop()
                if not trans == self._transaction_level:
                    LOGGER.warning(
                        "FLSqlDatabase: El cursor %s va a deshacer la transacción %s pero la última que inició es la %s",
                        cur.curName(),
                        self._transaction_level,
                        trans,
                    )
            else:
                LOGGER.warning(
                    "FLSqlDatabaser : El cursor va a deshacer la transacción %s pero no ha iniciado ninguna",
                    self._transaction_level,
                )

            self._transaction_level -= 1
        else:
            return True

        if self._transaction_level:
            text_ = "Restaurando punto de salvaguarda %s:%s..." % (
                self._name,
                self._transaction_level,
            )
        else:
            text_ = "Deshaciendo Transacción... %s" % self._transaction_level

        application.PROJECT.message_manager().send("status_help_msg", "send", [text_])

        # LOGGER.warning(
        #    "Desaciendo transacción número:%s, cursor:%s", self._transaction_level, cur.curName()
        # )

        if not self.rollback():
            return False

        cur.setModeAccess(cur.Browse)

        if not self._transaction_level:
            self._last_active_cursor = None
            application.PROJECT.aq_app.emitTransactionRollback(cur)

            if cancel:
                cur.select()

        return True

    def interactiveGUI(self) -> str:
        """Return if it is an interactive GUI."""

        return self._interactive_gui

    def doCommit(self, cur: "isqlcursor.ISqlCursor", notify: bool = True) -> bool:
        """Approve changes to a transaction or a save point based on your transaction level."""

        if not notify:
            cur.autoCommit.emit()

        if self._transaction_level:
            if cur.private_cursor._transactions_opened:
                trans = cur.private_cursor._transactions_opened.pop()
                if not trans == self._transaction_level:
                    LOGGER.warning(
                        "El cursor %s va a terminar la transacción %s pero la última que inició es la %s",
                        cur.curName(),
                        self._transaction_level,
                        trans,
                        stack_info=True,
                    )
            else:
                LOGGER.warning(
                    "El cursor va a terminar la transacción %s pero no ha iniciado ninguna",
                    self._transaction_level,
                )

            self._transaction_level -= 1
        else:

            return True

        if self._transaction_level:
            text_ = "Liberando punto de salvaguarda %s:%s..." % (
                self._name,
                self._transaction_level,
            )
        else:
            text_ = "Terminando Transacción... %s" % self._transaction_level

        application.PROJECT.message_manager().send("status_help_msg", "send", [text_])

        # LOGGER.warning(
        #    "Aceptando transacción número:%s, cursor:%s", self._transaction_level, cur.curName()
        # )

        if not self.commit():
            return False

        if not self._transaction_level:
            self._last_active_cursor = None
            application.PROJECT.aq_app.emitTransactionEnd(cur)

        if notify:
            cur.setModeAccess(cur.Browse)

        return True

    def canDetectLocks(self) -> bool:
        """Indicate if the connection detects locks in the database."""

        return self.driver().canDetectLocks()

    def canOverPartition(self) -> bool:
        """Return True if the database supports the OVER statement."""

        return self.connManager().dbAux().driver().canOverPartition()

    def Mr_Proper(self):
        """Clean the database of unnecessary tables and records."""

        self.connManager().dbAux().driver().Mr_Proper()

    def transaction(self) -> bool:
        """Create a transaction."""

        try:
            session_ = self.session()
            if not session_.transaction:
                LOGGER.debug("ISOLATION LEVEL %s", session_.connection().get_isolation_level())
                session_.begin()
            else:
                session_.begin_nested()
            return True
        except Exception as error:
            self._last_error = "No se pudo crear la transacción: %s" % str(error)
            LOGGER.warning(self._last_error)

        return False

    def commit(self) -> bool:
        """Release a transaction."""

        try:

            session_ = self.session()
            session_.commit()

            return True
        except Exception as error:
            LOGGER.warning("Commit: %s", str(error), stack_info=True)
            self._last_error = "No se pudo aceptar la transacción: %s" % str(error)

        return False

    def rollback(self) -> bool:
        """Roll back a transaction."""
        try:
            session_ = self.session()
            session_.rollback()
            return True
        except Exception as error:
            self._last_error = "No se pudo deshacer la transacción: %s" % str(error)

        return False

    def nextSerialVal(self, table: str, field: str) -> int:
        """Indicate next available value of a serial type field."""

        return self.driver().nextSerialVal(table, field)

    def existsTable(self, name: str) -> bool:
        """Indicate the existence of a table in the database."""

        return self.driver().existsTable(name)

    def createTable(self, tmd: "pntablemetadata.PNTableMetaData") -> bool:
        """Create a table in the database, from a PNTableMetaData."""

        sql = self.driver().sqlCreateTable(tmd, True)
        if not sql:
            return False

        use_save_points = self.driver()._use_create_table_save_points

        if use_save_points:
            self.transaction()
        for single_sql in sql.split(";"):
            self.execute_query(single_sql)
            if self.driver().last_error():
                LOGGER.exception(
                    "createTable: Error happened executing sql: %s...%s"
                    % (single_sql[:80], str(self.driver().last_error()))
                )
                if use_save_points:
                    self.rollback()
                self.driver().set_last_error_null()
                return False

        if use_save_points:
            self.commit()
        return True

    def mismatchedTable(self, tablename: str, tmd: "pntablemetadata.PNTableMetaData") -> bool:
        """Compare an existing table with a PNTableMetaData and return if there are differences."""

        return self.connManager().dbAux().driver().mismatchedTable(tablename, tmd)

    def normalizeValue(self, text: str) -> Optional[str]:
        """Return the value of a correctly formatted string to the database type from a string."""
        return self.driver().normalizeValue(text)

    # def queryUpdate(self, name: str, update: str, filter: str) -> Optional[str]:
    #    """Return a correct UPDATE query for the database type."""

    #    return self.driver().queryUpdate(name, update, filter)

    def execute_query(self, qry) -> Optional["result.ResultProxy"]:
        """Execute a query in a database cursor."""

        return self.driver().execute_query(qry)

    def alterTable(self, new_metadata: "pntablemetadata.PNTableMetaData") -> bool:
        """Modify the fields of a table in the database based on the differences of two PNTableMetaData."""
        # print(
        #    "* ALTER TABLE %s * %s "
        #    % ("LEGACY" if application.USE_ALTER_TABLE_LEGACY else "ALEMBIC", new_metadata.name())
        # )
        if application.USE_ALTER_TABLE_LEGACY:
            return self.connManager().dbAux().driver().alterTable(new_metadata)

        alm = alembic_tools.Migration(self.connManager().dbAux())
        return alm.upgrade(new_metadata)

    def canRegenTables(self) -> bool:
        """Return if can regenerate tables."""

        return self.driver().canRegenTables() if self._driver_name else False

    def regenTable(self, table_name: str, mtd: "pntablemetadata.PNTableMetaData") -> bool:
        """Regenerate a table."""

        return self.driver().regenTable(table_name, mtd)

    def getTimeStamp(self) -> str:
        """Return timestamp."""

        return self.driver().getTimeStamp()

    def __str__(self):
        """Return the name of the database in text format."""

        return self.DBName()

    def __repr__(self):
        """Return the name of the database in text format."""

        return self.DBName()

    def close(self):
        """Close connection."""
        if self._session_legacy is not None:
            self._session_legacy.close()
            self._session_legacy = None
        self._is_open = False
        self.driver().close()

    def sqlLength(self, field_name: str, size: int) -> str:
        """Return length formated."""

        return self.driver().sqlLength(field_name, size)

    def resolve_dsn(self) -> str:
        """Return dsn data."""

        return self.driver().loadConnectionString(
            self._db_name, self._db_host, self._db_port, self._db_user_name, self._db_password
        )
