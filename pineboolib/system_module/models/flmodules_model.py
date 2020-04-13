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


class Flmodules(BASE):
    __tablename__ = "flmodules"

    # --- Fields --->

    bloqueo = Column("bloqueo", Boolean, unique=False, default=True)
    idmodulo = Column("idmodulo", String(15), primary_key=True, nullable=False)
    idarea = Column("idarea", String(15), ForeignKey("flareas.idarea"), nullable=False)
    descripcion = Column("descripcion", String(100), nullable=False)
    version = Column("version", String(3), nullable=False, default="0.0")
    icono = Column("icono", String)

    # <--- Fields ---

    # --- Relations 1:M --->

    flfiles_idmodulo = relationship("Flfiles", foreign_keys="Flfiles.idmodulo")


# <--- Relations 1:M ---
