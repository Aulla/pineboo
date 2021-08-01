"""
ITableMetadata module.
"""
from typing import List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.application.metadata import pnfieldmetadata


class ITableMetaData:
    """Abstract class for PNTableMetaData."""

    def __init__(
        self,
        name: Optional[Union["ITableMetaData", str]] = None,
        alias: Optional[str] = None,
        qry_name: Optional[str] = None,
    ) -> None:
        """Create new tablemetadata."""
        return  # pragma: no cover

    def addFieldMD(self, fielf_metadata) -> None:
        """Add new field to this object."""
        return  # pragma: no cover

    def field(self, field_name: str) -> Optional["pnfieldmetadata.PNFieldMetaData"]:
        """Retrieve field by name."""
        return None  # pragma: no cover

    def fieldIsIndex(self, field_name: str) -> int:
        """Get if a field is an index."""
        return -1  # pragma: no cover

    def fieldList(self) -> List["pnfieldmetadata.PNFieldMetaData"]:
        """Return list of fields."""
        return []  # pragma: no cover

    def fieldListOfCompoundKey(
        self, field_name: str
    ) -> Optional[List["pnfieldmetadata.PNFieldMetaData"]]:
        """Return list of fields for CK."""
        return None  # pragma: no cover

    def fieldNameToAlias(self, field_name: str) -> str:
        """Get alias of field."""
        return ""  # pragma: no cover

    def fieldNames(self) -> List[str]:
        """Get list of field names."""
        return []  # pragma: no cover

    def fieldNamesUnlock(self) -> List[str]:
        """Get field names for unlock fields."""
        return []  # pragma: no cover

    def inCache(self) -> bool:
        """Get if in cache."""
        return False  # pragma: no cover

    def indexFieldObject(self, position: int):
        """Get field by position."""
        return  # pragma: no cover

    def indexPos(self, field_name: str) -> int:
        """Get field position by name."""
        return 0  # pragma: no cover

    def inicializeNewFLTableMetaData(self, name: str, alias: str, qry_name: Optional[str]) -> None:
        """Initialize object."""
        return  # pragma: no cover

    def isQuery(self) -> bool:
        """Return true if is a query."""
        return False  # pragma: no cover

    def name(self) -> str:
        """Get table name."""
        return ""  # pragma: no cover

    def primaryKey(self, prefix_table: bool) -> str:
        """Get primary key field."""
        return ""  # pragma: no cover

    def query(self) -> str:
        """Get query string."""
        return ""  # pragma: no cover

    def relation(self, field_name: str, foreign_field_name: str, foreign_table_name: str):
        """Get relation object."""
        return  # pragma: no cover

    def setCompoundKey(self, compound_key) -> None:
        """Set CK."""
        return  # pragma: no cover

    def setConcurWarn(self, state: bool) -> None:
        """Enable concurrency warning."""
        return  # pragma: no cover

    def setDetectLocks(self, state: bool) -> None:
        """Enable Lock detection."""
        return  # pragma: no cover

    def setFTSFunction(self, full_text_search_function: str) -> None:
        """Set Full-Text-Search function."""
        return  # pragma: no cover
