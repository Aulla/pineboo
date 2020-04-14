# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18

import sqlalchemy
from sqlalchemy.orm import relationship, validates
from pineboolib import application

BASE = application.PROJECT.conn_manager.mainConn().declarative_base()


class Flvar(BASE):
    __tablename__ = "flvar"

    # --- Metadata --->
    legacy_metadata = {
        "name": "flvar",
        "alias": "Variables",
        "fields": [
            {
                "name": "id",
                "alias": "Identificador",
                "primarykey": True,
                "type": "serial",
                "visiblegrid": False,
            },
            {
                "name": "idvar",
                "alias": "Identificador de la variable",
                "compoundkey": True,
                "type": "string",
                "length": 30,
            },
            {
                "name": "idsesion",
                "alias": "Identificador de la sesión",
                "compoundkey": True,
                "type": "string",
                "length": 30,
            },
            {"name": "valor", "alias": "Valor", "type": "stringlist", "visiblegrid": False},
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    id = sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True)
    idvar = sqlalchemy.Column("idvar", sqlalchemy.String(30))
    idsesion = sqlalchemy.Column("idsesion", sqlalchemy.String(30))
    valor = sqlalchemy.Column("valor", sqlalchemy.String)


# <--- Fields ---
