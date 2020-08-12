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

import time
import threading

from typing import Dict, List, Optional, Any, Union, TYPE_CHECKING


if TYPE_CHECKING:
    from pineboolib.interfaces import isqlcursor
    from pineboolib.application.metadata import pntablemetadata
    from . import pnconnectionmanager

    from sqlalchemy.engine import base
    from sqlalchemy import orm  # type: ignore [name-defined] # noqa: F821

LOGGER = utils.logging.get_logger(__name__)


class PNConnection(QtCore.QObject, iconnection.IConnection):
    """Wrapper for database cursors which are used to emulate FLSqlCursor."""

    _name: str

    _db_name: str
    _db_host: Optional[str]
    _db_port: Optional[int]
    _db_user_name: Optional[str]
    _db_password: str = ""
    # conn: Optional["base.Connection"] = None  # Connection from the actual driver

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
    _current_session: Optional["orm.Session"]

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
        self._transaction_level = 0
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

        # self._transaction_level = 0
        # self.stackSavePoints_ = []
        # self.queueSavePoints_ = []
        self._interactive_gui = "Pineboo" if not utils_base.is_library() else "Pinebooapi"
        self._last_active_cursor = None
        # self._current_transaction = None
        self._last_error = ""
        self._is_open = False
        self._current_session = None
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

        types = ["", "Tables", "SystemTables", "Views"]

        if isinstance(tables_type, int):
            item = None
            if tables_type < len(types):
                item = types[tables_type]
        else:
            item = tables_type

        return self.driver().tables(item)

    def DBName(self) -> str:
        """Return the database name."""
        return self.driver().DBName()

    def driver(self) -> Any:
        """Return the instance of the driver that is using the connection."""
        if self._driver is None:
            self._driver = self._driver_sql.driver()

        self.update_activity_time()
        return self._driver

    def session(self) -> "orm.Session":
        """
        Sqlalchemy session.

        When using the ORM option this function returns the session for sqlAlchemy.
        """
        if self._name == "main_conn":
            raise Exception("main_conn no es valido para session")

        id_thread = threading.current_thread().ident
        key = "%s_%s" % (id_thread, self._name)
        if (
            key in self._conn_manager.thread_atomic_sessions.keys()
        ):  # si estoy en atomic retorno sessión atomica.
            LOGGER.debug("Returning atomic session %s!", key)
            return self._conn_manager.thread_atomic_sessions[key]

        force_new = False
        if self._current_session is None:
            force_new = True
        else:
            try:
                result = hasattr(  # noqa: F841
                    self._current_session.connection(), "_Connection__connection"
                )
            except AttributeError as error:
                LOGGER.warning(
                    "Very possibly, you are trying to use a session in which"
                    " a previous error has occurred and has not"
                    " been recovered with a rollback. Current session is discarded.\n%s.",
                    str(error),
                )
                force_new = True
            else:
                if self._current_session.connection().closed:
                    force_new = True

        if force_new:
            self._current_session = self.driver().session()

        if self._current_session is None:
            raise ValueError("Invalid session!")

        return self._current_session

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
        LOGGER.info(
            " NEW CONNECTION NAME: %s, HOST: %s, PORT: %s, DB NAME: %s, USER NAME: %s",
            self._name,
            db_host,
            db_port,
            db_name,
            db_user_name,
        )
        LOGGER.info("")

        result = self.driver().connect(
            db_name, db_host, db_port, db_user_name, db_password, limit_conn
        )
        LOGGER.info("FAILURE" if not result else "ESTABLISHED")
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

    # ===============================================================================
    #     def seek(self, offs, whence=0) -> bool:
    #         """Position the cursor at a position in the database."""
    #
    #         if self.conn is None:
    #             raise Exception("seek. Empty conn!!")
    #
    #         return self.conn.seek(offs, whence)
    # ===============================================================================

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

        if settings.CONFIG.value("application/isDebuggerMode", False):
            if self._transaction_level:
                text_ = "Creando punto de salvaguarda %s:%s" % (self._name, self._transaction_level)
            else:
                text_ = "Iniciando Transacción... %s" % self._transaction_level

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
                    if res == QtWidgets.QMessageBox.No:
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
            if not self.session().transaction:
                self.session().begin()
            else:
                self.session().begin_nested()

            return True
        except Exception as error:
            self._last_error = "No se pudo crear la transacción: %s" % str(error)

        return False

    def commit(self) -> bool:
        """Release a transaction."""

        # print("COMMIT TRANSACCION!!", self.session().transaction)
        try:

            session_ = self.session()
            # LOGGER.debug("COMMIT session: %s, transaction: %s", session_, session_.transaction)
            # self.driver()._session = None
            session_.commit()
            # session_.close()
            # session_.begin()
            # session_.close()
            # self.driver()._session = None
            return True
        except Exception as error:
            LOGGER.warning("Commit: %s", str(error))
            self._last_error = "No se pudo aceptar la transacción: %s" % str(error)

        return False

    def rollback(self) -> bool:
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

    def createTable(self, tmd: "pntablemetadata.PNTableMetaData", is_view: bool = False) -> bool:
        """Create a table in the database, from a PNTableMetaData."""

        sql = self.driver().sqlCreateTable(tmd, True, is_view)
        if not sql:
            return False

        self.transaction()
        # if not self._transaction_level:
        #    do_transaction = True

        # if do_transaction:
        #    self.transaction()
        #    self._transaction_level += 1

        for single_sql in sql.split(";"):
            self.execute_query(single_sql)
            if self.driver().last_error():
                LOGGER.exception(
                    "createTable: Error happened executing sql: %s...%s"
                    % (single_sql[:80], str(self.driver().last_error()))
                )
                self.rollback()
                self.driver().set_last_error_null()
                return False

        self.commit()
        # if do_transaction:
        #    self.commit()
        #    self._transaction_level -= 1

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


