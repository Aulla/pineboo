# -*- coding: utf-8 -*-
"""
Module for PNSqlCursor class.
"""

from PyQt6 import QtCore, QtWidgets  # type: ignore[import]

from pineboolib.core.utils import logging
from pineboolib.core import decorators, settings, garbage_collector

from . import pnsqlquery, utils
from pineboolib.application.utils import xpm
from pineboolib.application import types, qsadictmodules
from pineboolib.application.parsers.parser_mtd import pnormmodelsfactory
from pineboolib.application.acls import pnaccesscontrolfactory

from pineboolib import application

from pineboolib.interfaces import isqlcursor

from . import pnbuffer
from . import pncursortablemodel


import weakref
import datetime

from typing import Any, Optional, List, Dict, Union, TYPE_CHECKING


from pineboolib.application.acls import pnboolflagstate

if TYPE_CHECKING:

    from pineboolib.application.metadata import pntablemetadata  # noqa: F401 # pragma: no cover
    from pineboolib.application.metadata import pnrelationmetadata  # noqa: F401 # pragma: no cover
    from pineboolib.application.metadata import pnaction  # noqa: F401 # pragma: no cover
    from pineboolib.interfaces import iconnection  # noqa: F401 # pragma: no cover

CONNECTION_CURSORS: Dict[str, List[str]] = {}


LOGGER = logging.get_logger(__name__)


