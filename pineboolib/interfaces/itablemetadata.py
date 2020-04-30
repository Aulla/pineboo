"""
ITableMetadata module.
"""
from typing import List, Optional, Any, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.application.metadata.pnfieldmetadata import PNFieldMetaData  # noqa


class ITableMetaData:
    """Abstract class for PNTableMetaData."""

    def __init__(
        self,
        name: Optional[Union["ITableMetaData", str]] = None,
        alias: Optional[str] = None,
        qry_name: Optional[str] = None,
    ) -> None:
        """Create new tablemetadata."""
        return

    def addFieldMD(self, fielf_metadata) -> None:
        """Add new field to this object."""
        return

    def field(self, field_name: str) -> Any:
        """Retrieve field by name."""
        return

    def fieldIsIndex(self, field_name: str) -> int:
        """Get if a field is an index."""
        return -1

    def fieldList(self):
        """Return list of fields."""
        return

    def fieldListOfCompoundKey(self, field_name: str) -> Optional[List["PNFieldMetaData"]]:
        """Return list of fields for CK."""
        return []

    def fieldNameToAlias(self, field_name: str) -> str:
        """Get alias of field."""
        return ""

    def fieldNames(self) -> List[str]:
        """Get list of field names."""
        return []

    def fieldNamesUnlock(self) -> List[str]:
        """Get field names for unlock fields."""
        return []

    def inCache(self) -> bool:
        """Get if in cache."""
        return False

    def indexFieldObject(self, position: int):
        """Get field by position."""
        return

    def indexPos(self, field_name: str) -> int:
        """Get field position by name."""
        return 0

    def inicializeNewFLTableMetaData(self, name: str, alias: str, qry_name: Optional[str]) -> None:
        """Initialize object."""
        return

    def isQuery(self) -> bool:
        """Return true if is a query."""
        return False

    def name(self) -> str:
        """Get table name."""
        return ""

    def primaryKey(self, prefix_table: bool) -> str:
        """Get primary key field."""
        return ""

    def query(self) -> str:
        """Get query string."""
        return ""

    def relation(self, field_name: str, foreign_field_name: str, foreign_table_name: str):
        """Get relation object."""
        return

    def setCompoundKey(self, compound_key) -> None:
        """Set CK."""
        return

    def setConcurWarn(self, state: bool) -> None:
        """Enable concurrency warning."""
        return

    def setDetectLocks(self, state: bool) -> None:
        """Enable Lock detection."""
        return

    def setFTSFunction(self, full_text_search_function: str) -> None:
        """Set Full-Text-Search function."""
        return
