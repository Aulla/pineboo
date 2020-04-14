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


def mtd_parse(table_name: str, path_mtd: str) -> str:
    """
    Parse MTD into SqlAlchemy model.
    """
    # if not action._table:
    #    return ""

    # table_name = action._table

    # if table_name.endswith(".mtd"):
    #    table_name = table_name[:-4]

    if application.PROJECT.conn_manager is None:
        raise Exception("Project is not connected yet")

    # if mtd_.isQuery():
    #    return None
    dest_file = "%s_model.py" % path_mtd

    # print("** Convirtiendo", mtd_.name(), "->", dest_file)

    # if not os.path.exists(dest_file):
    if not os.path.exists(dest_file):
        print("GENERANDO", dest_file)
        mtd_ = application.PROJECT.conn_manager.manager().metadata(table_name, True)
        if mtd_ is None:
            return ""
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
    metadata_table: List = []
    metadata_table.append("'name' : '%s'" % mtd_table.name())
    metadata_table.append("'alias' : '%s'" % mtd_table.alias())
    if mtd_table.isQuery():
        metadata_table.append("'query':'%s'" % mtd_table.query())
    if mtd_table.concurWarn():
        metadata_table.append("'concurwarn': True")
    if mtd_table.detectLocks():
        metadata_table.append("'detectlocks':True")
    if mtd_table.FTSFunction():
        metadata_table.append("'ftsfunction' :'%s'" % mtd_table.FTSFunction())

    field_list: List[str] = []
    pk_found = False

    for field in mtd_table.fieldList():  # Crea los campos

        if field.isPrimaryKey():
            pk_found = True

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

            field_data.append(" = sqlalchemy.Column('%s', " % field.name())
            field_list.append(generate_field_metadata(field))
            field_data.append(generate_field(field))
            field_data.append(")")
            validator_list.append(field.name())
            if field.isPrimaryKey():
                pk_found = True

        list_data_field.append("".join(field_data))

    meta_fields: List = []
    for meta_field in field_list:
        meta_fields.append("{%s}" % ", ".join(meta_field))

    metadata_table.append(
        "\n        'fields' : [\n        %s\n        ]" % ",\n        ".join(meta_fields)
    )

    data.append("# -*- coding: utf-8 -*-")
    data.append("# Translated with pineboolib %s" % application.PROJECT.version.split(" ")[1])
    data.append("")
    data.append("import sqlalchemy")
    # data.append("from sqlalchemy.ext.declarative import declarative_base")
    # data.append(
    #    "from sqlalchemy import Column, Integer, Numeric, String, BigInteger, Boolean, DateTime, ForeignKey, LargeBinary"
    # )
    # data.append("from sqlalchemy import String as Calculated")
    data.append("from sqlalchemy.orm import relationship, validates")
    # data.append(
    #    "from pineboolib.application.parsers.mtdparser.pnormmodelsfactory import Calculated"
    # )
    data.append("from pineboolib import application")
    # data.append("from pineboolib.qsa import qsa")
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
    data.append("")
    data.append("# --- Metadata ---> ")
    data.append("    legacy_metadata = {%s}" % ", ".join(metadata_table))
    data.append("")
    data.append("# <--- Metadata --- ")
    # data.append("    __actionname__ = '%s'" % action_name)
    data.append("")

    data.append("")
    data.append("# --- Fields ---> ")
    data.append("")

    for data_field in list_data_field:
        data.append(data_field)

    data.append("")
    data.append("# <--- Fields --- ")
    data.append("")

    if not pk_found:

        LOGGER.warning(
            "La tabla %s no tiene definida una clave primaria. No se generará el model."
            % (mtd_table.name())
        )

    return data


