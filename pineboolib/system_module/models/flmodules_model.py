# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18

import sqlalchemy
from sqlalchemy.orm import relationship, validates
from pineboolib import application

BASE = application.PROJECT.conn_manager.mainConn().declarative_base()


class Flmodules(BASE):
    __tablename__ = "flmodules"

    # --- Metadata --->
    legacy_metadata = {
        "name": "flmodules",
        "alias": "Módulos",
        "fields": [
            {"name": "bloqueo", "alias": "Bloqueo", "type": "unlock", "defaultvalue": "True"},
            {
                "name": "idmodulo",
                "alias": "Id. del Módulo",
                "primarykey": True,
                "type": "string",
                "length": 15,
                "relations": [{"card": "1M", "table": "flfiles", "field": "idmodulo"}],
            },
            {
                "name": "idarea",
                "alias": "Id. del Área",
                "type": "string",
                "length": 15,
                "visiblegrid": False,
            },
            {"name": "descripcion", "alias": "Descripción", "type": "string", "length": 100},
            {
                "name": "version",
                "alias": "Versión",
                "type": "string",
                "length": 3,
                "regexp": "[0-9]\.[0-9]",
                "defaultvalue": "0.0",
                "editable": False,
            },
            {"name": "icono", "alias": "Icono", "type": "pixmap", "allownull": True},
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    bloqueo = sqlalchemy.Column("bloqueo", sqlalchemy.Boolean)
    idmodulo = sqlalchemy.Column("idmodulo", sqlalchemy.String(15), primary_key=True)
    idarea = sqlalchemy.Column("idarea", sqlalchemy.String(15))
    descripcion = sqlalchemy.Column("descripcion", sqlalchemy.String(100))
    version = sqlalchemy.Column("version", sqlalchemy.String(3))
    icono = sqlalchemy.Column("icono", sqlalchemy.String)


# <--- Fields ---
