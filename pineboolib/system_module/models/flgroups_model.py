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


class Flgroups(BASE):
    __tablename__ = "flgroups"

    # --- Fields --->

    idgroup = Column("idgroup", String(30), primary_key=True, nullable=False)
    descripcion = Column("descripcion", String(100))

    # <--- Fields ---

    # --- Relations 1:M --->

    flusers_idgroup = relationship("Flusers", foreign_keys="Flusers.idgroup")
    flacs_idgroup = relationship("Flacs", foreign_keys="Flacs.idgroup")


# <--- Relations 1:M ---