def generate_field(field: "pnfieldmetadata.PNFieldMetaData") -> str:
    """
    Get text representation for sqlAlchemy of a field type given its pnfieldmetadata.PNFieldMetaData.
    """
    data: List[str] = []
    # TYPE

    # = "String"
    ret = ""
    if field.type() in ("int, serial"):
        ret = "sqlalchemy.Integer"
    elif field.type() in ("uint"):
        ret = "sqlalchemy.BigInteger"
    elif field.type() in ("calculated"):
        ret = "sqlalchemy.String"
    elif field.type() in ("double"):
        ret = "sqlalchemy.Numeric"
        ret += "(%s , %s)" % (field.partInteger(), field.partDecimal())

    elif field.type() in ("string", "stringlist", "pixmap"):
        ret = "sqlalchemy.String"
        if field.length():
            ret += "(%s)" % field.length()

    elif field.type() in ("bool", "unlock"):
        ret = "sqlalchemy.Boolean"

    elif field.type() in ("time", "date", "timestamp"):
        ret = "sqlalchemy.DateTime"

    elif field.type() in ("bytearray"):
        ret = "sqlalchemy.LargeBinary"

    else:
        ret = "Desconocido %s" % field.type()

    data.append(ret)

    if field.isPrimaryKey():
        data.append("primary_key = True")

    return ", ".join(data)


def generate_field_metadata(field: "pnfieldmetadata.PNFieldMetaData") -> List[str]:

    field_data: List = []

    # NAME
    field_data.append("'name' : '%s'" % field.name())

    # ALIAS
    if field.alias():
        field_data.append("'alias' : '%s'" % field.alias())

    # PK
    if field.isPrimaryKey():
        field_data.append("'pk' : True")
    # CK
    if field.isCompoundKey():
        field_data.append("'ck' : True")

    # TYPE
    field_relation: List[str] = []
    field_data.append("'type' : '%s'" % field.type())

    # LENGTH
    if field.length():
        field_data.append("'length' : %s" % field.length())

    # REGEXP
    if field.regExpValidator():
        field_data.append("'regexp' : '%s'" % field.regExpValidator())

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
        if not rel.checkIn():
            rel_list.append("'checkin' : False")

        field_relation.append("{%s}" % ", ".join(rel_list))

    if field_relation:
        field_data.append("'relations' : [%s]" % ", ".join(field_relation))

    # ASSOCIATED
    if field.private.associated_field_name:

        field_data.append(
            "'associated':{'with' : '%s', 'by' : '%s' }"
            % (field.private.associated_field_filter_to, field.private.associated_field_name)
        )

    # UNIQUE
    if field.isUnique():
        field_data.append("'isunique' : True")

    # ALLOW_NULL
    if not field.allowNull():
        field_data.append("'null' : False")

    # DEFAULT_VALUE
    if field.defaultValue():
        field_data.append("'default' : '%s'" % field.defaultValue())

    # OUT_TRANSACTION
    if field.outTransaction():
        field_data.append("'outtransaction' : True")

    # COUNTER
    if field.isCounter():
        field_data.append("'counter' : True")

    # CALCULATED
    if field.calculated():
        field_data.append("'calculated' : True")

    # FULLY_CALCULATED
    if field.fullyCalculated():
        field_data.append("'fullycalculated' : True")

    # TRIMMED
    if field.trimmed():
        field_data.append("'trimmed' : True")

    # VISIBLE
    if not field.visible():
        field_data.append("'visible' : False")

    # VISIBLE_GRID
    if not field.visibleGrid():
        field_data.append("'visiblegrid' : False")

    # EDITABLE
    if not field.editable():
        field_data.append("'editable' : False")

    if field.type() == "double":
        # PARTI
        if field.partInteger():
            field_data.append("'partI' : %s" % field.partInteger())

        # PARTD
        if field.partDecimal():
            field_data.append("'partD' : %s" % field.partDecimal())

    # INDEX
    if field.isIndex():
        field_data.append("'index' : True")

    # OPTIONS_LIST
    if field.optionsList():
        texto = ""
        for item in field.optionsList():
            texto += "'%s', " % item

        field_data.append("'optionslist' : [%s]" % texto)
    # SEARCH_OPTIONS
    if field.searchOptions():
        texto = ""
        for item in field.searchOptions():
            texto += "'%s', " % item

        field_data.append("'searchoptions' : [%s]" % texto)

    return field_data
