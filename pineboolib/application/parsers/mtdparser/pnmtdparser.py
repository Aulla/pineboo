# -*- coding: utf-8 -*-
"""
MTD Parser to sqlAlchemy model.

Creates a Python file side by side with the original MTD file.
Can be overloaded with a custom class to enhance/change available
functions. See pineboolib/pnobjectsfactory.py
"""

from pineboolib import logging
from typing import List, cast, Optional, TYPE_CHECKING
from pineboolib.application.utils.path import _path
from pineboolib import application
from pineboolib.application.metadata import pnfieldmetadata, pntablemetadata
from pineboolib.core import settings

import os

LOGGER = logging.get_logger(__name__)

RESERVER_WORDS = ["pass"]

if TYPE_CHECKING:
    from pineboolib.application import xmlaction


def mtd_parse(action: "xmlaction.XMLAction") -> Optional[str]:
    """
    Parse MTD into SqlAlchemy model.
    """
    if not action._table:
        return ""

    table_name = action._table

    if table_name.endswith(".mtd"):
        table_name = table_name[:-4]

    if table_name.find("alteredtable") > -1 or table_name.startswith("fllarge_"):
        return None

    if application.PROJECT.conn_manager is None:
        raise Exception("Project is not connected yet")
    mtd_ = application.PROJECT.conn_manager.manager().metadata(table_name, True)
    if mtd_ is None:
        return None

    # if mtd_.isQuery():
    #    return None

    dest_file = _path("%s.mtd" % table_name)
    if dest_file.find("system_module/tables") == -1:
        path_model = dest_file[: dest_file.find("file.mtd") - 1]
        if not os.path.exists("%s/file.model" % path_model):
            os.mkdir("%s/file.model" % path_model)
        print("FIXME nombre_model como sha1")
        dest_file = "%s/file.model/%s_model.py" % (path_model, table_name)
    else:
        return None

    # if mtd_file is None:
    #    LOGGER.warning("No se encuentra %s.mtd", table_name)
    #    return None

    # dest_file = "%s_model.py" % mtd_file[: len(mtd_file) - 4]

    # if dest_file.find("system_module") > -1:
    #    path_dir = "%s/cache/%s/sys" % (
    #        settings.CONFIG.value("ebcomportamiento/temp_dir"),
    #        application.PROJECT.conn_manager.mainConn().DBName(),
    #    )
    #    dest_file = "%s/file.model/%s_model.py" % (path_dir, table_name)

    # if not os.path.exists(path_dir):
    #    os.mkdir(path_dir)
    # if not os.path.exists("%s/file.model" % path_dir):
    #    os.mkdir("%s/file.model" % path_dir)
    print("Convirtiendo", mtd_.name(), "->", dest_file)

    if not os.path.exists(dest_file):
        lines = generate_model(mtd_)

        if lines:
            file_ = open(dest_file, "w", encoding="UTF-8")
            for line in lines:
                file_.write("%s\n" % line)
            file_.close()

    return dest_file


def generate_model(mtd_table: "pntablemetadata.PNTableMetaData") -> List[str]:
    """
    Create a list of lines from a mtd_table (pntablemetadata.PNTableMetaData).
    """

    data = []
    list_data_field: str = []
    validator_list: List[str] = []

    field_lists: "pnfieldmetadata.PNFieldMetaData" = []

    field_list = mtd_table.fieldList()

    for field in field_list:  # Crea los campos
        if field.name() in validator_list:
            LOGGER.warning(
                "Hay un campo %s duplicado en %s.mtd. Omitido", field.name(), mtd_table.name()
            )
        else:

            field_data = []
            field_data.append("    ")
            if field.name() in RESERVER_WORDS:
                field_data.append("%s_" % field.name())
            else:
                field_data.append(field.name())

            field_data.append(" = Column('%s', " % field.name())
            field_data.append(generate_metadata(field))
            field_data.append(")")
            validator_list.append(field.name())
            if field.isPrimaryKey():
                pk_found = True

        list_data_field.append("".join(field_data))

    pk_found = False
    data.append("# -*- coding: utf-8 -*-")
    # data.append("from sqlalchemy.ext.declarative import declarative_base")
    data.append(
        "from sqlalchemy import Column, Integer, Numeric, String, BigInteger, Boolean, DateTime, ForeignKey, LargeBinary"
    )
    data.append("from sqlalchemy.orm import relationship, validates")
    data.append(
        "from pineboolib.application.parsers.mtdparser.pnormmodelsfactory import Calculated"
    )
    data.append("from pineboolib import application")
    data.append("from pineboolib.qsa import qsa")
    data.append("")
    # data.append("Base = declarative_base()")
    data.append("BASE = application.PROJECT.conn_manager.mainConn().declarative_base()")
    # data.append("ENGINE = application.PROJECT.conn_manager.mainConn().engine()")
    data.append("")
    # for field in mtd_table.fieldList():
    #    if field.relationM1():
    #        rel = field.relationM1()
    #        data.append("load_model('%s')" % rel.foreignTable())

    data.append("")
    data.append("class %s%s(BASE):" % (mtd_table.name()[0].upper(), mtd_table.name()[1:]))
    data.append("    __tablename__ = '%s'" % mtd_table.name())

    data.append("    metadata_alias = '%s'" % mtd_table.alias())

    if mtd_table.isQuery():
        data.append("    metadata_query = '%s'" % mtd_table.query())

    if mtd_table.concurWarn():
        data.append("    metadata_concurwarn = True")
    if mtd_table.detectLocks():
        data.append("    metadata_detectlocks = True")
    if mtd_table.FTSFunction():
        data.append('    metadata_ftsfunction = "%s"' % mtd_table.FTSFunction())
    # data.append("    __actionname__ = '%s'" % action_name)
    data.append("")

    data.append("")
    data.append("# --- Fields ---> ")
    data.append("")

    for data_field in list_data_field:
        data.appen(data_field)

    data.append("")
    data.append("# <--- Fields --- ")
    data.append("")

    if not pk_found:

        if settings.CONFIG.value("application/isDebuggerMode", False):
            LOGGER.warning(
                "La tabla %s no tiene definida una clave primaria. No se generará el model."
                % (mtd_table.name())
            )
        data = []

    return data


