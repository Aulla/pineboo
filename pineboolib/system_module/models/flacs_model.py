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


class Flacs(BASE):
    __tablename__ = "flacs"

    # --- Fields --->

    idac = Column("idac", Integer, primary_key=True, nullable=False)
    prioridad = Column("prioridad", BigInteger, nullable=False)
    tipo = Column("tipo", String(30), primary_key=True, nullable=False, default="mainwindow")
    nombre = Column("nombre", String(50), primary_key=True, nullable=False)
    iduser = Column("iduser", String(30), ForeignKey("flusers.iduser"), primary_key=True)
    idgroup = Column("idgroup", String(30), ForeignKey("flgroups.idgroup"), primary_key=True)
    permiso = Column("permiso", String(50))
    idacl = Column(
        "idacl", String(15), ForeignKey("flacls.idacl", ondelete="CASCADE"), nullable=False
    )
    descripcion = Column("descripcion", String(100))
    degrupo = Column("degrupo", Boolean, unique=False, default=False)
    idarea = Column("idarea", String(15), ForeignKey("flareas.idarea"))
    idmodule = Column("idmodule", String(15), ForeignKey("flmodules.idmodulo"))
    tipoform = Column("tipoform", String(30), nullable=False, default="Maestro")


# <--- Fields ---


# --- Relations 1:M --->


# <--- Relations 1:M ---
