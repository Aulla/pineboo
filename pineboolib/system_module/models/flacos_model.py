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


class Flacos(BASE):
    __tablename__ = "flacos"

    # --- Fields --->

    idaco = Column("idaco", Integer, primary_key=True, nullable=False)
    nombre = Column("nombre", String(100), primary_key=True, nullable=False)
    permiso = Column("permiso", String(50), nullable=False, default="--")
    idac = Column(
        "idac",
        BigInteger,
        ForeignKey("flacs.idac", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    descripcion = Column("descripcion", String(100))
    tipocontrol = Column("tipocontrol", String(30), default="Todos")


# <--- Fields ---


# --- Relations 1:M --->


# <--- Relations 1:M ---
