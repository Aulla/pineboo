"""
Manage buffers used by PNSqlCursor.

*What is a buffer?*

Buffers are the data records pointed to by a PNSqlCursor.
"""
from pineboolib.application import types
from pineboolib.application.database import utils as utils_database
from pineboolib import logging
from pineboolib.core.utils import utils_base
from pineboolib.application.utils import xpm

import datetime
import sqlalchemy

from typing import List, Union, Optional, Callable, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.interfaces import isqlcursor  # pragma: no cover
    from pineboolib.application.database import pncursortablemodel  # pragma: no cover
    import decimal  # noqa : F821 # pragma: no cover

LOGGER = logging.get_logger(__name__)

ACCEPTABLE_VALUES = (
    int,
    float,
    str,
    "datetime.time",
    "datetime.date",
    bool,
    types.Date,
    bytearray,
    "decimal.Decimal",
    "datetime.timedelta",
)
TVALUES = Union[
    int,
    float,
    str,
    "datetime.time",
    "datetime.date",
    bool,
    types.Date,
    bytearray,
    "datetime.timedelta",
    None,
    Dict[Any, Any],
]


class PNBuffer(object):
    """
    Cursor buffer.

    When a query is done, after first(), a PNBuffer is created which holds
    the fields of the record.
    """

    _orm_obj: Optional[Callable]
    _generated_fields: List[str]
    _cache_buffer: Dict[str, TVALUES]
    _cursor: "isqlcursor.ISqlCursor"

    def __init__(self, cursor: "isqlcursor.ISqlCursor") -> None:
        """Create a Buffer from the specified PNSqlCursor."""
        super().__init__()
        if not cursor:
            raise Exception("Missing cursor")
        self._cursor = cursor
        self._orm_obj = None
        self._generated_fields = []
        self._cache_buffer = {}

    def prime_insert(self, row: int = None) -> None:
        """
        Set the initial values of the buffer fields.

        @param row = cursor line.
        """
        self.clear()

        self._orm_obj = self._cursor._cursor_model(session=self._cursor.db().session())
        self.inicialized_ = True

    def prime_update(self) -> None:
        """Set the initial copy of the cursor values into the buffer."""

        self.clear()
        self._orm_obj = self.model().get_obj_from_row(self._cursor.currentRegister())

    def setNull(self, name) -> None:
        """
        Empty the value of the specified field.

        @param name = field name.
        """
        setattr(self._orm_obj, name, None)

    def value(self, field_name: str, return_none: bool = False) -> "TVALUES":
        """
        Return the value of a field.

        @param field_name field identification.
        @return Any = field value.
        """

        if field_name in self._cache_buffer.keys():
            value = self._cache_buffer[field_name]
        else:
            if self._orm_obj and sqlalchemy.inspect(self._orm_obj).expired:
                self._orm_obj = self.model().get_obj_from_row(self._cursor.currentRegister())

            value = getattr(self._orm_obj, field_name, None)

        metadata = self._cursor.metadata().field(field_name)

        if metadata is not None:
            type_ = metadata.type()

            if value is not None:
                if type_ == "pixmap":
                    v_large = (
                        xpm.cache_xpm(str(value))
                        if self._cursor.private_cursor._is_system_table
                        else self._cursor.db().connManager().manager().fetchLargeValue(str(value))
                    )

                    value = v_large if v_large else value
                else:
                    value = utils_database.resolve_qsa_value(type_, value)
            elif return_none is False:
                value = utils_database.resolve_empty_qsa_value(type_)

        return value

    def set_value(self, field_name: str, value: "TVALUES") -> bool:
        """Set values to cache_buffer."""

        if field_name not in self._cursor.metadata().fieldNames():
            return False

        self._cache_buffer[field_name] = value
        return True

    def apply_buffer(self) -> bool:
        """Aply buffer to object (commitBuffer)."""
        ret_ = True

        for field_name in self._cache_buffer.keys():
            value: Any = self._cache_buffer[field_name]
            ret_ = self.set_value_to_objet(field_name, value)
            if not ret_:
                break

        return ret_

    def set_value_to_objet(self, field_name: str, value: "TVALUES") -> bool:
        """
        Set the value of a field.

        @param name = Field name.
        @param value = new value.
        @param mark_. If True verifies that it has changed from the value assigned in primeUpdate and mark it as modified (Default to True).
        """
        if value is not None:
            metadata = self._cursor.metadata().field(field_name)
            if metadata is not None:
                type_ = metadata.type()

                if type_ == "double":
                    if isinstance(value, str) and value == "":
                        value = None
                    else:
                        value = float(value)  # type: ignore [arg-type]
                elif type_ in ("int", "uint", "serial"):
                    if isinstance(value, str) and value == "":
                        value = None
                    else:
                        value = int(value)  # type: ignore [arg-type]
                elif type_ in ("string", "pixmap", "stringlist", "counter"):
                    value = str(value)
                elif type_ in ("boolean", "unlock"):
                    value = utils_base.text2bool(str(value))

                if value in ["", "NULL"]:
                    if isinstance(value, str) and value == "NULL":
                        value = None
                else:
                    if type_ == "date":
                        value = datetime.datetime.strptime(str(value)[:10], "%Y-%m-%d")
                    elif type_ == "timestamp":
                        value = datetime.datetime.strptime(str(value)[0:19], "%Y-%m-%d %H:%M:%S")
                    elif type_ == "time":
                        value = str(value)
                        if value.find("T") > -1:
                            value = value[value.find("T") + 1 :]

                        value = datetime.datetime.strptime(str(value)[:8], "%H:%M:%S").time()
                    elif type_ in ["bool", "unlock"]:
                        value = True if value in [True, 1, "1", "true"] else False

        try:
            setattr(self._orm_obj, field_name, value)
        except Exception as error:
            LOGGER.error("setValue: %s", str(error))
            return False
        return True

    def current_object(self) -> "Callable":
        """Return current db object."""

        if not self._orm_obj:
            raise Exception("buffer orm object doesn't exists!!")

        return self._orm_obj

    def model(self) -> "pncursortablemodel.PNCursorTableModel":
        """Return cursor table model."""

        return self._cursor.model()

    def clear(self):
        """Clear buffer object."""

        del self._orm_obj
        self._orm_obj = None
        del self._cache_buffer
        self._cache_buffer = {}

    def is_null(self, field_name: str) -> bool:
        """Return if a field is null."""

        return self.value(field_name, True) is None

    def set_generated(self, field_name: str, status: bool):
        """Mark a field as generated."""

        if status:
            if field_name not in self._generated_fields:
                self._generated_fields.append(field_name)
        else:
            if field_name in self._generated_fields:
                self._generated_fields.remove(field_name)

    def is_generated(self, field_name: str) -> bool:
        """Return if the field has marked as generated."""

        return field_name in self._generated_fields

    def is_valid(self) -> bool:
        """Return if buffer object is valid."""

        try:
            if not self._orm_obj:
                return False
            value = getattr(self._orm_obj, self._cursor.metadata().primaryKey())  # noqa: F841
        except sqlalchemy.orm.exc.ObjectDeletedError:  # type: ignore [attr-defined] # noqa: F821
            return False

        return True
