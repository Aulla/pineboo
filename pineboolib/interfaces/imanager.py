"""
IManager Module.
"""
from typing import Any, Callable, Dict, Optional, Union, TYPE_CHECKING


if TYPE_CHECKING:
    from pineboolib.application.database import pnsqlquery  # noqa: F401 # pragma: no cover
    from pineboolib.application.metadata import pntablemetadata  # noqa: F401 # pragma: no cover
    from pineboolib.application.metadata import pnfieldmetadata  # noqa: F401 # pragma: no cover
    from pineboolib.application.metadata import pnrelationmetadata  # noqa: F401 # pragma: no cover
    from xml.etree import ElementTree  # noqa: F401 # pragma: no cover
    from PyQt5 import QtXml  # noqa: F401 # pragma: no cover
#     import pineboolib.application.database.pnconnection
#     import pineboolib.application.metadata.pnfieldmetadata
#     import pineboolib.application.metadata.pntablemetadata
#     import pineboolib.application.metadata.pnrelationmetadata
#     import pineboolib.application.metadata.pnaction


class IManager(object):
    """
    Abstract class for FLManager.
    """

    __doc__: str
    buffer_: None
    cacheAction_: Optional[Dict[str, Any]]  # "pnaction.PNAction"
    cacheMetaDataSys_: Optional[dict]
    cacheMetaData_: Optional[dict]
    db_: Optional[Any]  # "pineboolib.application.database.pnconnection.PNConnection"
    dictKeyMetaData_: Optional[Dict[str, Any]]
    initCount_: int
    listTables_: Any
    metadataCachedFails: list
    metadataDev: Callable
    queryGroup: Callable
    queryParameter: Callable

    def __init__(self, *args) -> None:
        """Create manager."""
        return None  # pragma: no cover

    def action(self, name: str) -> Any:  # "pnaction.PNAction"
        """Retrieve action object by name."""
        raise Exception("must be implemented")  # pragma: no cover

    def alterTable(self, metadata: "pntablemetadata.PNTableMetaData") -> bool:
        """Issue an alter table to db."""
        return False  # pragma: no cover

    def checkMetaData(self, mtd1, mtd2) -> Any:
        """Validate MTD against DB."""
        return None  # pragma: no cover

    def cleanupMetaData(self) -> None:
        """Clean up MTD."""
        return None  # pragma: no cover

    def createSystemTable(self, name: str) -> bool:
        """Create named system table."""
        return False  # pragma: no cover

    def createTable(self, name_or_metadata) -> Any:
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

    def formatAssignValue(self, *args, **kwargs) -> str:
        """Format value for DB update."""
        return ""  # pragma: no cover

    def formatAssignValueLike(self, *args, **kwargs) -> str:
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
