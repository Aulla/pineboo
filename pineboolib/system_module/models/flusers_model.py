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


class Flusers(BASE):
    __tablename__ = "flusers"

    # --- Fields --->

    iduser = Column("iduser", String(30), primary_key=True, nullable=False)
    idgroup = Column("idgroup", String(30), ForeignKey("flgroups.idgroup"), nullable=False)
    descripcion = Column("descripcion", String(100))

    # <--- Fields ---

    # --- Relations 1:M --->

    flacs_iduser = relationship("Flacs", foreign_keys="Flacs.iduser")


# <--- Relations 1:M ---
