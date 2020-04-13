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


class Flareas(BASE):
    __tablename__ = "flareas"

    # --- Fields --->

    bloqueo = Column("bloqueo", Boolean, unique=False, default=True)
    idarea = Column("idarea", String(15), primary_key=True, nullable=False)
    descripcion = Column("descripcion", String(100), nullable=False)

    # <--- Fields ---

    # --- Relations 1:M --->

    flmodules_idarea = relationship("Flmodules", foreign_keys="Flmodules.idarea")


# <--- Relations 1:M ---
