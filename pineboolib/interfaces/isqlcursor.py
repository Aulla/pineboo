"""
ISqlCursor module.
"""

from PyQt6 import QtCore  # type: ignore[import]


from pineboolib.interfaces import cursoraccessmode


from typing import Any, Optional, Dict, List, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.application.acls import pnboolflagstate  # noqa: F401 # pragma: no cover
    from pineboolib.application.database import (  # noqa : F401
        pnbuffer,  # noqa: F401
        pncursortablemodel,  # noqa: F401
    )  # noqa: F401 # pragma: no cover
    from pineboolib.application.metadata import (  # noqa : F401 # pragma: no cover
        pntablemetadata,
        pnrelationmetadata,
        pnaction,
    )
    from pineboolib.interfaces import iconnection  # pragma: no cover
    import sqlalchemy  # type: ignore [import] # noqa: F821 # pragma: no cover


class ICursorPrivate(QtCore.QObject):
    """ICursorPrivate class."""

    """
    Buffer with a cursor record.

    According to the FLSqlCursor :: Mode access mode set for the cusor, this buffer will contain
    the active record of said cursor ready to insert, edit, delete or navigate.
    """

    buffer_: Optional["pnbuffer.PNBuffer"] = None

    """
    Copia del buffer.

    Aqui se guarda una copia del FLSqlCursor::buffer_ actual mediante el metodo FLSqlCursor::updateBufferCopy().
    """
    _buffer_copy: Optional["pnbuffer.PNBuffer"] = None

    """
    Metadatos de la tabla asociada al cursor.
    """
    metadata_: Optional["pntablemetadata.PNTableMetaData"]

    """
    Mantiene el modo de acceso actual del cursor, ver FLSqlCursor::Mode.
    """
    mode_access_ = -1

    """
    Cursor relacionado con este.
    """
    cursor_relation_: Optional["ISqlCursor"]

    """
    Relación que determina como se relaciona con el cursor relacionado.
    """
    relation_: Optional["pnrelationmetadata.PNRelationMetaData"]

    """
    Esta bandera cuando es TRUE indica que se abra el formulario de edición de regitros en
    modo edición, y cuando es FALSE se consulta la bandera FLSqlCursor::browse. Por defecto esta
    bandera está a TRUE
    """
    edition_: bool

    """
    Esta bandera cuando es TRUE y la bandera FLSqlCuror::edition es FALSE, indica que se
    abra el formulario de edición de registro en modo visualización, y cuando es FALSE no hace
    nada. Por defecto esta bandera está a TRUE
    """
    browse_: bool
    browse_states_: "pnboolflagstate.PNBoolFlagStateList"

    """
    Filtro principal para el cursor.

    Este filtro persiste y se aplica al cursor durante toda su existencia,
    los filtros posteriores, siempre se ejecutaran unidos con 'AND' a este.
    """
    # self.d._model.where_filters["main-filter"] = None

    """
    Accion asociada al cursor, esta accion pasa a ser propiedad de FLSqlCursor, que será el
    encargado de destruirla
    """
    action_: "pnaction.PNAction"

    """
    Cuando esta propiedad es TRUE siempre se pregunta al usuario si quiere cancelar
    cambios al editar un registro del cursor.
    """
    _ask_for_cancel_changes: bool

    """
    Indica si estan o no activos los chequeos de integridad referencial
    """
    _activated_check_integrity: bool

    """
    Indica si estan o no activas las acciones a realiar antes y después del Commit
    """
    _activated_commit_actions: bool

    """
    Contexto de ejecución de scripts.

    El contexto de ejecución será un objeto formulario el cual tiene asociado un script.
    Ese objeto formulario corresponde a aquel cuyo origen de datos es este cursor.
    El contexto de ejecución es automáticamente establecido por las clases FLFormXXXX.
    """
    ctxt_: Any

    """
    Cronómetro interno
    """
    timer_: Optional[QtCore.QTimer]

    """
    Cuando el cursor proviene de una consulta indica si ya se han agregado al mismo
    la definición de los campos que lo componen
    """
    populated_: bool

    """
    Cuando el cursor proviene de una consulta contiene la sentencia sql
    """
    _is_query: bool

    """
    Cuando el cursor proviene de una consulta contiene la clausula order by
    """
    _query_order_by: str

    """
    Base de datos sobre la que trabaja
    """
    db_: Optional["iconnection.IConnection"]

    """
    Pila de los niveles de transacción que han sido iniciados por este cursor
    """
    _transactions_opened: List[int]

    """
    Filtro persistente para incluir en el cursor los registros recientemente insertados aunque estos no
    cumplan los filtros principales. Esto es necesario para que dichos registros sean válidos dentro del
    cursor y así poder posicionarse sobre ellos durante los posibles refrescos que puedan producirse en
    el proceso de inserción. Este filtro se agrega a los filtros principales mediante el operador OR.
    """
    _persistent_filter: Optional[str]

    """
    Cursor propietario
    """
    cursor_: Optional["ISqlCursor"]

    """
    Nombre del cursor
    """
    cursor_name_: str

    """
    Orden actual
    """
    sort_: str
    """
    Auxiliares para la comprobacion de riesgos de bloqueos
    """
    _in_loop_risk_locks: bool
    _in_risks_locks: bool

    """
    Para el control de acceso dinámico en función del contenido de los registros
    """

    acl_table_: Dict[str, Any] = {}
    _ac_perm_table = None
    _acos_permanent_backup_table: Dict[str, str] = {}
    _acos_table: List[str] = []
    _acos_backup_table: Dict[str, str] = {}
    _acos_cond_name: Optional[str] = None
    _acos_cond: int
    _acos_cond_value = None
    _last_at = None
    _acl_done = False
    _id_ac = 0
    _id_acos = 0
    _id_cond = 0
    id_ = "000"

    """ Uso interno """
    _is_system_table: bool
    # rawValues_: bool

    _md5_tuples: str

    _count_ref_cursor: int

    _model: "pncursortablemodel.PNCursorTableModel"

    edition_states_: "pnboolflagstate.PNBoolFlagStateList"
    _current_changed = QtCore.pyqtSignal(int)
    _id_acl: str

    _currentregister: int

    def __init__(
        self, cursor_: "ISqlCursor", action_name: str, db_: "iconnection.IConnection"
    ) -> None:
        """
        Initialize the private part of the cursor.
        """

        super().__init__()

    def __del__(self) -> None:
        """
        Delete instance values.
        """

        pass  # pragma: no cover

    def msgBoxWarning(self, msg: str, throw_exception: bool = False) -> None:
        """Return msgbox if an error exists."""

        pass  # pragma: no cover

    def needUpdate(self) -> bool:
        """Indicate if the cursor needs to be updated."""

        pass  # pragma: no cover

    def undoAcl(self) -> None:
        """Delete restrictions according to access control list."""

        pass  # pragma: no cover

    def doAcl(self) -> None:
        """Create restrictions according to access control list."""

        pass  # pragma: no cover