# ===============================================================================
#     def before_flush(self, session, flush_context, instances=None) -> bool:
#         """Before flush."""
#
#         items = []
#         for item in session.new:
#             items.append(item)
#
#         for item in session.dirty:
#             items.append(item)
#
#         for item in session.deleted:
#             items.append(item)
#
#         try:
#             for item in items:
#                 before_flush_func = getattr(item, "_before_flush", None)
#                 if before_flush_func:
#                     return before_flush_func(session)
#         except Exception as error:
#             LOGGER.warning("BEFORE FLUSH! %s. items: %s", str(error), items)
#
#         return True
#
#     def after_flush(self, session, flush_context) -> bool:
#         """Before flush."""
#
#         items = []
#
#         for item in session.new:
#             items.append(item)
#
#         for item in session.dirty:
#             items.append(item)
#
#         for item in session.deleted:
#             items.append(item)
#
#         try:
#             for item in items:
#
#                 after_flush_func = getattr(item, "_after_flush", None)
#                 if after_flush_func:
#                     return after_flush_func(session)
#         except Exception as error:
#             LOGGER.warning("AFTER FLUSH! %s. items: %s", str(error), items)
#
#         return True
# ===============================================================================


# ===============================================================================
#     def after_bulk_delete(self, delete_context) -> None:
#         """After bulk delete."""
#
#         objects = delete_context.query.all()
#         print(
#             "**",
#             objects,
#             delete_context.query,
#             delete_context.context,
#             delete_context.result.fetchall(),
#         )
#         for obj in objects:
#             print("*", obj)
#             obj.mode_access = 3
#             obj._alfter_flush()
#             if not obj._result_after_flush:
#                 return
#
#     def after_bulk_update(self, update_context) -> None:
#         """After bulk delete."""
#
#         objects = update_context.query.all()
#         for obj in objects:
#             obj.mode_access = 2
#             obj._alfter_flush()
#             if not obj._result_after_flush:
#                 return
# ===============================================================================
