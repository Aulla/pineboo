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
        dest_file = "%s/file.model/%s_model.py" % (
            mtd_file[: mtd_file.find("file.mtd")],
            table_name,
        )
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
    # data.append("    __actionname__ = '%s'" % action_name)
    data.append("")

    validator_list: List[str] = []

    data.append("")
    data.append("# --- Fields ---> ")
    data.append("")

    for field in mtd_table.fieldList():  # Crea los campos
        if field.name() in validator_list:
            LOGGER.warning(
                "Hay un campo %s duplicado en %s.mtd. Omitido", field.name(), mtd_table.name()
            )
        else:
            field_data = []
            field_data.append("    ")
            field_data.append(
                "%s" % field.name() + "_" if field.name() in RESERVER_WORDS else field.name()
            )
            field_data.append(" = Column('%s', " % field.name())
            field_data.append(field_type(field))
            field_data.append(")")
            validator_list.append(field.name())
            if field.isPrimaryKey():
                pk_found = True

        data.append("".join(field_data))

    data.append("")
    data.append("# <--- Fields --- ")
    data.append("")

    data.append("")
    data.append("# --- Relations 1:M ---> ")
    data.append("")
    if application.PROJECT.conn_manager is None:
        raise Exception("Project is not connected yet")
    manager = application.PROJECT.conn_manager.manager()
    for field in mtd_table.fieldList():  # Creamos relaciones 1M
        for relation in field.relationList():
            foreign_table_mtd = manager.metadata(relation.foreignTable())
            # if application.PROJECT.conn.manager().existsTable(r.foreignTable()):
            if foreign_table_mtd:
                # comprobamos si existe el campo...
                if foreign_table_mtd.field(relation.foreignField()):

                    foreign_object = "%s%s" % (
                        relation.foreignTable()[0].upper(),
                        relation.foreignTable()[1:],
                    )
                    relation_ = "    %s_%s = relationship('%s'" % (
                        relation.foreignTable(),
                        relation.foreignField(),
                        foreign_object,
                    )
                    relation_ += ", foreign_keys='%s.%s'" % (
                        foreign_object,
                        relation.foreignField(),
                    )
                    relation_ += ")"
                    data.append(relation_)

    data.append("")
    data.append("# <--- Relations 1:M --- ")
    """
    data.append("")
    data.append("")
    data.append("")
    data.append("    @validates('%s')" % "','".join(validator_list))
    data.append("    def validate(self, key, value):")
    data.append(
        "        self.__dict__[key] = value #Chapuza para que el atributo ya contenga el valor"
    )
    data.append("        self.bufferChanged(key)")
    data.append("        return value #Ahora si se asigna de verdad")
    data.append("")
    data.append("    def bufferChanged(self, fn):")
    data.append("        pass")

    data.append("")
    data.append("    def beforeCommit(self):")
    data.append("        return True")
    data.append("")
    data.append("    def afterCommit(self):")
    data.append("        return True")
    data.append("")
    data.append("    def commitBuffer(self):")
    data.append("        if not self.beforeCommit():")
    data.append("            return False")
    data.append("")
    data.append("        aqApp.db().session().commit()")
    data.append("")
    data.append("        if not self.afterCommit():")
    data.append("            return False")

    # for field in mtd_table.fieldList():  # Relaciones M:1
    #     if field.relationList():
    #         rel_data = []
    #         for r in field.relationList():
    #             if r.cardinality() == r.RELATION_1M:
    #                 obj_name = "%s%s" % (r.foreignTable()[0].upper(), r.foreignTable()[1:])
    #                 rel_data.append(
    #                     "    %s = relationship('%s', backref='parent'%s)\n"
    #                     % (r.foreignTable(), obj_name, ", cascade ='all, delete'" if r.deleteCascade() else "")
    #                 )
    #
    #         data.append("".join(rel_data))
    #
    # data.append("if not ENGINE.dialect.has_table(ENGINE.connect(),'%s'):" % mtd_table.name())
    # data.append("    %s%s.__table__.create(ENGINE)" % (mtd_table.name()[0].upper(), mtd_table.name()[1:]))
    """
    if not pk_found:

        if settings.CONFIG.value("application/isDebuggerMode", False):
            LOGGER.warning(
                "La tabla %s no tiene definida una clave primaria. No se generará el model."
                % (mtd_table.name())
            )
        data = []

    return data


def field_type(field: "pnfieldmetadata.PNFieldMetaData") -> str:
    """
    Get text representation for sqlAlchemy of a field type given its pnfieldmetadata.PNFieldMetaData.
    """
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
        ret += ", unique=False"

    elif field.type() in ("time", "date", "timestamp"):
        ret = "DateTime"

    elif field.type() in ("bytearray"):
        ret = "LargeBinary"

    else:
        ret = "Desconocido %s" % field.type()

    if field.relationM1() is not None:
        if application.PROJECT.conn_manager is None:
            raise Exception("Project is not connected yet")
        rel = field.relationM1()
        if rel and application.PROJECT.conn_manager.manager().existsTable(rel.foreignTable()):
            ret += ", ForeignKey('%s.%s'" % (rel.foreignTable(), rel.foreignField())
            if rel.deleteCascade():
                ret += ", ondelete='CASCADE'"

            ret += ")"

    if field.isPrimaryKey() or field.isCompoundKey():
        ret += ", primary_key=True"

    if (not field.isPrimaryKey() and not field.isCompoundKey()) and field.type() == "serial":
        ret += ", autoincrement=True"

    if field.isUnique():
        ret += ", unique=True"

    if not field.allowNull() and field.type() not in ("bool", "unlock"):
        ret += ", nullable=False"

    if field.defaultValue() is not None:
        value = field.defaultValue()
        if isinstance(value, str):
            value = "'%s'" % value
        ret += ", default=%s" % value

    return ret
