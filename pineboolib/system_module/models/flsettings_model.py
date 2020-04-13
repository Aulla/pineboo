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


class Flsettings(BASE):
    __tablename__ = "flsettings"

    # --- Fields --->

    flkey = Column("flkey", String(30), primary_key=True, nullable=False)
    valor = Column("valor", String)


# <--- Fields ---


# --- Relations 1:M --->


# <--- Relations 1:M ---
