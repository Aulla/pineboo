"""
Manage buffers used by PNSqlCursor.

*What is a buffer?*

Buffers are the data records pointed to by a PNSqlCursor.
"""
from pineboolib.application import types
from pineboolib import logging

import datetime
import decimal

from typing import List, Union, Optional, Callable, TYPE_CHECKING


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

        del self._current_model_obj
        self._current_model_obj = self.cursor_._cursor_model()
        # print("B *", self._current_model_obj)
        self.inicialized_ = True

    def prime_update(self) -> None:
        """Set the initial copy of the cursor values into the buffer."""
        del self._current_model_obj
        self._current_model_obj = list(self.cursor_.model()._data_proxy)[
            self.cursor_.currentRegister()
        ]
        # print("B * *", self._current_model_obj, self.cursor_.currentRegister())

    def prime_delete(self) -> None:
        """Clear the values ​​of all buffer fields."""
        # for field_key in self.field_dict_.keys():
        #    field = self.field_dict_[field_key]
        del self._current_model_obj
        self._current_model_obj = list(self.cursor_.model()._data_proxy)[
            self.cursor_.currentRegister()
        ]
        # print("B * * *", self._current_model_obj, self.cursor_.currentRegister())

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
        return getattr(self._current_model_obj, field_name, None)

    def setValue(self, field_name: str, value: TVALUES, mark_: bool = True) -> bool:
        """
        Set the value of a field.

        @param name = Field name.
        @param value = new value.
        @param mark_. If True verifies that it has changed from the value assigned in primeUpdate and mark it as modified (Default to True).
        """

        if value is not None:
            metadata = self.cursor_.metadata().field(field_name)
            if metadata.type() == "date":
                value = datetime.datetime.strptime(str(value)[:10], "%Y-%m-%d")

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

    def is_null(self, field_name: str) -> bool:
        """Return if a field is null."""

        if self._current_model_obj:
            value = getattr(self._current_model_obj, field_name)
            return value in [None, ""]

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
