"""Flmanager module."""

# -*- coding: utf-8 -*-
from PyQt5 import QtCore  # type: ignore
from PyQt5.QtXml import QDomDocument  # type: ignore


from pineboolib.core import decorators
from pineboolib.core.settings import config
from pineboolib.core.utils.utils_base import filedir, auto_qt_translate_text
from pineboolib.application.utils.xpm import cacheXPM


from pineboolib.application.metadata.pncompoundkeymetadata import PNCompoundKeyMetaData
from pineboolib.application.metadata.pntablemetadata import PNTableMetaData
from pineboolib.application.metadata.pnrelationmetadata import PNRelationMetaData
from pineboolib.application.metadata.pnfieldmetadata import PNFieldMetaData

from .flutil import FLUtil

from xml import etree  # type: ignore
from pineboolib import logging
from pineboolib.interfaces import IManager

from PyQt5.QtXml import QDomElement  # type: ignore


from pineboolib.application.database.pnsqlquery import PNSqlQuery
from pineboolib.application.database.pngroupbyquery import PNGroupByQuery
from pineboolib.application.database.pnsqlcursor import PNSqlCursor

from typing import Optional, Union, Any, List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.interfaces.iconnection import IConnection
    from pineboolib.application.metadata import pnaction

logger = logging.getLogger(__name__)

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

    listTables_: List[str] = []  # Lista de las tablas de la base de datos, para optimizar lecturas
    dictKeyMetaData_: Dict[str, str]  # Diccionario de claves de metadatos, para optimizar lecturas
    cacheMetaData_: Dict[str, PNTableMetaData]  # Caché de metadatos, para optimizar lecturas
    cacheAction_: Dict[
        str, "pnaction.PNAction"
    ]  # Caché de definiciones de acciones, para optimizar lecturas
    # Caché de metadatos de talblas del sistema para optimizar lecturas
    cacheMetaDataSys_: Dict[str, PNTableMetaData]
    db_: "IConnection"  # Base de datos a utilizar por el manejador
    initCount_: int  # Indica el número de veces que se ha llamado a FLManager::init()
    buffer_: Any
    metadataCachedFails: List[str]

    def __init__(self, db: "IConnection") -> None:
        """
        Inicialize.
        """
        super(FLManager, self).__init__()
        self.db_ = db
        self.buffer_ = None
        self.listTables_ = []
        self.dictKeyMetaData_ = {}
        self.initCount_ = 0
        self.cacheMetaData_ = {}
        self.cacheMetaDataSys_ = {}
        self.cacheAction_ = {}
        QtCore.QTimer.singleShot(100, self.init)
        self.metadataCachedFails = []

    def init(self) -> None:
        """
        Initialize.
        """
        self.initCount_ = self.initCount_ + 1
        self.createSystemTable("flmetadata")
        self.createSystemTable("flseqs")

        if not self.db_:
            raise Exception("FLManagar.__init__. self.db_ is empty!")

        if not self.db_.dbAux():
            return

        # q = PNSqlQuery(None, self.db_.dbAux())
        # q.setForwardOnly(True)

        self.createSystemTable("flsettings")
        """
        if not q.exec_("SELECT * FROM flsettings WHERE flkey = 'sysmodver'"):

            if project.conn.driver().cascadeSupport():
                q.exec_("DROP TABLE flsettings CASCADE")
            else:
                q.exec_("DROP TABLE flsettings")

            self.createSystemTable("flsettings")

        if not self.dictKeyMetaData_:
            self.dictKeyMetaData_ = {}
            # self.dictKeyMetaData_.setAutoDelete(True)
        else:
            self.dictKeyMetaData_.clear()

        q.exec_("SELECT tabla,xml FROM flmetadata")
        while q.next():
            self.dictKeyMetaData_[q.value(0)] = q.value(1)

        q.exec_("SELECT * FROM flsettings WHERE flkey = 'sysmodver'")
        if not q.next():

            if project.conn.driver().cascadeSupport():
                q.exec_("DROP TABLE flmetadata CASCADE")
            else:
                q.exec_("DROP TABLE flmetadata")

            self.createSystemTable("flmetadata")

            c = FLSqlCursor("flmetadata", True, self.db_.dbAux())
            for key, value in self.dictKeyMetaData_:
                buffer = c.primeInsert()
                buffer.setValue("tabla", key)
                buffer.setValue("xml", value)
                c.insert()
        """
        if not self.cacheMetaData_:
            self.cacheMetaData_ = {}

        if not self.cacheAction_:
            self.cacheAction_ = {}

        if not self.cacheMetaDataSys_:
            self.cacheMetaDataSys_ = {}

    def finish(self) -> None:
        """Apply close process."""

        self.dictKeyMetaData_ = {}
        self.listTables_ = []
        self.cacheMetaData_ = {}
        self.cacheAction_ = {}

        del self

    def metadata(
        self, n: Union[str, QDomElement], quick: Optional[bool] = None
    ) -> Optional["PNTableMetaData"]:
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

        @param n Name of the database table from which to obtain the metadata
        @param quick If TRUE does not check, use carefully
        @return A PNTableMetaData object with the metadata of the requested table
        """

        util = FLUtil()

        if not n:
            return None

        if not self.db_:
            raise Exception("metadata. self.db_ is empty!")

        if quick is None:
            dbadmin = config.value("application/dbadmin_enabled", False)
            quick = not bool(dbadmin)

        if isinstance(n, str):
            if not n:
                return None

            ret: Any = False
            acl: Any = None
            key = n.strip()
            stream = None
            isSysTable = n[0:3] == "sys" or self.isSystemTable(n)

            if n in self.metadataCachedFails:
                return None

            elif isSysTable:
                if key in self.cacheMetaDataSys_.keys():
                    ret = self.cacheMetaDataSys_[key]
            else:
                if key in self.cacheMetaData_.keys():
                    ret = self.cacheMetaData_[key]

            if not ret:
                stream = self.db_.managerModules().contentCached("%s.mtd" % n)

                if not stream:
                    if n.find("alteredtable") == -1:
                        logger.info(
                            "FLManager : "
                            + util.tr("Error al cargar los metadatos para la tabla %s" % n)
                        )
                    self.metadataCachedFails.append(n)
                    return None

                doc = QDomDocument(n)

                if not util.domDocumentSetContent(doc, stream):
                    logger.info(
                        "FLManager : "
                        + util.tr("Error al cargar los metadatos para la tabla %s" % n)
                    )
                    self.metadataCachedFails.append(n)
                    return None

                docElem = doc.documentElement()
                ret = self.metadata(docElem, quick)
                if ret is None:
                    return None

                if not ret.isQuery() and not self.existsTable(n):
                    self.createTable(ret)

                if not isSysTable:
                    self.cacheMetaData_[key] = ret
                else:
                    self.cacheMetaDataSys_[key] = ret

                if (
                    not quick
                    and not isSysTable
                    and not ret.isQuery()
                    and self.db_.mismatchedTable(n, ret)
                    and self.existsTable(n)
                ):
                    msg = util.translate(
                        "application",
                        "La estructura de los metadatos de la tabla '%1' y su estructura interna en la base de datos no coinciden.\n"
                        "Regenerando la base de datos.",
                    ).replace("%1", n)
                    logger.warning(msg)

                    must_alter = self.db_.mismatchedTable(n, ret)
                    if must_alter:
                        if not self.alterTable(stream, stream, "", True):
                            logger.warning("La regeneración de la tabla %s ha fallado", n)

                # throwMsgWarning(self.db_, msg)
            from pineboolib.fllegacy import flapplication

            acl = flapplication.aqApp.acl()
            if acl:
                acl.process(ret)

            return ret

        else:
            # QDomDoc
            name = None
            q = None
            a = None
            ftsfun = None
            v = True
            ed = True
            cw = False
            dl = False
            no = n.firstChild()
            while not no.isNull():
                e = no.toElement()
                if not e.isNull():
                    if e.tagName() == "field":
                        no = no.nextSibling()
                        continue

                    elif e.tagName() == "name":
                        name = e.text()
                        no = no.nextSibling()
                        continue

                    elif e.tagName() == "query":
                        q = e.text()
                        no = no.nextSibling()
                        continue

                    elif e.tagName() == "alias":
                        a = auto_qt_translate_text(e.text())
                        a = util.translate("Metadata", a)
                        no = no.nextSibling()
                        continue

                    elif e.tagName() == "visible":
                        v = e.text() == "true"
                        no = no.nextSibling()
                        continue

                    elif e.tagName() == "editable":
                        ed = e.text() == "true"
                        no = no.nextSibling()
                        continue

                    elif e.tagName() == "concurWarn":
                        cw = e.text() == "true"
                        no = no.nextSibling()
                        continue

                    elif e.tagName() == "detectLocks":
                        dl = e.text() == "true"
                        no = no.nextSibling()
                        continue

                    elif e.tagName() == "FTSFunction":
                        ftsfun = e.text()
                        no = no.nextSibling()
                        continue

                no = no.nextSibling()
            tmd = PNTableMetaData(name, a, q)
            cK = None
            assocs = []
            tmd.setFTSFunction(ftsfun or "")
            tmd.setConcurWarn(cw)
            tmd.setDetectLocks(dl)
            no = n.firstChild()

            while not no.isNull():
                e = no.toElement()
                if not e.isNull():
                    if e.tagName() == "field":
                        f = self.metadataField(e, v, ed)
                        if not tmd:
                            tmd = PNTableMetaData(name, a, q)
                        tmd.addFieldMD(f)
                        if f.isCompoundKey():
                            if not cK:
                                cK = PNCompoundKeyMetaData()
                            cK.addFieldMD(f)

                        if f.associatedFieldName():
                            assocs.append(f.associatedFieldName())
                            assocs.append(f.associatedFieldFilterTo())
                            assocs.append(f.name())

                        no = no.nextSibling()
                        continue

                no = no.nextSibling()

            tmd.setCompoundKey(cK)
            aWith = None
            aBy = None

            for it in assocs:
                if not aWith:
                    aWith = it
                    continue
                elif not aBy:
                    aBy = it
                    continue

                elif tmd.field(it) is None:
                    continue

                if tmd.field(aWith) is not None:
                    tmd.field(it).setAssociatedField(tmd.field(aWith), aBy)
                aWith = None
                aBy = None

            if q and not quick:
                qry = self.query(q)
                if qry:
                    fL = qry.fieldList()
                    table = None
                    field = None
                    fields = tmd.fieldNames()
                    # .split(",")
                    fieldsEmpty = not fields

                    for it2 in fL:
                        pos = it2.find(".")
                        if pos > -1:
                            table = it2[:pos]
                            field = it2[pos + 1 :]
                        else:
                            field = it2

                        # if not (not fieldsEmpty and table == name and fields.find(field.lower())) != fields.end():
                        # print("Tabla %s nombre %s campo %s buscando en %s" % (table, name, field, fields))
                        # if not fieldsEmpty and table == name and (field.lower() in fields): Asi
                        # esta en Eneboo, pero incluye campos repetidos
                        if not fieldsEmpty and (field.lower() in fields):
                            continue

                        if table is None:
                            raise ValueError("table is empty!")

                        mtdAux = self.metadata(table, True)
                        if mtdAux is not None:
                            fmtdAux = mtdAux.field(field)
                            if fmtdAux is not None:
                                isForeignKey = False
                                if fmtdAux.isPrimaryKey() and not table == name:
                                    fmtdAux = PNFieldMetaData(fmtdAux)
                                    fmtdAux.setIsPrimaryKey(False)
                                    fmtdAux.setEditable(False)

                                # newRef = not isForeignKey
                                fmtdAuxName = fmtdAux.name().lower()
                                if fmtdAuxName.find(".") == -1:
                                    # fieldsAux = tmd.fieldNames().split(",")
                                    fieldsAux = tmd.fieldNames()
                                    if fmtdAuxName not in fieldsAux:
                                        if not isForeignKey:
                                            fmtdAux = PNFieldMetaData(fmtdAux)

                                        fmtdAux.setName("%s.%s" % (table, field))
                                        # newRef = False

                                # FIXME: ref() does not exist. Probably a C++ quirk from Qt to reference counting.
                                # if newRef:
                                #    fmtdAux.ref()

                                tmd.addFieldMD(fmtdAux)

                    del qry

            from pineboolib.fllegacy import flapplication

            acl = flapplication.aqApp.acl()
            if acl:
                acl.process(tmd)

            return tmd

    @decorators.NotImplementedWarn
    def metadataDev(self, n: str, quick: bool = False) -> bool:
        """Deprecated."""
        return True

    def query(self, name: str, parent: Optional[PNSqlQuery] = None) -> Optional["PNSqlQuery"]:
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

        qryName = "%s.qry" % name
        qry_ = self.db_.managerModules().contentCached(qryName)

        if not qry_:
            return None

        # parser_ = etree.XMLParser(
        #    ns_clean=True,
        #    encoding="UTF-8",
        #    remove_blank_text=True,
        # )
        from pineboolib.application.database.pnsqlquery import PNSqlQuery

        q = PNSqlQuery("", self.db_.connectionName())
        q.setName(name)
        root_ = etree.ElementTree.fromstring(qry_)
        elem_select = root_.find("select")
        elem_from = root_.find("from")

        if elem_select is not None:
            if elem_select.text is not None:
                q.setSelect(
                    elem_select.text.replace(" ", "")
                    .replace("\n", "")
                    .replace("\t", "")
                    .replace("\r", "")
                )
        if elem_from is not None:
            if elem_from.text is not None:
                q.setFrom(elem_from.text.strip(" \t\n\r"))

        for where in root_.iter("where"):
            if where.text is not None:
                q.setWhere(where.text.strip(" \t\n\r"))

        elem_tables = root_.find("tables")
        if elem_tables is not None:
            if elem_tables.text is not None:
                q.setTablesList(elem_tables.text.strip(" \t\n\r"))

        elem_order = root_.find("order")
        if elem_order is not None:
            if elem_order.text is not None:
                orderBy_ = elem_order.text.strip(" \t\n\r")
                q.setOrderBy(orderBy_)

        groupXml_ = root_.findall("group")

        if not groupXml_:
            groupXml_ = []
        # group_ = []

        for i in range(len(groupXml_)):
            gr = groupXml_[i]
            if gr is not None:
                elem_level = gr.find("level")
                elem_field = gr.find("field")
                if elem_field is not None and elem_level is not None:
                    if elem_level.text is not None and elem_field.text is not None:
                        if float(elem_level.text.strip(" \t\n\r")) == i:
                            # print("LEVEL %s -> %s" % (i,gr.xpath("field/text()")[0].strip(' \t\n\r')))
                            q.addGroup(PNGroupByQuery(i, elem_field.text.strip(" \t\n\r")))

        return q

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
        if action_name in self.cacheAction_.keys():
            pnaction_ = self.cacheAction_[action_name]
        else:
            from pineboolib.application.utils.convert_flaction import convert2FLAction

            pnaction_ = convert2FLAction(action_name)
            self.cacheAction_[action_name] = pnaction_

        return pnaction_

        """
        from pineboolib.fllegacy.flaction import FLAction

        util = FLUtil()
        doc = QDomDocument(action_name)
        list_modules = self.db_.managerModules().listAllIdModules()
        content_actions = ""

        for it in list_modules:

            content_actions = self.db_.managerModules().contentCached("%s.xml" % it)
            if not content_actions:
                continue

            if content_actions.find("<name>%s</name>" % action_name) > -1:
                break

        if action_name not in list_modules:
            if (
                not util.domDocumentSetContent(doc, content_actions)
                and action_name.find("alteredtable") == -1
            ):
                logger.warning(
                    "FLManager : "
                    + FLUtil().translate("application", "Error al cargar la accion ")
                    + action_name
                )

        doc_elem = doc.documentElement()
        no = doc_elem.firstChild()

        a = FLAction(action_name)
        # a.setTable(n)
        while not no.isNull():
            e = no.toElement()

            if not e.isNull():
                if e.tagName() == "action":
                    nl = e.elementsByTagName("name")
                    if nl.count() == 0:
                        self.logger.warning(
                            "Debe indicar la etiqueta <name> en acción '%s'" % action_name
                        )
                        no = no.nextSibling()
                        continue
                    else:
                        it = nl.item(0).toElement()
                        if it.text() != action_name:
                            no = no.nextSibling()
                            continue

                    no2 = e.firstChild()
                    e2 = no2.toElement()

                    is_valid_name = False

                    while not no2.isNull():
                        e2 = no2.toElement()
                        if not e2.isNull():
                            if e2.tagName() == "name":
                                is_valid_name = e2.text() == action_name
                                break
                        no2 = no2.nextSibling()

                    no2 = e.firstChild()
                    e2 = no2.toElement()
                    if is_valid_name:
                        if not e2.isNull():
                            if e2.tagName() != "name":
                                logger.debug(
                                    "WARN: El primer tag de la acción '%s' no es name, se encontró '%s'."
                                    % (action_name, e2.tagName())
                                )
                        else:
                            self.logger.debug(
                                "WARN: Se encontró una acción vacia para '%s'." % action_name
                            )

                    while is_valid_name and not no2.isNull():
                        e2 = no2.toElement()

                        if not e2.isNull():
                            if e2.tagName() == "name":
                                a.setName(e2.text())
                                no2 = no2.nextSibling()
                                continue
                            elif e2.tagName() == "scriptformrecord":
                                a.setScriptFormRecord(e2.text())
                                no2 = no2.nextSibling()
                                continue
                            elif e2.tagName() == "scriptform":
                                a.setScriptForm(e2.text())
                                no2 = no2.nextSibling()
                                continue
                            elif e2.tagName() == "table":
                                a.setTable(e2.text())
                                no2 = no2.nextSibling()
                                continue
                            elif e2.tagName() == "form":
                                a.setForm(e2.text())
                                no2 = no2.nextSibling()
                                continue
                            elif e2.tagName() == "formrecord":
                                a.setFormRecord(e2.text())
                                no2 = no2.nextSibling()
                                continue
                            elif e2.tagName() == "caption":
                                txt_ = e2.text()
                                txt_ = auto_qt_translate_text(txt_)
                                a.setCaption(txt_)
                                no2 = no2.nextSibling()
                                continue
                            elif e2.tagName() == "description":
                                txt_ = e2.text()
                                txt_ = auto_qt_translate_text(txt_)

                                if a.caption() == "":
                                    a.setDescription(txt_)
                                no2 = no2.nextSibling()
                                continue
                            elif e2.tagName() == "alias":
                                txt_ = e2.text()
                                txt_ = auto_qt_translate_text(txt_)

                                a.setCaption(txt_)
                                no2 = no2.nextSibling()
                                continue

                        no2 = no2.nextSibling()

                    no = no.nextSibling()
                    continue

            no = no.nextSibling()
        logger.trace("action: saving cache and finishing %s", action_name)

        self.cacheAction_[action_name] = a
        return a
        """

    def existsTable(self, n: str, cache: bool = True) -> bool:
        """
        Check if the table specified in the database exists.

        @param n Name of the table to check if it exists
        @param cache If a certain query first checks the table cache, otherwise
                    make a query to the base to obtain the existing tables
        @return TRUE if the table exists, FALSE otherwise.
        """
        if not self.db_ or n is None:
            return False

        if cache and n in self.listTables_:
            return True
        else:
            return self.db_.existsTable(n)

    def checkMetaData(self, mtd1: Union[str, PNTableMetaData], mtd2: PNTableMetaData) -> bool:
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

            field_list = mtd1.fieldList()

            for field1 in field_list:
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

            field_list = mtd2.fieldList()
            for field1 in field_list:
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

    def alterTable(
        self, mtd1: PNTableMetaData, mtd2: PNTableMetaData, key: str, force: bool = False
    ) -> bool:
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

        return self.db_.dbAux().alterTable(mtd1, mtd2, key, force)

    def createTable(self, n_or_tmd: Union[str, PNTableMetaData, None]) -> Optional[PNTableMetaData]:
        """
        Create a table in the database.

        @param n_tmd Name or metadata of the table you want to create
        @return A PNTableMetaData object with the metadata of the table that was created, or
          0 if the table could not be created or already existed
        """
        if not self.db_:
            raise Exception("createTable. self.db_ is empty!")

        util = FLUtil()
        if n_or_tmd is None:
            logger.debug("createTable: Called with no table.")
            return None

        if isinstance(n_or_tmd, str):
            tmd = self.metadata(n_or_tmd)
            if not tmd:
                return None

            if self.existsTable(tmd.name()):
                self.listTables_.append(n_or_tmd)
                return tmd
            else:
                if not tmd.isQuery():
                    logger.warning("FLMAnager :: No existe tabla %s", n_or_tmd)

            return self.createTable(tmd)
        else:
            if n_or_tmd.isQuery() or self.existsTable(n_or_tmd.name(), False):
                return n_or_tmd

            if not self.db_.createTable(n_or_tmd):
                logger.warning(
                    "createTable: %s", util.tr("No se ha podido crear la tabla ") + n_or_tmd.name()
                )
                return None
            else:
                logger.info("createTable: Created new table %r", n_or_tmd.name())

            return n_or_tmd

    def formatValueLike(
        self, fmd_or_type: Union[PNFieldMetaData, str], value: Any, upper: bool = False
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
            if fmd_or_type is None:
                return ""

            return self.formatValueLike(fmd_or_type.type(), value, upper)
        else:
            return self.db_.formatValueLike(fmd_or_type, value, upper)

    def formatAssignValueLike(self, *args, **kwargs) -> str:
        """
        Return the value content of a formatted field to be recognized by the current database, within the SQL WHERE closing.

        This method takes as parameters the field metadata defined with
        PNFieldMetaData. In addition to TRUE and FALSE as possible values ​​of a field
        logical also accepts the values ​​Yes and No (or its translation into the corresponding language).
        The dates are adapted to the YYYY-MM-DD form, which is the format recognized by PostgreSQL.

        @param fMD PNFieldMetaData object that describes the metadata for the field
        @param v Value to be formatted for the indicated field
        @param upper If TRUE converts the value to uppercase (if it is a string type)
        """
        if isinstance(args[0], PNFieldMetaData):
            # Tipo 1
            if args[0] is None:
                return "1 = 1"

            mtd = args[0].metadata()

            if not mtd:
                return self.formatAssignValueLike(args[0].name(), args[0].type(), args[1], args[2])

            if args[0].isPrimaryKey():
                return self.formatAssignValueLike(
                    mtd.primaryKey(True), args[0].type(), args[1], args[2]
                )

            fieldName = args[0].name()
            if mtd.isQuery() and fieldName.find(".") == -1:
                qry = PNSqlQuery(mtd.query())

                if qry:
                    fL = qry.fieldList()

                for it in fL:
                    if it.find(".") > -1:
                        itFieldName = it[it.find(".") + 1 :]
                    else:
                        itFieldName = it

                    if itFieldName == fieldName:
                        break
                # FIXME: deleteLater() is a C++ internal to clear the memory later. Not used in Python
                # qry.deleteLater()
            prefixTable = mtd.name()
            return self.formatAssignValueLike(
                "%s.%s" % (prefixTable, fieldName), args[0].type(), args[1], args[2]
            )

        elif isinstance(args[1], PNFieldMetaData):
            # tipo 2
            if args[1] is None:
                return "1 = 1"

            return self.formatAssignValueLike(args[0], args[1].type(), args[2], args[3])

        else:
            # tipo 3
            # args[0] = fieldName
            # args[1] = type
            # args[2] = valor
            # args[3] = upper

            if args[0] is None or not args[1]:
                return "1 = 1"

            is_text = args[1] in ["string", "stringlist"]
            format_value = self.formatValueLike(args[1], args[2], args[3])

            if not format_value:
                return "1 = 1"

            field_name = args[0]
            if is_text:
                if args[3]:
                    field_name = "upper(%s)" % args[0]

            return "%s %s" % (field_name, format_value)

    def formatValue(self, fMD_or_type: str, v: Any, upper: bool = False) -> str:
        """Return format value."""

        if not self.db_:
            raise Exception("formatValue. self.db_ is empty!")

        if not fMD_or_type:
            raise ValueError("fMD_or_type is required")

        if not isinstance(fMD_or_type, str):
            return self.formatValue(fMD_or_type.type(), v, upper)

        return str(self.db_.formatValue(fMD_or_type, v, upper))

    def formatAssignValue(self, *args, **kwargs) -> str:
        """Return format assign value."""

        if args[0] is None:
            # print("FLManager.formatAssignValue(). Primer argumento vacio %s" % args[0])
            return "1 = 1"

        # print("tipo 0", type(args[0]))
        # print("tipo 1", type(args[1]))
        # print("tipo 2", type(args[2]))]

        if isinstance(args[0], PNFieldMetaData) and len(args) == 3:
            fMD = args[0]
            mtd = fMD.metadata()
            if not mtd:
                return self.formatAssignValue(fMD.name(), fMD.type(), args[1], args[2])

            if fMD.isPrimaryKey():
                return self.formatAssignValue(mtd.primaryKey(True), fMD.type(), args[1], args[2])

            fieldName = fMD.name()
            if mtd.isQuery() and "." not in fieldName:
                prefixTable = mtd.name()
                qry = self.query(mtd.query())

                if qry:
                    fL = qry.fieldList()

                    for f in fL:
                        # print("fieldName = " + f)

                        fieldSection = None
                        pos = f.find(".")
                        if pos > -1:
                            prefixTable = f[:pos]
                            fieldSection = f[pos + 1 :]
                        else:
                            fieldSection = f

                        # prefixTable = f.section('.', 0, 0)
                        # if f.section('.', 1, 1) == fieldName:
                        if fieldSection == fieldName:
                            break

                    del qry

                # fieldName.prepend(prefixTable + ".")
                fieldName = prefixTable + "." + fieldName

            return self.formatAssignValue(fieldName, args[0].type(), args[1], args[2])

        elif isinstance(args[1], PNFieldMetaData) and isinstance(args[0], str):
            return self.formatAssignValue(args[0], args[1].type(), args[2], args[3])

        elif isinstance(args[0], PNFieldMetaData) and len(args) == 2:
            return self.formatAssignValue(args[0].name(), args[0], args[1], False)
        else:
            if args[1] is None:
                return "1 = 1"

            formatV = self.formatValue(args[1], args[2], args[3])
            if formatV is None:
                return "1 = 1"

            if len(args) == 4 and args[1] == "string":
                fName = "upper(%s)" % args[0]
            else:
                fName = args[0]

            # print("%s=%s" % (fName, formatV))
            if args[1] == "string":
                if formatV.find("%") > -1:
                    retorno = "%s LIKE %s" % (fName, formatV)
                else:
                    retorno = "%s = %s" % (fName, formatV)
            else:
                retorno = "%s = %s" % (fName, formatV)

            return retorno

    def metadataField(
        self, field: QDomElement, v: bool = True, ed: bool = True
    ) -> "PNFieldMetaData":
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

        util = FLUtil()

        ck = False
        n: str = ""
        a: str = ""
        ol: Optional[str] = None
        rX = None
        assocBy = None
        assocWith = None
        so = None

        aN = True
        iPK = False
        c = False
        iNX = False
        uNI = False
        coun = False
        oT = False
        vG = True
        fullCalc = False
        trimm = False

        t: Optional[str] = None
        length = 0
        pI = 4
        pD = 0

        dV = None

        no = field.firstChild()

        while not no.isNull():
            e = no.toElement()
            if not e.isNull():
                if e.tagName() in ("relation", "associated"):
                    no = no.nextSibling()
                    continue

                elif e.tagName() == "name":
                    n = e.text()
                    no = no.nextSibling()
                    continue

                elif e.tagName() == "alias":
                    a = auto_qt_translate_text(e.text())
                    no = no.nextSibling()
                    continue

                elif e.tagName() == "null":
                    aN = e.text() == "true"
                    no = no.nextSibling()
                    continue

                elif e.tagName() == "pk":
                    iPK = e.text() == "true"
                    no = no.nextSibling()
                    continue

                elif e.tagName() == "type":
                    if e.text() == "int":
                        t = "int"
                    elif e.text() == "uint":
                        t = "uint"
                    elif e.text() == "bool":
                        t = "bool"
                    elif e.text() == "double":
                        t = "double"
                    elif e.text() == "time":
                        t = "time"
                    elif e.text() == "date":
                        t = "date"
                    elif e.text() == "pixmap":
                        t = "pixmap"
                    elif e.text() == "bytearray":
                        t = "bytearray"
                    elif e.text() == "string":
                        t = "string"
                    elif e.text() == "stringlist":
                        t = "stringlist"
                    elif e.text() == "unlock":
                        t = "unlock"
                    elif e.text() == "serial":
                        t = "serial"
                    no = no.nextSibling()
                    continue

                elif e.tagName() == "length":
                    length = int(e.text())
                    no = no.nextSibling()
                    continue

                elif e.tagName() == "regexp":
                    rX = e.text()
                    no = no.nextSibling()
                    continue

                elif e.tagName() == "default":
                    if e.text().find("QT_TRANSLATE_NOOP") > -1:
                        dV = auto_qt_translate_text(e.text())
                    else:
                        dV = e.text()

                    no = no.nextSibling()
                    continue

                elif e.tagName() == "outtransaction":
                    oT = e.text() == "true"
                    no = no.nextSibling()
                    continue

                elif e.tagName() == "counter":
                    coun = e.text() == "true"
                    no = no.nextSibling()
                    continue

                elif e.tagName() == "calculated":
                    c = e.text() == "true"
                    no = no.nextSibling()
                    continue

                elif e.tagName() == "fullycalculated":
                    fullCalc = e.text() == "true"
                    no = no.nextSibling()
                    continue

                elif e.tagName() == "trimmed":
                    trimm = e.text() == "true"
                    no = no.nextSibling()
                    continue

                elif e.tagName() == "visible":
                    v = e.text() == "true"
                    no = no.nextSibling()
                    continue

                elif e.tagName() == "visiblegrid":
                    vG = e.text() == "true"
                    no = no.nextSibling()
                    continue

                elif e.tagName() == "editable":
                    ed = e.text() == "true"
                    no = no.nextSibling()
                    continue

                elif e.tagName() == "partI":
                    pI = int(e.text())
                    no = no.nextSibling()
                    continue

                elif e.tagName() == "partD":
                    pD = int(e.text())
                    no = no.nextSibling()
                    continue

                elif e.tagName() == "index":
                    iNX = e.text() == "true"
                    no = no.nextSibling()
                    continue

                elif e.tagName() == "unique":
                    uNI = e.text() == "true"
                    no = no.nextSibling()
                    continue

                elif e.tagName() == "ck":
                    ck = e.text() == "true"
                    no = no.nextSibling()
                    continue

                elif e.tagName() == "optionslist":
                    ol = e.text()
                    no = no.nextSibling()
                    continue

                elif e.tagName() == "searchoptions":
                    so = e.text()
                    no = no.nextSibling()
                    continue

            no = no.nextSibling()

        f = PNFieldMetaData(
            n,
            util.translate("Metadata", a),
            aN,
            iPK,
            t,
            length,
            c,
            v,
            ed,
            pI,
            pD,
            iNX,
            uNI,
            coun,
            dV,
            oT,
            rX,
            vG,
            True,
            ck,
        )
        f.setFullyCalculated(fullCalc)
        f.setTrimed(trimm)

        if ol is not None:
            f.setOptionsList(ol)
        if so is not None:
            f.setSearchOptions(so)

        no = field.firstChild()

        while not no.isNull():
            e = no.toElement()
            if not e.isNull():
                if e.tagName() == "relation":
                    f.addRelationMD(self.metadataRelation(e))
                    no = no.nextSibling()
                    continue

                elif e.tagName() == "associated":
                    noas = e.firstChild()
                    while not noas.isNull():
                        eas = noas.toElement()
                        if not eas.isNull():
                            if eas.tagName() == "with":
                                assocWith = eas.text()
                                noas = noas.nextSibling()
                                continue

                            elif eas.tagName() == "by":
                                assocBy = eas.text()
                                noas = noas.nextSibling()
                                continue

                        noas = noas.nextSibling()

                    no = no.nextSibling()
                    continue

            no = no.nextSibling()

        if assocWith and assocBy:
            f.setAssociatedField(assocWith, assocBy)

        return f

    def metadataRelation(self, relation: QDomElement) -> "PNRelationMetaData":
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

        fT = ""
        fF = ""
        rC = PNRelationMetaData.RELATION_M1
        dC = False
        uC = False
        cI = True

        no = relation.firstChild()

        while not no.isNull():
            e = no.toElement()
            if not e.isNull():

                if e.tagName() == "table":
                    fT = e.text()
                    no = no.nextSibling()
                    continue

                elif e.tagName() == "field":
                    fF = e.text()
                    no = no.nextSibling()
                    continue

                elif e.tagName() == "card":
                    if e.text() == "1M":
                        rC = PNRelationMetaData.RELATION_1M

                    no = no.nextSibling()
                    continue

                elif e.tagName() == "delC":
                    dC = e.text() == "true"
                    no = no.nextSibling()
                    continue

                elif e.tagName() == "updC":
                    uC = e.text() == "true"
                    no = no.nextSibling()
                    continue

                elif e.tagName() == "checkIn":
                    cI = e.text() == "true"
                    no = no.nextSibling()
                    continue

            no = no.nextSibling()

        return PNRelationMetaData(fT, fF, rC, dC, uC, cI)

    @decorators.NotImplementedWarn
    def queryParameter(self, parameter: QDomElement) -> Any:
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

    @decorators.NotImplementedWarn
    def queryGroup(self, group: QDomElement) -> Any:
        """
        Create a FLGroupByQuery object from an XML element.

        Given an XML element, which contains the description of a grouping level
        of a query, build and return the corresponding FLGroupByQuery object.
        NO SYMPATHIC ERROR CHECKS ARE MADE IN THE XML.

        @param group XML element with the description of the grouping level of a query.
        @return FLGroupByQuery object that contains the description of the grouping level
        """
        return True

    def createSystemTable(self, n: str) -> bool:
        """
        Create a system table.

        This method reads directly from disk the file with the description of a table
        of the system and creates it in the database. Its normal use is to initialize
        The system with initial tables.

        @param n Name of the table.
        @return A PNTableMetaData object with the metadata of the table that was created, or
          False if the table could not be created or already existed.
        """
        util = FLUtil()
        if not self.existsTable(n):
            doc = QDomDocument()
            _path = filedir(".", "system_module", "tables")
            from pineboolib.application.types import Dir

            dir = Dir(_path)
            _tables = dir.entryList("%s.mtd" % n)

            for f in _tables:
                path = "%s/%s" % (_path, f)
                _file = QtCore.QFile(path)
                _file.open(QtCore.QIODevice.ReadOnly)
                _in = QtCore.QTextStream(_file)
                _data = _in.readAll()
                if not util.domDocumentSetContent(doc, _data):
                    logger.warning(
                        "FLManager::createSystemTable: %s",
                        self.tr("Error al cargar los metadatos para la tabla %s" % n),
                    )
                    return False
                else:
                    docElem = doc.documentElement()

                    mtd = self.createTable(self.metadata(docElem, True))
                    if mtd:
                        return True
                    else:
                        return False
                # FIXME: f.close() is closing an unknown object. it is a file?
                # ... also, close, but we have return inside the loop.
                # f.close()

        return False

    def loadTables(self) -> None:
        """
        Load in the table list the names of the database tables.
        """
        if not self.db_:
            raise Exception("loadTables. self.db_ is empty!")

        if not self.listTables_:
            self.listTables_ = []
        else:
            self.listTables_.clear()

        self.listTables_ = self.db_.dbAux().tables()

    def cleanupMetaData(self) -> None:
        """
        Clean the flmetadata table, update the xml content with that of the .mtd file currently loaded.
        """
        if not self.db_:
            raise Exception("cleanupMetaData. self.db_ is empty!")

        # util = FLUtil()
        if not self.existsTable("flfiles") or not self.existsTable("flmetadata"):
            return

        buffer = None
        table = ""

        # q.setForwardOnly(True)
        # c.setForwardOnly(True)

        if self.dictKeyMetaData_:
            self.dictKeyMetaData_.clear()
        else:
            self.dictKeyMetaData_ = {}

        self.loadTables()
        self.db_.managerModules().loadKeyFiles()
        self.db_.managerModules().loadAllIdModules()
        self.db_.managerModules().loadIdAreas()

        q = PNSqlQuery(None, "dbAux")
        q.exec_("SELECT tabla,xml FROM flmetadata")
        while q.next():
            self.dictKeyMetaData_[str(q.value(0))] = str(q.value(1))

        c = PNSqlCursor("flmetadata", True, "dbAux")

        q2 = PNSqlQuery(None, "dbAux")
        q2.exec_(
            "SELECT nombre,sha FROM flfiles WHERE nombre LIKE '%.mtd' and nombre not like '%%alteredtable%'"
        )
        while q2.next():
            table = str(q2.value(0))
            table = table.replace(".mtd", "")
            tmd = self.metadata(table)
            if not self.existsTable(table):
                self.createTable(table)
            if not tmd:
                logger.warning(
                    "FLManager::cleanupMetaData %s",
                    FLUtil().translate(
                        "application", "No se ha podido crear los metadatatos para la tabla %s"
                    )
                    % table,
                )

            c.select("tabla='%s'" % table)
            if c.next():
                buffer = c.primeUpdate()
                buffer.setValue("xml", q2.value(1))
                c.update()
            self.dictKeyMetaData_[table] = q2.value(1)

    def isSystemTable(self, table_name: str) -> bool:
        """
        Return if the given table is a system table.

        @param n Name of the table.
        @return TRUE if it is a system table
        """
        from pineboolib.application import project

        if project._DGI and table_name in project.DGI.sys_mtds():
            return True

        if table_name[0:2] != "fl":
            return False

        if table_name.endswith(".mtd"):
            table_name = table_name[:-4]

        if table_name in (
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
        ):
            return True

        return False

    def storeLargeValue(self, mtd: PNFieldMetaData, largeValue: str) -> Optional[str]:
        """
        Store large field values ​​in separate indexed tables by SHA keys of the value content.

        It is used to optimize queries that include fields with large values,
        such as images, to handle the reference to the value in the SQL queries
        which is of constant size instead of the value itself. This decreases traffic by
        considerably reduce the size of the records obtained.

        Queries can use a reference and get its value only when
        you need via FLManager :: fetchLargeValue ().


        @param mtd Metadata of the table containing the field
        @param largeValue Large field value
        @return Value reference key
        """
        if not self.db_:
            raise Exception("storeLareValue. self.db_ is empty!")

        if largeValue[0:3] == "RK@" or mtd is None:
            return None

        tableName = mtd.name()
        # if self.isSystemTable(tableName):
        #    return None

        tableLarge = None
        from pineboolib.fllegacy.flapplication import aqApp

        if aqApp.singleFLLarge():
            tableLarge = "fllarge"
        else:
            tableLarge = "fllarge_%s" % tableName
            if not self.existsTable(tableLarge):
                mtdLarge = PNTableMetaData(tableLarge, tableLarge)
                fieldLarge = PNFieldMetaData("refkey", "refkey", False, True, "string", 100)
                mtdLarge.addFieldMD(fieldLarge)
                fieldLarge2 = PNFieldMetaData("sha", "sha", True, False, "string", 50)
                mtdLarge.addFieldMD(fieldLarge2)
                fieldLarge3 = PNFieldMetaData("contenido", "contenido", True, False, "stringlist")
                mtdLarge.addFieldMD(fieldLarge3)
                mtdAux = self.createTable(mtdLarge)
                mtd.insertChild(mtdLarge)  # type: ignore
                if not mtdAux:
                    return None

        util = FLUtil()
        sha = str(util.sha1(largeValue))
        # print("-->", tableName, sha)
        refKey = "RK@%s@%s" % (tableName, sha)
        q = PNSqlQuery(None, "dbAux")
        q.setSelect("refkey")
        q.setFrom("fllarge")
        q.setWhere(" refkey = '%s'" % refKey)
        if q.exec_() and q.first():
            if not q.value(0) == sha:
                sql = "UPDATE %s SET contenido = '%s' WHERE refkey ='%s'" % (
                    tableLarge,
                    largeValue,
                    refKey,
                )
                if not util.execSql(sql, "Aux"):
                    logger.warning(
                        "FLManager::ERROR:StoreLargeValue.Update %s.%s", tableLarge, refKey
                    )
                    return None
        else:
            sql = "INSERT INTO %s (contenido,refkey) VALUES ('%s','%s')" % (
                tableLarge,
                largeValue,
                refKey,
            )
            if not util.execSql(sql, "Aux"):
                logger.warning("FLManager::ERROR:StoreLargeValue.Insert %s.%s", tableLarge, refKey)
                return None

        return refKey

    def fetchLargeValue(self, refKey: str) -> Optional[str]:
        """
        Return the large value according to its reference key.

        @param refKey Reference key. This key is usually obtained through FLManager :: storeLargeValue
        @return Large value stored
        """
        if refKey is None:
            return None
        if not refKey[0:3] == "RK@":
            return None

        from pineboolib.fllegacy.flapplication import aqApp

        tableName = "fllarge" if aqApp.singleFLLarge() else "fllarge_" + refKey.split("@")[1]

        if not self.existsTable(tableName):
            return None

        q = PNSqlQuery(None, "Aux")
        q.setSelect("contenido")
        q.setFrom(tableName)
        q.setWhere(" refkey = '%s'" % refKey)
        if q.exec_() and q.first():
            v = q.value(0)
            del q
            # print(v)
            v = cacheXPM(v)
            # print(v)

            return v

        return None

    def initCount(self) -> int:
        """
        Indicate the number of times FLManager :: init () has been called.
        """
        return self.initCount_
