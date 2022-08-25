"""Dummy_cursor module."""


from pineboolib.core.utils import logging
from pineboolib.application.metadata import pntablemetadata, pnaction
from pineboolib.application import types
from pineboolib.application.qsatypes import date
from pineboolib import application
import datetime


from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from . import basemodel  # pragma: no cover
    from pineboolib.interfaces import iconnection  # pragma: no cover
    from pineboolib.application.database import pnsqlcursor  # noqa: F401 # pragma: no cover

LOGGER = logging.get_logger(__name__)


class DummyCursor(object):
    """DummyCursor class."""

    Insert: int = 0
    Edit: int = 1
    Del: int = 2
    Browse: int = 3

    _parent: "basemodel.BaseModel"

    def __init__(self, parent_model: "basemodel.BaseModel") -> None:
        """Initialize."""

        self._parent = parent_model

    def modeAccess(self) -> int:
        """Return mode_access."""

        return (
            self._parent.mode_access
            if self._parent._current_mode is None
            else self._parent._current_mode
        )

    def valueBuffer(self, field_name: str) -> Any:
        """Return field value."""

        value = (
            self._parent._cached_bufferchanged[field_name]
            if field_name in self._parent._cached_bufferchanged.keys()
            else getattr(self._parent, field_name)
        )
        meta_table = self._parent.table_metadata()
        meta_field = meta_table.field(field_name)
        if meta_field is None:
            LOGGER.warning(
                "dummy_cursor.valueBuffer. Field metadata %s not found in %s table."
                % (field_name, meta_table.name())
            )
        else:

            type_ = meta_field.type()  # type: ignore [union-attr]

            if type_ == "date":
                if isinstance(value, datetime.date):
                    value = types.Date(value.strftime("%Y-%m-%d"))
            elif type_ == "time":
                if isinstance(value, datetime.time):
                    value = value.strftime("%H:%M:%S")

        return value

    def valueBufferCopy(self, field_name: str) -> Any:
        """Return field value copy."""

        value = getattr(self._parent.copy(), field_name)

        meta_table = self._parent.table_metadata()
        meta_field = meta_table.field(field_name)
        if meta_field is None:
            LOGGER.warning(
                "dummy_cursor.valueBufferCopy. Field metadata %s not found in %s table."
                % (field_name, meta_table.name())
            )
        else:

            type_ = meta_field.type()  # type: ignore [union-attr]

            if type_ == "date":
                if isinstance(value, datetime.date):
                    value = types.Date(value.strftime("%Y-%m-%d"))
            elif type_ == "time":
                if isinstance(value, datetime.time):
                    value = value.strftime("%H:%M:%S")

        return value

    def setValueBuffer(self, field_name: str, value: Any) -> Any:
        """Set field value."""

        meta_table = self._parent.table_metadata()
        meta_field = meta_table.field(field_name)
        if meta_field is None:
            LOGGER.warning(
                "dummy_cursor.setValueBuffer. Field metadata %s not found in %s table."
                % (field_name, meta_table.name())
            )
        else:

            type_ = meta_field.type()  # type: ignore [union-attr]

            if type_ == "date":
                if not isinstance(value, datetime.date):
                    value = datetime.datetime.strptime(str(value)[0:10], "%Y-%m-%d").date()
            elif type_ == "time":
                if not isinstance(value, datetime.time):
                    value = datetime.datetime.strptime(str(value)[:8], "%H:%M:%S").time()

        setattr(self._parent, field_name, value)

    def setValueBufferCopy(self, field_name: str, value: Any) -> Any:
        """Set field value."""

        meta_table = self._parent.table_metadata()
        meta_field = meta_table.field(field_name)
        if meta_field is None:
            LOGGER.warning(
                "dummy_cursor.setValueBufferCopy. Field metadata %s not found in %s table."
                % (field_name, meta_table.name())
            )
        else:

            type_ = meta_field.type()  # type: ignore [union-attr]

            if type_ == "date":
                if isinstance(value, date.Date):
                    value = datetime.datetime.strptime(str(value)[0:10], "%Y-%m-%d").date()

        setattr(self._parent.copy(), field_name, value)

    def isNull(self, field_name: str) -> bool:
        """Return if value is Null."""

        return getattr(self._parent, field_name) is None

    def isValid(self):
        """Return if cursor is valid."""

        return self._parent is not None

    def setNull(self, field_name: str):
        """Set value to Null."""

        setattr(self._parent, field_name, None)

    def metadata(self) -> "pntablemetadata.PNTableMetaData":
        """Return metadata."""

        return self._parent.table_metadata()

    def db(self) -> "iconnection.IConnection":
        """Return pnconnection."""

        return application.PROJECT.conn_manager.useConn(
            self._parent._session._conn_name  # type: ignore [union-attr] # noqa: F821
        )

    def table(self) -> str:
        """Return table name."""

        return self._parent.__tablename__  # type: ignore [attr-defined] # noqa: F821

    def primaryKey(self) -> str:
        """Return primary key name."""

        return self._parent.pk_name

    def cursorRelation(self) -> Optional["pnsqlcursor.PNSqlCursor"]:
        """Return cursor Relation."""

        LOGGER.warning("FIXME: Avoid using cursorRelation from a DummyCursor returns empty always")
        return None

    def get_bc_signal(self):
        """Return beforeCommit fake signal."""

        return self._parent.bufferChanged

    def isModifiedBuffer(self):
        """Return if buffer is modified."""

        return len(self._parent.changes()) > 0

    def action(self) -> "pnaction.PNAction":
        """Return PNAction."""

        return pnaction.PNAction(self._parent._action)  # type: ignore [arg-type]

    def getattr(self, name: str) -> None:
        """Search unknown functions."""

        raise Exception("PLEASE IMPLEMENT DummyCursor.%s." % name)

    bufferChanged = property(get_bc_signal)
