"""
Manage buffers used by PNSqlCursor.

*What is a buffer?*

Buffers are the data records pointed to by a PNSqlCursor.
"""
from pineboolib.application import types
from pineboolib import logging

import copy
import datetime
import decimal

from typing import Dict, List, Union, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.interfaces import ifieldmetadata, isqlcursor

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

    _current_model_obj: str

    def __init__(self, cursor: "isqlcursor.ISqlCursor") -> None:
        """Create a Buffer from the specified PNSqlCursor."""
        super().__init__()
        if not cursor:
            raise Exception("Missing cursor")
        self.cursor_ = cursor
        self.field_dict_ = {}
        self.line_: int = -1
        self.inicialized_: bool = False
        self._current_model_obj = None

        tmd = self.cursor_.metadata()
        campos = tmd.fieldList()

    def primeInsert(self, row: int = None) -> None:
        """
        Set the initial values ​​of the buffer fields.

        @param row = cursor line.
        """
        # if self.inicialized_:
        #    LOGGER.debug("(%s)PNBuffer. Se inicializa nuevamente el cursor", self.cursor_.curName())

        # self.primeUpdate(row)

        del self._current_model_obj
        self._current_model_obj = self.cursor_._cursor_model()
        print("*", self._current_model_obj)
        self.inicialized_ = True

    def primeUpdate(self) -> None:
        """Set the initial copy of the cursor values into the buffer."""
        del self._current_model_obj
        self._current_model_obj = list(self.cursor_.model()._data_proxy)[
            self.cursor_.currentRegister()
        ]
        print("* *", self._current_model_obj, self.cursor_.currentRegister())

    def primeDelete(self) -> None:
        """Clear the values ​​of all buffer fields."""
        # for field_key in self.field_dict_.keys():
        #    field = self.field_dict_[field_key]
        del self._current_model_obj
        self._current_model_obj = list(self.cursor_.model()._data_proxy)[
            self.cursor_.currentRegister()
        ]
        print("* * *", self._current_model_obj, self.cursor_.currentRegister())

    def setNull(self, name) -> bool:
        """
        Empty the value of the specified field.

        @param name = field name.
        """
        setattr(self._current_model_obj, name, None)

    def value(self, field_name: Union[str, int]) -> TVALUES:
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
        try:
            setattr(self._current_model_obj, field_name, value)
        except Exception as error:
            LOGGER.error("setValue: %s", str(error))
            return False
        return True
