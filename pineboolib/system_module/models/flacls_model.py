# -*- coding: utf-8 -*-
from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    String,
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    LargeBinary,
)
from sqlalchemy.orm import relationship, validates
from pineboolib.application.parsers.mtdparser.pnormmodelsfactory import Calculated
from pineboolib import application
from pineboolib.qsa import qsa

BASE = application.PROJECT.conn_manager.mainConn().declarative_base()


class Flacls(BASE):
    __tablename__ = "flacls"

    # --- Fields --->

    idacl = Column("idacl", String(15), primary_key=True, nullable=False)
    descripcion = Column("descripcion", String(100))
    instalada = Column("instalada", Boolean, unique=False, default=False)
    idgroupintro = Column("idgroupintro", String(30), ForeignKey("flgroups.idgroup"))
    iduserintro = Column("iduserintro", String(30), ForeignKey("flusers.iduser"))
    prioridadgrupointro = Column("prioridadgrupointro", BigInteger, default="2")
    prioridadusuariointro = Column("prioridadusuariointro", BigInteger, default="1")

    # <--- Fields ---

    # --- Relations 1:M --->

    flacs_idacl = relationship("Flacs", foreign_keys="Flacs.idacl")


# <--- Relations 1:M ---
