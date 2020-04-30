"""Flmanager module."""

# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtXml

from pineboolib.core import decorators, settings
from pineboolib.core.utils import utils_base

from pineboolib.application.metadata import (
    pncompoundkeymetadata,
    pntablemetadata,
    pnrelationmetadata,
    pnfieldmetadata,
)

from pineboolib.application.database import pnsqlquery, pngroupbyquery, pnsqlcursor
from pineboolib.application.utils import xpm, convert_flaction
from pineboolib.application import qsadictmodules

from pineboolib.interfaces import IManager

from pineboolib import logging, application

from . import flutil

from xml.etree import ElementTree

from typing import Optional, Union, Any, List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.interfaces import iconnection
    from pineboolib.application.metadata import pnaction


LOGGER = logging.get_logger(__name__)

# FIXME: This class is emulating Eneboo, but the way is set up it is a core part of Pineboo now.
# ... we should probably create our own one. Not this one.


class FLManager(QtCore.QObject, IManager):
    """
    Serve as the database administrator.

    Responsible for opening the forms or obtaining their definitions (.ui files).
    It also maintains the metadata of all tables in the database base.
    data, offering the ability to retrieve metadata
    using PNTableMetaData objects from a given table.

    @author InfoSiAL S.L.
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
    init_count_: int = 0  # Indica el número de veces que se ha llamado a FLManager::init()

    metadata_cache_fails_: List[str]

    def __init__(self, db: "iconnection.IConnection") -> None:
        """
        Inicialize.
        """
        super().__init__()
        self.db_ = db

        self.list_tables_ = []
        self.dict_key_metadata_ = {}
        self.cache_metadata_ = {}
        self._cache_action = {}
        QtCore.QTimer.singleShot(100, self.init)
        self.metadata_cache_fails_ = []
        self.init_count_ += 1

    def init(self) -> None:
        """
        Initialize.
        """
        self.init_count_ = self.init_count_ + 1
        # self.createSystemTable("flmetadata")
        # self.createSystemTable("flseqs")

        if not self.db_:
            raise Exception("FLManagar.__init__. self.db_ is empty!")

        if not self.db_.connManager().dbAux():
            return

        if not self.cache_metadata_:
            self.cache_metadata_ = {}

        if not self._cache_action:
            self._cache_action = {}

    def finish(self) -> None:
        """Apply close process."""

        self.dict_key_metadata_ = {}
        self.list_tables_ = []
        self.cache_metadata_ = {}
        self.metadata_cache_fails_ = []
        self._cache_action = {}

    def metadata(
        self,
        metadata_name_or_xml: Union[str, "ElementTree.Element", Dict[str, Any]],
        quick: bool = False,
    ) -> Optional["pntablemetadata.PNTableMetaData"]:
        """
        To obtain definition of a database table, from an XML file.

        The name of the table corresponds to the name of the file plus the extension ".mtd"
        which contains in XML the description of the tables. This method scans the file
        and builds / returns the corresponding PNTableMetaData object, in addition
        make a copy of these metadata in a table of the same database
        to be able to determine when it has been modified and thus, if necessary, rebuild
        the table so that it adapts to the new metadata. NOT MADE
        CHECKS OF SYNTATIC ERRORS IN THE XML.

        IMPORTANT: For these methods to work properly, it is strictly
            it is necessary to have created the database in PostgreSQL with coding
            UNICODE; "createdb -E UNICODE abanq".

        @param metadata_name_or_xml Name of the database table from which to obtain the metadata
        @param quick If TRUE does not check, use carefully
        @return A PNTableMetaData object with the metadata of the requested table
        """

        if not metadata_name_or_xml:
            return None

        if not self.db_:
            raise Exception("metadata. self.db_ is empty!")

        util = flutil.FLUtil()

        if quick is None:
            dbadmin = settings.CONFIG.value("application/dbadmin_enabled", False)
            quick = not bool(dbadmin)

        if isinstance(metadata_name_or_xml, str):
            ret: Any = False
            acl: Any = None
            key = metadata_name_or_xml.strip()
            stream = None

            if metadata_name_or_xml in self.metadata_cache_fails_:
                return None

            if key in self.cache_metadata_.keys():
                ret = self.cache_metadata_[key]

            if not ret:
                table_name = (
                    metadata_name_or_xml
                    if metadata_name_or_xml.endswith(".mtd")
                    else "%s.mtd" % metadata_name_or_xml
                )

                # Buscamos primero si es un model_.
                model_name = (
                    metadata_name_or_xml[: metadata_name_or_xml.find(".mtd")]
                    if metadata_name_or_xml.find(".mtd") > -1
                    else metadata_name_or_xml
                )
                model_ = qsadictmodules.QSADictModules.from_project("%s_orm" % model_name)
                if model_:

                    ret = self.metadata(model_.legacy_metadata)
                else:
                    # LOGGER.warning("metadata %s from xml is deprecated", metadata_name_or_xml)
                    stream = self.db_.connManager().managerModules().contentCached(table_name)

                    if not stream:
                        if metadata_name_or_xml.find("alteredtable") == -1:
                            LOGGER.info(
                                "FLManager : "
                                + util.translate(
                                    "FLManager",
                                    "Error al cargar los metadatos para la tabla %s"
                                    % metadata_name_or_xml,
                                )
                            )
                        self.metadata_cache_fails_.append(metadata_name_or_xml)
                        return None

                    # docElem = doc.documentElement()
                    # tree = utils_base.load2xml(stream)
                    tree = None
                    try:
                        tree = ElementTree.fromstring(stream)

                    except Exception as error:
                        LOGGER.error("Failed loading %s :%s", metadata_name_or_xml, error)

                    if tree is None:
                        return None

                    ret = self.metadata(tree, quick)
                if ret is None:
                    return None

                if not ret.isQuery() and not self.existsTable(metadata_name_or_xml):
                    self.createTable(ret)

                self.cache_metadata_[key] = ret

                if (
                    not quick
                    and not ret.isQuery()
                    and self.db_.mismatchedTable(metadata_name_or_xml, ret)
                    and self.existsTable(metadata_name_or_xml)
                ):
                    msg = util.translate(
                        "application",
                        "La estructura de los metadatos de la tabla '%s' y su estructura interna en la base de datos no coinciden.\n"
                        "Regenerando la base de datos." % metadata_name_or_xml,
                    )
                    LOGGER.warning(msg)

                    # must_alter = self.db_.mismatchedTable(metadata_name_or_xml, ret)
                    # if must_alter:
                    # if not self.alterTable(stream, stream, "", True):
                    if not self.alterTable(ret):
                        LOGGER.warning(
                            "La regeneración de la tabla %s ha fallado", metadata_name_or_xml
                        )

                # throwMsgWarning(self.db_, msg)

            acl = application.PROJECT.aq_app.acl()
            if acl:
                acl.process(ret)

            return ret

        elif isinstance(metadata_name_or_xml, dict):

            meta_dict = metadata_name_or_xml

            name = meta_dict["name"]
            alias = meta_dict["alias"]
            query = meta_dict["query"] if "query" in meta_dict.keys() else ""
            # visible = True
            # editable = True
            ftsfun = meta_dict["ftsfunction"] if "ftsfunction" in meta_dict.keys() else ""
            concur_warn = meta_dict["concurwarn"] if "concurwarn" in meta_dict.keys() else False
            detect_locks = meta_dict["detectlocks"] if "detectlocks" in meta_dict.keys() else False

            table_metadata = pntablemetadata.PNTableMetaData(name, alias, query)
            table_metadata.setFTSFunction(ftsfun)
            table_metadata.setConcurWarn(concur_warn)
            table_metadata.setDetectLocks(detect_locks)

            compound_key = pncompoundkeymetadata.PNCompoundKeyMetaData()
            assocs = []

            for child in meta_dict["fields"]:
                field_mtd = self.metadataField(child)
                table_metadata.addFieldMD(field_mtd)
                if field_mtd.isCompoundKey():
                    compound_key.addFieldMD(field_mtd)

                if field_mtd.associatedFieldName():
                    assocs.append(
                        [
                            field_mtd.associatedFieldName(),
                            field_mtd.associatedFieldFilterTo(),
                            field_mtd.name(),
                        ]
                    )

        else:
            # QDomDoc
            # root = n.getroot()
            name: str = ""  # type: ignore [no-redef] # noqa: F821
            query: str = ""  # type: ignore [no-redef] # noqa: F821
            alias: str = ""  # type: ignore [no-redef] # noqa: F821
            ftsfun: str = ""  # type: ignore [no-redef] # noqa: F821
            visible = True
            editable = True
            concur_warn = False
            detect_locks = False

            for child in metadata_name_or_xml:
                if child.tag == "field":
                    continue
                elif child.tag == "name":
                    name = child.text or ""
                elif child.tag == "query":
                    query = child.text or ""
                elif child.tag == "alias":
                    alias = util.translate(
                        "Metadata", utils_base.auto_qt_translate_text(child.text)
                    )
                elif child.tag == "visible":
                    visible = child.text == "true"
                elif child.tag == "editable":
                    editable = child.text == "true"
                elif child.tag == "detectLocks":
                    detect_locks = child.text == "true"
                elif child.tag == "concurWarn":
                    concur_warn = child.text == "true"
                elif child.tag == "FTSFunction":
                    ftsfun = child.text or ""

            table_metadata = pntablemetadata.PNTableMetaData(name, alias, query)

            table_metadata.setFTSFunction(ftsfun)
            table_metadata.setConcurWarn(concur_warn)
            table_metadata.setDetectLocks(detect_locks)

            compound_key = pncompoundkeymetadata.PNCompoundKeyMetaData()
            assocs = []

            for child in metadata_name_or_xml:
                if child.tag == "field":
                    field_mtd = self.metadataField(child, visible, editable)
                    table_metadata.addFieldMD(field_mtd)
                    if field_mtd.isCompoundKey():
                        compound_key.addFieldMD(field_mtd)

                    if field_mtd.associatedFieldName():
                        assocs.append(
                            [
                                field_mtd.associatedFieldName(),
                                field_mtd.associatedFieldFilterTo(),
                                field_mtd.name(),
                            ]
                        )

        table_metadata.setCompoundKey(compound_key)

        for assoc_with, assoc_by, field_name in assocs:
            field_metadata = table_metadata.field(field_name)
            assoc_field_mtd = table_metadata.field(assoc_with)
            if field_metadata and assoc_field_mtd and assoc_by:
                field_metadata.setAssociatedField(assoc_field_mtd, assoc_by)

        acl = application.PROJECT.aq_app.acl()
        if acl:
            acl.process(table_metadata)

        return table_metadata

    @decorators.not_implemented_warn
    def metadataDev(self, table_name: str, quick: bool = False) -> bool:
        """Return metadata (deprecated)."""
        return True

    def query(
        self, name: str, parent: Optional["pnsqlquery.PNSqlQuery"] = None
    ) -> Optional["pnsqlquery.PNSqlQuery"]:
        """
        To obtain a query of the database, from an XML file.

        The name of the query corresponds to the name of the file plus the extension ".qry"
        which contains the description of the query in XML. This method scans the file
        and build / return the FLSqlQuery object. NOT MADE
        CHECKS OF SYNTATIC ERRORS IN THE XML.

        @param name Name of the database query you want to obtain
        @return An FLSqlQuery object that represents the query you want to get
        """
        if self.db_ is None:
            raise Exception("query. self.db_ is empty!")

        qry_ = self.db_.connManager().managerModules().contentCached("%s.qry" % name)

        if not qry_:
            return None

        # parser_ = xml.etree.XMLParser(
        #    ns_clean=True,
        #    encoding="UTF-8",
        #    remove_blank_text=True,
        # )

        qry = pnsqlquery.PNSqlQuery()
        qry.setName(name)
        root_ = ElementTree.fromstring(qry_)
        elem_select = root_.find("select")
        elem_from = root_.find("from")
        elem_tables = root_.find("tables")
        elem_order = root_.find("order")
        group_xml = root_.findall("group") or []

        if elem_select is not None and elem_select.text:
            qry.setSelect(elem_select.text.strip(" \t\n\r"))

        if elem_from is not None and elem_from.text:
            qry.setFrom(elem_from.text.strip(" \t\n\r"))

        for where in root_.iter("where"):
            if where is not None and where.text:
                qry.setWhere(where.text.strip(" \t\n\r"))

        if elem_tables is not None and elem_tables.text:
            qry.setTablesList(elem_tables.text.strip(" \t\n\r"))

        if elem_order is not None and elem_order.text:
            qry.setOrderBy(elem_order.text.strip(" \t\n\r"))

        for level, item in enumerate(group_xml):
            elem_level = item.find("level")
            elem_field = item.find("field")
            if (
                elem_field is not None
                and elem_field.text
                and elem_level is not None
                and elem_level.text
            ):
                if float(elem_level.text.strip(" \t\n\r")) == level:
                    # print("LEVEL %s -> %s" % (i,gr.xpath("field/text()")[0].strip(' \t\n\r')))
                    qry.addGroup(
                        pngroupbyquery.PNGroupByQuery(level, elem_field.text.strip(" \t\n\r"))
                    )

        return qry

    def action(self, action_name: str) -> "pnaction.PNAction":
        """
        Return the definition of an action from its name.

        This method looks in the [id_modulo] .xml for the action that is passed
        as a name and build and return the corresponding FLAction object.
        NO SYMPATHIC ERROR CHECKS ARE MADE IN THE XML.

        @param n Name of the action
        @return A FLAction object with the description of the action

        """

        if not self.db_:
            raise Exception("action. self.db_ is empty!")

        # FIXME: This function is really inefficient. Pineboo already parses the actions much before.
        if action_name in self._cache_action.keys():
            pnaction_ = self._cache_action[action_name]
        else:

            pnaction_ = convert_flaction.convert_to_flaction(action_name)
            if not pnaction_.table():
                pnaction_.setTable(action_name)

            self._cache_action[action_name] = pnaction_

        return pnaction_

    def existsTable(self, table_name: str, cache: bool = True) -> bool:
        """
        Check if the table specified in the database exists.

        @param n Name of the table to check if it exists
        @param cache If a certain query first checks the table cache, otherwise
                    make a query to the base to obtain the existing tables
        @return TRUE if the table exists, FALSE otherwise.
        """
        if not self.db_ or table_name is None:
            return False

        if cache and table_name in self.list_tables_:
            return True
        else:
            return self.db_.existsTable(table_name)

    def checkMetaData(
        self,
        mtd1: Union[str, "pntablemetadata.PNTableMetaData"],
        mtd2: "pntablemetadata.PNTableMetaData",
    ) -> bool:
        """
        Compare the metadata of two tables.

        The XML definition of those two tables is they pass as two strings of characters.

        @param mtd1 Character string with XML describing the first table
        @param mtd2 Character string with XML describing the second table
        @return TRUE if the two descriptions are equal, and FALSE otherwise
        """
        if isinstance(mtd1, str):
            if mtd1 == mtd2.name():
                return True
            return False
        else:
            if mtd1 is None or mtd2 is None:
                return False

            for field1 in mtd1.fieldList():
                if field1.isCheck():
                    continue

                field2 = mtd2.field(field1.name())
                if field2 is None:
                    return False

                if field2.isCheck():
                    continue

                if field1.type() != field2.type() or field1.allowNull() != field2.allowNull():
                    return False

                if field1.isUnique() != field2.isUnique() or field1.isIndex() != field2.isIndex():
                    return False

                if (
                    field1.length() != field2.length()
                    or field1.partDecimal() != field2.partDecimal()
                    or field1.partInteger() != field2.partInteger()
                ):
                    return False

            for field1 in mtd2.fieldList():
                if field1.isCheck():
                    continue

                field2 = mtd1.field(field1.name())
                if field2 is None:
                    return False

                if field2.isCheck():
                    continue

                if field1.type() != field2.type() or field1.allowNull() != field2.allowNull():
                    return False

                if field1.isUnique() != field2.isUnique() or field1.isIndex() != field2.isIndex():
                    return False

                if (
                    field1.length() != field2.length()
                    or field1.partDecimal() != field2.partDecimal()
                    or field1.partInteger() != field2.partInteger()
                ):
                    return False

            return True

    def alterTable(self, new_metadata: "pntablemetadata.PNTableMetaData") -> bool:
        """
        Modify the structure or metadata of a table. Preserving the possible data that can contain.

        According to the existing definition of metadata in the .mtd file at a given time, this
        method reconstructs the table with those metadata without the loss of information or data,
        that might exist at that time in the table.

        @param n Name of the table to rebuild
        @param mtd1 XML description of the old structure
        @param mtd2 XML description of the new structure
        @param key Sha1 key of the old structure
        @return TRUE if the modification was successful
        """
        if not self.db_:
            raise Exception("alterTable. self.db_ is empty!")

        return self.db_.alterTable(new_metadata)

    def createTable(
        self, n_or_tmd: Union[str, "pntablemetadata.PNTableMetaData", None]
    ) -> Optional["pntablemetadata.PNTableMetaData"]:
        """
        Create a table in the database.

        @param n_tmd Name or metadata of the table you want to create
        @return A PNTableMetaData object with the metadata of the table that was created, or
          0 if the table could not be created or already existed
        """
        if not self.db_:
            raise Exception("createTable. self.db_ is empty!")

        if n_or_tmd is not None:

            if isinstance(n_or_tmd, str):
                tmd = self.metadata(n_or_tmd)
                if not tmd:
                    return None

                n_or_tmd = tmd

            if n_or_tmd.name() in self.list_tables_:
                return n_or_tmd

            if n_or_tmd.isQuery() or self.existsTable(n_or_tmd.name(), False):
                self.list_tables_.append(n_or_tmd.name())
                return n_or_tmd

            elif not self.db_.createTable(n_or_tmd):
                LOGGER.warning(
                    "createTable: %s", self.tr("No se ha podido crear la tabla ") + n_or_tmd.name()
                )
                return None
            # else:
            #    LOGGER.info("createTable: Created new table %r", n_or_tmd.name())

        return n_or_tmd

    def formatValueLike(
        self,
        fmd_or_type: Union["pnfieldmetadata.PNFieldMetaData", str],
        value: Any,
        upper: bool = False,
    ) -> str:
        """
        Return the value content of a formatted field.

        Return the value content of a formatted field to be recognized by the current database in LIKE conditions.
        within the SQL WHERE closing.

        This method takes as parameters the field metadata defined with
        PNFieldMetaData. In addition to TRUE and FALSE as possible values ​​of a field
        logical also accepts the values ​​Yes and No (or its translation into the corresponding language).
        The dates are adapted to the YYYY-MM-DD form, which is the format recognized by PostgreSQL.

        @param fmd_or_type PNFieldMetaData object that describes the metadata for the field
        @param value Value to be formatted for the indicated field
        @param upper If TRUE converts the value to uppercase (if it is a string type)
        """

        if not self.db_:
            raise Exception("formatValueLike. self.db_ is empty!")

        if not isinstance(fmd_or_type, str):
            fmd_or_type = fmd_or_type.type()

        return self.db_.formatValueLike(fmd_or_type, value, upper)

    def formatAssignValueLike(self, *args, **kwargs) -> str:
        """
        Return the value content of a formatted field to be recognized by the current database, within the SQL WHERE closing.

        This method takes as parameters the field metadata defined with
        PNFieldMetaData. In addition to TRUE and FALSE as possible values ​​of a field
        logical also accepts the values ​​Yes and No (or its translation into the corresponding language).
        The dates are adapted to the YYYY-MM-DD form, which is the format recognized by PostgreSQL.

        @param field_metadata PNFieldMetaData object that describes the metadata for the field
        @param v Value to be formatted for the indicated field
        @param upper If TRUE converts the value to uppercase (if it is a string type)
        """

        type_: str = ""
        field_name_: str = ""
        value_: Any = args[1]
        upper_: bool = args[2]

        if isinstance(args[0], pnfieldmetadata.PNFieldMetaData):

            field_name_ = args[0].name()
            type_ = args[0].type()

            mtd_ = args[0].metadata()

            if mtd_ is None:
                return ""

            if args[0].isPrimaryKey():
                field_name_ = mtd_.primaryKey(True)

            item_field_name = args[0].name()
            if mtd_.isQuery() and field_name_.find(".") == -1:
                qry = pnsqlquery.PNSqlQuery(mtd_.query())

                if qry:
                    field_list = qry.fieldList()

                for item in field_list:
                    if item.find(".") > -1:
                        item_field_name = item[item.find(".") + 1 :]
                    else:
                        item_field_name = item

                    if item_field_name == field_name_:
                        break

            field_name_ = "%s.%s" % (mtd_.name(), item_field_name)

        elif isinstance(args[1], pnfieldmetadata.PNFieldMetaData):

            field_name_ = args[0]
            type_ = args[1].type()
        else:

            field_name_ = args[0]
            type_ = args[1]

            if len(args) == 4:
                value_ = args[2]
                upper_ = args[3]

        is_text = type_ in ["string", "stringlist", "timestamp"]
        format_value_ = self.formatValueLike(type_, value_, upper_)

        if not format_value_:
            return "1 = 1"

        if is_text:
            if upper_:
                field_name_ = "upper(%s)" % field_name_

        return "%s %s" % (field_name_, format_value_)

    def formatValue(self, field_metadata_or_type: str, v: Any, upper: bool = False) -> str:
        """Return format value."""

        if not self.db_:
            raise Exception("formatValue. self.db_ is empty!")

        if not field_metadata_or_type:
            raise ValueError("field_metadata_or_type is required")

        if not isinstance(field_metadata_or_type, str):
            field_metadata_or_type = field_metadata_or_type.type()

        return str(self.db_.formatValue(field_metadata_or_type, v, upper))

    def formatAssignValue(self, *args, **kwargs) -> str:
        """Return format assign value."""

        if args[0] is None:
            # print("FLManager.formatAssignValue(). Primer argumento vacio %s" % args[0])
            return "1 = 1"

        field_name_: str = ""
        field_type_: str = ""
        value_: Any = None
        upper_: bool = False

        # print("tipo 0", type(args[0]))
        # print("tipo 1", type(args[1]))
        # print("tipo 2", type(args[2]))]

        if isinstance(args[0], pnfieldmetadata.PNFieldMetaData) and len(args) == 3:
            field_metadata = args[0]
            mtd = field_metadata.metadata()
            if mtd is None:
                field_name_ = field_metadata.name()
                field_type_ = field_metadata.type()
                value_ = args[1]
                upper_ = args[2]

            elif field_metadata.isPrimaryKey():
                field_name_ = mtd.primaryKey(True)
                field_type_ = field_metadata.type()
                value_ = args[1]
                upper_ = args[2]
            else:

                field_name_ = field_metadata.name()
                if mtd.isQuery() and "." not in field_name_:
                    prefix_table_ = mtd.name()
                    qry = self.query(mtd.query())

                    if qry:

                        for field in qry.fieldList():
                            # print("fieldName = " + f)

                            field_section_ = field
                            pos = field.find(".")
                            if pos > -1:
                                prefix_table_ = field[:pos]
                                field_section_ = field[pos + 1 :]
                            else:
                                field_section_ = field

                            # prefixTable = f.section('.', 0, 0)
                            # if f.section('.', 1, 1) == fieldName:
                            if field_section_ == field_name_:
                                break

                    # fieldName.prepend(prefixTable + ".")
                    field_name_ = "%s.%s" % (prefix_table_, field_name_)

                field_type_ = args[0].type()
                value_ = args[1]
                upper_ = args[2]

        elif isinstance(args[1], pnfieldmetadata.PNFieldMetaData) and isinstance(args[0], str):

            field_name_ = args[0]
            field_type_ = args[1].type()
            value_ = args[2]
            upper_ = args[3]

        elif isinstance(args[0], pnfieldmetadata.PNFieldMetaData) and len(args) == 2:

            field_name_ = args[0].name()
            field_type_ = args[0].type()
            value_ = args[1]
            upper_ = False

        elif isinstance(args[0], str):
            field_name_ = args[0]
            field_type_ = args[1]
            value_ = args[2]
            upper_ = args[3]

        if not field_type_:
            return "1 = 1"

        format_value_ = self.formatValue(field_type_, value_, upper_)
        if format_value_ is None:
            return "1 = 1"

        if not field_name_:
            field_name_ = args[0] if isinstance(args[0], str) else args[0].name()

        if upper_ and field_type_ in ["string", "stringlist", "timestamp"]:
            field_name_ = "upper(%s)" % field_name_

        if field_type_ == "string":
            if format_value_.find("%") > -1:
                retorno = "%s LIKE %s" % (field_name_, format_value_)
            else:
                retorno = "%s = %s" % (field_name_, format_value_)
        else:
            retorno = "%s = %s" % (field_name_, format_value_)

        return retorno

    def metadataField(
        self, field: Union["ElementTree.Element", Dict], v: bool = True, ed: bool = True
    ) -> "pnfieldmetadata.PNFieldMetaData":
        """
        Create a PNFieldMetaData object from an XML element.

        Given an XML element, which contains the description of a
        table field builds and adds to a list of descriptions
        of fields the corresponding PNFieldMetaData object, which contains
        said definition of the field. It also adds it to a list of keys
        composite, if the constructed field belongs to a composite key.
        NO SYMPATHIC ERROR CHECKS ARE MADE IN THE XML.

        @param field XML element with field description
        @param v Default value used for the visible property
        @param ed Value used by default for editable property
        @return PNFieldMetaData object that contains the description of the field
        """
        if not field:
            raise ValueError("field is required")

        valid_types = [
            "int",
            "uint",
            "bool",
            "double",
            "time",
            "date",
            "pixmap",
            "bytearray",
            "string",
            "stringlist",
            "unlock",
            "serial",
            "timestamp",
        ]
        util = flutil.FLUtil()

        compound_key = False
        name: str = ""
        alias: str = ""
        options_list: Optional[str] = None
        reg_exp = None
        search_options = None

        as_null = True
        is_primary_key = False
        calculated = False
        is_index = False
        is_unique = False
        coun = False
        out_transaction = False
        visible_grid = True
        full_calculated = False
        trimm = False
        visible = True
        editable = True

        type_: Optional[str] = None
        length = 0
        part_integer = 4
        part_decimal = 0

        default_value = None
        if isinstance(field, dict):
            for tag in field.keys():
                if tag in ("relation", "associated"):
                    continue

                elif tag == "name":
                    name = field[tag]

                elif tag == "alias":
                    alias = utils_base.auto_qt_translate_text(field[tag])

                elif tag == "null":
                    as_null = field[tag]

                elif tag == "pk":
                    is_primary_key = field[tag]

                elif tag == "type":
                    type_ = field[tag]

                elif tag == "length":
                    length = field[tag]

                elif tag == "regexp":
                    reg_exp = field[tag]

                elif tag == "default":
                    default_value = field[tag]
                    if isinstance(default_value, str):
                        default_value = utils_base.auto_qt_translate_text(default_value)

                elif tag == "outtransaction":
                    out_transaction = field[tag]

                elif tag == "counter":
                    coun = field[tag]

                elif tag == "calculated":
                    calculated = field[tag]

                elif tag == "fullycalculated":
                    full_calculated = field[tag]

                elif tag == "trimmed":
                    trimm = field[tag]

                elif tag == "visible":
                    visible = field[tag]

                elif tag == "visiblegrid":
                    visible_grid = field[tag]

                elif tag == "editable":
                    editable = field[tag]

                elif tag == "partI":
                    part_integer = field[tag]

                elif tag == "partD":
                    part_decimal = field[tag]

                elif tag == "index":
                    is_index = field[tag]

                elif tag == "unique":
                    is_unique = field[tag]

                elif tag == "ck":
                    compound_key = field[tag]

                elif tag == "optionslist":
                    options_list = ", ".join(field[tag])

                elif tag == "searchoptions":
                    search_options = ", ".join(field[tag])

        else:
            for child in field:
                tag = child.tag
                if tag in ("relation", "associated"):
                    continue

                elif tag == "name":
                    name = child.text or ""
                    continue

                elif tag == "alias":
                    alias = utils_base.auto_qt_translate_text(child.text)
                    continue

                elif tag == "null":
                    as_null = child.text == "true"
                    continue

                elif tag == "pk":
                    is_primary_key = child.text == "true"
                    continue

                elif tag == "type":
                    type_ = child.text
                    if type_ not in valid_types:
                        type_ = None
                    continue

                elif tag == "length":
                    length = int(child.text or 0)
                    continue

                elif tag == "regexp":
                    reg_exp = child.text
                    continue

                elif tag == "default":
                    default_value = child.text or ""
                    if default_value.find("QT_TRANSLATE_NOOP") > -1:
                        default_value = utils_base.auto_qt_translate_text(default_value)
                    continue
                elif tag == "outtransaction":
                    out_transaction = child.text == "true"
                    continue
                elif tag == "counter":
                    coun = child.text == "true"
                    continue
                elif tag == "calculated":
                    calculated = child.text == "true"
                    continue
                elif tag == "fullycalculated":
                    full_calculated = child.text == "true"
                    continue
                elif tag == "trimmed":
                    trimm = child.text == "true"
                    continue
                elif tag == "visible":
                    visible = child.text == "true"
                    continue
                elif tag == "visiblegrid":
                    visible_grid = child.text == "true"
                    continue
                elif tag == "editable":
                    editable = child.text == "true"
                    continue
                elif tag == "partI":
                    part_integer = int(child.text or 4)
                    continue
                elif tag == "partD":
                    part_decimal = int(child.text or 0)
                    continue
                elif tag == "index":
                    is_index = child.text == "true"
                    continue
                elif tag == "unique":
                    is_unique = child.text == "true"
                    continue
                elif tag == "ck":
                    compound_key = child.text == "true"
                    continue
                elif tag == "optionslist":
                    options_list = child.text
                    continue
                elif tag == "searchoptions":
                    search_options = child.text
                    continue

        field_mtd = pnfieldmetadata.PNFieldMetaData(
            name,
            util.translate("Metadata", alias),
            as_null,
            is_primary_key,
            type_,
            length,
            calculated,
            visible,
            editable,
            part_integer,
            part_decimal,
            is_index,
            is_unique,
            coun,
            default_value,
            out_transaction,
            reg_exp,
            visible_grid,
            True,
            compound_key,
        )
        field_mtd.setFullyCalculated(full_calculated)
        field_mtd.setTrimed(trimm)

        if options_list:
            field_mtd.setOptionsList(options_list)
        if search_options:
            field_mtd.setSearchOptions(search_options)

        assoc_by = ""
        assoc_with = ""
        if isinstance(field, dict):
            for tag in field.keys():
                if tag == "relations":
                    for rel_ in field[tag]:
                        field_mtd.addRelationMD(self.metadataRelation(rel_))

                elif tag == "associated":
                    for sub_tag in field[tag].keys():
                        if sub_tag == "with":
                            assoc_with = field[tag][sub_tag]
                        elif sub_tag == "by":
                            assoc_by = field[tag][sub_tag]

            if assoc_with and assoc_by:
                field_mtd.setAssociatedField(assoc_with, assoc_by)

        else:

            for child in field:
                tag = child.tag
                if tag == "relation":
                    field_mtd.addRelationMD(self.metadataRelation(child))
                    continue
                elif tag == "associated":
                    for sub in child:
                        sub_tag = sub.tag
                        if sub_tag == "with":
                            assoc_with = sub.text or ""
                        elif sub_tag == "by":
                            assoc_by = sub.text or ""

            if assoc_with and assoc_by:
                field_mtd.setAssociatedField(assoc_with, assoc_by)

        return field_mtd

    def metadataRelation(
        self, relation: Union[QtXml.QDomElement, "ElementTree.Element"]
    ) -> "pnrelationmetadata.PNRelationMetaData":
        """
        Create a FLRelationMetaData object from an XML element.

        Given an XML element, which contains the description of a
        relationship between tables, builds and returns the FLRelationMetaData object
        corresponding, which contains said definition of the relationship.
        NO SYMPATHIC ERROR CHECKS ARE MADE IN THE XML.

        @param relation XML element with the description of the relationship
        @return FLRelationMetaData object that contains the description of the relationship
        """
        if not relation:
            raise ValueError("relation is required")

        foreign_table = ""
        foreign_field = ""
        relation_card = pnrelationmetadata.PNRelationMetaData.RELATION_M1
        delete_cascade = False
        update_cascade = False
        check_integrity = True

        if isinstance(relation, QtXml.QDomElement):
            LOGGER.warning(
                "QtXml.QDomElement is deprecated for declare metadata relation. Please use xml.etree.ElementTree.ElementTree instead"
            )
            node = relation.firstChild()

            while not node.isNull():
                elem = node.toElement()
                if not elem.isNull():

                    if elem.tagName() == "table":
                        foreign_table = elem.text()
                        node = node.nextSibling()
                        continue

                    elif elem.tagName() == "field":
                        foreign_field = elem.text()
                        node = node.nextSibling()
                        continue

                    elif elem.tagName() == "card":
                        if elem.text() == "1M":
                            relation_card = pnrelationmetadata.PNRelationMetaData.RELATION_1M

                        node = node.nextSibling()
                        continue

                    elif elem.tagName() == "delC":
                        delete_cascade = elem.text() == "true"
                        node = node.nextSibling()
                        continue

                    elif elem.tagName() == "updC":
                        update_cascade = elem.text() == "true"
                        node = node.nextSibling()
                        continue

                    elif elem.tagName() == "checkIn":
                        check_integrity = elem.text() == "true"
                        node = node.nextSibling()
                        continue

                node = node.nextSibling()

        elif isinstance(relation, dict):
            for key in relation.keys():
                if key == "table":
                    foreign_table = relation[key]
                elif key == "field":
                    foreign_field = relation[key]
                elif key == "card":
                    if relation[key] == "1M":
                        relation_card = pnrelationmetadata.PNRelationMetaData.RELATION_1M
                elif key == "delC":
                    delete_cascade = relation[key]
                elif key == "updC":
                    update_cascade = relation[key]
                elif key == "checkIn":
                    check_integrity = relation[key]
        else:
            for child in relation:
                tag = child.tag
                if tag == "table":
                    foreign_table = child.text or ""
                    continue
                elif tag == "field":
                    foreign_field = child.text or ""
                    continue
                elif tag == "card":
                    if child.text == "1M":
                        relation_card = pnrelationmetadata.PNRelationMetaData.RELATION_1M
                    continue
                elif tag == "delC":
                    delete_cascade = child.text == "true"
                    continue
                elif tag == "updC":
                    update_cascade = child.text == "true"
                    continue
                elif tag == "checkIn":
                    check_integrity = child.text == "true"
                    continue

        return pnrelationmetadata.PNRelationMetaData(
            foreign_table,
            foreign_field,
            relation_card,
            delete_cascade,
            update_cascade,
            check_integrity,
        )

    @decorators.not_implemented_warn
    def queryParameter(self, parameter: QtXml.QDomElement) -> Any:
        """
        Create an FLParameterQuery object from an XML element.

        Given an XML element, which contains the description of a
        parameter of a query, build and return the FLParameterQuery object
        correspondent.
        NO SYMPATHIC ERROR CHECKS ARE MADE IN THE XML.

        @param parameter XML element with the description of the parameter of a query
        @return FLParameterQuery object that contains the parameter description.
        """
        return True

    @decorators.not_implemented_warn
    def queryGroup(self, group: QtXml.QDomElement) -> Any:
        """
        Create a FLGroupByQuery object from an XML element.

        Given an XML element, which contains the description of a grouping level
        of a query, build and return the corresponding FLGroupByQuery object.
        NO SYMPATHIC ERROR CHECKS ARE MADE IN THE XML.

        @param group XML element with the description of the grouping level of a query.
        @return FLGroupByQuery object that contains the description of the grouping level
        """
        return True

    def createSystemTable(self, table_name: str) -> bool:
        """
        Create a system table.

        This method reads directly from disk the file with the description of a table
        of the system and creates it in the database. Its normal use is to initialize
        The system with initial tables.

        @param table_name Name of the table.
        @return A PNTableMetaData object with the metadata of the table that was created, or
          False if the table could not be created or already existed.
        """
        # if not self.existsTable(table_name):
        if self.createTable(self.metadata("%s.mtd" % table_name, True)):
            return True

        return False

    def loadTables(self) -> None:
        """
        Load in the table list the names of the database tables.
        """
        if not self.db_:
            raise Exception("loadTables. self.db_ is empty!")

        self.list_tables_.clear()

        self.list_tables_ = self.db_.connManager().dbAux().tables()

    def cleanupMetaData(self) -> None:
        """
        Clean the flmetadata table, update the xml content with that of the .mtd file currently loaded.
        """
        if not self.db_:
            raise Exception("cleanupMetaData. self.db_ is empty!")

        # util = flutil.FLUtil()
        if not self.existsTable("flfiles") or not self.existsTable("flmetadata"):
            return

        buffer = None
        table = ""

        # q.setForwardOnly(True)
        # c.setForwardOnly(True)

        if self.dict_key_metadata_:
            self.dict_key_metadata_.clear()
        else:
            self.dict_key_metadata_ = {}

        if self.metadata_cache_fails_:
            self.metadata_cache_fails_.clear()

        self.metadata_cache_fails_ = []

        self.loadTables()
        self.db_.connManager().managerModules().loadKeyFiles()
        self.db_.connManager().managerModules().loadAllIdModules()
        self.db_.connManager().managerModules().loadIdAreas()

        qry = pnsqlquery.PNSqlQuery(None, "dbAux")
        qry.exec_("SELECT tabla,xml FROM flmetadata")
        while qry.next():
            self.dict_key_metadata_[str(qry.value(0))] = str(qry.value(1))

        cursor = pnsqlcursor.PNSqlCursor("flmetadata", True, "dbAux")

        qry2 = pnsqlquery.PNSqlQuery(None, "dbAux")
        qry2.exec_(
            "SELECT nombre,sha FROM flfiles WHERE nombre LIKE '%.mtd' and nombre not like '%%alteredtable%'"
        )
        while qry2.next():
            table = str(qry2.value(0))
            table = table.replace(".mtd", "")
            tmd = self.metadata(table)
            if not self.existsTable(table):
                self.createTable(table)
            if not tmd:
                LOGGER.warning(
                    "FLManager::cleanupMetaData %s",
                    flutil.FLUtil().translate(
                        "application", "No se ha podido crear los metadatatos para la tabla %s"
                    )
                    % table,
                )
                continue

            cursor.select("tabla = '%s'" % table)
            if cursor.next():
                buffer = cursor.prime_update()
                buffer.set_value("xml", qry2.value(1))
                cursor.update()
            self.dict_key_metadata_[table] = qry2.value(1)

    def isSystemTable(self, table_name: str) -> bool:
        """
        Return if the given table is a system table.

        @param n Name of the table.
        @return TRUE if it is a system table
        """
        return (
            True
            if table_name[0:3] == "sys"
            or table_name.startswith(
                (
                    "flfiles",
                    "flmetadata",
                    "flmodules",
                    "flareas",
                    "flserial",
                    "flvar",
                    "flsettings",
                    "flseqs",
                    "flupdates",
                    "flacls",
                    "flacos",
                    "flacs",
                    "flgroups",
                    "flusers",
                )
            )
            else False
        )

    def storeLargeValue(
        self, mtd: "pntablemetadata.PNTableMetaData", large_value: str
    ) -> Optional[str]:
        """
        Store large field values ​​in separate indexed tables by SHA keys of the value content.

        It is used to optimize queries that include fields with large values,
        such as images, to handle the reference to the value in the SQL queries
        which is of constant size instead of the value itself. This decreases traffic by
        considerably reduce the size of the records obtained.

        Queries can use a reference and get its value only when
        you need via FLManager :: fetchLargeValue ().


        @param mtd Metadata of the table containing the field
        @param large_value Large field value
        @return Value reference key
        """
        if not self.db_:
            raise Exception("storeLareValue. self.db_ is empty!")

        if large_value[0:3] == "RK@":
            return None

        table_name = mtd.name()

        table_large = "fllarge"

        if not application.PROJECT.aq_app.singleFLLarge():
            table_large = "fllarge_%s" % table_name

            if not self.existsTable(table_large):
                mtd_large = pntablemetadata.PNTableMetaData(table_large, table_large)
                field_refkey = pnfieldmetadata.PNFieldMetaData(
                    "refkey", "refkey", False, True, "string", 100
                )

                field_sha = pnfieldmetadata.PNFieldMetaData("sha", "sha", True, False, "string", 50)

                field_contenido = pnfieldmetadata.PNFieldMetaData(
                    "contenido", "contenido", True, False, "stringlist"
                )

                mtd_large.addFieldMD(field_refkey)
                mtd_large.addFieldMD(field_sha)
                mtd_large.addFieldMD(field_contenido)

                if not self.createTable(mtd_large):
                    return None

        util = flutil.FLUtil()
        sha = str(util.sha1(large_value))
        ref_key = "RK@%s@%s" % (table_name, sha)
        qry = pnsqlquery.PNSqlQuery(None, "dbAux")
        qry.setSelect("refkey")
        qry.setFrom(table_large)
        qry.setWhere(" refkey = '%s'" % ref_key)
        if qry.exec_() and qry.first():
            if qry.value(0) != sha:
                sql = "UPDATE %s SET contenido = '%s' WHERE refkey ='%s'" % (
                    table_large,
                    large_value,
                    ref_key,
                )
                if not util.execSql(sql, "dbAux"):
                    LOGGER.warning(
                        "FLManager::ERROR:StoreLargeValue.Update %s.%s", table_large, ref_key
                    )
                    return None
        else:
            sql = "INSERT INTO %s (contenido,refkey) VALUES ('%s','%s')" % (
                table_large,
                large_value,
                ref_key,
            )
            if not util.execSql(sql, "dbAux"):
                LOGGER.warning(
                    "FLManager::ERROR:StoreLargeValue.Insert %s.%s", table_large, ref_key
                )
                return None

        return ref_key

    def fetchLargeValue(self, ref_key: Optional[str]) -> Optional[str]:
        """
        Return the large value according to its reference key.

        @param ref_key Reference key. This key is usually obtained through FLManager :: storeLargeValue
        @return Large value stored
        """
        if ref_key and ref_key[0:3] == "RK@":

            table_name = (
                "fllarge"
                if application.PROJECT.aq_app.singleFLLarge()
                else "fllarge_" + ref_key.split("@")[1]
            )

            if self.existsTable(table_name):
                qry = pnsqlquery.PNSqlQuery(None, "dbAux")
                qry.setSelect("contenido")
                qry.setFrom(table_name)
                qry.setWhere("refkey = '%s'" % ref_key)
                if qry.exec_() and qry.first():
                    return xpm.cache_xpm(qry.value(0))

        return None

    def initCount(self) -> int:
        """
        Indicate the number of times FLManager :: init () has been called.
        """
        return self.init_count_
