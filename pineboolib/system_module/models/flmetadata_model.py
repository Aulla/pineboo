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


class Flmetadata(BASE):
    __tablename__ = "flmetadata"

    # --- Fields --->

    tabla = Column("tabla", String(255), primary_key=True, nullable=False)
    xml = Column("xml", String)
    bloqueo = Column("bloqueo", Boolean, unique=False)
    seq = Column("seq", BigInteger, nullable=False)


# <--- Fields ---


# --- Relations 1:M --->


# <--- Relations 1:M ---
