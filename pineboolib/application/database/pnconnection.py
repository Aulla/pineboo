# -*- coding: utf-8 -*-
"""
Defines the PNConnection class.
"""
from PyQt5 import QtCore, QtWidgets

from pineboolib.core import settings, utils, decorators
from pineboolib.core.utils import utils_base
from pineboolib.interfaces import iconnection
from . import pnsqldrivers
from pineboolib import application

# from .pnsqlsavepoint import PNSqlSavePoint
from . import DB_SIGNALS
from typing import Dict, List, Optional, Any, Union, TYPE_CHECKING

import time

if TYPE_CHECKING:
    from pineboolib.interfaces import isqlcursor
    from pineboolib.application.metadata import pntablemetadata
    from . import pnconnectionmanager

    from sqlalchemy.engine import base  # type: ignore [import] # noqa: F821, F401
LOGGER = utils.logging.get_logger(__name__)


class PNConnection(QtCore.QObject, iconnection.IConnection):
    """Wrapper for database cursors which are used to emulate FLSqlCursor."""

    _name: str
    _db_name: str
    _db_host: Optional[str]
    _db_port: Optional[int]
    _db_user_name: Optional[str]
    _db_password: str = ""
    conn: Optional["base.Connection"] = None  # Connection from the actual driver

    _driver_sql: "pnsqldrivers.PNSqlDrivers"
    _driver_name: str
    # currentSavePoint_: Optional[PNSqlSavePoint]
    # stackSavePoints_: List[PNSqlSavePoint]
    # queueSavePoints_: List[PNSqlSavePoint]
    _interactive_gui: str
    _db_aux = None
    _is_open: bool
    _driver = None
    _last_active_cursor: Optional["isqlcursor.ISqlCursor"]
    connections_dict: Dict[str, "iconnection.IConnection"] = {}
    _conn_manager: "pnconnectionmanager.PNConnectionManager"
    _last_activity_time: float
    # _current_transaction: Optional["session.Session"]
    _last_error: str

    def __init__(
        self,
        db_name: str,
        db_host: Optional[str] = None,
        db_port: Optional[int] = None,
        db_user_name: Optional[str] = None,
        db_password: str = "",
        driver_alias: Optional[str] = None,
    ) -> None:
        """Database connection through a sql driver."""

        super().__init__()
        self.update_activity_time()
        self.conn = None

        self._driver = None
        self._db_name = db_name
        self._driver_sql = pnsqldrivers.PNSqlDrivers()

        conn_manager = application.PROJECT.conn_manager
        self._conn_manager = conn_manager
        if conn_manager is None:
            raise Exception("conn_manager is not Initialized!")

        if "main_conn" in conn_manager.connections_dict.keys():
            main_conn_ = conn_manager.connections_dict["main_conn"]
            if main_conn_._db_name == db_name and db_host is None:
                db_host = main_conn_._db_host
                db_port = main_conn_._db_port
                db_user_name = main_conn_._db_user_name
                db_password = main_conn_._db_password
                driver_alias = main_conn_.driverAlias()

        self._db_host = db_host
        self._db_port = db_port
        self._db_user_name = db_user_name
        self._db_password = db_password

        if driver_alias is None:
            raise Exception("driver alias is empty!")

        self._driver_name = self._driver_sql.aliasToName(driver_alias)

        # self.driver()._transaction = 0
        # self.stackSavePoints_ = []
        # self.queueSavePoints_ = []
        self._interactive_gui = "Pineboo" if not utils_base.is_library() else "Pinebooapi"
        self._last_active_cursor = None
        # self._current_transaction = None
        self._last_error = ""
        self._is_open = False
        # if self._driver_name and self._driver_sql.loadDriver(self._driver_name):
        #    self.conn = self.conectar(db_name, db_host, db_port, db_user_name, db_password)
        #    if self.conn is False:
        #        return

        # else:
        #    LOGGER.error("PNConnection.ERROR: No se encontro el driver '%s'", driverAlias)
        #    import sys

        #    sys.exit(0)

    def connManager(self):
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

    def tables(self, tables_type: Optional[Union[str, int]] = "") -> List[str]:
        """Return a list of available tables in the database, according to a given filter."""

        if isinstance(tables_type, int):
            if tables_type == 1:
                tables_type = "Tables"
            elif tables_type == 2:
                tables_type = "SystemTables"
            elif tables_type == 3:
                tables_type = "Views"
            else:
                tables_type = ""

        return self.driver().tables(tables_type)

    def DBName(self) -> str:
        """Return the database name."""
        return self.driver().DBName()

    def driver(self) -> Any:
        """Return the instance of the driver that is using the connection."""
        if self._driver is None:
            self._driver = self._driver_sql.driver()

        self.update_activity_time()
        return self._driver

    def session(self) -> "base.Connection":
        """
        Sqlalchemy session.

        When using the ORM option this function returns the session for sqlAlchemy.
        """

        return self.driver().session()

    def engine(self) -> Any:
        """Sqlalchemy connection."""

        return self.driver().engine()

    def conectar(
        self,
        db_name: str,
        db_host: Optional[str],
        db_port: Optional[int],
        db_user_name: Optional[str],
        db_password: str = "",
        limit_conn: int = 0,
    ) -> Any:
        """Request a connection to the database."""

        self._db_name = db_name
        self._db_host = db_host
        self._db_port = db_port
        self._db_user_name = db_user_name
        self._db_password = db_password
        # if self._db_name:
        #    self.driver().alias_ = self.driverName() + ":" + self._name
        self.driver().db_ = self

        LOGGER.info("**********************************")
        LOGGER.info(" ESTABLISHING DATABASE CONNECTION ")
        LOGGER.info(" * CONN NAME : %s", self.connectionName())
        LOGGER.info(" * HOST      : %s", db_host)
        LOGGER.info(" * PORT      : %s", db_port)
        LOGGER.info(" * DB NAME   : %s", db_name)
        LOGGER.info(" * USER NAME : %s", db_user_name)
        LOGGER.info("")

        result = self.driver().connect(
            db_name, db_host, db_port, db_user_name, db_password, limit_conn
        )
        LOGGER.info(
            " CONNECTION TO %s %s ",
            self.connectionName(),
            "FAILURE" if isinstance(result, bool) else "ESTABLISHED",
        )
        LOGGER.info("**********************************")
        return result

    def driverName(self) -> str:
        """Return sql driver name."""

        return self.driver().driverName()

    def driverAlias(self) -> str:
        """Return sql driver alias."""
        return self.driver().alias_

    def driverNameToDriverAlias(self, name: str) -> str:
        """Return the alias from the name of a sql driver."""

        if self._driver_sql is None:
            raise Exception("driverNameoDriverAlias. Sql driver manager is not defined")

        return self._driver_sql.nameToAlias(name)

    def lastError(self) -> str:
        """Return the last error reported by the sql driver."""

        return self.driver().last_error()

    def host(self) -> Optional[str]:
        """Return the name of the database host."""

        return self._db_host

    def port(self) -> Optional[int]:
        """Return the port used by the database."""

        return self._db_port

    def user(self) -> Optional[str]:
        """Return the user name used by the database."""

        return self._db_user_name

    def returnword(self) -> str:
        """Return the password used by the database."""

        return self._db_password

    @decorators.deprecated
    def password(self) -> str:
        """Return the password used by the database."""

        return self._db_password

    def seek(self, offs, whence=0) -> Any:
        """Position the cursor at a position in the database."""

        if self.conn is None:
            raise Exception("seek. Empty conn!!")

        return self.conn.seek(offs, whence)

    def setInteractiveGUI(self, b):
        """Set if it is an interactive GUI."""

        self._interactive_gui = b

    def formatValue(self, table: str, value: Any, upper: bool) -> Any:
        """Return a correctly formatted value to be assigned as a where filter."""

        return self.driver().formatValue(table, value, upper)

    def formatValueLike(self, table: str, value: Any, upper: bool) -> str:
        """Return a correctly formatted value to be assigned as a WHERE LIKE filter."""

        return self.driver().formatValueLike(table, value, upper)

    def lastActiveCursor(self):
        """Return the last active cursor in the sql driver."""

        return self._last_active_cursor

    def doTransaction(self, cursor: "isqlcursor.ISqlCursor") -> bool:
        """Make a transaction or savePoint according to transaction level."""

        if self.driver()._transaction == 0:
            application.PROJECT.message_manager().send(
                "status_help_msg",
                "send",
                ["Iniciando Transacción... %s" % self.driver()._transaction],
            )
            if self.transaction():
                self._last_active_cursor = cursor
                DB_SIGNALS.emitTransactionBegin(cursor)

                self.driver()._transaction = +1
                LOGGER.warning(
                    "Creando transaccion número:%s, cursor:%s",
                    self.driver()._transaction,
                    cursor.curName(),
                )
                cursor.private_cursor._transactions_opened.insert(0, self.driver()._transaction)
                return True
            else:
                LOGGER.warning("doTransaction: Fallo al intentar iniciar la transacción")
                return False

        else:
            if settings.CONFIG.value("application/isDebuggerMode", False):
                application.PROJECT.message_manager().send(
                    "status_help_msg",
                    "send",
                    [
                        "Creando punto de salvaguarda %s:%s"
                        % (self._name, self.driver()._transaction)
                    ],
                )

            self.savePoint(self.driver()._transaction)

            self.driver()._transaction = self.driver()._transaction + 1
            LOGGER.warning(
                "Creando savePoint número:%s, cursor:%s",
                self.driver()._transaction,
                cursor.curName(),
            )
            if cursor.private_cursor._transactions_opened:
                cursor.private_cursor._transactions_opened.insert(
                    0, self.driver()._transaction
                )  # push
            else:
                cursor.private_cursor._transactions_opened.append(self.driver()._transaction)
            return True

    def transactionLevel(self) -> int:
        """Indicate the level of transaction."""

        return self.driver()._transaction

    def doRollback(self, cur: "isqlcursor.ISqlCursor") -> bool:
        """Drop a transaction or savepoint depending on the transaction level."""

        cancel = False
        if (
            cur.modeAccess() in (cur.Insert, cur.Edit)
            and cur.isModifiedBuffer()
            and cur.private_cursor._ask_for_cancel_changes
        ):

            dgi = application.PROJECT.DGI

            if dgi:
                msg_box = getattr(dgi, "msgBoxQuestion", None)
                if msg_box is not None:
                    res = msg_box(
                        "Todos los cambios se cancelarán.¿Está seguro?", None, "Cancelar Cambios"
                    )

                    if res is not None:
                        if res == QtWidgets.QMessageBox.No:
                            return False

            cancel = True

        if self.driver()._transaction > 0:
            if cur.private_cursor._transactions_opened:
                trans = cur.private_cursor._transactions_opened.pop()
                if not trans == self.driver()._transaction:
                    LOGGER.warning(
                        "FLSqlDatabase: El cursor %s va a deshacer la transacción %s pero la última que inició es la %s",
                        cur.curName(),
                        self.driver()._transaction,
                        trans,
                        stack_info=True,
                    )
            else:
                LOGGER.warning(
                    "FLSqlDatabaser : El cursor va a deshacer la transacción %s pero no ha iniciado ninguna",
                    self.driver()._transaction,
                )

            self.driver()._transaction = self.driver()._transaction - 1
        else:
            return True

        if self.driver()._transaction == 0:
            application.PROJECT.message_manager().send(
                "status_help_msg",
                "send",
                ["Deshaciendo Transacción... %s" % self.driver()._transaction],
            )
            LOGGER.warning(
                "Desaciendo transacción número:%s, cursor:%s",
                self.driver()._transaction + 1,
                cur.curName(),
            )
            if self.rollbackTransaction():
                self._last_active_cursor = None

                cur.setModeAccess(cur.Browse)
                if cancel:
                    cur.select()

                DB_SIGNALS.emitTransactionRollback(cur)
                return True
            else:
                LOGGER.warning("doRollback: Fallo al intentar deshacer transacción")
                return False

        else:

            application.PROJECT.message_manager().send(
                "status_help_msg",
                "send",
                [
                    "Restaurando punto de salvaguarda %s:%s..."
                    % (self._name, self.driver()._transaction)
                ],
            )
            LOGGER.warning(
                "Desaciendo savePoint número:%s, cursor:%s",
                self.driver()._transaction + 1,
                cur.curName(),
            )
            self.rollbackSavePoint(self.driver()._transaction)

            cur.setModeAccess(cur.Browse)
            return True

    def interactiveGUI(self) -> str:
        """Return if it is an interactive GUI."""

        return self._interactive_gui

    def doCommit(self, cur: "isqlcursor.ISqlCursor", notify: bool = True) -> bool:
        """Approve changes to a transaction or a save point based on your transaction level."""

        if not notify:
            cur.autoCommit.emit()

        if self.driver()._transaction > 0:
            if cur.private_cursor._transactions_opened:
                trans = cur.private_cursor._transactions_opened.pop()
                if not trans == self.driver()._transaction:
                    LOGGER.warning(
                        "El cursor %s va a terminar la transacción %s pero la última que inició es la %s",
                        cur.curName(),
                        self.driver()._transaction,
                        trans,
                        stack_info=True,
                    )
            else:
                LOGGER.warning(
                    "El cursor va a terminar la transacción %s pero no ha iniciado ninguna",
                    self.driver()._transaction,
                )

            self.driver()._transaction = self.driver()._transaction - 1
        else:

            return True

        if self.driver()._transaction == 0:
            application.PROJECT.message_manager().send(
                "status_help_msg",
                "send",
                ["Terminando Transacción... %s" % self.driver()._transaction],
            )
            try:
                LOGGER.warning(
                    "Aceptando transacción número:%s, cursor:%s",
                    self.driver()._transaction + 1,
                    cur.curName(),
                )
                if self.commit():
                    self._last_active_cursor = None

                    if notify:
                        cur.setModeAccess(cur.Browse)

                    DB_SIGNALS.emitTransactionEnd(cur)
                    return True

                else:
                    LOGGER.error(
                        "doCommit: Fallo al intentar terminar transacción: %s"
                        % self.driver()._transaction
                    )
                    return False

            except Exception as exception:
                LOGGER.error("doCommit: Fallo al intentar terminar transacción: %s", exception)
                return False
        else:
            application.PROJECT.message_manager().send(
                "status_help_msg",
                "send",
                [
                    "Liberando punto de salvaguarda %s:%s..."
                    % (self._name, self.driver()._transaction)
                ],
            )
            LOGGER.warning(
                "Aceptando savePoint número:%s, cursor:%s",
                self.driver()._transaction + 1,
                cur.curName(),
            )
            self.releaseSavePoint(self.driver()._transaction)

            if notify:
                cur.setModeAccess(cur.Browse)

            return True

    def canDetectLocks(self) -> bool:
        """Indicate if the connection detects locks in the database."""

        return self.driver().canDetectLocks()

    def commit(self) -> bool:
        """Send the commit order to the database."""

        return self.commitTransaction()

    def canOverPartition(self) -> bool:
        """Return True if the database supports the OVER statement."""

        return self.connManager().dbAux().driver().canOverPartition()

    def savePoint(self, save_point: int) -> bool:
        """Create a save point."""
        # print("CREA SAVE_POINT!!", self.session().transaction)
        try:
            self.session().begin_nested()
            return True
        except Exception as error:
            self._last_error = "No se pudo crear punto de salvaguarda: %s" % str(error)

        return False

    def releaseSavePoint(self, save_point: int) -> bool:
        """Release a save point."""
        # print("RELEASE SAVE_POINT!!", self.session().transaction)
        try:
            self.session().commit()
            return True
        except Exception as error:
            self._last_error = "No se pudo release a punto de salvaguarda: %s" % str(error)

        return False

    def Mr_Proper(self):
        """Clean the database of unnecessary tables and records."""

        self.connManager().dbAux().driver().Mr_Proper()

    def rollbackSavePoint(self, save_point: int) -> bool:
        """Roll back a save point."""
        # print("CANCELA SAVE_POINT!!", self.session().transaction)
        try:
            self.session().rollback()
            return True
        except Exception as error:
            self._last_error = "No se pudo rollback a punto de salvaguarda: %s" % str(error)

        return False

    def transaction(self) -> bool:
        """Create a transaction."""

        try:
            self.session()
            # print("CREA TRANSACCION!!", self.session().transaction)
            return True
        except Exception as error:
            self._last_error = "No se pudo crear la transacción: %s" % str(error)

        return False

    def commitTransaction(self) -> bool:
        """Release a transaction."""

        # print("COMMIT TRANSACCION!!", self.session().transaction)
        try:

            session_ = self.session()
            LOGGER.debug("COMMIT session: %s, transaction: %s", session_, session_.transaction)
            # self.driver()._session = None
            session_.commit()
            # session_.close()
            # session_.begin()
            # session_.close()
            # self.driver()._session = None
            LOGGER.debug("COMMIT OK transaction: %s", session_.transaction)
            return True
        except Exception as error:
            self._last_error = "No se pudo aceptar la transacción: %s" % str(error)

        return False

    def rollbackTransaction(self) -> bool:
        """Roll back a transaction."""

        # print("ROLLBACK TRANSACCION!!", self.session().transaction)
        try:
            session_ = self.session()
            # self.driver()._session = None
            session_.rollback()
            # session_.close()
            # session_.begin()
            # session_.close()
            # self.driver()._session = None

            return True
        except Exception as error:
            self._last_error = "No se pudo deshacer la transacción: %s" % str(error)

        return False

    def nextSerialVal(self, table: str, field: str) -> Any:
        """Indicate next available value of a serial type field."""

        return self.driver().nextSerialVal(table, field)

    def existsTable(self, name: str) -> bool:
        """Indicate the existence of a table in the database."""

        return self.driver().existsTable(name)

    def createTable(self, tmd: "pntablemetadata.PNTableMetaData") -> bool:
        """Create a table in the database, from a PNTableMetaData."""

        do_transaction = False

        sql = self.driver().sqlCreateTable(tmd)
        if not sql:
            return False

        if self.driver()._transaction == 0:
            do_transaction = True

        if do_transaction:
            self.transaction()
            self.driver()._transaction += 1

        for single_sql in sql.split(";"):
            self.execute_query(single_sql)
            if self.driver().last_error():
                LOGGER.exception(
                    "createTable: Error happened executing sql: %s...%s"
                    % (single_sql[:80], str(self.driver().last_error()))
                )
                self.rollbackTransaction()
                self.driver().set_last_error_null()
                return False

        if do_transaction:
            self.commitTransaction()
            self.driver()._transaction -= 1

        return True

    def mismatchedTable(self, tablename: str, tmd: "pntablemetadata.PNTableMetaData") -> bool:
        """Compare an existing table with a PNTableMetaData and return if there are differences."""

        return self.connManager().dbAux().driver().mismatchedTable(tablename, tmd)

    def normalizeValue(self, text: str) -> Optional[str]:
        """Return the value of a correctly formatted string to the database type from a string."""

        if getattr(self.driver(), "normalizeValue", None):
            return self.driver().normalizeValue(text)

        LOGGER.warning(
            "PNConnection: El driver %s no dispone de normalizeValue(text)", self.driverName()
        )
        return text

    def queryUpdate(self, name: str, update: str, filter: str) -> Optional[str]:
        """Return a correct UPDATE query for the database type."""

        return self.driver().queryUpdate(name, update, filter)

    def execute_query(self, qry) -> Any:
        """Execute a query in a database cursor."""

        return self.driver().execute_query(qry)

    def alterTable(self, new_metadata: "pntablemetadata.PNTableMetaData") -> bool:
        """Modify the fields of a table in the database based on the differences of two PNTableMetaData."""

        return self.connManager().dbAux().driver().alterTable(new_metadata)

    def canRegenTables(self) -> bool:
        """Return if can regenerate tables."""
        if not self._driver_name:
            return False

        return self.driver().canRegenTables()

    def regenTable(self, table_name: str, mtd: "pntablemetadata.PNTableMetaData") -> bool:
        """Regenerate a table."""

        return self.driver().regenTable(table_name, mtd)

    def idle_time(self) -> float:
        """Return idle time in Seconds."""
        actual_time = time.time()
        return actual_time - self._last_activity_time

    def update_activity_time(self):
        """Update activity time."""
        self._last_activity_time = time.time()

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

        self._is_open = False
        self.driver().close()

    def sqlLength(self, field_name: str, size: int) -> str:
        """Return length formated."""

        return self.driver().sqlLength(field_name, size)
