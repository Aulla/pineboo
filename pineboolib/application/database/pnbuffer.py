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

LOGGER = logging.getLogger(__name__)

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
T_VALUES = Union[
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


class FieldStruct(object):
    """Specific class for fields exclusive within this private module."""

    tablename: Any
    name: str
    query_table: Any
    value: Any  # T_VALUE
    metadata: Any
    type_: Any
    modified: bool
    _original_value: Any  # T_VALUE
    generated: bool

    def __init__(self, field: "ifieldmetadata.IFieldMetaData"):
        """Structure of each field that composes a buffer."""

        self.name = field.name()
        self.value = None
        self.metadata = field
        self.type_ = field.type()
        self.modified = False
        self._original_value = None
        self.generated = field.generated()

    def parse_value_input(self, value: T_VALUES) -> T_VALUES:
        """Given an user-provided input, it parses and reformats it suitable for database use."""
        txtvalue: str
        if self.type_ == "double" and value and value not in ("", "-"):
            if isinstance(value, str):
                if value.find(":") > -1:
                    # Convertimos a horas
                    list_ = value.split(":")
                    numvalue: int = int(list_[0])  # Horas
                    numvalue += int(list_[1]) // 60  # Minutos a hora
                    numvalue += int(list_[2]) // 3600  # Segundos a hora
                    return numvalue
                else:
                    if value.find(",") > -1:
                        value = value.replace(",", "")

                    return float(value)

        elif self.type_ in ("string", "stringlist", "timestamp"):
            if value is None:
                return None
            else:
                return str(value)

        elif self.type_ == "time":
            if value is not None:
                if isinstance(value, types.Date):
                    txtvalue = value.toString()
                elif isinstance(value, datetime.timedelta):
                    txtvalue = str(value)
                elif isinstance(value, str):
                    txtvalue = value
                else:
                    return None

                if txtvalue.find("T") > -1:
                    txtvalue = txtvalue[txtvalue.find("T") + 1 :]

                if txtvalue.find(".") > -1:
                    txtvalue = txtvalue[0 : txtvalue.find(".")]

                elif txtvalue.find("+") > -1:
                    txtvalue = txtvalue[0 : txtvalue.find("+")]
                return txtvalue

        elif self.type_ == "date":
            if value in ("", None):
                return None
            if isinstance(value, types.Date):
                txtvalue = value.toString()
            else:
                txtvalue = str(value)

            if txtvalue.upper() == "NAN":
                return "NAN"
            else:
                if txtvalue.find("T") > -1:
                    txtvalue = txtvalue[: txtvalue.find("T")]

                list_ = txtvalue.split("-")
                return datetime.date(int(list_[0]), int(list_[1]), int(list_[2]))
        elif self.type_ in ("unlock", "bool"):
            if isinstance(value, str):
                if value == "true":
                    return True
                elif value == "false":
                    return False
                else:
                    raise ValueError("bool type can't accept %s" % value)

        return value

    """
    Comprueba si un campo tiene valor diferente. Esto es especialmente util para los número con decimales
    @return True si ha cambiado, False si es el mismo valor
    """

    def has_changed(self, val: T_VALUES) -> bool:
        """Check if a buffer field has changed in value since it was initially loaded."""

        if self.value is None:
            if val is None:
                return False
            else:
                return True

        elif self.type_ in ("unlock", "bool"):
            return self.value != val
        elif self.type_ in ("string", "stringlist", "timestamp"):
            return self.value != val
        elif self.type_ in ("int", "uint", "serial", "date"):
            return str(self.value) != str(val)
        elif self.type_ == "double":
            try:
                return float(self.value) != float(val)  # type: ignore
            except Exception:
                LOGGER.trace("has_changed: Error converting %s != %s to floats", self.value, val)
                return True
        elif isinstance(self.value, str) and isinstance(val, str):
            return self.value != val
        elif isinstance(val, (datetime.date, datetime.time)):
            return str(self.value) != str(val)

        return True


class PNBuffer(object):
    """
    Cursor buffer.

    When a query is done, after first(), a PNBuffer is created which holds
    the fields of the record.
    """

    field_dict_: Dict[str, FieldStruct]

    def __init__(self, cursor: "isqlcursor.ISqlCursor") -> None:
        """Create a Buffer from the specified PNSqlCursor."""
        super().__init__()
        if not cursor:
            raise Exception("Missing cursor")
        self.cursor_ = cursor
        self.field_dict_ = {}
        self.line_: int = -1
        self.inicialized_: bool = False

        tmd = self.cursor_.metadata()
        campos = tmd.fieldList()
        # FIXME: Should not inspect the fields in each create, this should be cached in the metadata()
        for campo in campos:
            field = FieldStruct(campo)
            # self.field_list_.append(field)
            self.field_dict_[field.name.lower()] = field

    def count(self) -> int:
        """
        Return the number of fields that make up the buffer.

        @return int
        """
        return len(self.field_dict_.keys())

    def clear_buffer(self):
        """Empty the values ​​buffer and mark the fields as unmodified."""
        self.clearValues()
        self.setNoModifiedFields()

    def primeInsert(self, row: int = None) -> None:
        """
        Set the initial values ​​of the buffer fields.

        @param row = cursor line.
        """
        if self.inicialized_:
            LOGGER.debug("(%s)PNBuffer. Se inicializa nuevamente el cursor", self.cursor_.curName())

        self.primeUpdate(row)
        self.inicialized_ = True

    def primeUpdate(self, row: int = None) -> None:
        """Set the initial copy of the cursor values into the buffer."""
        if row is None or row < 0:
            row = self.cursor_.currentRegister()
        if row is None:
            raise Exception("Unexpected: No currentRegister")
        self.clear_buffer()

        if row == -1:
            LOGGER.warning(
                "PrimeUpdate sobre posición inválida de %s, size: %s, filtro: %s, row: %s",
                self.cursor_.metadata().name(),
                self.cursor_.size(),
                self.cursor_.filter(),
                row,
                stack_info=True,
            )
            return

        for field in self.fieldsList():
            value = self.cursor_.model().value(row, field.name)
            if value is not None:
                if field.type_ in ("unlock", "bool"):
                    value = value in ("True", True, 1, "1")

                elif field.type_ == "date":
                    if isinstance(value, str):
                        date_ = value.split("-")
                        if len(date_[2]) == 4:
                            value = date_[2] + "-" + date_[1] + "-" + date_[0]

                elif field.type_ == "bytearray":
                    value = bytearray(value)

            field.value = value
            field._original_value = copy.copy(value)
        # self.cursor_.bufferChanged.emit(field.name)
        self.setRow(row)

    def primeDelete(self) -> None:
        """Clear the values ​​of all buffer fields."""
        # for field_key in self.field_dict_.keys():
        #    field = self.field_dict_[field_key]
        for field in self.fieldsList():
            field.value = None
            field.modified = field._original_value is not None

    def row(self) -> int:
        """
        Set the cursor line referenced by the buffer.

        @return int = reference line.
        """
        return self.line_

    def setRow(self, row: int) -> None:
        """
        Set the cursor line referenced by the buffer.

        @param l = cursor register index.
        """
        self.line_ = row

    def setNull(self, name) -> bool:
        """
        Empty the value of the specified field.

        @param name = field name.
        """
        return self.setValue(name, None)

    def isGenerated(self, name: str) -> bool:
        """
        Specify whether it is a generated field or not.

        @return True or False.
        """
        field = self.field(name)
        if field is not None:
            return field.generated

        raise Exception("Field %s not found!" % name)
        # return self.field_dict_[name].generated

    def setGenerated(
        self, field_name_or_metadata: Union[int, str, "ifieldmetadata.IFieldMetaData"], value: bool
    ) -> None:
        """
        Set that is a generated field.

        @param f = FLField Metadata of the field to be marked.
        @param value = True or False.
        """
        if not isinstance(field_name_or_metadata, (str, int)):
            field_name_or_metadata = field_name_or_metadata.name()

        field = self._field(field_name_or_metadata)
        if field:
            field.generated = value
        else:
            raise Exception("Field %s not found!" % field_name_or_metadata)

    def clearValues(self) -> None:
        """
        Set all values ​​to None and check field.modified to True.
        """
        # for field_key in self.field_dict_.keys():
        #    field = self.field_dict_[field_key]
        for field in self.fieldsList():
            field.value = None
            field.modified = True

    def isEmpty(self) -> bool:
        """
        Return if the field is initialized.

        @return bool = True or False.
        """
        return self.inicialized_

    def isNull(self, field_name: Union[str, int]) -> bool:
        """
        Return if the field is empty.

        @param field_name = field identification to check if empty.
        @return bool = True or False.
        """
        field = self.field(field_name)

        if field is None:
            raise Exception("PNBuffer.isNull: Field <%s> not found", field_name)

        return field.value in (None, "")

    def value(self, field_name: Union[str, int]) -> T_VALUES:
        """
        Return the value of a field.

        @param field_name field identification.
        @return Any = field value.
        """
        field = self._field(field_name)
        if not field:
            raise Exception("Field %s not found!" % field_name)

        value = field.value

        if field.type_ in ("bool", "unlock"):
            return field.value in (True, "true")

        if field.value is None:
            return None

        if field.type_ in ("string", "pixmap", "time", "date", "datetime", "timestamp"):
            try:
                value = str(field.value)
            except Exception as expcetion:
                LOGGER.trace("Error trying to convert %s to string: %s", field.value, expcetion)
                value = ""
        elif field.type_ in ("int", "uint", "serial"):
            try:
                value = int(field.value)
            except Exception as expcetion:
                LOGGER.trace("Error trying to convert %s to int: %s", field.value, expcetion)
                value = 0

        elif field.type_ == "double":
            try:
                value = float(field.value)
            except Exception as expcetion:
                LOGGER.trace("Error trying to convert %s to float: %s", field.value, expcetion)
                value = 0.0

        # LOGGER.trace("---->retornando %s %s %s",v , type(v), field.value, field.name)
        return value

    def setValue(self, name: str, value: T_VALUES, mark_: bool = True) -> bool:
        """
        Set the value of a field.

        @param name = Field name.
        @param value = new value.
        @param mark_. If True verifies that it has changed from the value assigned in primeUpdate and mark it as modified (Default to True).
        """
        if value is not None and not isinstance(value, ACCEPTABLE_VALUES):
            raise ValueError(
                "No se admite el tipo %r , en setValue(%s,%r)" % (type(value), name, value)
            )

        field = self.field(name)

        if field is None:
            LOGGER.warning("setValue: no such field %s", name)
            return False

        if field.has_changed(value):
            field.value = field.parse_value_input(value)

            if mark_:
                if not field.value == field._original_value:
                    field.modified = True
                else:
                    field.modified = False
                # self.setMd5Sum(value)

        return True

    def cursor(self) -> "isqlcursor.ISqlCursor":
        """
        Indicate the parent cursor.

        @return parent cursor.
        """
        return self.cursor_

    def modifiedFields(self) -> List[str]:
        """
        Return the modified fields from primeUpdate.

        @return array = List of modified fields.
        """
        lista = []
        for field in self.fieldsList():
            if field.modified:
                lista.append(field.name)

        return lista

    def setNoModifiedFields(self) -> None:
        """
        Set all fields as unmodified."""

        for field in self.fieldsList():
            field.modified = False

    def pK(self) -> Optional[str]:
        """
        Return which buffer field is the primary key.

        @return field name Primary key.
        """
        for field in self.fieldsList():
            if field.metadata.isPrimaryKey():
                return field.name
        LOGGER.warning("PNBuffer.pk(): No se ha encontrado clave Primaria")
        return None

    def indexField(self, name) -> Optional[int]:
        """
        Return the position of a given field.

        @param name = field name.
        @return field position.
        """
        for i, field in enumerate(self.fieldsList()):
            if field.name == name:
                return i
        LOGGER.warning("indexField: %s not found", name)
        return None

    def fieldsList(self) -> List[FieldStruct]:
        """
        List of fields that contain the buffer."""

        return list(self.field_dict_.values())

    def field(self, field_name: Union[str, int]) -> Optional[FieldStruct]:
        """
        Retrieve a field by ID/position or by name.

        Ignores errors and returns None if not found.
        Still can raise Exception if called with a bad type.
        """
        try:
            return self._field(field_name)
        except (KeyError, ValueError):
            return None

    def _field(self, field_name_or_index: Union[str, int]) -> Optional[FieldStruct]:
        """Fieldstruct of a specified field."""
        mtd_field = None

        if isinstance(field_name_or_index, str):
            name = field_name_or_index.lower()
            if name in self.field_dict_.keys():
                return self.field_dict_[name]
            else:
                mtd_field = self.cursor_.metadata().field(name)
        elif isinstance(field_name_or_index, int):
            if field_name_or_index > 0 and field_name_or_index < len(self.fieldsList()):
                return self.fieldsList()[field_name_or_index]
            else:
                mtd_field = self.cursor_.metadata().indexFieldObject(field_name_or_index)

        else:
            raise Exception("Bad call to _field, type not supported %s" % type(field_name_or_index))

        new_field_struct = None

        if mtd_field is not None:
            new_field_struct = FieldStruct(mtd_field)
            self.field_dict_[new_field_struct.name] = new_field_struct

        return new_field_struct
