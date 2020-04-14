# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18

import sqlalchemy
from sqlalchemy.orm import relationship, validates
from pineboolib import application

BASE = application.PROJECT.conn_manager.mainConn().declarative_base()


class Flusers(BASE):
    __tablename__ = "flusers"

    # --- Metadata --->
    legacy_metadata = {
        "alias": "Usuarios",
        "fields": [
            {
                "name": "iduser",
                "alias": "Nombre",
                "primarykey": True,
                "type": "string",
                "length": 30,
                "relations": [{"card": "1M", "table": "flacs", "field": "iduser"}],
            },
            {"name": "idgroup", "alias": "Grupo", "type": "string", "length": 30},
            {
                "name": "descripcion",
                "alias": "Descripción",
                "type": "string",
                "length": 100,
                "allownull": True,
            },
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    iduser = sqlalchemy.Column("iduser", sqlalchemy.String(30), primary_key=True)
    idgroup = sqlalchemy.Column("idgroup", sqlalchemy.String(30))
    descripcion = sqlalchemy.Column("descripcion", sqlalchemy.String(100))


# <--- Fields ---
