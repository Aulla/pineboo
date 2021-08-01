"""
IManager Module.
"""
from typing import Any, Dict, Optional, Union, List, TYPE_CHECKING


if TYPE_CHECKING:
    from pineboolib.application.database import pnsqlquery  # noqa: F401 # pragma: no cover
    from pineboolib.application.metadata import pntablemetadata  # noqa: F401 # pragma: no cover
    from pineboolib.application.metadata import pnfieldmetadata  # noqa: F401 # pragma: no cover
    from pineboolib.application.metadata import pnrelationmetadata  # noqa: F401 # pragma: no cover
    from pineboolib.application.metadata import pnaction  # pragma: no cover
    from . import iconnection  # pragma: no cover
    from xml.etree import ElementTree  # noqa: F401 # pragma: no cover
    from PyQt6 import QtXml  # type: ignore[import] # noqa: F401 # pragma: no cover
#     import pineboolib.application.database.pnconnection
#     import pineboolib.application.metadata.pnfieldmetadata
#     import pineboolib.application.metadata.pntablemetadata
#     import pineboolib.application.metadata.pnrelationmetadata
#     import pineboolib.application.metadata.pnaction


class IManager(object):
    """
    Abstract class for FLManager.
    """

    list_tables_: List[str]  # Lista de las tablas de la base de datos, para optimizar lecturas
    dict_key_metadata_: Dict[
        str, str
    ]  # Diccionario de claves de metadatos, para optimizar lecturas
    cache_metadata_: Dict[
        str, "pntablemetadata.PNTableMetaData"
    ]  # Caché de metadatos, para optimizar lecturas
    _cache_action: Dict[
        str, "pnaction.PNAction"
    ]  # Caché de definiciones de acciones, para optimizar lecturas
    # Caché de metadatos de talblas del sistema para optimizar lecturas

    db_: "iconnection.IConnection"  # Base de datos a utilizar por el manejador

    __doc__: str
    buffer_: None

    def __init__(self, *args) -> None:
        """Create manager."""
        return None  # pragma: no cover

    def action(self, name: str) -> "pnaction.PNAction":  # "pnaction.PNAction"
        """Retrieve action object by name."""
        raise Exception("must be implemented")  # pragma: no cover

    def alterTable(self, metadata: "pntablemetadata.PNTableMetaData") -> bool:
        """Issue an alter table to db."""
        return False  # pragma: no cover

    def checkMetaData(self, mtd1, mtd2) -> bool:
        """Validate MTD against DB."""
        return False  # pragma: no cover

    def cleanupMetaData(self) -> None:
        """Clean up MTD."""
        return None  # pragma: no cover

    def createSystemTable(self, name: str) -> bool:
        """Create named system table."""
        return False  # pragma: no cover

    def createTable(self, name_or_metadata) -> Optional["pntablemetadata.PNTableMetaData"]:
        """Create new table."""
        return None  # pragma: no cover

    def existsTable(self, name: str, cache: bool = False) -> bool:
        """Check if table does exist in db."""
        return False  # pragma: no cover

    def fetchLargeValue(self, ref_key: str) -> Optional[str]:
        """Fetch from fllarge."""
        return None  # pragma: no cover

    def finish(self) -> None:
        """Finish?."""
        return None  # pragma: no cover

    def formatAssignValue(self, *args) -> str:
        """Format value for DB update."""
        return ""  # pragma: no cover

    def formatAssignValueLike(self, *args) -> str:
        """Format value for DB "LIKE" statement."""
        return ""  # pragma: no cover

    def formatValue(self, fmd_or_type: str, value: Any, upper: bool = False) -> str:
        """Format value for DB."""
        return ""  # pragma: no cover

    def formatValueLike(
        self,
        fmd_or_type: Union["pnfieldmetadata.PNFieldMetaData", str],
        value: Any,
        upper: bool = False,
    ) -> str:
        """Format value for DB LIKE."""
        return ""  # pragma: no cover

    def init(self) -> None:
        """Initialize this object."""
        return None  # pragma: no cover

    def initCount(self) -> int:
        """Track number of inits."""
        return 0  # pragma: no cover

    def isSystemTable(self, name: str) -> bool:
        """Return if given name is a system table."""
        return False  # pragma: no cover

    def loadTables(self) -> None:
        """Load tables."""
        return None  # pragma: no cover

    def metadata(
        self, name_or_xml, quick: bool = False
    ) -> Optional["pntablemetadata.PNTableMetaData"]:  # PNTableMetaData"
        """Retrieve table metadata by table name."""
        return None  # pragma: no cover

    def metadataField(
        self, field: "ElementTree.Element", vvisible: bool = False, ededitable: bool = False
    ) -> Optional["pnfieldmetadata.PNFieldMetaData"]:  # "PNFieldMetaData"
        """Retrieve field metadata."""
        raise Exception("must be implemented")  # pragma: no cover

    def metadataRelation(
        self, relation: Union["QtXml.QDomElement", "ElementTree.Element"]
    ) -> Optional["pnrelationmetadata.PNRelationMetaData"]:  # "PNRelationMetaData"
        """Retrieve relationship."""
        raise Exception("must be implemented")  # pragma: no cover

    def query(
        self, name: str, parent: Optional["pnsqlquery.PNSqlQuery"]
    ) -> Optional["pnsqlquery.PNSqlQuery"]:  # "PNSqlQuery"
        """Create query."""
        return None  # pragma: no cover

    def storeLargeValue(self, mtd, large_value: str) -> Optional[str]:
        """Store value in fllarge."""
        return None  # pragma: no cover
