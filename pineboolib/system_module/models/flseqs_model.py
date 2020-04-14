# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18

import sqlalchemy
from sqlalchemy.orm import relationship, validates
from pineboolib import application

BASE = application.PROJECT.conn_manager.mainConn().declarative_base()


class Flseqs(BASE):
    __tablename__ = "flseqs"

    # --- Metadata --->
    legacy_metadata = {
        "name": "flseqs",
        "alias": "Secuencias",
        "fields": [
            {
                "name": "tabla",
                "alias": "Nombre de la tabla",
                "primarykey": True,
                "type": "string",
                "length": 255,
            },
            {
                "name": "campo",
                "alias": "Nombre del campo",
                "compoundkey": True,
                "type": "string",
                "length": 255,
            },
            {"name": "seq", "alias": "Secuencia", "type": "uint"},
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    tabla = sqlalchemy.Column("tabla", sqlalchemy.String(255), primary_key=True)
    campo = sqlalchemy.Column("campo", sqlalchemy.String(255))
    seq = sqlalchemy.Column("seq", sqlalchemy.BigInteger)


# <--- Fields ---
