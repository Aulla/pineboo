"""
IFieldMetaData module.
"""
from typing import List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .itablemetadata import ITableMetaData  # noqa: F401 # pragma: no cover
    from pineboolib.application.metadata.pnrelationmetadata import (  # noqa: F401
        PNRelationMetaData,  # noqa: F401
    )  # noqa: F401 # pragma: no cover


class IFieldMetaData:
    """
    Abastract class for FieldMetaData.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Create new FieldMetaData."""
        return  # pragma: no cover

    def __len__(self) -> int:
        """Get size of field."""
        return 0  # pragma: no cover

    def addRelationMD(self, relation) -> None:
        """Add relation M1 or 1M."""
        return  # pragma: no cover

    def alias(self) -> str:
        """Get alias for this field."""
        return ""  # pragma: no cover

    def allowNull(self) -> bool:
        """Determine if this field allos NULLs."""
        return False  # pragma: no cover

    def associatedField(self) -> Optional["IFieldMetaData"]:
        """Return associated field."""
        return None  # pragma: no cover

    def associatedFieldFilterTo(self) -> str:
        """Return associated field filter in sql string format."""
        return ""  # pragma: no cover

    def associatedFieldName(self) -> Optional[str]:
        """Return associated field name."""
        return None  # pragma: no cover

    def defaultValue(self) -> Optional[Union[str, bool]]:
        """Return field default value."""
        return None  # pragma: no cover

    def editable(self) -> bool:
        """Get if field is editable."""
        return False  # pragma: no cover

    def formatAssignValue(self, field_name: str, value: int, upper: bool) -> str:
        """Format a value for this field."""
        return ""  # pragma: no cover

    def generated(self) -> bool:
        """Get if field is computed."""
        return False  # pragma: no cover

    def getIndexOptionsList(self, name: str) -> Optional[int]:
        """Get list of options."""
        return None  # pragma: no cover

    def hasOptionsList(self) -> bool:
        """Return if this field has list of options."""
        return False  # pragma: no cover

    def inicializeFLFieldMetaData(self, other) -> None:
        """Initialize."""
        return  # pragma: no cover

    def inicializeNewFLFieldMetaData(
        self,
        name: str,
        alias: str,
        allow_null: bool,
        is_primary_key: bool,
        ttype: str,
        length_: int = 0,
        calculated: bool = False,
        visible: bool = True,
        editable: bool = True,
        part_integer: int = 4,
        part_decimal: int = 0,
        is_index: bool = False,
        is_unique: bool = False,
        coun: bool = False,
        default_value: Optional[str] = None,
        out_transaction: bool = False,
        regular_exp: Optional[str] = None,
        visible_grib: bool = True,
        generated: bool = True,
        is_compound_key: bool = False,
    ) -> None:
        """Initialize."""
        return  # pragma: no cover

    def isCompoundKey(self) -> bool:
        """Return if this field is part of CK."""
        return False  # pragma: no cover

    def isPrimaryKey(self) -> bool:
        """Return if this field is PK."""
        return False  # pragma: no cover

    def length(self) -> int:
        """Return field size."""
        return 0  # pragma: no cover

    def metadata(self) -> Optional["ITableMetaData"]:
        """Return table metadata for this field."""
        return None  # pragma: no cover

    def name(self) -> str:
        """Get name of this field."""
        return ""  # pragma: no cover

    def optionsList(self) -> List[str]:
        """Get list of options for this field."""
        return []  # pragma: no cover

    def outTransaction(self) -> bool:
        """Return if this field should be updated outside of transaction."""
        return False  # pragma: no cover

    def partDecimal(self) -> int:
        """Return the amount of digits after dot when formatting numbers."""
        return 0  # pragma: no cover

    def partInteger(self) -> int:
        """Return amount of digits before decimal dot."""
        return 0  # pragma: no cover

    def regExpValidator(self) -> Optional[str]:
        """Validate regexp."""
        return None  # pragma: no cover

    def relationM1(self) -> Optional["PNRelationMetaData"]:
        """Return M1 relationship in this field."""
        return None  # pragma: no cover

    def setAssociatedField(self, relation_or_name, field: str) -> None:
        """Set new associated field."""
        return  # pragma: no cover

    def setEditable(self, editable: bool) -> None:
        """Set if this field should be editable."""
        return  # pragma: no cover

    def setFullyCalculated(self, calculated: bool) -> None:
        """Set if this field should be fully calculated."""
        return  # pragma: no cover

    def setMetadata(self, metadata) -> None:
        """Set TableMetadata for this field."""
        return  # pragma: no cover

    def setOptionsList(self, options_list: str) -> None:
        """Set option list for this field."""
        return  # pragma: no cover

    def setTrimed(self, trimed: bool) -> None:
        """Set if this field should be trimed."""
        return  # pragma: no cover

    def setVisible(self, visible: bool) -> None:
        """Set if this field should be visible."""
        return  # pragma: no cover

    def type(self) -> str:
        """Return field type."""
        return ""  # pragma: no cover

    def visible(self) -> bool:
        """Get if this field should be visible in UI."""
        return False  # pragma: no cover

    def visibleGrid(self) -> bool:
        """Get if this field should be visible in grids."""
        return False  # pragma: no cover
