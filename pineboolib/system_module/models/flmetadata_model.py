# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18

import sqlalchemy
from sqlalchemy.orm import relationship, validates
from pineboolib import application

BASE = application.PROJECT.conn_manager.mainConn().declarative_base()


class Flmetadata(BASE):
    __tablename__ = "flmetadata"

    # --- Metadata --->
    legacy_metadata = {
        "name": "flmetadata",
        "alias": "Metadatos",
        "fields": [
            {
                "name": "tabla",
                "alias": "Nombre de la tabla",
                "primarykey": True,
                "type": "string",
                "length": 255,
            },
            {
                "name": "xml",
                "alias": "Descripción XML",
                "type": "stringlist",
                "allownull": True,
                "visiblegrid": False,
            },
            {"name": "bloqueo", "alias": "Tabla bloqueada", "type": "bool", "allownull": True},
            {"name": "seq", "alias": "Secuencia", "type": "uint"},
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    tabla = sqlalchemy.Column("tabla", sqlalchemy.String(255), primary_key=True)
    xml = sqlalchemy.Column("xml", sqlalchemy.String)
    bloqueo = sqlalchemy.Column("bloqueo", sqlalchemy.Boolean)
    seq = sqlalchemy.Column("seq", sqlalchemy.BigInteger)


# <--- Fields ---
