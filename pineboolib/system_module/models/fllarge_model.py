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


class Fllarge(BASE):
    __tablename__ = "fllarge"

    # --- Fields --->

    refkey = Column("refkey", String(100), primary_key=True, nullable=False)
    sha1 = Column("sha1", String(50))
    contenido = Column("contenido", String)


# <--- Fields ---


# --- Relations 1:M --->


# <--- Relations 1:M ---