class PNSqlCursor(isqlcursor.ISqlCursor):
    """
    Database Cursor class.
    """

    def __init__(
        self,
        name: str = "",
        conn_or_autopopulate: Union[bool, str] = True,
        connection_name_or_db: Union[str, "iconnection.IConnection"] = "default",
        cursor_relation: Optional["isqlcursor.ISqlCursor"] = None,
        relation_mtd: Optional["pnrelationmetadata.PNRelationMetaData"] = None,
        parent=None,
    ) -> None:
        """Create a new cursor."""
        global CONNECTION_CURSORS

        identifier = application.PROJECT.session_id()
        if identifier not in CONNECTION_CURSORS.keys():
            CONNECTION_CURSORS[identifier] = []

        name = name.lower()

        super().__init__(
            name, conn_or_autopopulate, connection_name_or_db, cursor_relation, relation_mtd, parent
        )
        # LOGGER.warning("CURSOR! %s", name)
        if not name:
            LOGGER.warning(
                "Se está iniciando un cursor Huerfano (%s). Posiblemente sea una declaración en un qsa parseado",
                self,
            )
            return

        id_cursor = "%s@%s" % (name, datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"))
        CONNECTION_CURSORS[identifier].append(id_cursor)
        if application.SHOW_CURSOR_EVENTS:
            LOGGER.warning("CURSOR_EVENT: %s añadido al pool de cursores %s", id_cursor, identifier)

        autopopulate = True
        # act_ = application.PROJECT.conn_manager.manager().action(name)

        if isinstance(conn_or_autopopulate, bool):
            autopopulate = conn_or_autopopulate
        elif isinstance(conn_or_autopopulate, str):
            connection_name_or_db = conn_or_autopopulate

        db_connection: "iconnection.IConnection" = (
            application.PROJECT.conn_manager.useConn(connection_name_or_db)
            if isinstance(connection_name_or_db, str)
            else connection_name_or_db
        )

        self._name = ""
        self._valid = False

        self.private_cursor = PNCursorPrivate(self, name, db_connection)
        self.private_cursor.id_ = id_cursor
        self.init(name, autopopulate, cursor_relation, relation_mtd)

    def init(
        self,
        name: str,
        autopopulate: bool,
        cursor_relation: Optional["isqlcursor.ISqlCursor"],
        relation_mtd: Optional["pnrelationmetadata.PNRelationMetaData"],
    ) -> None:
        """
        Initialize class.

        Common init code for constructors.
        """
        private_cursor = self.private_cursor

        if application.SHOW_CURSOR_EVENTS:
            LOGGER.warning(
                "CURSOR_EVENT: Se crea el cursor (%s) para la action %s",
                self.id(),
                name,
                stack_info=True,
            )

        if self.setAction(name):
            private_cursor._count_ref_cursor += 1
        else:
            return

        private_cursor.mode_access_ = self.Browse

        # if self.private_cursor.cursor_relation_:
        #    self.private_cursor.cursor_relation_.bufferChanged.disconnect(self.refresh)
        #    self.private_cursor.cursor_relation_.newBuffer.disconnect(self.refresh)
        #    self.private_cursor.cursor_relation_.newBuffer.disconnect(self.clearPersistentFilter)

        private_cursor.cursor_relation_ = cursor_relation
        private_cursor.relation_ = relation_mtd

        mtd = private_cursor.metadata_
        if not mtd:
            return

        self._cursor_model = qsadictmodules.QSADictModules.from_project("%s_orm" % mtd.name())
        # Por si se crea un metadata al vuelo y no se ha registrado al inicio...
        if not self._cursor_model:
            if pnormmodelsfactory.register_metadata_as_model(mtd):
                self._cursor_model = qsadictmodules.QSADictModules.from_project(
                    "%s_orm" % mtd.name()
                )

        if not self._cursor_model:
            raise Exception("_cursor_model for action %s not found !" % name)

        private_cursor._is_query = mtd.isQuery()
        private_cursor._is_system_table = (
            self.db().connManager().manager().isSystemTable(mtd.name())
        )
        self.setName(mtd.name(), autopopulate)

        if cursor_relation and relation_mtd is not None:

            cursor_relation.bufferChanged.connect(  # type: ignore [attr-defined] # noqa: F821
                self.refresh
            )
            cursor_relation.newBuffer.connect(  # type: ignore [attr-defined] # noqa: F821
                self.refresh
            )
            cursor_relation.newBuffer.connect(  # type: ignore [attr-defined] # noqa: F821
                self.clearPersistentFilter
            )

        else:
            self.seek(self.at())

        self._valid = True
        private_cursor.timer_ = QtCore.QTimer(self)
        private_cursor.timer_.timeout.connect(  # type: ignore [attr-defined] # noqa: F821
            self.refreshDelayed
        )

    def conn(self) -> "iconnection.IConnection":
        """Get current connection for this cursor."""
        return self.db()

    def table(self) -> str:
        """Get current table or empty string."""
        return self._name or ""

    def setName(self, name: str, autop: bool) -> None:
        """Set cursor name."""
        self._name = name
        # FIXME: autopop probably means it should do a refresh upon construction.
        # autop = autopopulate para que??

    def metadata(self) -> "pntablemetadata.PNTableMetaData":
        """
        Retrieve PNTableMetaData for current table.

        @return PNTableMetaData object with metadata related to cursor table.
        """
        if self.private_cursor.metadata_ is None:
            raise Exception("metadata is empty!")

        return self.private_cursor.metadata_

    def currentRegister(self) -> int:
        """
        Get current row number selected by the cursor.

        @return Integer cotining record number.
        """
        return self.private_cursor._currentregister

    def modeAccess(self) -> int:
        """
        Get current access mode for cursor.

        @return PNSqlCursor::Mode constant defining mode access prepared
        """
        return self.private_cursor.mode_access_

    def mainFilter(self) -> str:
        """
        Retrieve main filter for cursor.

        @return String containing the WHERE clause part that will be appended on select.
        """
        ret = (
            self.private_cursor._model.where_filters["main-filter"]
            if "main-filter" in self.private_cursor._model.where_filters.keys()
            else ""
        )
        return ret or ""

    def action(self) -> Optional["pnaction.PNAction"]:
        """
        Get PNAction related to this cursor.

        @return PNAction object.
        """
        return self._action

    def actionName(self) -> str:
        """Get action name from pnaction.PNAction related to the cursor. Returns empty string if none is set."""
        return self._action.name() if self._action else ""

    def setAction(self, action_or_name: Union[str, "pnaction.PNAction"]) -> bool:
        """
        Set action to be related to this cursor.

        @param PNAction object
        @return True if success, otherwise False.
        """

        new_action = (
            self.db().connManager().manager().action(action_or_name.lower())
            if isinstance(action_or_name, str)
            else action_or_name
        )

        if not new_action.table():
            return False

        if self._action is None:
            self._action = new_action
        else:

            if (
                self._action.table() == new_action.table()
            ):  # Esto es para evitar que se setee en un FLTableDB con metadata inválido un action sobre un cursor del parentWidget.

                LOGGER.debug(
                    "Se hace setAction sobre un cursor con la misma table %s\nAction anterior: %s\nAction nueva: %s",
                    new_action.table(),
                    self._action.name(),
                    new_action.name(),
                )
                self._action = new_action
                return True

            else:  # La action previa existe y no es la misma tabla
                self._action = new_action
                self.private_cursor.buffer_ = None

        if self._action:
            self.private_cursor.metadata_ = (
                self.db().connManager().manager().metadata(self._action.table())
            )
            self.private_cursor.doAcl()
            self.private_cursor._model = pncursortablemodel.PNCursorTableModel(self.conn(), self)
            self._selection = QtCore.QItemSelectionModel(self.private_cursor._model)
            self._selection.currentRowChanged.connect(  # type: ignore [attr-defined]
                self.selection_currentRowChanged
            )
            self.private_cursor._activated_check_integrity = True
            self.private_cursor._activated_commit_actions = True
            return True

        return False

    def setMainFilter(self, filter_: str = "", do_refresh: bool = True) -> None:
        """
        Set main cursor filter.

        @param filter_ String containing the filter in SQL WHERE format (excluding WHERE)
        @param do_refresh By default, refresh the cursor afterwards. Set to False to avoid this.
        """
        if self.private_cursor._model:
            self.private_cursor._model.where_filters["main-filter"] = filter_
            if do_refresh:
                self.refresh()

    def setModeAccess(self, mode_access: int) -> None:
        """
        Set cursor access mode.

        @param mode_access PNSqlCursor::Mode constant which inidicates access mode.
        """
        self.private_cursor.mode_access_ = mode_access

    def connectionName(self) -> str:
        """
        Get database connection alias name.

        @return String containing the connection name.
        """
        return self.db()._name

    def setAtomicValueBuffer(self, field_name: str, function_name: str) -> None:
        """
        Set a buffer field value in atomic fashion and outside transaction.

        Invoca a la función, cuyo nombre se pasa como parámetro, del script del contexto del cursor
        (ver PNSqlCursor::ctxt_) para obtener el valor del campo. El valor es establecido en el campo de forma
        atómica, bloqueando la fila durante la actualización. Esta actualización se hace fuera de la transacción
        actual, dentro de una transacción propia, lo que implica que el nuevo valor del campo está inmediatamente
        disponible para las siguientes transacciones.

        @param field_name Nombre del campo
        @param function_name Nombre de la función a invocar del script
        """
        mtd = self.private_cursor.metadata_
        if not self.private_cursor.buffer_ or not field_name or not mtd:
            return

        field = mtd.field(field_name)

        if field is None:
            LOGGER.warning(
                "setAtomicValueBuffer(): No existe el campo %s:%s", self.table(), field_name
            )
            return

        conn_manager = self.db().connManager()
        db_aux = conn_manager.dbAux()

        type = field.type()
        primary_key = mtd.primaryKey()
        value: Any

        if self.private_cursor.cursor_relation_ and self.modeAccess() == self.Browse:
            self.private_cursor.cursor_relation_.commit(False)

        if primary_key and self.db() is not db_aux:
            primary_key_value = self.private_cursor.buffer_.value(primary_key)
            db_aux.transaction()

            value = application.PROJECT.call(
                function_name,
                [field_name, self.private_cursor.buffer_.value(field_name)],
                self.context(),
            )

            manager = conn_manager.manager()

            qry = pnsqlquery.PNSqlQuery(None, db_aux)
            ret = qry.exec_(
                "UPDATE  %s SET %s = %s WHERE %s"
                % (
                    self.table(),
                    field_name,
                    manager.formatValue(type, value),
                    manager.formatAssignValue(mtd.field(primary_key), primary_key_value),
                )
            )
            if ret:
                db_aux.commit()
            else:
                db_aux.rollback()
        else:
            LOGGER.warning(
                "No se puede actualizar el campo de forma atómica, porque no existe clave primaria"
            )

        self.private_cursor.buffer_.set_value(field_name, value)
        self.bufferChanged.emit(field_name)
        application.PROJECT.app.processEvents()  # type: ignore[misc] # noqa: F821

    def setValueBuffer(self, field_name: str, value: Any) -> None:
        """
        Set buffer value for a particular field.

        @param field_name field name
        @param value Value to be set to the buffer field.
        """

        mtd = self.private_cursor.metadata_

        if not field_name or mtd is None:
            LOGGER.warning("setValueBuffer(): No fieldName, or no metadata found")
            return

        field_name = str(field_name).lower()

        if not self.private_cursor.buffer_:
            LOGGER.warning("%s.setValueBuffer(%s): No buffer", self.table(), field_name)
            return

        field = mtd.field(field_name)
        if field is None:
            LOGGER.warning("setValueBuffer(): No existe el campo %s:%s", self.table(), field_name)
            return

        database = self.db()
        manager = database.connManager().manager()

        if field.type() in ("uint", "int") and value == "":
            value = None

        if field.type() == "pixmap" and value and not self.private_cursor._is_system_table:
            value = database.normalizeValue(value)
            table_metadata = self.private_cursor.metadata_
            if table_metadata is not None:
                value = manager.storeLargeValue(table_metadata, value) or value

        if (
            field.outTransaction()
            and self.db()._name not in ["dbAux"]
            and self.modeAccess() != self.Insert
        ):
            primary_key = mtd.primaryKey()

            if (
                self.private_cursor.cursor_relation_ is not None
                and self.modeAccess() != self.Browse
            ):
                self.private_cursor.cursor_relation_.commit(False)

            if primary_key:
                primary_key_value = self.private_cursor.buffer_.value(primary_key)
                qry = pnsqlquery.PNSqlQuery(None, "dbAux")
                qry.exec_(
                    "UPDATE %s SET %s = %s WHERE %s;"
                    % (
                        mtd.name(),
                        field_name,
                        manager.formatValue(field.type(), value),
                        manager.formatAssignValue(mtd.field(primary_key), primary_key_value),
                    )
                )
            else:
                LOGGER.warning(
                    "FLSqlCursor : No se puede actualizar el campo fuera de transaccion, porque no existe clave primaria"
                )

        else:
            self.private_cursor.buffer_.set_value(field_name, value)

        self.bufferChanged.emit(field_name)
        QtWidgets.QApplication.processEvents()

    def valueBuffer(self, field_name: str, with_not_value: bool = False) -> Any:
        """
        Retrieve a value from a field buffer (self.private_cursor.buffer_).

        @param field_name field name
        """
        table_metadata = self.private_cursor.metadata_

        if not table_metadata:
            return None

        if not self.private_cursor.buffer_:
            if not self.refreshBuffer():
                return None

        field_name = str(field_name).lower()

        field_metadata = table_metadata.field(field_name)
        if field_metadata is None:
            LOGGER.warning("valueBuffer(): No existe el campo %s:%s.", self._name, field_name)
            return None

        value = self.buffer().value(field_name)

        if (
            field_metadata.outTransaction()
            and self.db()._name not in ["dbAux"]
            and self.modeAccess() != self.Insert
        ):
            pk_name = table_metadata.primaryKey()
            pk_value = self.buffer().value(pk_name)
            where = (
                self.db()
                .connManager()
                .manager()
                .formatAssignValue(table_metadata.field(pk_name), pk_value)
            )
            sql_query = "SELECT %s FROM %s WHERE %s" % (field_name, table_metadata.name(), where)

            qry = pnsqlquery.PNSqlQuery(None, "dbAux")
            qry.exec_(sql_query)
            if qry.next():
                value = qry.value(0)

        type_ = field_metadata.type()

        if value:

            if type_ == "date":
                if isinstance(value, datetime.date):
                    value = types.Date(value.strftime("%Y-%m-%d"))
            elif type_ == "time":
                if isinstance(value, datetime.time):
                    value = value.strftime("%H:%M:%S")

            elif type_ == "pixmap":
                v_large = (
                    xpm.cache_xpm(str(value))
                    if self.private_cursor._is_system_table
                    else self.db().connManager().manager().fetchLargeValue(str(value))
                )

                value = v_large if v_large else value
            elif type_ == "double":
                value = float(value)  # type: ignore [arg-type] # noqa: F821
            elif type_ in ("int", "uint"):
                value = int(value)  # type: ignore [arg-type] # noqa: F821

        elif with_not_value is False:
            if type_ in ("string", "stringlist", "date", "timestamp"):
                value = ""
            elif type_ in ("double", "int", "uint", "serial"):
                value = 0
            elif type_ == "json":
                value = {}

        return value

    def fetchLargeValue(self, value: str) -> Optional[str]:
        """Retrieve large value from database."""
        return self.db().connManager().manager().fetchLargeValue(value)

    def valueBufferCopy(self, field_name: str) -> Any:
        """
        Retrieve original value for a field before it was changed.

        @param field_name field name
        """
        if not self.private_cursor._buffer_copy or not self.private_cursor.metadata_:
            return None

        field_metadata = self.private_cursor.metadata_.field(field_name)
        if field_metadata is None:
            LOGGER.warning(
                "FLSqlCursor::valueBufferCopy() : No existe el campo %s.%s",
                self.table(),
                field_name,
            )
            return None

        value = self.bufferCopy().value(field_name)
        type_ = field_metadata.type()

        if value:

            if type_ == "date":
                if isinstance(value, datetime.date):
                    value = types.Date(value.strftime("%Y-%m-%d"))
            elif type_ == "time":
                if isinstance(value, datetime.time):
                    value = value.strftime("%H:%M:%S")

            elif type_ == "pixmap":
                v_large = (
                    xpm.cache_xpm(str(value))
                    if self.private_cursor._is_system_table
                    else self.db().connManager().manager().fetchLargeValue(str(value))
                )

                value = v_large if v_large else value
        else:
            if type_ in ("string", "stringlist", "date", "timestamp"):
                value = ""
            elif type_ in ("double", "int", "uint"):
                value = 0
            elif type_ == "json":
                value = {}

        return value

    def setEdition(self, value: bool, modifier: Optional[str] = None) -> None:
        """
        Put cursor into "edition" mode.

        @param b TRUE or FALSE
        """
        # FIXME: What is "edition" ??
        if modifier is None:
            self.private_cursor.edition_ = value
            return

        state_changes = value != self.private_cursor.edition_

        if state_changes and not self.private_cursor.edition_states_:
            self.private_cursor.edition_states_ = pnboolflagstate.PNBoolFlagStateList()

        state_modifier = self.private_cursor.edition_states_.find(modifier)
        if not state_modifier:
            if state_changes:
                state_modifier = pnboolflagstate.PNBoolFlagState()
                state_modifier.modifier_ = modifier
                state_modifier.prev_value_ = self.private_cursor.edition_
                self.private_cursor.edition_states_.append(state_modifier)
        else:
            if state_changes:
                self.private_cursor.edition_states_.pushOnTop(state_modifier)
                state_modifier.prev_value_ = self.private_cursor.edition_
            else:
                self.private_cursor.edition_states_.erase(state_modifier)

        if state_changes:
            self.private_cursor.edition_ = value

    def restoreEditionFlag(self, modifier: str) -> None:
        """Restore Edition flag to its previous value."""
        edition_state = self.private_cursor.edition_states_
        if edition_state:

            state_modifier = edition_state.find(modifier)

            if state_modifier:
                if state_modifier == edition_state.current():
                    self.private_cursor.edition_ = state_modifier.prev_value_

                edition_state.erase(state_modifier)

    def setBrowse(self, value: bool, modifier: Optional[str] = None) -> None:
        """
        Put cursor into browse mode.

        @param value TRUE or FALSE
        """
        if not modifier:
            self.private_cursor.browse_ = value
            return

        state_changes = value != self.private_cursor.browse_

        if state_changes and not self.private_cursor.browse_states_:
            self.private_cursor.browse_states_ = pnboolflagstate.PNBoolFlagStateList()

        if not self.private_cursor.browse_states_:
            return

        state_modifier = self.private_cursor.browse_states_.find(modifier)
        if not state_modifier:
            if state_changes:
                state_modifier = pnboolflagstate.PNBoolFlagState()
                state_modifier.modifier_ = modifier
                state_modifier.prev_value_ = self.private_cursor.browse_
                self.private_cursor.browse_states_.append(state_modifier)
        else:
            if state_changes:
                self.private_cursor.browse_states_.pushOnTop(state_modifier)
                state_modifier.prev_value_ = self.private_cursor.browse_
            else:
                self.private_cursor.browse_states_.erase(state_modifier)

        if state_changes:
            self.private_cursor.browse_ = value

    def restoreBrowseFlag(self, modifier: str) -> None:
        """Restores browse flag to its previous state."""
        browse_state = self.private_cursor.browse_states_
        if browse_state:
            state_modifier = browse_state.find(modifier)

            if state_modifier:
                if state_modifier == browse_state.current():
                    self.private_cursor.browse_ = state_modifier.prev_value_

                browse_state.erase(state_modifier)

    # def meta_model(self) -> Callable:
    #    """
    #    Check if DGI requires models (SqlAlchemy?).
    #    """
    #    return self.meta_model if application.PROJECT.DGI.use_model() else None

    def setContext(self, context: Any = None) -> None:
        """
        Set cursor context for script execution.

        This can be for master or formRecord.

        See FLSqlCursor::ctxt_.

        @param c Execution Context
        """
        if context:
            self.private_cursor.ctxt_ = weakref.ref(context)

    def context(self) -> Any:
        """
        Retrieve current context of execution of scripts for this cursor.

        See FLSqlCursor::ctxt_.

        @return Execution context
        """
        if not self.private_cursor.ctxt_:
            LOGGER.debug("%s.context(). No hay contexto" % self.curName())
            return

        return self.private_cursor.ctxt_()

    def fieldDisabled(self, field_name: str) -> bool:
        """
        Check if a field is disabled.

        Un campo estará deshabilitado, porque esta clase le dará un valor automáticamente.
        Estos campos son los que están en una relación con otro cursor, por lo que
        su valor lo toman del campo foráneo con el que se relacionan.

        @param field_name Nombre del campo a comprobar
        @return TRUE si está deshabilitado y FALSE en caso contrario
        """

        if self.modeAccess() in (self.Insert, self.Edit):
            if self.private_cursor.cursor_relation_ and self.private_cursor.relation_:
                if self.private_cursor.cursor_relation_.metadata() is not None:
                    field = self.private_cursor.relation_.field()
                    return field.lower() == field_name.lower()

        return False

    def inTransaction(self) -> bool:
        """
        Check if there is a transaction in progress.

        @return TRUE if there is one.
        """

        return True if self.db()._transaction_level else False

    def transaction(self, lock: bool = False) -> bool:
        """
        Start a new transaction.

        Si ya hay una transacción en curso simula un nuevo nivel de anidamiento de
        transacción mediante un punto de salvaguarda.

        @param  lock Actualmente no se usa y no tiene ningún efecto. Se mantiene por compatibilidad hacia atrás
        @return TRUE si la operación tuvo exito
        """

        if application.SHOW_CURSOR_EVENTS:
            LOGGER.warning("CURSOR_EVENT: TRANSACTION %s", self.table(), stack_info=True)

        return self.db().doTransaction(self)

    def rollback(self) -> bool:
        """
        Undo operations from a transaction and cleans up.

        @return TRUE if success.
        """

        if application.SHOW_CURSOR_EVENTS:
            LOGGER.warning("CURSOR_EVENT: ROLLBACK %s", self.table(), stack_info=True)

        return self.db().doRollback(self)

    def commit(self, notify: bool = True) -> bool:
        """
        Finishes and commits transaction.

        @param notify If TRUE emits signal cursorUpdated and sets cursor on BROWSE,
              If FALSE skips and emits autoCommit signal.
        @return TRUE if success.
        """

        if application.SHOW_CURSOR_EVENTS:
            LOGGER.warning("CURSOR_EVENT: COMMIT %s", self.table(), stack_info=True)

        result = self.db().doCommit(self, notify)
        if result:
            self.commited.emit()

        return result

    def size(self) -> int:
        """Get number of records in the cursor."""
        model = self.model()
        return model.rowCount() if model else 0

    def openFormInMode(self, mode_: int, wait: bool = True, cont: bool = True) -> None:
        """
        Open form associated with the table in the specified mode.

        @param m Opening mode. (FLSqlCursor::Mode)
        @param wait Indica que se espera a que el formulario cierre para continuar
        @param cont Indica que se abra el formulario de edición de registros con el botón de
        aceptar y continuar
        """
        if not self.private_cursor.metadata_:
            return

        if (not self.isValid() or self.size() <= 0) and not mode_ == self.Insert:
            if not self.size():
                self.private_cursor.msgBoxWarning(self.tr("No hay ningún registro seleccionado"))
                # QtWidgets.QMessageBox.warning(
                #    QApplication.focusWidget(),
                #    self.tr("Aviso"),
                #    self.tr("No hay ningún registro seleccionado"),
                # )
                return
            self.first()

        self.private_cursor.mode_access_ = mode_

        if mode_ == self.Del:
            msg = self.tr("El registro activo será borrado. ¿ Está seguro ?")

            res = application.PROJECT.message_manager().send(
                "msgBoxWarning",
                None,
                [
                    msg,
                    QtWidgets.QApplication.focusWidget(),
                    self.tr("Aviso"),
                    [
                        QtWidgets.QMessageBox.StandardButton.Ok,
                        QtWidgets.QMessageBox.StandardButton.No,
                    ],
                ],
            )
            if res != QtWidgets.QMessageBox.StandardButton.No:

                if self.transaction():
                    if not self.refreshBuffer():
                        self.commit()

                    elif not self.commitBuffer():
                        self.rollback()
                    else:
                        self.commit()

        elif not self._action:
            LOGGER.warning(
                "Para poder abrir un registro de edición se necesita una acción asociada al cursor, "
                "o una acción definida con el mismo nombre que la tabla de la que procede el cursor."
            )

        elif not self._action.formRecord():
            msg = self.tr(
                "No hay definido ningún formulario para manejar\nregistros de esta tabla : %s"
                % self.curName()
            )

            application.PROJECT.message_manager().send(
                "msgBoxWarning", None, [msg, QtWidgets.QApplication.focusWidget(), self.tr("Aviso")]
            )

        elif self.refreshBuffer():  # Hace doTransaction antes de abrir formulario y crear savepoint
            # if mode_ != self.Insert:
            #    self.updateBufferCopy()

            action = application.PROJECT.actions[self._action.name()]
            action.openDefaultFormRecord(self, wait)

    def setNull(self, field_name: str) -> None:
        """
        Set the content of a field in the buffer to be null.

        @param pos_or_name Name or pos of the field in the buffer.
        """

        if self.private_cursor.buffer_ is not None:
            self.buffer().set_value(field_name, None)

    def setCopyNull(self, field_name: str) -> None:
        """
        Set the content of a field in the buffer to be null.

        @param pos_or_name Name or pos of the field in the buffer.
        """

        if self.private_cursor._buffer_copy is not None:
            self.bufferCopy().set_value(field_name, None)

    def isNull(self, field_name: str) -> bool:
        """Get if a field is null."""

        return (
            self.buffer().is_null(field_name) if self.private_cursor.buffer_ is not None else True
        )

    def isCopyNull(self, field_name: str) -> bool:
        """Get if a field was null before changing."""

        return (
            self.bufferCopy().is_null(field_name)
            if self.private_cursor._buffer_copy is not None
            else True
        )

    def updateBufferCopy(self) -> None:
        """
        Copy contents of FLSqlCursor::buffer_ into FLSqlCursor::_buffer_copy.

        This copy allows later to check if the buffer was changed using
        FLSqlCursor::isModifiedBuffer().
        """

        if not self.private_cursor.buffer_:
            return None

        if self.private_cursor._buffer_copy:
            del self.private_cursor._buffer_copy

        self.private_cursor._buffer_copy = pnbuffer.PNBuffer(self)
        # self.bufferCopy()._orm_obj = self._cursor_model()

        for field_name in self.metadata().fieldNames():
            value = self.buffer().value(field_name)
            if value is not None:
                self.bufferCopy().set_value(field_name, value)

    def isModifiedBuffer(self) -> bool:
        """
        Check if current buffer contents are different from the original copy.

        See FLSqlCursor::_buffer_copy .

        @return True if different. False if equal.
        """

        return (
            True
            if self.private_cursor.buffer_ and self.private_cursor.buffer_._cache_buffer
            else False
        )

    def setAskForCancelChanges(self, ask: bool) -> None:
        """
        Set value for FLSqlCursor::_ask_for_cancel_changes .

        @param a If True, a popup will appear warning the user for unsaved changes on cancel.
        """
        self.private_cursor._ask_for_cancel_changes = ask

    def setActivatedCheckIntegrity(self, ask: bool) -> None:
        """
        Enable or disable integrity checks.

        @param a TRUE los activa y FALSE los desactiva
        """
        self.private_cursor._activated_check_integrity = ask

    def activatedCheckIntegrity(self) -> bool:
        """Retrieve if integrity checks are enabled."""
        return self.private_cursor._activated_check_integrity

    def setActivatedCommitActions(self, ask: bool) -> None:
        """
        Enable or disable before/after commit actions.

        @param a True to enable, False to disable.
        """
        self.private_cursor._activated_commit_actions = ask

    def activatedCommitActions(self) -> bool:
        """
        Retrieve wether before/after commits are enabled.
        """
        return self.private_cursor._activated_commit_actions

    def msgCheckIntegrity(self) -> str:
        """
        Get message for integrity checks.

        The referential integrity is checked when trying to delete, the non-duplication of
        primary keys and if there are nulls in fields that do not allow it when inserted or edited.
        If any verification fails, it returns a message describing the fault.

        @return Error message
        """
        message = ""

        if self.private_cursor.buffer_ is None or self.private_cursor.metadata_ is None:
            return "\nBuffer vacío o no hay metadatos"

        if not self.buffer().is_valid():
            return "\nEl registro ha sido borrado de la BD"

        field_list = self.metadata().fieldList()
        manager = self.db().connManager().manager()

        if self.private_cursor.mode_access_ in [self.Insert, self.Edit]:
            if self.private_cursor.mode_access_ == self.Edit:
                if not self.isModifiedBuffer():
                    return ""

            checked_compound_key = False

            for field in field_list:
                field_name = field.name()
                relation_m1 = field.relationM1()
                value = self.buffer().value(field_name)
                table_metadata = (
                    manager.metadata(relation_m1.foreignTable()) if relation_m1 else None
                )

                if not self.isNull(field_name):
                    assoc_field_metadata = field.associatedField()
                    if assoc_field_metadata:
                        if relation_m1:
                            if not relation_m1.checkIn() or table_metadata is None:
                                continue
                        else:
                            message += (
                                "\n"
                                + "FLSqlCursor : Error en metadatos, el campo %s tiene un campo asociado pero no existe "
                                "relación muchos a uno:%s" % (self.table(), field_name)
                            )
                            continue

                        field_metadata_name = assoc_field_metadata.name()
                        assoc_value = self.private_cursor.buffer_.value(field_metadata_name)
                        if field.type() == "uint" and value == 0:
                            LOGGER.warning(
                                "El id 0 , no pertenece a %s.Sin embargo, se permite por temas de compatibilidad.Convirtiendo a Nulo"
                                % assoc_value
                            )
                            self.buffer().setNull(field_name)

                        elif not self.isNull(field_metadata_name):

                            filter_ = "%s AND %s" % (
                                manager.formatAssignValue(
                                    field.associatedFieldFilterTo(),
                                    assoc_field_metadata,
                                    assoc_value,
                                    True,
                                ),
                                manager.formatAssignValue(
                                    relation_m1.foreignField(), field, value, True
                                ),
                            )

                            qry = pnsqlquery.PNSqlQuery(None, self.db())
                            qry.setTablesList(table_metadata.name())
                            qry.setSelect(field.associatedFieldFilterTo())
                            qry.setFrom(table_metadata.name())
                            qry.setWhere(filter_)
                            qry.setForwardOnly(True)
                            qry.exec_()
                            if not qry.first():
                                message += "\n%s:%s : %s no pertenece a %s" % (
                                    self.table(),
                                    field.alias(),
                                    value,
                                    assoc_value,
                                )
                            else:
                                self.private_cursor.buffer_.set_value(
                                    field_metadata_name, qry.value(0)
                                )

                        else:
                            message += "\n%s:%s : %s no se puede asociar aun valor NULO" % (
                                self.table(),
                                field.alias(),
                                value,
                            )

                if self.private_cursor.mode_access_ == self.Edit:
                    if self.buffer().value(field_name) == self.bufferCopy().value(field_name):
                        continue

                if (
                    self.isNull(field_name)
                    and not field.allowNull()
                    and not field.type() in ("serial")
                ):
                    message += "\n%s:%s : No puede ser nulo" % (self.table(), field.alias())

                if field.isUnique():
                    primary_key = self.metadata().primaryKey()
                    if not self.buffer().is_null(primary_key) and value is not None:
                        value_primary_key = self.private_cursor.buffer_.value(primary_key)
                        field_mtd = self.private_cursor.metadata_.field(primary_key)
                        if field_mtd is None:
                            raise Exception("pk field is not found!")
                        qry = pnsqlquery.PNSqlQuery(None, self.db().connectionName())
                        qry.setTablesList(self.table())
                        qry.setSelect(field_name)
                        qry.setFrom(self.table())
                        qry.setWhere(
                            "%s AND %s <> %s"
                            % (
                                manager.formatAssignValue(field, value, True),
                                self.private_cursor.metadata_.primaryKey(
                                    self.private_cursor._is_query
                                ),
                                manager.formatValue(field_mtd.type(), value_primary_key),
                            )
                        )
                        qry.setForwardOnly(True)
                        qry.exec_()
                        if qry.first():
                            message += (
                                "\n%s:%s : Requiere valores únicos, y ya hay otro registro con el valor %s en este campo"
                                % (self.table(), field.alias(), value)
                            )

                if (
                    field.isPrimaryKey()
                    and self.private_cursor.mode_access_ == self.Insert
                    and value is not None
                ):
                    qry = pnsqlquery.PNSqlQuery(None, self.db())
                    qry.setTablesList(self.table())
                    qry.setSelect(field_name)
                    qry.setFrom(self.table())
                    qry.setWhere(manager.formatAssignValue(field, value, True))
                    qry.setForwardOnly(True)
                    qry.exec_()
                    if qry.next():
                        message += (
                            "\n%s:%s : Es clave primaria y requiere valores únicos, y ya hay otro registro con el valor %s en este campo"
                            % (self.table(), field.alias(), value)
                        )

                if relation_m1 and value and str(value) != "NULL" and table_metadata is not None:
                    if relation_m1.checkIn() and not relation_m1.foreignTable() == self.table():
                        # r = field.relationM1()
                        qry = pnsqlquery.PNSqlQuery(None, self.db())
                        qry.setTablesList(table_metadata.name())
                        qry.setSelect(relation_m1.foreignField())
                        qry.setFrom(table_metadata.name())
                        qry.setWhere(
                            manager.formatAssignValue(
                                relation_m1.foreignField(), field, value, True
                            )
                        )
                        qry.setForwardOnly(True)
                        # LOGGER.debug(
                        #    "SQL linea = %s conn name = %s", qry.sql(), self.connectionName()
                        # )
                        qry.exec_()
                        if not qry.next():
                            LOGGER.warning(
                                " msgCheckIntegrity. No se encuentra el valor en session: %s, transacción: %s, sql: %s, size: %s",
                                qry.db().session(),
                                qry.db().session().transaction,
                                qry.sql(),
                                qry.size(),
                            )
                            message += "\n%s:%s : El valor %s no existe en la tabla %s" % (
                                self.table(),
                                field.alias(),
                                value,
                                relation_m1.foreignTable(),
                            )
                        else:
                            self.private_cursor.buffer_.set_value(field_name, qry.value(0))

                        if not table_metadata.inCache():
                            del table_metadata

                field_list_compound_key = self.private_cursor.metadata_.fieldListOfCompoundKey(
                    field_name
                )
                if (
                    field_list_compound_key
                    and not checked_compound_key
                    and self.private_cursor.mode_access_ == self.Insert
                ):
                    filter_compound_key: str = ""
                    field_1: str = ""
                    values_fields: str = ""
                    for field_compound_key in field_list_compound_key:
                        value_compound_key = self.private_cursor.buffer_.value(
                            field_compound_key.name()
                        )

                        filter_compound_key += " AND " if filter_compound_key else ""

                        filter_compound_key += "%s" % manager.formatAssignValue(
                            field_compound_key, value_compound_key, True
                        )

                        field_1 += "+" if field_1 else ""

                        field_1 += "%s" % field_compound_key.alias()

                        values_fields += "+" if values_fields else ""

                        values_fields = "%s" % str(value_compound_key)

                    qry = pnsqlquery.PNSqlQuery(None, self.db().connectionName())
                    qry.setTablesList(self.table())
                    qry.setSelect(field_name)
                    qry.setFrom(self.table())
                    if filter_compound_key:
                        qry.setWhere(filter_compound_key)
                    qry.setForwardOnly(True)
                    qry.exec_()

                    if qry.next():
                        message += (
                            "\n%s : Requiere valor único, y ya hay otro registro con el valor %s en la tabla %s"
                            % (field_1, values_fields, self.table())
                        )
                    checked_compound_key = True

        elif self.private_cursor.mode_access_ == self.Del:

            for field in field_list:
                if self.isNull(field.name()):
                    continue

                value = self.buffer().value(field.name())

                for relation in field.relationList():
                    if not relation.checkIn():
                        continue
                    metadata = manager.metadata(relation.foreignTable())
                    if not metadata:
                        continue
                    field_metadata = metadata.field(relation.foreignField())
                    if field_metadata is not None:
                        relation_m1 = field_metadata.relationM1()
                        if relation_m1 is not None:
                            if relation_m1.deleteCascade() or not relation_m1.checkIn():
                                continue
                        else:
                            continue

                    else:
                        message += (
                            "\nFLSqlCursor : Error en metadatos, %s.%s no es válido.\nCampo relacionado con %s.%s."
                            % (metadata.name(), relation.foreignField(), self.table(), field.name())
                        )
                        continue

                    qry = pnsqlquery.PNSqlQuery(None, self.db().connectionName())
                    qry.setTablesList(metadata.name())
                    qry.setSelect(relation.foreignField())
                    qry.setFrom(metadata.name())
                    qry.setWhere(
                        manager.formatAssignValue(relation.foreignField(), field, value, True)
                    )
                    qry.setForwardOnly(True)
                    qry.exec_()
                    if qry.next():
                        message += "\n%s:%s : Con el valor %s hay registros en la tabla %s" % (
                            self.table(),
                            field.alias(),
                            value,
                            metadata.name(),
                        )

        return message

    def checkIntegrity(self, showError: bool = True) -> bool:
        """
        Perform integrity checks.

        The referential integrity is checked when trying to delete, the non-duplication of
        primary keys and if there are nulls in fields that do not allow it when inserted or edited.
        If any check fails it displays a dialog box with the type of fault found and the method
        returns FALSE.

        @param showError If TRUE shows the dialog box with the error that occurs when the pass integrity checks
        @return TRUE if the buffer could be delivered to the cursor, and FALSE if any verification failed of integrity
        """
        if not self.private_cursor._activated_check_integrity:
            return True
        if not self.private_cursor.buffer_ or not self.private_cursor.metadata_:
            return False
        msg = self.msgCheckIntegrity()
        if msg:
            if showError:
                if self.private_cursor.mode_access_ in (self.Insert, self.Edit):
                    self.private_cursor.msgBoxWarning(
                        "No se puede validad el registro actual:\n" + msg
                    )
                elif self.private_cursor.mode_access_ == self.Del:
                    self.private_cursor.msgBoxWarning("No se puede borrar registro:\n" + msg)

            LOGGER.warning(msg)
            return False

        return True

    def cursorRelation(self) -> Optional["isqlcursor.ISqlCursor"]:
        """
        Return the cursor relationed.

        @return PNSqlCursor relationed or None
        """
        return self.private_cursor.cursor_relation_

    def relation(self) -> Optional["pnrelationmetadata.PNRelationMetaData"]:
        """
        Return the relation metadata.

        @return PNRelationMetaData relationed or None.
        """
        return self.private_cursor.relation_

    def obj(self) -> Optional["QtWidgets.QTableView"]:
        """Return parent widget."""

        model = self.model()
        return model.parent_view if model is not None else None  # type: ignore [unreachable]

    def setUnLock(self, field_name: str, value: bool) -> None:
        """
        Unlock the current cursor record.

        @param field_name Field name.
        @param v Value for the unlock field.
        """

        if not self.private_cursor.metadata_ or not self.modeAccess() == self.Browse:
            return

        field_mtd = self.private_cursor.metadata_.field(field_name)
        if field_mtd is None:
            raise Exception("Field %s is empty!" % field_name)

        if not field_mtd.type() == "unlock":
            LOGGER.warning("setUnLock sólo permite modificar campos del tipo Unlock")
            return

        if not self.private_cursor.buffer_:
            self.prime_update()

        if not self.private_cursor.buffer_:
            raise Exception("Unexpected null buffer")

        self.setModeAccess(self.Edit)
        self.private_cursor.buffer_.set_value(field_name, value)
        self.private_cursor.buffer_.apply_buffer()
        self.update()
        self.refreshBuffer()

    def isLocked(self) -> bool:
        """
        To check if the current cursor record is locked.

        @return TRUE if blocked, FALSE otherwise.
        """
        if not self.private_cursor.metadata_:
            return False
        if not self.private_cursor.buffer_:
            return True

        ret_ = False
        if self.private_cursor.mode_access_ is not self.Insert:
            if self.private_cursor._currentregister > -1:

                for field_name in self.private_cursor.metadata_.fieldNamesUnlock():
                    if self.private_cursor.buffer_.value(field_name) not in ("True", True, 1, "1"):
                        ret_ = True
                        break

        if not ret_ and self.private_cursor.cursor_relation_ is not None:
            ret_ = self.private_cursor.cursor_relation_.isLocked()

        return ret_

    def buffer(self) -> "pnbuffer.PNBuffer":
        """
        Return the content of the buffer.

        @return PNBuffer or None.
        """
        if not self.private_cursor.buffer_:
            raise Exception("buffer is empty!")

        return self.private_cursor.buffer_

    def bufferIsNull(self, field_name: str) -> bool:
        """Return if buffer is null."""

        return self.private_cursor.buffer_ is None or self.private_cursor.buffer_.is_null(
            field_name
        )

    def bufferCopy(self) -> "pnbuffer.PNBuffer":
        """
        Return the contents of the bufferCopy.

        @return PNBuffer or None.
        """
        if not self.private_cursor._buffer_copy:
            raise Exception("bufferCopy is empty!")

        return self.private_cursor._buffer_copy

    def clear_buffer(self) -> None:
        """Clear buffer."""

        if self.private_cursor.buffer_ and self.modeAccess() != self.Insert:
            self.buffer().clear()

    def atFrom(self) -> int:
        """
        Get the position of the current record, according to the primary key contained in the self.private_cursor.buffer_.

        The position of the current record within the cursor is calculated taking into account the
        Current filter (FLSqlCursor :: curFilter ()) and the field or sort fields of it (QSqlCursor :: sort ()).
        This method is useful, for example, to know at what position within the cursor
        A record has been inserted.

        @return Position of the record within the cursor, or 0 if it does not match.
        """

        if not self.private_cursor.buffer_ or not self.private_cursor.metadata_:
            return 0
        # Faster version for this function::
        return self.at() if self.isValid() else 0

    def atFromBinarySearch(self, field_name: str, value: Any, order_asc: bool = True) -> int:
        """
        Get the position within the cursor of the first record in the indicated field start with the requested value.

        It assumes that the records are ordered by that field, to perform a binary search.
        The position of the current record within the cursor is calculated taking into account the
        Current filter (FLSqlCursor :: curFilter ()) and the field or sort fields
        of it (QSqlCursor :: sort ()).
        This method is useful, for example, to know at what position within the cursor
        a record with a certain value is found in a field.

        @param field_name Name of the field in which to look for the value
        @param value Value to look for (using like 'v%')
        @param orderAsc TRUE (default) if the order is ascending, FALSE if it is descending
        @return Position of the record within the cursor, or 0 if it does not match.
        """

        ret = -1
        ini = 0
        fin = self.size() - 1

        if not self.private_cursor.metadata_:
            raise Exception("Metadata is not set")

        if field_name in self.metadata().fieldNames():
            while ini <= fin:
                mid = int((ini + fin) / 2)
                mid_value = str(self.model().value(mid, field_name))
                if value == mid_value:
                    ret = mid
                    break

                comp = value < mid_value if order_asc else value > mid_value

                if not comp:
                    ini = mid + 1
                else:
                    fin = mid - 1
                ret = ini

        return ret

    # """
    # Redefinido por conveniencia
    # """

    # @decorators.not_implemented_warn
    # def exec_(self, query: str) -> bool:
    # if query:
    #    LOGGER.debug("ejecutando consulta " + query)
    #    QSqlQuery.exec(self, query)

    #    return True

    def db(self) -> "iconnection.IConnection":
        """
        To get the database you work on.

        @return PNConnection used by the cursor.
        """

        if not self.private_cursor.db_:
            raise Exception("db_ is not defined!")

        return self.private_cursor.db_

    def curName(self) -> str:
        """
        To get the cursor name (usually the table name).

        @return cursor Name
        """
        return self.private_cursor.cursor_name_

    def filterAssoc(
        self, field_name: str, tableMD: Optional["pntablemetadata.PNTableMetaData"] = None
    ) -> Optional[str]:
        """
        To get the default filter in associated fields.

        @param field_name Name of the field that has associated fields. It must be the name of a field of this cursor.
        @param tableMD Metadata to use as a foreign table. If it is zero use the foreign table defined by the relation M1 of 'field_name'.
        """

        if self.private_cursor.buffer_ is None:
            return None

        mtd = self.private_cursor.metadata_

        field = mtd.field(field_name) if mtd else None
        if field is None:
            return None

        if tableMD is None:
            rel_m1 = field.relationM1()
            tableMD = (
                self.db().connManager().manager().metadata(rel_m1.foreignTable())
                if rel_m1 is not None
                else None
            )

        if tableMD is None:
            return None

        assoc_field = field.associatedField()
        if assoc_field is None:
            return None

        field_by = field.associatedFieldFilterTo()

        if not tableMD.field(field_by) or self.buffer().is_null(assoc_field.name()):
            return None

        assoc_value = self.buffer().value(assoc_field.name())
        if assoc_value:
            return (
                self.db()
                .connManager()
                .manager()
                .formatAssignValue(field_by, assoc_field, assoc_value, True)
            )

        return None

    @decorators.beta_implementation
    def aqWasDeleted(self) -> bool:
        """
        Indicate if the cursor has been deleted.

        @return True or False.
        """
        return False

    @decorators.not_implemented_warn
    def calculateField(self, name: str) -> bool:
        """
        Indicate if the field is calculated.

        @return True or False.
        """
        return True

    def model(self) -> "pncursortablemodel.PNCursorTableModel":
        """
        Return the tablemodel used by the cursor.

        @return PNCursorTableModel used.
        """
        return self.private_cursor._model

    def selection(self) -> Optional["QtCore.QItemSelectionModel"]:
        """
        Return the item pointed to in the tablemodel.

        @return selected Item.
        """
        return self._selection

    @decorators.pyqt_slot(QtCore.QModelIndex, QtCore.QModelIndex)
    @decorators.pyqt_slot(int, int)
    @decorators.pyqt_slot(int)
    def selection_currentRowChanged(self, current: Any, previous: Any = None) -> None:
        """
        Update the current record pointed to by the tablemodel.

        @param current. new item selected.
        @param previous. old item selected.
        """

        current_row = current.row()

        if self.private_cursor._currentregister != current_row:
            self.private_cursor._currentregister = current_row
            self.private_cursor._current_changed.emit(self.at())

        self.refreshBuffer()

        self.private_cursor.doAcl()
        if self._action:
            LOGGER.debug(
                "cursor:%s , row:%s:: %s",
                self._action.table(),
                self.private_cursor._currentregister,
                self,
            )

    def selection_pk(self, value: Any) -> bool:
        """
        Move the cursor position to the one that matches the primaryKey value.

        @param value. primaryKey value to search.
        @return True if seek the position else False.
        """

        if not self.private_cursor.buffer_:
            raise Exception("Buffer not set")

        grid_row = self.model().find_pk_row(value)

        if grid_row > -1:
            return self.move(grid_row) if self.at() != grid_row else True

        return False

    def at(self) -> int:
        """
        Return the current position to which the cursor points.

        @return Index position.
        """

        row = self.private_cursor._currentregister

        return 0 if not row else -1 if row < 0 else -2 if row >= self.size() else row

    def isValid(self) -> bool:
        """
        Specify whether the position to which the cursor points is valid.

        @return True if ok else False.
        """

        return True if (self._valid and self.at() >= 0) or not self.size() else False

    @decorators.pyqt_slot()
    @decorators.pyqt_slot(str)
    def refresh(self, field_name: Optional[str] = None) -> None:
        """
        Refresh the cursor content.

        If no related cursor has been indicated, get the complete cursor, according to the query
        default. If it has been indicated that it depends on another cursor with which it relates,
        The content of the cursor will depend on the value of the field that determines the relationship.
        If the name of a field is indicated, it is considered that the buffer has only changed in that
        field and thus avoid repetitions in the soda.

        @param field_name Name of the buffer field that has changed
        """

        if not self.private_cursor.metadata_:
            return

        if (
            self.private_cursor.cursor_relation_ is not None
            and self.private_cursor.relation_ is not None
        ):
            self.clearPersistentFilter()
            if not self.private_cursor.cursor_relation_.metadata():
                return
            if (
                self.private_cursor.cursor_relation_.primaryKey() == field_name
                and self.private_cursor.cursor_relation_.modeAccess() == self.Insert
            ):
                return

            if self.private_cursor.cursor_relation_.modeAccess() == self.Insert:
                self.setModeAccess(self.Browse)

            if not field_name or self.private_cursor.relation_.foreignField() == field_name:
                # if self.private_cursor.buffer_:
                #    self.private_cursor.buffer_.clear_buffer()
                self.refreshDelayed(0)
                return

        else:
            emite = False
            pk_value = self.valueBuffer(self.primaryKey())
            self.model().refresh()  # Hay que hacer refresh previo pq si no no recoge valores de un commitBuffer paralelo
            # self.select()
            if pk_value:
                if self.selection_pk(pk_value):
                    if (
                        self.private_cursor.buffer_ is None
                    ):  # Esto no debería pasar, pero por si acaso...
                        self.private_cursor.buffer_ = pnbuffer.PNBuffer(self)
                        self.private_cursor.buffer_.prime_insert()
                    else:
                        self.private_cursor.buffer_.prime_update()

            else:
                buffer = self.private_cursor.buffer_
                if buffer is not None:
                    buffer.clear()
                pos = self.atFrom()
                current_size = self.size()
                if pos > current_size:
                    pos = current_size - 1

                if not self.seek(pos, False, True):
                    emite = True

                    # if self.private_cursor.buffer_:
                    #    self.private_cursor.buffer_.clear_buffer()
            if emite:
                self.newBuffer.emit()

    @decorators.pyqt_slot()
    def refreshDelayed(self, msec: int = 50) -> None:  # keep > 50ms
        """
        Update the recordset with a delay.

        Accept a lapse of time in milliseconds, activating the internal timer for
        to perform the final refresh upon completion of said lapse.

        @param msec Amount of lapsus time, in milliseconds.
        """
        # if self.buffer():
        #    return
        if not self.private_cursor.timer_:
            return

        obj = self.sender()
        if not obj or not obj.inherits("QTimer"):
            self.private_cursor.timer_.start(msec)
            return
        else:
            self.private_cursor.timer_.stop()

        pos = self.atFrom()

        # ---> SI NO METEMOS ESTO EL AUTOCOMPLETADO EN FIELDS PETA
        base_filter = self.baseFilter()
        current_filter = self.filter()

        if base_filter not in current_filter:

            self.setFilter()

        # <---

        self.select()

        if not self.seek(pos, False, True):
            self.newBuffer.emit()

        cur_relation = self.private_cursor.cursor_relation_
        relation = self.private_cursor.relation_

        if cur_relation and relation and cur_relation.metadata():
            value = self.valueBuffer(relation.field())
            if value:
                foreign_value = cur_relation.valueBuffer(relation.foreignField())
                if foreign_value != value:
                    cur_relation.setValueBuffer(relation.foreignField(), value)

    def prime_insert(self) -> None:
        """
        Refill the buffer for the first time.
        """

        if not self.private_cursor.buffer_:
            self.private_cursor.buffer_ = pnbuffer.PNBuffer(self)

        self.private_cursor.buffer_.prime_insert()

    def prime_update(self) -> pnbuffer.PNBuffer:
        """
        Update the buffer.

        @return buffer refresh.
        """

        if self.private_cursor.buffer_ is None:
            self.private_cursor.buffer_ = pnbuffer.PNBuffer(self)
        # LOGGER.warning("Realizando prime_update en pos %s y estado %s , filtro %s", self.at(), self.modeAccess(), self.filter())
        self.private_cursor.buffer_.prime_update()
        return self.private_cursor.buffer_

    @decorators.pyqt_slot()
    def refreshBuffer(self) -> bool:
        """
        Refresh the buffer according to the established access mode.

        Bring cursor information to the buffer to edit or navigate, or prepare the buffer to
        insert or delete

        If there is a counter field, the "calculateCounter" function of the script of the
        context (see FLSqlCursor :: ctxt_) set for the cursor. This function is passed
        as an argument the name of the counter field and must return the value it must contain
        that field

        @return TRUE if the refreshment could be performed, FALSE otherwise
        """

        if not self.private_cursor.metadata_ or not self._action:
            raise Exception("Not initialized")

        # if (
        #    isinstance(self.sender(), QtCore.QTimer)
        #    and self.private_cursor.mode_access_ != self.Browse
        # ):
        #    return False

        if self.private_cursor.mode_access_ != self.Insert:
            if not self.isValid():
                return False

        if self.private_cursor.mode_access_ == self.Insert:
            if not self.commitBufferCursorRelation():
                return False

            if not self.private_cursor.buffer_:
                self.private_cursor.buffer_ = pnbuffer.PNBuffer(self)

            self.buffer().prime_insert()

            # self.setNotGenerateds()

            field_list = self.private_cursor.metadata_.fieldList()

            for field in field_list:

                field_name = field.name()
                type_ = field.type()
                default_value = field.defaultValue()

                if default_value is not None:
                    self.buffer().set_value(field_name, default_value)

                if type_ == "serial":
                    val = self.db().nextSerialVal(self.table(), field_name)
                    self.buffer().set_value(field_name, val)
                elif type_ == "timestamp":
                    if not field.allowNull():
                        val_str = self.db().getTimeStamp()
                        self.buffer().set_value(field_name, val_str)

                if field.isCounter():

                    function_counter = None
                    if self._action.scriptFormRecord():
                        from pineboolib.application.safeqsa import SafeQSA

                        context_ = SafeQSA.formrecord("formRecord%s" % self._action.name()).iface
                        function_counter = getattr(context_, "calculateCounter", None)

                    siguiente = (
                        utils.next_counter(field_name, self)
                        if function_counter is None
                        else function_counter()
                    )

                    if siguiente:
                        self.private_cursor.buffer_.set_value(field_name, siguiente)

            if (
                self.private_cursor.cursor_relation_ is not None
                and self.private_cursor.relation_ is not None
                and self.private_cursor.cursor_relation_.metadata()
            ):
                self.setValueBuffer(
                    self.private_cursor.relation_.field(),
                    self.private_cursor.cursor_relation_.valueBuffer(
                        self.private_cursor.relation_.foreignField()
                    ),
                )

            self.private_cursor.undoAcl()
            self.updateBufferCopy()
            self.newBuffer.emit()

        elif self.private_cursor.mode_access_ == self.Edit:
            if not self.commitBufferCursorRelation():
                return False

            self.prime_update()
            if self.isLocked() and not self.private_cursor._acos_cond_name:
                self.private_cursor.mode_access_ = self.Browse

            self.setNotGenerateds()
            self.updateBufferCopy()
            self.private_cursor.doAcl()
            self.newBuffer.emit()

        elif self.private_cursor.mode_access_ == self.Del:

            if self.isLocked():
                self.private_cursor.msgBoxWarning("Registro bloqueado, no se puede eliminar")
                self.private_cursor.mode_access_ = self.Browse
                return False

            self.prime_update()
            self.setNotGenerateds()
            self.updateBufferCopy()

        elif self.private_cursor.mode_access_ == self.Browse:
            self.prime_update()
            self.setNotGenerateds()
            self.newBuffer.emit()
            self.private_cursor.doAcl()

        else:
            LOGGER.error("refreshBuffer(). No hay definido modeAccess()")

        return True

    @decorators.pyqt_slot()
    def setEditMode(self) -> bool:
        """
        Change the cursor to Edit mode.

        @return True if the cursor is in Edit mode or was in Insert mode and has successfully switched to Edit mode
        """
        if self.private_cursor.mode_access_ == self.Insert:
            if not self.commitBuffer():
                return False
            self.refresh()
            self.setModeAccess(self.Edit)
        elif self.private_cursor.mode_access_ == self.Edit:
            return True

        return False

    @decorators.pyqt_slot()
    def seek(self, index: int, relative: Optional[bool] = False, emite: bool = False) -> bool:
        """
        Simply refreshes the buffer with the FLSqlCursor :: refreshBuffer () method.

        @param index. New position.
        @param relative. Not used.
        @param emite If TRUE emits the FLSqlCursor :: currentChanged () signal.

        @return True if ok or False.
        """
        result = self.move(index)
        if result:
            if emite:
                self.currentChanged.emit(self.at())

            result = self.refreshBuffer()
        return result

    @decorators.pyqt_slot()
    @decorators.pyqt_slot(bool)
    def next(self, emite: bool = True) -> bool:
        """
        Move the position to which the +1 position and execute refreshBuffer.

        @param emits If TRUE emits the FLSqlCursor :: currentChanged () signal
        """
        # if self.private_cursor.mode_access_ == self.Del:
        #    return False

        result = self.moveby(1)
        if result:
            if emite:
                self.private_cursor._current_changed.emit(self.at())

            result = self.refreshBuffer()

        return result

    def moveby(self, pos: int) -> bool:
        """
        Move the cursor to the specified position.

        @param pos. index position to seek.
        @return True if ok else False.
        """

        pos += self.private_cursor._currentregister if self.private_cursor._currentregister else 0

        return self.move(pos)

    @decorators.pyqt_slot()
    @decorators.pyqt_slot(bool)
    def prev(self, emite: bool = True) -> bool:
        """
        Move the position to which the -1 position and execute refreshBuffer.

        @param emits If TRUE emits the FLSqlCursor :: currentChanged () signal
        """
        # if self.private_cursor.mode_access_ == self.Del:
        #    return False

        result = self.moveby(-1)

        if result:
            if emite:
                self.private_cursor._current_changed.emit(self.at())

            result = self.refreshBuffer()

        return result

    def move(self, row: int = -1) -> bool:
        """
        Move the cursor across the table.

        @return True if ok else False.
        """
        # if row is None:
        #     row = -1
        model = self.private_cursor._model
        if not model:
            return False

        if not model.seek_row(-1 if row < 0 else row):
            return False
        elif self.private_cursor._currentregister == model._current_row_index:
            return False

        top_left = model.index(model._current_row_index, 0)
        botton_right = model.index(model._current_row_index, model.cols - 1)
        new_selection = QtCore.QItemSelection(top_left, botton_right)
        if self._selection is None:
            raise Exception("Call setAction first.")
        self._selection.select(
            new_selection, QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect
        )
        # self.private_cursor._current_changed.emit(self.at())
        if model._current_row_index > -1 and model._current_row_index < self.size():
            self.private_cursor._currentregister = model._current_row_index
            return True

        return False

    @decorators.pyqt_slot()
    @decorators.pyqt_slot(bool)
    def first(self, emite: bool = True) -> bool:
        """
        Move the position to which the first position and execute refreshBuffer.

        @param emits If TRUE emits the FLSqlCursor :: currentChanged () signal
        """
        # if self.private_cursor.mode_access_ == self.Del:
        #    return False

        result = self.move(0) if not self.private_cursor._currentregister == 0 else True

        if result:
            if emite:
                self.private_cursor._current_changed.emit(self.at())

            result = self.refreshBuffer()

        return result

    @decorators.pyqt_slot()
    @decorators.pyqt_slot(bool)
    def last(self, emite: bool = True) -> bool:
        """
        Move the position to which the last position and execute refreshBuffer.

        @param emits If TRUE emits the FLSqlCursor :: currentChanged () signal
        """
        # if self.private_cursor.mode_access_ == self.Del:
        #    return False

        result = self.move(self.size() - 1)
        if result:
            if emite:
                self.private_cursor._current_changed.emit(self.at())

            result = self.refreshBuffer()

        return result

    @decorators.pyqt_slot()
    def __del__(self, invalidate: bool = True) -> None:
        """
        Check if it is deleted in cascade, if so, also delete related records in 1M cardinality.

        @param invalidate. Not used.
        """
        global CONNECTION_CURSORS

        for id_conn in CONNECTION_CURSORS.keys():
            if self.id() in CONNECTION_CURSORS[id_conn]:
                CONNECTION_CURSORS[id_conn].remove(self.id())

                if application.SHOW_CURSOR_EVENTS:
                    LOGGER.warning(
                        "CURSOR_EVENT: %s eliminado pool de cursores %s.", self.id(), id_conn
                    )
                    return

        if application.SHOW_CURSOR_EVENTS:
            LOGGER.warning(
                "CURSOR_EVENT: No se ha eliminado %s del pool de cursores, porque no se ha encontrado.",
                self.id(),
            )
        # FIXME: Pongo que tiene que haber mas de una trasaccion abierta
        # try:
        # message = None

        if not hasattr(self, "private_cursor"):
            return

        if self.private_cursor._transactions_opened and not getattr(
            application, "TESTING_MODE", False
        ):
            LOGGER.warning(
                "FLSqlCursor(%s).Transacciones abiertas!! %s",
                self.curName(),
                self.private_cursor._transactions_opened,
            )
            raise Exception("Transacctions opened!")

            # ===================================================================
            # message = (
            #     "Se han detectado transacciones no finalizadas en la última operación.\n"
            #     "Se van a cancelar las transacciones pendientes.\n"
            #     "Los últimos datos introducidos no han sido guardados, por favor\n"
            #     "revise sus últimas acciones y repita las operaciones que no\n"
            #     "se han guardado.\nSqlCursor::~SqlCursor: %s\n" % self.table()
            # )
            # self.rollbackOpened(-1, message)
            # ===================================================================
        # except Exception as error:
        #    LOGGER.warning("__del__: %s", error)

        obj_ = self.private_cursor._model
        del self.private_cursor._model
        garbage_collector.check_delete(obj_, "cursor_%s.tableModel" % self.curName())

    @decorators.pyqt_slot()
    def select(
        self, final_filter: str = "", sort: Optional[str] = None
    ) -> bool:  # sort = QtCore.QSqlIndex()
        """
        Execute the filter specified in the cursor and refresh the information of the affected records.

        @param _filter. Optional filter.
        @param sort. Optional sort order.

        @return True if ok or False.
        """

        if not self.private_cursor.metadata_:
            return False

        if not self.filter():  # Con esto aplicamos el filtro existente , relaciones ....
            self.setFilter()

        if self.private_cursor.cursor_relation_:
            if (
                self.private_cursor.cursor_relation_.modeAccess() == self.Insert
                and not self.curFilter()
            ):
                final_filter = "1 = 0"

        self.private_cursor._model.where_filters["select_filter"] = final_filter

        if sort:
            self.private_cursor._model.setSortOrder(sort)

        self.private_cursor._model.refresh()
        self.private_cursor._currentregister = -1
        self.private_cursor._model.where_filters["select_filter"] = ""

        if self.modeAccess() == self.Browse and self.private_cursor.cursor_relation_:
            self.private_cursor._currentregister = self.atFrom()

        self.refreshBuffer()
        # if self.modeAccess() == self.Browse:
        #    self.private_cursor._currentregister = -1
        self.newBuffer.emit()

        return True

    @decorators.pyqt_slot()
    def setSort(self, sort_order: str) -> None:
        """
        Specify the sort order in the tablemodel.

        @param str. new sort order.
        """
        self.private_cursor._model.setSortOrder(sort_order)

    @decorators.pyqt_slot()
    def baseFilter(self) -> str:
        """
        Return the base filter.

        @return base filter.
        """

        relation_filter = None

        if (
            self.private_cursor.cursor_relation_
            and self.private_cursor.relation_
            and self.private_cursor.metadata_
            and self.private_cursor.cursor_relation_.private_cursor.metadata_ is not None
        ):
            relation_value = self.private_cursor.cursor_relation_.valueBuffer(
                self.private_cursor.relation_.foreignField()
            )
            field = self.private_cursor.metadata_.field(self.private_cursor.relation_.field())

            if field is not None and relation_value is not None:

                relation_filter = (
                    self.db().connManager().manager().formatAssignValue(field, relation_value, True)
                )
                filter_assoc = self.private_cursor.cursor_relation_.filterAssoc(
                    self.private_cursor.relation_.foreignField(), self.private_cursor.metadata_
                )
                if filter_assoc:
                    if not relation_filter:
                        relation_filter = filter_assoc
                    else:
                        relation_filter = "%s AND %s" % (relation_filter, filter_assoc)

        final_filter = self.mainFilter() if self.mainFilter() else ""

        if relation_filter:
            if not final_filter:
                final_filter = relation_filter
            else:
                if relation_filter not in final_filter:
                    final_filter = "%s AND %s" % (final_filter, relation_filter)

        # if self.filter():
        #    if final_filter and self.filter() not in final_filter:
        #        final_filter = "%s AND %s" % (final_filter, self.filter())
        #    else:
        #        final_filter = self.filter()

        return final_filter

    @decorators.pyqt_slot()
    def curFilter(self) -> str:
        """
        Return the actual filter.

        @return actual filter.
        """

        filter = self.filter()
        base_filter = self.baseFilter()
        while filter.endswith(";"):
            filter = filter[0 : len(filter) - 1]

        if not base_filter or base_filter in filter:
            return filter
        elif not filter or filter in base_filter:
            return base_filter

        return "%s AND %s" % (base_filter, filter)

    @decorators.pyqt_slot()
    def setFilter(self, final_filter: str = "") -> None:
        """
        Specify the cursor filter.

        @param _filter. Text string with the filter to apply.
        """

        base_filter = self.baseFilter()

        if not final_filter or final_filter in base_filter:
            final_filter = base_filter
        elif base_filter and base_filter not in final_filter:
            final_filter = base_filter + " AND " + final_filter

        if (
            self.private_cursor._persistent_filter
            and self.private_cursor._persistent_filter not in final_filter
        ):
            final_filter += " OR " + self.private_cursor._persistent_filter

        self.private_cursor._model.where_filters["filter"] = final_filter

    @decorators.pyqt_slot()
    def insertRecord(self, wait: bool = True) -> None:
        """
        Open the form record in insert mode.

        @param wait. wait to form record close.
        """

        LOGGER.trace("insertRecord %s", self._action and self._action.name())
        self.openFormInMode(self.Insert, wait)

    @decorators.pyqt_slot()
    def editRecord(self, wait: bool = True) -> None:
        """
        Open the form record in edit mode.

        @param wait. wait to form record close.
        """

        LOGGER.trace("editRecord %s", self.actionName())
        if self.private_cursor.needUpdate():
            if not self.private_cursor.metadata_:
                raise Exception("self.private_cursor.metadata_ is not defined!")

            primary_key = self.private_cursor.metadata_.primaryKey()
            primary_key_value = self.valueBuffer(primary_key)
            self.refresh()
            pos = self.atFromBinarySearch(primary_key, primary_key_value)
            if not pos == self.at():
                self.seek(pos, False, False)

        self.openFormInMode(self.Edit, wait)

    @decorators.pyqt_slot()
    def browseRecord(self, wait: bool = True) -> None:
        """
        Open the form record in browse mode.

        @param wait. wait to form record close.
        """

        LOGGER.trace("browseRecord %s", self.actionName())
        if self.private_cursor.needUpdate():
            if not self.private_cursor.metadata_:
                raise Exception("self.private_cursor.metadata_ is not defined!")
            primary_key = self.private_cursor.metadata_.primaryKey()
            primary_key_value = self.valueBuffer(primary_key)
            self.refresh()
            pos = self.atFromBinarySearch(primary_key, primary_key_value)
            if not pos == self.at():
                self.seek(pos, False, False)
        self.openFormInMode(self.Browse, wait)

    @decorators.pyqt_slot()
    def deleteRecord(self, wait: bool = True) -> None:
        """
        Open the form record in insert mode.Ask for confirmation to delete the record.

        @param wait. wait to record delete to continue.
        """

        LOGGER.trace("deleteRecord %s", self.actionName())
        self.openFormInMode(self.Del, wait)
        # self.private_cursor._action.openDefaultFormRecord(self)

    def copyRecord(self) -> None:
        """
        Perform the action of inserting a new record, and copy the value of the record fields current.
        """

        if not self.private_cursor.metadata_ or not self.private_cursor.buffer_:
            return

        if not self.isValid() or self.size() <= 0:
            self.private_cursor.msgBoxWarning(self.tr("No hay ningún registro seleccionado"))
            return

        field_list = self.private_cursor.metadata_.fieldList()
        if not field_list:
            return

        if self.private_cursor.needUpdate():
            pk_value = self.valueBuffer(self.primaryKey())
            self.refresh()
            pos = self.model().find_pk_row(pk_value)
            if pos != self.at():
                self.seek(pos, False, True)

        old_data = {}
        for item in field_list:
            value = self.buffer().value(item.name())
            if value is None:
                continue
            old_data[item.name()] = value

        self.insertRecord()

        for item in field_list:
            if item.isPrimaryKey() or self.metadata().fieldListOfCompoundKey(item.name()):
                continue

            if item.name() in old_data.keys():
                self.buffer().set_value(item.name(), old_data[item.name()])

        self.newBuffer.emit()

    @decorators.pyqt_slot()
    def chooseRecord(self, wait: bool = True) -> None:
        """
        Perform the action associated with choosing a cursor record.

        By default the form of record edition, calling the PNSqlCursor :: editRecord () method, if the PNSqlCursor :: edition flag
        indicates TRUE, if it indicates FALSE this method does nothing
        """

        if not settings.CONFIG.value("ebcomportamiento/FLTableDoubleClick", False):
            if self.private_cursor.edition_:
                self.editRecord(wait)
            else:
                if self.private_cursor.browse_:
                    self.browseRecord(wait)
        else:
            if self.private_cursor.browse_:
                self.browseRecord(wait)

        self.recordChoosed.emit()

    def setForwardOnly(self, value: bool) -> None:
        """
        Avoid refreshing the associated model.
        """

        if not self.private_cursor._model:
            return

        self.private_cursor._model.disable_refresh(value)

    @decorators.pyqt_slot()
    def commitBuffer(self, emite: bool = True, check_locks: bool = False) -> bool:
        """
        Send the contents of the buffer to the cursor, or perform the appropriate action for the cursor.

        All changes made to the buffer become effective at the cursor when invoking this method.
        The way to make these changes is determined by the access mode established for
        the cursor, see FLSqlCursor :: Mode, if the mode is edit or insert update with the new value of
        the fields of the record, if the mode is delete deletes the record, and if the mode is navigation it does nothing.
        First of all it also checks referential integrity by invoking the FLSqlCursor :: checkIntegrity () method.

        If a calculated field exists, the "calculateField" function of the script of the
        context (see FLSqlCursor :: ctxt_) set for the cursor. This function is passed
        as an argument the name of the calculated field and must return the value it must contain
        that field, e.g. if the field is the total of an invoice and of type calculated the function
        "calculateField" must return the sum of lines of invoices plus / minus taxes and
        discounts

        @param issues True to emit cursorUpdated signal
        @param check_locks True to check block risks for this table and the current record
        @return TRUE if the buffer could be delivered to the cursor, and FALSE if the delivery failed
        """

        if not self.private_cursor.buffer_ or not self.private_cursor.metadata_:
            LOGGER.warning(
                "CommitBuffer cancelado. No hay buffer o metadata. buffer:%s, metadata:%s",
                self.private_cursor.buffer_,
                self.private_cursor.metadata_,
            )
            return False

        commit_buffer_session = self.db().session()

        if not self.checkIntegrity():
            LOGGER.warning("CommitBuffer cancelado. Problema de integridad.")
            return False

        field_name_check = None
        function_before_commit = (
            "beforeCommit_%s" % self.table() if self.activatedCommitActions() else ""
        )
        function_after_commit = (
            "afterCommit_%s" % self.table() if self.activatedCommitActions() else ""
        )
        function_record_del_after = "recordDelAfter%s" % self.table()
        function_record_del_before = "recordDelBefore%s" % self.table()

        script_record_iface = None
        pn_action = self.action()
        if pn_action is not None:
            if pn_action.name() in application.PROJECT.actions.keys():
                action_ = application.PROJECT.actions[pn_action.name()]
                if action_ is not None:
                    script_record = action_.load_record_widget()
                    script_record_iface = getattr(script_record, "iface", None)
        if self.modeAccess() in [self.Edit, self.Insert]:
            field_list = self.metadata().fieldList()

            for field in field_list:
                if field.isCheck():
                    field_name_check = field.name()
                    self.buffer().set_generated(field.name(), False)

                    if self.private_cursor._buffer_copy:
                        self.private_cursor._buffer_copy.set_generated(field.name(), False)
                    continue

                # if not self.private_cursor.buffer_.isGenerated(field.name()):
                #    continue

                if field.calculated():
                    func_ = getattr(script_record_iface, "calculateField", None)
                    if func_ is not None:
                        value = func_(field.name())

                        if value not in (True, False, None):
                            self.setValueBuffer(field.name(), value)

        id_module = self.db().connManager().managerModules().idModuleOfFile("%s.mtd" % self.table())
        # FIXME: module_script is FLFormDB
        action = application.PROJECT.actions[
            id_module if id_module in application.PROJECT.actions.keys() else "sys"
        ]

        module_script = action.load_master_widget()

        module_iface: Any = getattr(module_script, "iface", None)
        if self.modeAccess() != PNSqlCursor.Browse and function_before_commit:
            # BEFORE_COMMIT
            func_ = getattr(module_iface, function_before_commit, None)
            if func_ is not None:
                value = func_(self)
                if value and not isinstance(value, bool) or value is False:
                    LOGGER.warning(
                        "CommitBuffer cancelado. %s devolvió False.", function_before_commit
                    )
                    return False

        # primary_key = self.private_cursor.metadata_.primaryKey()
        updated = 0
        use_nested = False
        # savePoint = None

        if not self.transactionLevel():

            self.db().transaction()
            if application.SHOW_NESTED_WARNING:
                LOGGER.warning(
                    "NESTED STARTED: %s, SESSION : %s, PARENT : %s, CURRENT : %s,",
                    self.curName().upper(),
                    commit_buffer_session,
                    commit_buffer_session.transaction.parent,
                    commit_buffer_session.transaction,
                )
            use_nested = True

        if self.modeAccess() == self.Insert:
            if self.private_cursor.cursor_relation_ and self.private_cursor.relation_:
                if (
                    self.private_cursor.cursor_relation_.metadata()
                    and self.private_cursor.cursor_relation_.valueBuffer(
                        self.private_cursor.relation_.foreignField()
                    )
                ):
                    self.setValueBuffer(
                        self.private_cursor.relation_.field(),
                        self.private_cursor.cursor_relation_.valueBuffer(
                            self.private_cursor.relation_.foreignField()
                        ),
                    )
                    self.private_cursor.cursor_relation_.setAskForCancelChanges(True)

            if not self.buffer().apply_buffer():
                LOGGER.warning(
                    "CommitBuffer en Insert cancelado. Fallo al aplicar el buffer al objeto"
                )
                return False

            if not self.model().insert_current_buffer():
                LOGGER.warning(
                    "CommitBuffer cancelado. model().insert_current_buffer() devolvió False."
                )
                return False

            updated = 1

        elif self.modeAccess() == self.Edit:
            database = self.db()
            if database is None:
                raise Exception("db is not defined!")

            if self.private_cursor.cursor_relation_ and self.private_cursor.relation_:
                if self.private_cursor.cursor_relation_.metadata():
                    self.private_cursor.cursor_relation_.setAskForCancelChanges(True)

            if self.isModifiedBuffer():

                if not self.buffer().apply_buffer():
                    LOGGER.warning(
                        "CommitBuffer en Edit cancelado. Fallo al aplicar el buffer al objeto"
                    )
                    return False

                if not self.update(False):
                    LOGGER.warning("CommitBuffer cancelado. no se ha podido hacer update.")
                    return False

                self.setNotGenerateds()

            updated = 2

        elif self.modeAccess() == self.Del:

            if self.private_cursor.cursor_relation_ and self.private_cursor.relation_:
                if self.private_cursor.cursor_relation_.metadata():
                    self.private_cursor.cursor_relation_.setAskForCancelChanges(True)

            # RECORD_DEL_BEFORE

            func_ = getattr(script_record_iface, function_record_del_before, None)
            if func_ is not None:
                value = func_(self)

                if value and not isinstance(value, bool) or value is False:
                    LOGGER.info(
                        "CommitBuffer cancelado. %s devolvió False.", function_record_del_before
                    )
                    return False

            if not self.buffer().apply_buffer():
                LOGGER.warning(
                    "CommitBuffer en Delete cancelado. Fallo al aplicar el buffer al objeto"
                )
                return False

            # if not self.private_cursor.buffer_:

            #    self.buffer().prime_delete()

            field_list = self.metadata().fieldList()

            for field in field_list:

                field_name = field.name()

                if self.isNull(field_name):
                    continue

                result = self.private_cursor.buffer_.value(  # type: ignore [union-attr] # noqa: F821
                    field_name
                )

                for relation in field.relationList():

                    cursor = PNSqlCursor(relation.foreignTable())
                    foreign_mtd = cursor.private_cursor.metadata_
                    if foreign_mtd is None:
                        continue
                    foreign_field = foreign_mtd.field(relation.foreignField())
                    if foreign_field is None:
                        continue

                    relation_m1 = foreign_field.relationM1()

                    if relation_m1 and relation_m1.deleteCascade():
                        cursor.setForwardOnly(True)
                        cursor.select(
                            self.conn()
                            .connManager()
                            .manager()
                            .formatAssignValue(relation.foreignField(), foreign_field, result, True)
                        )

                        while cursor.next():
                            cursor.setModeAccess(self.Del)
                            cursor.refreshBuffer()
                            if not cursor.commitBuffer(False):
                                LOGGER.warning("CommitBuffer cancelado. delC devolvió False.")
                                return False

            if not self.model().delete_current_buffer():
                LOGGER.warning(
                    "CommitBuffer cancelado. model().insert_current_buffer() devolvió False."
                )
                return False

            if function_record_del_after:
                # RECORD DEL AFTER!!

                func_ = getattr(script_record_iface, function_record_del_after, None)
                if func_ is not None:
                    value = func_(self)

                    if value and not isinstance(value, bool) or value is False:
                        LOGGER.warning(
                            "CommitBuffer cancelado. %s devolvió False.", function_record_del_after
                        )
                        return False

            updated = 3

        if updated and self.lastError():
            LOGGER.warning("CommitBuffer cancelado. Error encontrado: %s.", self.lastError())
            return False

        if self.modeAccess() != self.Browse and function_after_commit:
            # AFTER_COMMIT
            func_ = getattr(module_iface, function_after_commit, None)

            if func_ is not None:
                value = func_(self)
                if value and not isinstance(value, bool) or value is False:
                    LOGGER.warning(
                        "CommitBuffer cancelado. %s devolvió False.", function_after_commit
                    )
                    return False

        if self.modeAccess() in (self.Del, self.Edit):
            self.setModeAccess(self.Browse)

        elif self.modeAccess() == self.Insert:
            self.setModeAccess(self.Edit)

        if updated or use_nested:
            # Para cuando usamos npsqlcursors solos!
            if use_nested:
                pk_value = self.buffer().value(self.primaryKey())
                if not self.commit():
                    LOGGER.warning(
                        "CommitBuffer cancelado. db().commitTransaction devolvió False.",
                        stack_info=True,
                    )
                    self.db().rollback()
                    return False

                if self.metadata().isQuery():
                    self.model().refresh()
                elif not self.model().updateCacheData(updated):
                    if self.size():
                        LOGGER.warning("update_cache_failed. Using classic method")

                    self.model().refresh()

                pk_row = self.model().find_pk_row(pk_value)

                if pk_row > -1:
                    self.move(pk_row)
                    self.refreshBuffer()

                if application.SHOW_NESTED_WARNING:
                    LOGGER.warning(
                        "ENDING NESTED : %s, SESSION : %s, PARENT : %s, CURRENT : %s,",
                        self.curName().upper(),
                        commit_buffer_session,
                        commit_buffer_session.transaction.parent,
                        commit_buffer_session.transaction,
                    )
                self.db().commit()

                if application.SHOW_NESTED_WARNING:
                    LOGGER.warning(
                        "RESULT NESTED : %s, CURRENT : %s",
                        self.curName().upper(),
                        commit_buffer_session.transaction,
                    )

            # if self.transactionLevel() == 0:
            #    self.db().commit()

            if field_name_check and self.private_cursor.buffer_:
                self.private_cursor.buffer_.set_generated(field_name_check, True)

                if self.private_cursor._buffer_copy:
                    self.private_cursor._buffer_copy.set_generated(field_name_check, True)

            self.setFilter("")
            # self.clearMapCalcFields()

            if emite:
                self.cursorUpdated.emit()

        self.bufferCommited.emit()
        return True

    @decorators.pyqt_slot()
    def commitBufferCursorRelation(self) -> bool:
        """
        Send the contents of the cursor buffer related to that cursor.

        It makes all changes in the related cursor buffer effective by placing itself in the registry corresponding receiving changes.
        """

        result = True
        active_widget_enabled = False
        active_widget = None

        cursor_relation = self.private_cursor.cursor_relation_

        if cursor_relation is None or self.relation() is None:
            return result

        if application.PROJECT.DGI.localDesktop():

            active_widget = QtWidgets.QApplication.activeModalWidget()
            if not active_widget:
                active_widget = QtWidgets.QApplication.activePopupWidget()
                if not active_widget:
                    active_widget = QtWidgets.QApplication.activeWindow()

            if active_widget:
                active_widget_enabled = active_widget.isEnabled()

        if self.private_cursor.mode_access_ in [self.Browse, self.Edit, self.Insert]:
            if (
                cursor_relation.private_cursor.metadata_ is not None
                and cursor_relation.modeAccess() == self.Insert
            ):
                if active_widget and active_widget_enabled:
                    active_widget.setEnabled(False)

                if not cursor_relation.commitBuffer():
                    self.private_cursor.mode_access_ = self.Browse
                    result = False
                else:
                    if self.private_cursor.mode_access_ == self.Insert:
                        self.setFilter("")
                    cursor_relation.refresh()
                    cursor_relation.setModeAccess(self.Edit)
                    cursor_relation.refreshBuffer()

                if active_widget and active_widget_enabled:
                    active_widget.setEnabled(True)

        return result

    @decorators.pyqt_slot()
    def transactionLevel(self) -> int:
        """
        Transaction level.

        @return The current level of transaction nesting, 0 there is no transaction.
        """

        return self.db().transactionLevel()

    @decorators.pyqt_slot()
    def transactionsOpened(self) -> List[str]:
        """
        Transactions opened by this cursor.

        @return The list with the levels of transactions that this cursor has initiated and remain open
        """
        return [str(item) for item in self.private_cursor._transactions_opened]

    @decorators.pyqt_slot()
    @decorators.beta_implementation
    def rollbackOpened(self, count: int = -1, message: str = "") -> None:
        """
        Undo transactions opened by this cursor.

        @param count Number of transactions to be undone, -1 all.
        @param msg Text string that is displayed in a dialog box before undoing transactions. If it is empty it shows nothing.
        """

        count = len(self.private_cursor._transactions_opened) if count < 0 else count
        if count > 0:
            if message != "":
                table_name: str = self.table() if self.private_cursor.metadata_ else self.curName()
                message = "%sSqlCursor::rollbackOpened: %s %s" % (message, count, table_name)
                self.private_cursor.msgBoxWarning(message, False)
            else:
                LOGGER.trace("rollbackOpened: %s %s", count, self.curName())

            self.rollback()

    @decorators.pyqt_slot()
    def commitOpened(self, count: int = -1, message: str = None) -> None:
        """
        Complete transactions opened by this cursor.

        @param count Number of transactions to finish, -1 all.
        @param msg A text string that is displayed in a dialog box before completing transactions. If it is empty it shows nothing.
        """
        count = len(self.private_cursor._transactions_opened) if count < 0 else count
        table_name: str = self.table() if self.private_cursor.metadata_ else self.curName()

        if count and message:
            message = "%sSqlCursor::commitOpened: %s %s" % (message, str(count), table_name)
            self.private_cursor.msgBoxWarning(message, False)
            LOGGER.warning(message)
        elif count > 0:
            LOGGER.warning("SqlCursor::commitOpened: %d %s" % (count, self.curName()))

        i = 0
        while i < count:
            LOGGER.warning("Terminando transacción abierta %s", self.transactionLevel())
            self.commit()
            i = i + 1

    @decorators.pyqt_slot()
    @decorators.not_implemented_warn
    def checkRisksLocks(self, terminate: bool = False) -> bool:
        """
        Enter a lockout risk loop for this table and the current record.

        The loop continues as long as there are locks, until this method is called again with 'terminate'
        activated or when the user cancels the operation.

        @param terminate True will end the check loop if it is active
        """

        return True

    @decorators.pyqt_slot()
    def setAcTable(self, acos) -> None:
        """
        Set the global access for the table, see FLSqlCursor :: setAcosCondition ().

        This will be the permission to apply to all default fields.

        @param ac Global permission; eg: "r-", "-w"
        """

        self.private_cursor._id_ac += 1
        self.private_cursor.id_ = "%s%s%s" % (
            self.private_cursor._id_ac,
            self.private_cursor._id_acos,
            self.private_cursor._id_cond,
        )
        self.private_cursor._ac_perm_table = acos

    @decorators.pyqt_slot()
    def setAcosTable(self, acos):
        """
        Set the access control list (ACOs) for the fields in the table, see FLSqlCursor :: setAcosCondition ().

        This list of texts should have in their order components the names of the fields,
        and in the odd order components the permission to apply to that field,
        eg: "name", "r-", "description", "-", "telephone", "rw", ...

        The permissions defined here overwrite the global.

        @param acos List of text strings with the names of fields and permissions.
        """

        self.private_cursor._id_acos += 1
        self.private_cursor.id_ = "%s%s%s" % (
            self.private_cursor._id_ac,
            self.private_cursor._id_acos,
            self.private_cursor._id_cond,
        )
        self.private_cursor._acos_table = acos

    @decorators.pyqt_slot()
    def setAcosCondition(self, condition_name: str, condition: int, condition_value: Any):
        """
        Set the condition that must be met to apply access control.

        For each record this condition is evaluated and if it is met, the rule applies
        of access control set with FLSqlCursor :: setAcTable and FLSqlCursor :: setAcosTable.

        setAcosCondition ("name", VALUE, "pepe"); // valueBuffer ("name") == "pepe"
        setAcosCondition ("name", REGEXP, "pe *"); // QRegExp ("pe *") .exactMatch (valueBuffer ("name") .toString ())
        setAcosCondition ("sys.checkAcos", FUNCTION, true); // call ("sys.checkAcos") == true



        @param condition Type of evaluation;
                    VALUE compares with a fixed value
                    REGEXP compares with a regular expression
                    FUNCTION compares with the value returned by a script function

        @param condition_name If it is empty, the condition is not evaluated and the rule is never applied.
                    For VALUE and REGEXP name of a field.
                    For FUNCTION name of a script function. The function is passed as
                    argument the cursor object.

        @param condition_value Value that makes the condition true
        """

        self.private_cursor._id_cond += 1
        self.private_cursor.id_ = "%s%s%s" % (
            self.private_cursor._id_ac,
            self.private_cursor._id_acos,
            self.private_cursor._id_cond,
        )
        self.private_cursor._acos_cond_name = condition_name
        self.private_cursor._acos_cond = condition
        self.private_cursor._acos_cond_value = condition_value

    @decorators.pyqt_slot()
    @decorators.not_implemented_warn
    def concurrencyFields(self) -> List[str]:
        """
        Check if there is a collision of fields edited by two sessions simultaneously.

        @return List with the names of the colliding fields
        """

        return []

    @decorators.pyqt_slot()
    def changeConnection(self, conn_name: str) -> None:
        """
        Change the cursor to another database connection.

        @param conn_name. connection name.
        """

        cur_conn_name = self.connectionName()
        if cur_conn_name == conn_name:
            return

        new_database = application.PROJECT.conn_manager.database(conn_name)
        if cur_conn_name == new_database.connectionName():
            return

        if self.private_cursor._transactions_opened:
            metadata = self.private_cursor.metadata_
            table_name = metadata.name() if metadata else self.curName()

            message = (
                "Se han detectado transacciones no finalizadas en la última operación.\n"
                "Se van a cancelar las transacciones pendientes.\n"
                "Los últimos datos introducidos no han sido guardados, por favor\n"
                "revise sus últimas acciones y repita las operaciones que no\n"
                "se han guardado.\n" + "SqlCursor::changeConnection: %s\n" % table_name
            )
            self.rollbackOpened(-1, message)

        buffer_backup = None
        if self.private_cursor.buffer_:
            buffer_backup = self.buffer()
            self.private_cursor.buffer_ = None

        self.private_cursor.db_ = new_database
        self.init(self.private_cursor.cursor_name_, True, self.cursorRelation(), self.relation())

        if buffer_backup:
            self.private_cursor.buffer_ = buffer_backup

        self.connectionChanged.emit()

    @decorators.not_implemented_warn
    def populateCursor(self) -> None:
        """
        If the cursor comes from a query, perform the process of adding the deficit from the fields to it.
        """
        return

    def setNotGenerateds(self) -> None:
        """
        Mark as no generated.

        When the cursor comes from a query, it performs the process that marks as
        not generated (the fields of the buffer are not taken into account in INSERT, EDIT, DEL)
        that do not belong to the main table.
        """

        if (
            self.private_cursor.metadata_
            and self.private_cursor._is_query
            and self.private_cursor.buffer_
        ):
            for field in self.metadata().fieldList():
                self.private_cursor.buffer_.set_generated(field.name(), False)

    def sort(self) -> str:
        """
        Choose the order of the main columns.

        @return sort order.
        """

        return self.private_cursor._model.getSortOrder()

    def filter(self) -> str:
        """
        Return the cursor filter.

        @return current filter.
        """

        return (
            self.private_cursor._model.where_filters["filter"]
            if "filter" in self.private_cursor._model.where_filters
            else ""
        )

    def update(self, notify: bool = True) -> bool:
        """
        Update tableModel with the buffer.

        @param notify. emit bufferCommited signal after update if True else None.
        """

        LOGGER.trace("PNSqlCursor.update --- BEGIN:")
        update_successful = False
        if self.modeAccess() == PNSqlCursor.Edit:

            if not self.private_cursor.buffer_:
                raise Exception("Buffer is not set. Cannot update")

            self.db().session().flush()
            update_successful = True

            if notify:
                self.bufferCommited.emit()

        LOGGER.trace("PNSqlCursor.update --- END")
        return update_successful

    def lastError(self) -> str:
        """
        Return the last error reported by the database connection.

        @return last error reported.
        """

        return self.db().lastError()

    def __iter__(self) -> "PNSqlCursor":
        """
        Make the cursor iterable.
        """

        self._iter_current = None
        return self

    def __next__(self) -> str:
        """
        Make the cursor iterable.

        @return function name.
        """
        self._iter_current = 0 if self._iter_current is None else self._iter_current + 1

        list_ = [attr for attr in dir(self) if not attr[0] == "_"]
        if self._iter_current >= len(list_):
            raise StopIteration

        return list_[self._iter_current]

    def primaryKey(self) -> str:
        """
        Return the primary cursor key.

        @return primary key field name.
        """

        return self.private_cursor.metadata_.primaryKey() if self.private_cursor.metadata_ else ""

    def fieldType(self, field_name: str = None) -> Optional[int]:
        """
        Return the field type.

        @param field_name. Specify the field to return type.
        @return int identifier.
        """

        return (
            self.private_cursor.metadata_.fieldType(field_name)
            if field_name and self.private_cursor.metadata_
            else None
        )

    """
    private slots:
    """

    """ Uso interno """
    # clearPersistentFilter = QtCore.pyqtSignal()

    # destroyed = QtCore.pyqtSignal()

    @decorators.pyqt_slot()
    def clearPersistentFilter(self):
        """
        Clear persistent filters.
        """

        self.private_cursor._persistent_filter = None

    def id(self) -> str:
        """
        Return cursor identifier.
        """

        return self.private_cursor.id_


class PNCursorPrivate(isqlcursor.ICursorPrivate):
    """PNCursorPrivate class."""

    def __init__(
        self, cursor_: "PNSqlCursor", action_name: str, db_: "iconnection.IConnection"
    ) -> None:
        """
        Initialize the private part of the cursor.
        """

        super().__init__(cursor_, action_name, db_)
        self.metadata_ = None
        self._count_ref_cursor = 0
        self._currentregister = -1
        self._acos_cond_name = None
        self.buffer_ = None
        self._buffer_copy = None
        self.edition_states_ = pnboolflagstate.PNBoolFlagStateList()
        self.browse_states_ = pnboolflagstate.PNBoolFlagStateList()
        self._activated_check_integrity = True
        self._activated_commit_actions = True
        self._ask_for_cancel_changes = True
        self._in_risks_locks = False
        self.populated_ = False
        self._transactions_opened = []
        self._id_ac = 0
        self._id_acos = 0
        self._id_cond = 0
        self.cursor_name_ = action_name
        self._acl_done = False
        self.edition_ = True
        self.browse_ = True
        self.cursor_ = cursor_
        self.cursor_relation_ = None
        self.relation_ = None
        # self.acl_table_ = None
        self.timer_ = None
        self.ctxt_ = None
        # self.rawValues_ = False
        self._persistent_filter = None
        self.db_ = db_

        self._id_acl = ""
        # self.nameCursor = "%s_%s" % (
        #    act_.name(),
        #    QtCore.QDateTime.currentDateTime().toString("dd.MM.yyyyThh:mm:ss.zzz"),
        # )

    def __del__(self) -> None:
        """
        Delete instance values.
        """

        if self.metadata_:
            self.undoAcl()

            if self._id_acl in self.acl_table_.keys():
                del self.acl_table_[self._id_acl]
                # self.acl_table_ = None

        del self._buffer_copy
        self._buffer_copy = None

        del self.relation_
        self.relation_ = None

        del self.edition_states_
        self.edition_states_ = pnboolflagstate.PNBoolFlagStateList()

        del self.browse_states_
        self.browse_states_ = pnboolflagstate.PNBoolFlagStateList()

        del self._transactions_opened
        self._transactions_opened = []

    def doAcl(self) -> None:
        """
        Create restrictions according to access control list.
        """

        if self.metadata_ is None:
            return

        if not self._id_acl:
            self._id_acl = "%s_%s" % (application.PROJECT.session_id(), self.metadata_.name())
        if self._id_acl not in self.acl_table_.keys():
            self.acl_table_[self._id_acl] = pnaccesscontrolfactory.PNAccessControlFactory().create(
                "table"
            )
            self.acl_table_[self._id_acl].setFromObject(self.metadata_)
            self._acos_backup_table[self._id_acl] = self.acl_table_[self._id_acl].getAcos()
            self._acos_permanent_backup_table[self._id_acl] = self.acl_table_[self._id_acl].perm()
            self.acl_table_[self._id_acl].clear()
        if self.cursor_ is None:
            raise Exception("Cursor not created yet")
        if self.mode_access_ == PNSqlCursor.Insert or (
            not self._last_at == -1 and self._last_at == self.cursor_.at()
        ):
            return

        if self._acos_cond_name is not None:
            condition_true = False

            if self._acos_cond == self.cursor_.Value:

                condition_true = (
                    self.cursor_.valueBuffer(self._acos_cond_name) == self._acos_cond_value
                )

            elif self._acos_cond == self.cursor_.RegExp:
                # condition_true = QtCore.QRegularExpression(str(self._acos_cond_value)).exactMatch(
                #    self.cursor_.valueBuffer(self._acos_cond_name)
                # )
                condition_true = str(self._acos_cond_value) == self.cursor_.valueBuffer(
                    self._acos_cond_name
                )
            elif self._acos_cond == self.cursor_.Function:
                condition_true = (
                    application.PROJECT.call(self._acos_cond_name, [self.cursor_])
                    == self._acos_cond_value
                )

            if condition_true:
                if self.acl_table_[self._id_acl].name() != self.id_:
                    self.acl_table_[self._id_acl].clear()
                    self.acl_table_[self._id_acl].setName(self.id_)
                    self.acl_table_[self._id_acl].setPerm(self._ac_perm_table)
                    self.acl_table_[self._id_acl].setAcos(self._acos_table)
                    self.acl_table_[self._id_acl].processObject(self.metadata_)
                    self._acl_done = True

                return

        elif self.cursor_.isLocked() or (
            self.cursor_relation_ and self.cursor_relation_.isLocked()
        ):

            if not self.acl_table_[self._id_acl].name() == self.id_:
                self.acl_table_[self._id_acl].clear()
                self.acl_table_[self._id_acl].setName(self.id_)
                self.acl_table_[self._id_acl].setPerm("r-")
                self.acl_table_[self._id_acl].processObject(self.metadata_)
                self._acl_done = True

            return

        self.undoAcl()

    def undoAcl(self) -> None:
        """
        Delete restrictions according to access control list.
        """
        if self.metadata_ is None or not self._id_acl:
            return

        if self._id_acl in self.acl_table_.keys():
            self._acl_done = False
            self.acl_table_[self._id_acl].clear()
            self.acl_table_[self._id_acl].setPerm(self._acos_permanent_backup_table[self._id_acl])
            self.acl_table_[self._id_acl].setAcos(self._acos_backup_table[self._id_acl])
            self.acl_table_[self._id_acl].processObject(self.metadata_)

    def needUpdate(self) -> bool:
        """
        Indicate if the cursor needs to be updated.

        @return True or False.
        """

        if self._is_query:
            return False

        need = self._model.need_update
        return need

    def msgBoxWarning(self, msg: str, throwException: bool = False) -> None:
        """
        Error message associated with the DGI.

        @param msg.Error message.
        @param throwException. No used.
        """

        application.PROJECT.message_manager().send("msgBoxWarning", None, [msg])
