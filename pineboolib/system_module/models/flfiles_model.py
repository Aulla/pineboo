# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18

import sqlalchemy
from sqlalchemy.orm import relationship, validates
from pineboolib import application

BASE = application.PROJECT.conn_manager.mainConn().declarative_base()


class Flfiles(BASE):
    __tablename__ = "flfiles"

    # --- Metadata --->
    legacy_metadata = {
        "alias": "Ficheros de Texto",
        "fields": [
            {
                "name": "nombre",
                "alias": "Nombre",
                "primarykey": True,
                "type": "string",
                "length": 255,
                "regexp": "\w+\.(mtd|ts|ui|qs|qry|kut|xml|jrxml|svg)",
            },
            {"name": "bloqueo", "alias": "Bloqueo", "type": "unlock", "defaultvalue": "True"},
            {"name": "idmodulo", "alias": "Módulo", "type": "string", "length": 15},
            {
                "name": "sha",
                "alias": "SHA1",
                "type": "string",
                "length": 255,
                "allownull": True,
                "calculated": True,
                "editable": False,
            },
            {
                "name": "contenido",
                "alias": "Contenido",
                "type": "stringlist",
                "allownull": True,
                "visiblegrid": False,
            },
            {
                "name": "binario",
                "alias": "Binario",
                "type": "bytearray",
                "allownull": True,
                "visiblegrid": False,
            },
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    nombre = sqlalchemy.Column("nombre", sqlalchemy.String(255), primary_key=True)
    bloqueo = sqlalchemy.Column("bloqueo", sqlalchemy.Boolean)
    idmodulo = sqlalchemy.Column("idmodulo", sqlalchemy.String(15))
    sha = sqlalchemy.Column("sha", sqlalchemy.String(255))
    contenido = sqlalchemy.Column("contenido", sqlalchemy.String)
    binario = sqlalchemy.Column("binario", sqlalchemy.LargeBinary)


# <--- Fields ---
