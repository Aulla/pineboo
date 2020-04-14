# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18

import sqlalchemy
from sqlalchemy.orm import relationship, validates
from pineboolib import application

BASE = application.PROJECT.conn_manager.mainConn().declarative_base()


class Flareas(BASE):
    __tablename__ = "flareas"

    # --- Metadata --->
    legacy_metadata = {
        "name": "flareas",
        "alias": "Áreas",
        "fields": [
            {"name": "bloqueo", "alias": "Bloqueo", "type": "unlock", "defaultvalue": "True"},
            {
                "name": "idarea",
                "alias": "Área",
                "primarykey": True,
                "type": "string",
                "length": 15,
                "relations": [{"card": "1M", "table": "flmodules", "field": "idarea"}],
            },
            {"name": "descripcion", "alias": "Descripción", "type": "string", "length": 100},
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    bloqueo = sqlalchemy.Column("bloqueo", sqlalchemy.Boolean)
    idarea = sqlalchemy.Column("idarea", sqlalchemy.String(15), primary_key=True)
    descripcion = sqlalchemy.Column("descripcion", sqlalchemy.String(100))


# <--- Fields ---
