"""Dummy_cursor module."""

from pineboolib.core.utils import logging
from pineboolib.application.metadata import pntablemetadata
from pineboolib import application

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from . import basemodel
    from pineboolib.interfaces import iconnection

LOGGER = logging.get_logger(__name__)


class DummyCursor(object):
    """DummyCursor class."""

    Insert: int = 0
    Edit: int = 1
    Del: int = 2
    Browse: int = 3

    _parent: Any

    def __init__(self, parent_model: "basemodel.BaseModel") -> None:
        """Initialize."""

        self._parent = parent_model

    def valueBuffer(self, field_name: str) -> Any:
        """Return field value."""

        return getattr(self._parent, field_name)

    def modeAccess(self) -> int:
        """Return mode_access."""
        if self._parent._current_mode is not None:
            return self._parent._current_mode

        return self._parent.mode_access

    def valueBufferCopy(self, field_name: str) -> Any:
        """Return field value copy."""

        return getattr(self._parent.copy(), field_name)

    def setValueBuffer(self, field_name: str, value: Any) -> Any:
        """Set field value."""

        setattr(self._parent, field_name, value)

    def setValueBufferCopy(self, field_name: str, value: Any) -> Any:
        """Set field value."""

        setattr(self._parent.copy(), field_name, value)

    def isNull(self, field_name: str) -> bool:
        """Return if value is Null."""

        return getattr(self._parent, field_name) is None

    def setNull(self, field_name):
        """Set value to Null."""

        setattr(self._parent, field_name, None)

    def metadata(self) -> "pntablemetadata.PNTableMetaData":
        """Return metadata."""

        return self._parent.table_metadata()

    def db(self) -> "iconnection.IConnection":
        """Return pnconnection."""

        return application.PROJECT.conn_manager.useConn(self._parent._session._conn_name)

    def table(self) -> str:
        """Return table name."""

        return self._parent.__tablename__  # type: ignore [attr-defined] # noqa: F821

    def primaryKey(self) -> str:
        """Return primery key name."""

        return self._parent.pk_name

    def get_bc_signal(self):
        """Return beforeCommit fake signal."""

        return self._parent.bufferChanged

    def getattr(self, name: str) -> None:
        """Search unknown functions."""

        raise Exception("PLEASE IMPLEMENT DummyCursor.%s." % name)

    bufferChanged = property(get_bc_signal)
