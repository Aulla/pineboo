"""Dummy_cursor module."""

from pineboolib.core.utils import logging

from typing import Any

LOGGER = logging.get_logger(__name__)


class DummyCursor(object):
    """DummyCursor class."""

    Insert: int = 0
    Edit: int = 1
    Del: int = 2
    Browse: int = 3

    _parent: Any

    def __init__(self, parent_model) -> None:
        """Initialize."""

        self._parent = parent_model

    def valueBuffer(self, field_name: str) -> Any:
        """Return field value."""

        return getattr(self._parent, field_name)

    def modeAccess(self) -> int:
        """Return mode_access."""

        return self._parent._current_mode

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

        return getattr(self._parent, field_name) in [None, ""]

    def setNull(self, field_name):
        """Set value to Null."""

        setattr(self._parent, field_name, None)

    def primaryKey(self) -> str:
        """Return primery key name."""

        return self._parent.pk_name

    def getattr(self, name: str) -> None:
        """Search unknown functions."""

        raise Exception("PLEASE IMPLEMENT DummyCursor.%s" % name)
