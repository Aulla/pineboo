# -*- coding: utf-8 -*-
"""
Defines the PNConnection class.
"""
from PyQt5 import QtCore, QtWidgets

from pineboolib.core import utils
from pineboolib.core import settings, decorators
from pineboolib.interfaces import iconnection
from . import pnsqldrivers
from pineboolib import application

# from .pnsqlsavepoint import PNSqlSavePoint
from . import db_signals
from typing import Dict, List, Optional, Any, Union, TYPE_CHECKING

import time

if TYPE_CHECKING:
    from pineboolib.interfaces import iapicursor
    from pineboolib.application.metadata import pntablemetadata
    from . import pnconnectionmanager, pnsqlcursor

logger = utils.logging.getLogger(__name__)


class PNConnection(QtCore.QObject, iconnection.IConnection):
    """Wrapper for database cursors which are used to emulate FLSqlCursor."""

    name: str
    db_name_: str
    db_host_: Optional[str]
    db_port_: Optional[int]
    db_user_name_: Optional[str]
    db_password_: Optional[str]
    conn: Any = None  # Connection from the actual driver
    driverSql: "pnsqldrivers.PNSqlDrivers"
    transaction_: int
    driver_name_: str
    # currentSavePoint_: Optional[PNSqlSavePoint]
    # stackSavePoints_: List[PNSqlSavePoint]
    # queueSavePoints_: List[PNSqlSavePoint]
    interactiveGUI_: bool
    _dbAux = None
    _isOpen: bool
    driver_ = None
    _last_active_cursor: Optional["pnsqlcursor.PNSqlCursor"]
    conn_dict: Dict[str, "iconnection.IConnection"] = {}
    _conn_manager: "pnconnectionmanager.PNConnectionManager"
    _last_activity_time: float

    def __init__(
        self,
        db_name: str,
        db_host: Optional[str] = None,
        db_port: Optional[int] = None,
        db_user_name: Optional[str] = None,
        db_password: Optional[str] = None,
        driver_alias: Optional[str] = None,
    ) -> None:
        """Database connection through a sql driver."""

        super().__init__()
        self.update_activity_time()
        self.conn = None
        self.driver_ = None
        self.db_name_ = db_name
        self.driverSql = pnsqldrivers.PNSqlDrivers()

        conn_manager = application.project.conn_manager
        self._conn_manager = conn_manager
        if conn_manager is None:
            raise Exception("conn_manager is not Initialized!")

        if "main_conn" in conn_manager.conn_dict.keys():
            main_conn_ = conn_manager.conn_dict["main_conn"]
            if main_conn_.db_name_ == db_name and db_host is None:
                db_host = main_conn_.db_host_
                db_port = main_conn_.db_port_
                db_user_name = main_conn_.db_user_name_
                db_password = main_conn_.db_password_
                driver_alias = main_conn_.driverAlias()

        self.db_host_ = db_host
        self.db_port_ = db_port
        self.db_user_name_ = db_user_name
        self.db_password_ = db_password

        if driver_alias is None:
            raise Exception("driver alias is empty!")

        self.driver_name_ = self.driverSql.aliasToName(driver_alias)

        self.transaction_ = 0
        # self.stackSavePoints_ = []
        # self.queueSavePoints_ = []
        self.interactiveGUI_ = True
        self._last_active_cursor = None

        self._isOpen = False
        # if self.driver_name_ and self.driverSql.loadDriver(self.driver_name_):
        #    self.conn = self.conectar(db_name, db_host, db_port, db_user_name, db_password)
        #    if self.conn is False:
        #        return

        # else:
        #    logger.error("PNConnection.ERROR: No se encontro el driver '%s'", driverAlias)
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
        return self.name

    def isOpen(self) -> bool:
        """Indicate if a connection is open."""

        return self._isOpen

    def tables(self, tables_type: Optional[Union[str, int]] = None) -> List[str]:
        """Return a list of available tables in the database, according to a given filter."""
        t_ = None
        if tables_type is not None:
            if isinstance(tables_type, int):
                if tables_type == 1:
                    t_ = "Tables"
                elif tables_type == 2:
                    t_ = "SystemTables"
                elif tables_type == 3:
                    t_ = "Views"
            else:
                t_ = tables_type

        return self.driver().tables(t_)

    def DBName(self) -> str:
        """Return the database name."""
        return self.driver().DBName()

    def driver(self) -> Any:
        """Return the instance of the driver that is using the connection."""
        if self.driver_ is None:
            self.driver_ = self.driverSql.driver()

        self.update_activity_time()
        return self.driver_

    def session(self) -> Any:
        """
        Sqlalchemy session.

        When using the ORM option this function returns the session for sqlAlchemy.
        """

        return self.driver().session()

    def engine(self) -> Any:
        """Sqlalchemy connection."""

        return self.driver().engine()

    def declarative_base(self) -> Any:
        """Contain the declared models for Sqlalchemy."""

        return self.driver().declarative_base()

    def cursor(self) -> "iapicursor.IApiCursor":
        """Return a cursor to the database."""
        if self.conn is None:
            raise Exception("cursor. Empty conn!! in %s", self.connectionName())
        return self.conn.cursor()

    def conectar(
        self,
        db_name: str,
        db_host: Optional[str],
        db_port: Optional[int],
        db_user_name: Optional[str],
        db_password: Optional[str],
    ) -> Any:
        """Request a connection to the database."""

        self.db_name_ = db_name
        self.db_host_ = db_host
        self.db_port_ = db_port
        self.db_user_name_ = db_user_name
        self.db_password_ = db_password
        # if self.name:
        #    self.driver().alias_ = self.driverName() + ":" + self.name
        self.driver().db_ = self
        return self.driver().connect(db_name, db_host, db_port, db_user_name, db_password)

    def driverName(self) -> str:
        """Return sql driver name."""

        return self.driver().driverName()

    def driverAlias(self) -> str:
        """Return sql driver alias."""
        return self.driver().alias_

    def driverNameToDriverAlias(self, name: str) -> str:
        """Return the alias from the name of a sql driver."""

        if self.driverSql is None:
            raise Exception("driverNameoDriverAlias. Sql driver manager is not defined")

        return self.driverSql.nameToAlias(name)

    def lastError(self) -> str:
        """Return the last error reported by the sql driver."""

        return self.driver().lastError()

    def host(self) -> Optional[str]:
        """Return the name of the database host."""

        return self.db_host_

    def port(self) -> Optional[int]:
        """Return the port used by the database."""

        return self.db_port_

    def user(self) -> Optional[str]:
        """Return the user name used by the database."""

        return self.db_user_name_

    def password(self) -> Optional[str]:
        """Return the password used by the database."""

        return self.db_password_

    def seek(self, offs, whence=0) -> Any:
        """Position the cursor at a position in the database."""

        if self.conn is None:
            raise Exception("seek. Empty conn!!")

        return self.conn.seek(offs, whence)

    # @decorators.NotImplementedWarn
    # def md5TuplesStateTable(self, curname: str) -> bool:
    #    """
    #    Return the sum md5 with the total records inserted, deleted and modified in the database so far.

    #    Useful to know if the database has been modified from a given moment.
    #    """

    #    return True

    def setInteractiveGUI(self, b):
        """Set if it is an interactive GUI."""

        self.interactiveGUI_ = b

    # @decorators.NotImplementedWarn
    # def setQsaExceptions(self, b: bool) -> None:
    #    """See properties of the qsa exceptions."""
    #    pass

    def formatValue(self, t: str, v: Any, upper: bool) -> Any:
        """Return a correctly formatted value to be assigned as a where filter."""

        return self.driver().formatValue(t, v, upper)

    def formatValueLike(self, t: str, v: Any, upper: bool) -> str:
        """Return a correctly formatted value to be assigned as a WHERE LIKE filter."""

        return self.driver().formatValueLike(t, v, upper)

    def canSavePoint(self) -> bool:
        """Inform if the sql driver can manage savepoints."""

        return self.connManager().dbAux().driver().canSavePoint()

    def canTransaction(self) -> bool:
        """Inform if the sql driver can manage transactions."""
        return self.driver().canTransaction()

    def lastActiveCursor(self):
        """Return the last active cursor in the sql driver."""

        return self._last_active_cursor

    def doTransaction(self, cursor: "pnsqlcursor.PNSqlCursor") -> bool:
        """Make a transaction or savePoint according to transaction level."""

        if self.transaction_ == 0 and self.canTransaction():
            if settings.config.value("application/isDebuggerMode", False):
                application.project.message_manager().send(
                    "status_help_msg", "send", ["Iniciando Transacción... %s" % self.transaction_]
                )
            if self.transaction():
                self._last_active_cursor = cursor
                db_signals.emitTransactionBegin(cursor)

                # if not self.canSavePoint():
                #    if self.currentSavePoint_:
                #        del self.currentSavePoint_
                #        self.currentSavePoint_ = None

                #    self.stackSavePoints_.clear()
                #    self.queueSavePoints_.clear()

                self.transaction_ = self.transaction_ + 1
                cursor.d.transactionsOpened_.insert(0, self.transaction_)
                return True
            else:
                logger.warning("doTransaction: Fallo al intentar iniciar la transacción")
                return False

        else:
            if settings.config.value("application/isDebuggerMode", False):
                application.project.message_manager().send(
                    "status_help_msg",
                    "send",
                    ["Creando punto de salvaguarda %s:%s" % (self.name, self.transaction_)],
                )
            # if not self.canSavePoint():
            #    if self.transaction_ == 0:
            #        if self.currentSavePoint_:
            #            del self.currentSavePoint_
            #            self.currentSavePoint_ = None

            #        self.stackSavePoints_.clear()
            #        self.queueSavePoints_.clear()

            #    if self.currentSavePoint_:
            #        if self.stackSavePoints_:
            #            self.stackSavePoints_.insert(0, self.currentSavePoint_)
            #        else:
            #            self.stackSavePoints_.append(self.currentSavePoint_)

            #    self.currentSavePoint_ = PNSqlSavePoint(self.transaction_)
            # else:
            self.savePoint(self.transaction_)

            self.transaction_ = self.transaction_ + 1
            if cursor.d.transactionsOpened_:
                cursor.d.transactionsOpened_.insert(0, self.transaction_)  # push
            else:
                cursor.d.transactionsOpened_.append(self.transaction_)
            return True

    def transactionLevel(self) -> int:
        """Indicate the level of transaction."""

        return self.transaction_

    def doRollback(self, cur: "pnsqlcursor.PNSqlCursor") -> bool:
        """Drop a transaction or savepoint depending on the transaction level."""

        cancel = False
        if (
            self.interactiveGUI()
            and cur.modeAccess() in (cur.Insert, cur.Edit)
            and cur.isModifiedBuffer()
            and cur.d.askForCancelChanges_
        ):

            if application.project.DGI.localDesktop():
                res = QtWidgets.QMessageBox.information(
                    QtWidgets.QApplication.activeWindow(),
                    "Cancelar Cambios",
                    "Todos los cambios se cancelarán.¿Está seguro?",
                    QtWidgets.QMessageBox.Yes,
                    QtWidgets.QMessageBox.No,
                )
                if res == QtWidgets.QMessageBox.No:
                    return False

            cancel = True

        if self.transaction_ > 0:
            if cur.d.transactionsOpened_:
                trans = cur.d.transactionsOpened_.pop()
                if not trans == self.transaction_:
                    logger.warning(
                        "FLSqlDatabase: El cursor va a deshacer la transacción %s pero la última que inició es la %s",
                        self.transaction_,
                        trans,
                    )
            else:
                logger.warning(
                    "FLSqlDatabaser : El cursor va a deshacer la transacción %s pero no ha iniciado ninguna",
                    self.transaction_,
                )

            self.transaction_ = self.transaction_ - 1
        else:
            return True

        if self.transaction_ == 0 and self.canTransaction():
            if settings.config.value("application/isDebuggerMode", False):
                application.project.message_manager().send(
                    "status_help_msg", "send", ["Deshaciendo Transacción... %s" % self.transaction_]
                )
            if self.rollbackTransaction():
                self._last_active_cursor = None

                # if not self.canSavePoint():
                #    if self.currentSavePoint_:
                #        del self.currentSavePoint_
                #        self.currentSavePoint_ = None

                #    self.stackSavePoints_.clear()
                #    self.queueSavePoints_.clear()

                cur.setModeAccess(cur.Browse)
                if cancel:
                    cur.select()

                db_signals.emitTransactionRollback(cur)
                return True
            else:
                logger.warning("doRollback: Fallo al intentar deshacer transacción")
                return False

        else:

            application.project.message_manager().send(
                "status_help_msg",
                "send",
                ["Restaurando punto de salvaguarda %s:%s..." % (self.name, self.transaction_)],
            )
            # if not self.canSavePoint():
            #    tam_queue = len(self.queueSavePoints_)
            #    for i in range(tam_queue):
            #        temp_save_point = self.queueSavePoints_.pop()
            #        temp_id = temp_save_point.id()

            #        if temp_id > self.transaction_ or self.transaction_ == 0:
            #            temp_save_point.undo()
            #            del temp_save_point
            #        else:
            #            self.queueSavePoints_.append(temp_save_point)

            #    if self.currentSavePoint_ is not None:
            #        self.currentSavePoint_.undo()
            #        self.currentSavePoint_ = None
            #        if self.stackSavePoints_:
            #            self.currentSavePoint_ = self.stackSavePoints_.pop()

            #    if self.transaction_ == 0:
            #        if self.currentSavePoint_:
            #            del self.currentSavePoint_
            #            self.currentSavePoint_ = None

            #        self.stackSavePoints_.clear()
            #        self.queueSavePoints_.clear()

            # else:
            self.rollbackSavePoint(self.transaction_)

            cur.setModeAccess(cur.Browse)
            return True

    def interactiveGUI(self) -> bool:
        """Return if it is an interactive GUI."""

        return self.interactiveGUI_

    def doCommit(self, cur: "pnsqlcursor.PNSqlCursor", notify: bool = True) -> bool:
        """Approve changes to a transaction or a save point based on your transaction level."""

        if not notify:
            cur.autoCommit.emit()

        if self.transaction_ > 0:
            if cur.d.transactionsOpened_:
                trans = cur.d.transactionsOpened_.pop()
                if not trans == self.transaction_:
                    logger.warning(
                        "El cursor va a terminar la transacción %s pero la última que inició es la %s",
                        self.transaction_,
                        trans,
                    )
            else:
                logger.warning(
                    "El cursor va a terminar la transacción %s pero no ha iniciado ninguna",
                    self.transaction_,
                )

            self.transaction_ = self.transaction_ - 1
        else:

            return True

        if self.transaction_ == 0 and self.canTransaction():
            if settings.config.value("application/isDebuggerMode", False):
                application.project.message_manager().send(
                    "status_help_msg", "send", ["Terminando Transacción... %s" % self.transaction_]
                )
            try:
                if self.commit():
                    self._last_active_cursor = None

                    # if not self.canSavePoint():
                    #    if self.currentSavePoint_:
                    #        del self.currentSavePoint_
                    #        self.currentSavePoint_ = None

                    #    self.stackSavePoints_.clear()
                    #    self.queueSavePoints_.clear()

                    if notify:
                        cur.setModeAccess(cur.Browse)

                    db_signals.emitTransactionEnd(cur)
                    return True

                else:
                    logger.error(
                        "doCommit: Fallo al intentar terminar transacción: %s" % self.transaction_
                    )
                    return False

            except Exception as e:
                logger.error("doCommit: Fallo al intentar terminar transacción: %s", e)
                return False
        else:
            application.project.message_manager().send(
                "status_help_msg",
                "send",
                ["Liberando punto de salvaguarda %s:%s..." % (self.name, self.transaction_)],
            )
            if (self.transaction_ == 1 and self.canTransaction()) or (
                self.transaction_ == 0 and not self.canTransaction()
            ):
                # if not self.canSavePoint():
                #    if self.currentSavePoint_:
                #        del self.currentSavePoint_
                #        self.currentSavePoint_ = None

                #    self.stackSavePoints_.clear()
                #    self.queueSavePoints_.clear()
                # else:
                self.releaseSavePoint(self.transaction_)
                if notify:
                    cur.setModeAccess(cur.Browse)

                return True
            # if not self.canSavePoint():
            #    tam_queue = len(self.queueSavePoints_)
            #    for i in range(tam_queue):
            #        temp_save_point = self.queueSavePoints_.pop()
            #        temp_save_point.setId(self.transaction_ - 1)
            #        self.queueSavePoints_.append(temp_save_point)

            #    if self.currentSavePoint_:
            #        self.queueSavePoints_.append(self.currentSavePoint_)
            #        self.currentSavePoint_ = None
            #        if self.stackSavePoints_:
            #            self.currentSavePoint_ = self.stackSavePoints_.pop()
            # else:
            self.releaseSavePoint(self.transaction_)

            if notify:
                cur.setModeAccess(cur.Browse)

            return True

    def canDetectLocks(self) -> bool:
        """Indicate if the connection detects locks in the database."""

        return self.driver().canDetectLocks()

    def commit(self) -> bool:
        """Send the commit order to the database."""

        return self.driver().commitTransaction()

    def canOverPartition(self) -> bool:
        """Return True if the database supports the OVER statement."""

        return self.connManager().dbAux().driver().canOverPartition()

    def savePoint(self, save_point: int) -> bool:
        """Create a save point."""

        return self.driver().savePoint(save_point)

    def releaseSavePoint(self, save_point: int) -> bool:
        """Release a save point."""

        return self.driver().releaseSavePoint(save_point)

    def Mr_Proper(self):
        """Clean the database of unnecessary tables and records."""

        self.connManager().dbAux().driver().Mr_Proper()

    def rollbackSavePoint(self, save_point: int) -> bool:
        """Roll back a save point."""

        return self.driver().rollbackSavePoint(save_point)

    def transaction(self) -> bool:
        """Create a transaction."""

        return self.driver().transaction()

    def commitTransaction(self) -> bool:
        """Release a transaction."""

        return self.driver().commitTransaction()

    def rollbackTransaction(self) -> bool:
        """Roll back a transaction."""

        return self.driver().rollbackTransaction()

    def nextSerialVal(self, table: str, field: str) -> Any:
        """Indicate next available value of a serial type field."""

        return self.connManager().dbAux().driver().nextSerialVal(table, field)

    def existsTable(self, name: str) -> bool:
        """Indicate the existence of a table in the database."""

        return self.connManager().dbAux().driver().existsTable(name)

    def createTable(self, tmd: "pntablemetadata.PNTableMetaData") -> bool:
        """Create a table in the database, from a PNTableMetaData."""

        do_transaction = False

        sql = self.connManager().dbAux().driver().sqlCreateTable(tmd)
        if not sql:
            return False
        if self.transaction_ == 0:
            do_transaction = True

        if do_transaction:
            self.transaction()
            self.transaction_ += 1

        for singleSql in sql.split(";"):
            try:
                self.connManager().dbAux().execute_query(singleSql)
            except Exception:
                logger.exception("createTable: Error happened executing sql: %s...", singleSql[:80])
                self.rollbackTransaction()
                return False

        if do_transaction:
            self.commitTransaction()
            self.transaction_ -= 1

        return True

    def mismatchedTable(self, tablename: str, tmd: "pntablemetadata.PNTableMetaData") -> bool:
        """Compare an existing table with a PNTableMetaData and return if there are differences."""

        return self.connManager().dbAux().driver().mismatchedTable(tablename, tmd, self)

    def normalizeValue(self, text: str) -> Optional[str]:
        """Return the value of a correctly formatted string to the database type from a string."""

        if getattr(self.driver(), "normalizeValue", None):
            return self.driver().normalizeValue(text)

        logger.warning(
            "PNConnection: El driver %s no dispone de normalizeValue(text)", self.driverName()
        )
        return text

    def queryUpdate(self, name: str, update: str, filter: str) -> Optional[str]:
        """Return a correct UPDATE query for the database type."""

        return self.driver().queryUpdate(name, update, filter)

    def execute_query(self, q, cursor: Any = None) -> Any:
        """Execute a query in a database cursor."""

        return self.driver().execute_query(q, cursor)

    def alterTable(
        self,
        mtd_1: "pntablemetadata.PNTableMetaData",
        mtd_2: "pntablemetadata.PNTableMetaData",
        key: str,
        force: bool = False,
    ) -> bool:
        """Modify the fields of a table in the database based on the differences of two PNTableMetaData."""

        return self.connManager().dbAux().driver().alterTable(mtd_1, mtd_2, key, force)

    def canRegenTables(self) -> bool:
        """Return if can regenerate tables."""

        return self.driver().canRegenTables()

    @decorators.NotImplementedWarn
    def regenTable(self, table_name: str, mtd: "pntablemetadata.PNTableMetaData") -> None:
        """Regenerate a table."""

        return None

    def idle_time(self) -> float:
        """Return idle time in Seconds."""
        actual_time = time.time()
        return actual_time - self._last_activity_time

    def update_activity_time(self):
        """Update activity time."""
        self._last_activity_time = time.time()

    def __str__(self):
        """Return the name of the database in text format."""

        return self.DBName()