def generate_metadata(field: "pnfieldmetadata.PNFieldMetaData") -> str:
    """
    Get text representation for sqlAlchemy of a field type given its pnfieldmetadata.PNFieldMetaData.
    """
    field_data: List[str] = []
    # TYPE

    ret = "String"
    if field.type() in ("int, serial"):
        ret = "Integer"
    elif field.type() in ("uint"):
        ret = "BigInteger"
    elif field.type() in ("calculated"):
        ret = "Calculated"
    elif field.type() in ("double"):
        ret = "Numeric"
        ret += "(%s , %s)" % (field.partInteger(), field.partDecimal())

    elif field.type() in ("string", "stringlist", "pixmap"):
        ret = "String"
        if field.length():
            ret += "(%s)" % field.length()

    elif field.type() in ("bool", "unlock"):
        ret = "Boolean"

    elif field.type() in ("time", "date", "timestamp"):
        ret = "DateTime"

    elif field.type() in ("bytearray"):
        ret = "LargeBinary"

    else:
        ret = "Desconocido %s" % field.type()

    field_data.append(ret)

    # ALIAS

    if field.alias():
        field_data.append("metadata_alias = '%s'" % field.alias())

    # PK
    if field.isPrimaryKey():
        field_data.append("primary_key = True")
        field_data.append("metadata_primarykey = True")
    # CK
    if field.isCompoundKey():
        field_data.append("metadata_compoundkey = True")

    # TYPE
    field_relation: List[str] = []
    field_data.append("metadata_type = '%s'" % field.type())

    # LENGTH
    if field.length():
        field_data.append("metadata_length = %s" % field.legth())

    # REGEXP
    if field.regExpValidator():
        field_data.append("metadata_regexp = '%s'" % field.regExpValidator())

    # RELATIONS
    for rel in field.relationList():
        rel_list: List[str] = []
        rel_list.append("'card' : '%s'" % rel.cardinality())
        rel_list.append("'table' : '%s'" % rel.foreignTable())
        rel_list.append("'field' : '%s'" % rel.foreignField())
        if rel.deleteCascade():
            rel_list.append("'delc' : True")
        if rel.updateCascade():
            rel_list.append("'updc' : True")
        if rel.checkIn():
            rel_list.append("'checkin' : True")

        field_relation.append("{%s}" % ", ".join(rel_list))

    if field_relation:
        field_data.append("metadata_relations = {%s}" % ", ".join(field_relation))

    # ASSOCIATED
    if field.associatedField():
        field_data.append(
            "metadata_associated = {'with' : '%s', 'by' : '%s' }"
            % (field.associated_field_filter_to, field.associated_field_name)
        )

    # UNIQUE
    if field.isUnique():
        field_data.append("metadata_isunique = True")

    # ALLOW_NULL
    if field.allowNull():
        field_data.append("metadata_allownull = True")

    # DEFAULT_VALUE
    if field.defaultValue():
        field_data.append("metadata_defaul= '%s'" % field.defaultValue())

    # OUT_TRANSACTION
    if field.outTransaction():
        field_data.append("metadata_outtransaction = True")

    # COUNTER
    if field.isCounter():
        field_data.append("metadata_counter = True")

    # CALCULATED
    if field.calculated():
        field_data.append("metadata_calculated = True")

    # FULLY_CALCULATED
    if field.fullyCalculated():
        field_data.append("metadata_fullycalculated = True")

    # TRIMMED
    if field.trimmed():
        field_data.append("metadata_trimmed = True")

    # VISIBLE
    if field.visible():
        field_data.append("metadata_visible = True")

    # VISIBLE_GRID
    if field.visibleGrid():
        field_data.append("metadata_visiblegrid = True")

    # EDITABLE
    if field.editable():
        field_data.append("metadata_editable = True")

    # PARTI
    if field.partInteger():
        field_data.append("metadata_partinteger = %s" % field.partInteger())

    # PARTD
    if field.partDecimal():
        field_data.append("metadata_partdecimal = %s" % field.partDecimal())

    # INDEX
    if field.isIndex():
        field_data.append("metadata_index = True")

    # OPTIONS_LIST
    if field.optionsList():
        field_data.append("metadata_optionslist =[%s]" % ", ".join(field.optionsList()))
    # SEARCH_OPTIONS
    if field.searchOptions():
        field_data.append("metadata_searchoptions =[%s]" % ", ".join(field.searchOptions()))

    return ", ".join(field_data)
