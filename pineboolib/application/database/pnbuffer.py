"""
Manage buffers used by PNSqlCursor.

*What is a buffer?*

Buffers are the data records pointed to by a PNSqlCursor.
"""
from pineboolib.application import types
from pineboolib import logging

import datetime
import decimal
import sqlalchemy

from typing import List, Union, Optional, Callable, Dict, TYPE_CHECKING


if TYPE_CHECKING:
    from pineboolib.interfaces import isqlcursor

LOGGER = logging.get_logger(__name__)

ACCEPTABLE_VALUES = (
    int,
    float,
    str,
    datetime.time,
    datetime.date,
    bool,
    types.Date,
    bytearray,
    decimal.Decimal,
    datetime.timedelta,
)
TVALUES = Union[
    int,
    float,
    str,
    datetime.time,
    datetime.date,
    bool,
    types.Date,
    bytearray,
    datetime.timedelta,
    None,
]


class PNBuffer(object):
    """
    Cursor buffer.

    When a query is done, after first(), a PNBuffer is created which holds
    the fields of the record.
    """

    _current_model_obj: Optional[Callable]
    _generated_fields: List[str]
    _cache_buffer: Dict[str, TVALUES]

    def __init__(self, cursor: "isqlcursor.ISqlCursor") -> None:
        """Create a Buffer from the specified PNSqlCursor."""
        super().__init__()
        if not cursor:
            raise Exception("Missing cursor")
        self.cursor_ = cursor
        # self.field_dict_ = {}
        # self.line_: int = -1
        # self.inicialized_: bool = False
        self._current_model_obj = None
        self._generated_fields = []
        self._cache_buffer = {}
        # tmd = self.cursor_.metadata()
        # campos = tmd.fieldList()

    def prime_insert(self, row: int = None) -> None:
        """
        Set the initial values ​​of the buffer fields.

        @param row = cursor line.
        """
        # if self.inicialized_:
        #    LOGGER.debug("(%s)PNBuffer. Se inicializa nuevamente el cursor", self.cursor_.curName())

        # self.primeUpdate(row)
        self.clear()

        self._current_model_obj = self.cursor_._cursor_model()
        self.inicialized_ = True

    def prime_update(self) -> None:
        """Set the initial copy of the cursor values into the buffer."""

        self.clear()
        self._current_model_obj = self.cursor_.model().get_obj_from_row(
            self.cursor_.currentRegister()
        )

    def prime_delete(self) -> None:
        """Load registr for delete."""

        self.clear()
        self._current_model_obj = self.cursor_.model().get_obj_from_row(
            self.cursor_.currentRegister()
        )

    def setNull(self, name) -> None:
        """
        Empty the value of the specified field.

        @param name = field name.
        """
        setattr(self._current_model_obj, name, None)

    def value(self, field_name: str) -> TVALUES:
        """
        Return the value of a field.

        @param field_name field identification.
        @return Any = field value.
        """

        if field_name in self._cache_buffer.keys():
            return self._cache_buffer[field_name]

        value = getattr(self._current_model_obj, field_name, None)

        metadata = self.cursor_.metadata().field(field_name)
        type_ = metadata.type()

        if isinstance(value, datetime.datetime):

            if type_ == "date":
                value = value.strftime("%Y-%m-%d")
            elif type_ == "time":
                value = value.strftime("%H:%M:%S")
        elif isinstance(value, decimal.Decimal):
            value = float(str(value))

        return value

    def set_value(self, field_name: str, value: TVALUES) -> bool:
        """Set values to cache_buffer."""

        if field_name in self.cursor_.metadata().fieldNames():
            self._cache_buffer[field_name] = value
        else:
            return False

        return True

    def apply_buffer(self) -> None:
        """Aply buffer to object (commitBuffer)."""

        for field_name in self._cache_buffer.keys():
            self.set_value_to_objet(field_name, self._cache_buffer[field_name])

    def set_value_to_objet(self, field_name: str, value: TVALUES) -> bool:
        """
        Set the value of a field.

        @param name = Field name.
        @param value = new value.
        @param mark_. If True verifies that it has changed from the value assigned in primeUpdate and mark it as modified (Default to True).
        """

        if value not in [None, ""]:
            metadata = self.cursor_.metadata().field(field_name)
            type_ = metadata.type()
            if type_ == "date":
                value = datetime.datetime.strptime(str(value)[:10], "%Y-%m-%d")
            elif type_ == "time":
                value = str(value)
                if value.find("T") > -1:
                    value = value[value.find("T") + 1 :]

                value = datetime.datetime.strptime(str(value)[:8], "%H:%M:%S")
            elif type_ in ["bool", "unlock"]:
                value = True if value in [True, 1, "1", "true"] else False

        try:
            setattr(self._current_model_obj, field_name, value)
        except Exception as error:
            LOGGER.error("setValue: %s", str(error))
            return False
        return True

    def clear(self):
        """"Clear buffer object."""
        del self._current_model_obj
        self._current_model_obj = None
        del self._cache_buffer
        self._cache_buffer = {}

    def is_null(self, field_name: str) -> bool:
        """Return if a field is null."""

        return self.value(field_name) in [None, ""]

        return True

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
        metadata = self.cursor_.metadata()
        pk_field = metadata.primaryKey()
        try:
            value = getattr(self._current_model_obj, pk_field, None)
        except sqlalchemy.orm.exc.ObjectDeletedError:
            return False

        return True
