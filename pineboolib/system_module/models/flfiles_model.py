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


class Flfiles(BASE):
    __tablename__ = "flfiles"

    # --- Fields --->

    nombre = Column("nombre", String(255), primary_key=True, nullable=False)
    bloqueo = Column("bloqueo", Boolean, unique=False, default=True)
    idmodulo = Column(
        "idmodulo", String(15), ForeignKey("flmodules.idmodulo", ondelete="CASCADE"), nullable=False
    )
    sha = Column("sha", String(255))
    contenido = Column("contenido", String)
    binario = Column("binario", LargeBinary)


# <--- Fields ---


# --- Relations 1:M --->


# <--- Relations 1:M ---