class ISqlCursor(QtCore.QObject):
    """
    Abstract class for PNSqlCursor.
    """

    """
    signals:
    """

    """
    Indica que se ha cargado un nuevo buffer
    """
    newBuffer = QtCore.pyqtSignal()

    """
    Indica ha cambiado un campo del buffer, junto con la señal se envía el nombre del campo que
    ha cambiado.
    """
    bufferChanged = QtCore.pyqtSignal(str)

    """
    Indica que se ha actualizado el cursor
    """
    cursorUpdated = QtCore.pyqtSignal()

    """
    Indica que se ha elegido un registro, mediante doble clic sobre él o bien pulsando la tecla Enter
    """
    recordChoosed = QtCore.pyqtSignal()

    """
    Indica que la posicion del registro activo dentro del cursor ha cambiado
    """
    currentChanged = QtCore.pyqtSignal(int)

    """
    Indica que se ha realizado un commit automático para evitar bloqueos
    """
    autoCommit = QtCore.pyqtSignal()

    """
    Indica que se ha realizado un commitBuffer
    """
    bufferCommited = QtCore.pyqtSignal()

    """
    Indica que se ha cambiado la conexión de base de datos del cursor. Ver changeConnection
    """
    connectionChanged = QtCore.pyqtSignal()

    """
    Indica que se ha realizado un commit
    """
    commited = QtCore.pyqtSignal()

    Insert = cursoraccessmode.CursorAccessMode.Insert
    Edit = cursoraccessmode.CursorAccessMode.Edit
    Del = cursoraccessmode.CursorAccessMode.Del
    Browse = cursoraccessmode.CursorAccessMode.Browse
    Value = 0
    RegExp = 1
    Function = 2

    private_cursor: "ICursorPrivate"

    _selection: Optional[QtCore.QItemSelectionModel] = None

    _iter_current: Optional[int]

    _action: Optional["pnaction.PNAction"] = None

    _name: str

    transactionBegin: QtCore.pyqtSignal = QtCore.pyqtSignal()
    transactionEnd: QtCore.pyqtSignal = QtCore.pyqtSignal()
    transactionRollback: QtCore.pyqtSignal = QtCore.pyqtSignal()

    _cursor_model: "sqlalchemy.ext.declarative.api.DeclarativeMeta"

    def __init__(
        self,
        name: Optional[str] = None,
        conn_or_autopopulate: Union[bool, str] = True,
        connection_name_or_db: Union[str, "iconnection.IConnection"] = "default",
        cursor_relation: Optional["ISqlCursor"] = None,
        relation: Optional["pnrelationmetadata.PNRelationMetaData"] = None,
        parent=None,
    ) -> None:
        """Create cursor."""
        super().__init__()

    def init(self, name: str, autopopulate, cusor_relation, relation) -> None:
        """Initialize cursor."""
        pass  # pragma: no cover

    def conn(self) -> "iconnection.IConnection":
        """Retrieve connection object."""
        pass  # pragma: no cover

    def table(self) -> str:
        """Retrieve table name."""
        return ""  # pragma: no cover

    def setName(self, name, autop) -> None:
        """Set cursor name."""
        pass  # pragma: no cover

    def metadata(self) -> "pntablemetadata.PNTableMetaData":
        """Get table metadata for this cursor table."""
        pass  # pragma: no cover

    def currentRegister(self) -> int:
        """Get current row number."""
        pass  # pragma: no cover

    def modeAccess(self) -> int:
        """Get current access mode."""
        pass  # pragma: no cover

    def filter(self) -> str:
        """Get SQL filter as a string."""
        return ""

    def mainFilter(self) -> str:
        """Get SQL Main filter as a string."""
        pass  # pragma: no cover

    def action(self) -> Optional["pnaction.PNAction"]:
        """Get action object."""
        pass  # pragma: no cover

    def actionName(self) -> str:
        """Get action name."""
        pass  # pragma: no cover

    def setAction(self, action) -> bool:
        """Set Action object."""
        pass  # pragma: no cover

    def setMainFilter(self, filter: str, do_refresh: bool = True) -> None:
        """Set Main filter for this cursor."""
        pass  # pragma: no cover

    def setModeAccess(self, mode_access) -> None:
        """Set Access mode for the cursor."""
        pass  # pragma: no cover

    def connectionName(self) -> str:
        """Get current connection name."""
        pass  # pragma: no cover

    def setValueBuffer(self, field_name: str, value: Any) -> None:
        """Set Value on the cursor buffer."""
        pass  # pragma: no cover

    def valueBuffer(self, field_name: str, with_no_value: bool = False) -> Any:
        """Get value from cursor buffer."""
        return False  # pragma: no cover

    def fetchLargeValue(self, value) -> Optional[str]:
        """Fetch from fllarge."""
        pass  # pragma: no cover

    def valueBufferCopy(self, field_name) -> Any:
        """Get original value on buffer."""
        pass  # pragma: no cover

    def setEdition(self, value, flag=None) -> None:
        """Set edit mode."""
        pass  # pragma: no cover

    def restoreEditionFlag(self, flag) -> None:
        """Restore edit flag."""
        pass  # pragma: no cover

    def setBrowse(self, value, flag=None) -> None:
        """Set browse mode."""
        pass  # pragma: no cover

    def restoreBrowseFlag(self, flag) -> None:
        """Restore browse flag."""
        pass  # pragma: no cover

    # def meta_model(self) -> Any:
    #    """Get sqlAlchemy model."""
    #    pass  # pragma: no cover

    def setContext(self, context=None) -> None:
        """Set script execution context."""
        pass  # pragma: no cover

    def context(self) -> Any:
        """Get script execution context."""
        pass  # pragma: no cover

    def fieldDisabled(self, field_name) -> bool:
        """Get if field is disabled."""
        pass  # pragma: no cover

    def inTransaction(self) -> bool:
        """Return if transaction is in progress."""
        pass  # pragma: no cover

    def transaction(self, lock=False) -> bool:
        """Open transaction."""
        pass  # pragma: no cover

    def rollback(self) -> bool:
        """Rollback transaction."""
        pass  # pragma: no cover

    def commit(self, notify=True) -> bool:
        """Commit transaction."""
        pass  # pragma: no cover

    def size(self) -> int:
        """Get current cursor size in rows."""
        pass  # pragma: no cover

    def openFormInMode(self, mode: int, wait: bool = True, cont: bool = True) -> None:
        """Open record form in specified mode."""
        pass  # pragma: no cover

    def isNull(self, field_name) -> bool:
        """Get if field is null."""
        pass  # pragma: no cover

    def updateBufferCopy(self) -> None:
        """Refresh buffer copy."""
        pass  # pragma: no cover

    def isModifiedBuffer(self) -> bool:
        """Get if buffer is modified."""
        pass  # pragma: no cover

    def setAskForCancelChanges(self, value) -> None:
        """Activate dialog for asking before closing."""
        pass  # pragma: no cover

    def setActivatedCheckIntegrity(self, value) -> None:
        """Activate integrity checks."""
        pass  # pragma: no cover

    def activatedCheckIntegrity(self) -> bool:
        """Get integrity check state."""
        pass  # pragma: no cover

    def setActivatedCommitActions(self, value) -> None:
        """Activate before/after commit."""
        pass  # pragma: no cover

    def activatedCommitActions(self) -> bool:
        """Get before/after commit status."""
        pass  # pragma: no cover

    def cursorRelation(self) -> Optional["ISqlCursor"]:
        """Get cursor relation."""
        pass  # pragma: no cover

    def relation(self) -> Optional["pnrelationmetadata.PNRelationMetaData"]:
        """Get relation."""
        pass  # pragma: no cover

    def setUnLock(self, field_name, value) -> None:
        """Set unlock field."""
        pass  # pragma: no cover

    def isLocked(self) -> bool:
        """Get if record is locked."""
        pass  # pragma: no cover

    def buffer(self) -> "pnbuffer.PNBuffer":
        """Get buffer object."""
        pass  # pragma: no cover

    def bufferCopy(self) -> "pnbuffer.PNBuffer":
        """Get buffer copy."""
        pass  # pragma: no cover

    def setNull(self, name) -> None:
        """Set field to null."""
        pass  # pragma: no cover

    def db(self) -> "iconnection.IConnection":
        """Return database object."""
        pass  # pragma: no cover

    def curName(self) -> str:
        """Get cursor name."""
        pass  # pragma: no cover

    def filterAssoc(self, field_name, table_metadata=None) -> Optional[str]:
        """Retrieve filter for associated field."""
        pass  # pragma: no cover

    def calculateField(self, field_name) -> bool:
        """Return the result of a field calculation."""
        pass  # pragma: no cover

    def model(self) -> "pncursortablemodel.PNCursorTableModel":
        """Get sqlAlchemy model."""
        pass  # pragma: no cover

    def selection(self) -> Optional["QtCore.QItemSelectionModel"]:
        """Get selection."""
        pass  # pragma: no cover

    def at(self) -> int:
        """Get row number."""
        pass  # pragma: no cover

    def isValid(self) -> bool:
        """Return if cursor is valid."""
        pass  # pragma: no cover

    def refresh(self, field_name=None) -> None:
        """Refresh cursor."""
        pass  # pragma: no cover

    def refreshBuffer(self) -> bool:
        """Refresh buffer."""
        pass  # pragma: no cover

    def setEditMode(self) -> bool:
        """Set cursor in edit mode."""
        pass  # pragma: no cover

    def seek(self, i, relative=None, emite=None) -> bool:
        """Move cursor without fetching."""
        pass  # pragma: no cover

    def next(self, emite=True) -> bool:
        """Get next row."""
        pass  # pragma: no cover

    def moveby(self, pos) -> bool:
        """Move cursor down "pos" rows."""
        pass  # pragma: no cover

    def prev(self, emite=True) -> bool:
        """Get previous row."""
        pass  # pragma: no cover

    def move(self, row) -> bool:
        """Move cursor to row number."""
        pass  # pragma: no cover

    def first(self, emite=True) -> bool:
        """Move cursor to first row."""
        pass  # pragma: no cover

    def last(self, emite=True) -> bool:
        """Move cursor to last row."""
        pass  # pragma: no cover

    def select(self, _filter=None, sort=None) -> bool:
        """Perform SQL Select."""
        pass  # pragma: no cover

    def setSort(self, filter) -> None:
        """Set sorting order."""
        pass  # pragma: no cover

    def insertRecord(self, wait: bool = True) -> None:
        """Open form in insert mode."""
        pass  # pragma: no cover

    def editRecord(self, wait: bool = True) -> None:
        """Open form in edit mode."""
        pass  # pragma: no cover

    def browseRecord(self, wait: bool = True) -> None:
        """Open form in browse mode."""
        pass  # pragma: no cover

    def deleteRecord(self, wait: bool = True) -> None:
        """Delete record."""
        pass  # pragma: no cover

    def copyRecord(self) -> None:
        """Copy record."""
        pass  # pragma: no cover

    def chooseRecord(self) -> None:
        """Emit chooseRecord."""
        pass  # pragma: no cover

    def setForwardOnly(self, value) -> None:
        """Set forward only."""
        pass  # pragma: no cover

    def commitBuffer(self, emite=True, check_locks=False) -> bool:
        """Commit current buffer to db."""
        pass  # pragma: no cover

    def commitBufferCursorRelation(self) -> bool:
        """Commit buffer from cursor relation."""
        pass  # pragma: no cover

    def transactionLevel(self) -> int:
        """Get number of nested transactions."""
        pass  # pragma: no cover

    def transactionsOpened(self) -> List[str]:
        """Return if any transaction is open."""
        pass  # pragma: no cover

    def rollbackOpened(self, count=-1, msg=None) -> None:
        """Return if in rollback."""
        pass  # pragma: no cover

    def commitOpened(self, count=-1, msg=None) -> None:
        """Return if in commit."""
        pass  # pragma: no cover

    def checkIntegrity(self, show_error: bool = True) -> bool:
        """Return check integrity result."""
        pass  # pragma: no cover

    def checkRisksLocks(self, terminate: bool = False) -> bool:
        """Return risks locks result."""

        pass  # pragma: no cover

    def msgCheckIntegrity(self) -> str:
        """Return msg check integrity."""

        pass  # pragma: no cover

    def aqWasDeleted(self) -> bool:
        """Indicate if the cursor has been deleted."""

        pass  # pragma: no cover

    def concurrencyFields(self) -> List[str]:
        """
        Check if there is a collision of fields edited by two sessions simultaneously.

        @return List with the names of the colliding fields
        """

        pass  # pragma: no cover

    def setFilter(self, _filter: str = "") -> None:
        """
        Specify the cursor filter.

        @param _filter. Text string with the filter to apply.
        """

        pass  # pragma: no cover

    # def field(self, name: str) -> Optional["pnbuffer.FieldStruct"]:
    #    """
    #    Return a specified FieldStruct of the buffer.
    #    """

    #    pass # pragma: no cover

    def curFilter(self) -> str:
        """
        Return the actual filter.

        @return actual filter.
        """

        return ""

    def sort(self) -> str:
        """
        Choose the order of the main columns.

        @return sort order.
        """

        return ""

    def id(self) -> str:
        """
        Return cursor identifier.
        """

        return ""

    def primaryKey(self) -> str:
        """
        Return the primary cursor key.

        @return primary key field name.
        """

        return ""

    def clear_buffer(self) -> None:
        """Clear buffer."""

        pass  # pragma: no cover

    def bufferIsNull(self, field_name: str) -> bool:
        """Return if buffer is null."""

        return False
