# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18
"""Flupdates_model module."""

import sqlalchemy

from sqlalchemy.ext import declarative  # type: ignore [import] # noqa: F821

BASE = declarative.declarative_base()


class Flupdates(BASE):
    """Flupdates class."""

    __tablename__ = "flupdates"

    # --- Metadata --->
    legacy_metadata = {
        "name": "flupdates",
        "alias": "Registro de instalaciÃ³n/actualizaciÃ³n de paquetes",
        "fields": [
            {
                "name": "id",
                "alias": "ID",
                "pk": True,
                "type": "serial",
                "null": False,
                "visiblegrid": False,
                "editable": False,
            },
            {
                "name": "actual",
                "alias": "Instalado actualmente",
                "type": "bool",
                "null": False,
                "default": True,
                "editable": False,
            },
            {"name": "fecha", "alias": "Fecha", "type": "date", "null": False, "editable": False},
            {"name": "hora", "alias": "Hora", "type": "time", "null": False, "editable": False},
            {
                "name": "nombre",
                "alias": "Nombre del Paquete",
                "type": "string",
                "length": 255,
                "regexp": "\w+\.(abanq)",  # noqa: W605
                "null": False,
                "editable": False,
            },
            {
                "name": "modulesdef",
                "alias": "Modules Def.",
                "type": "stringlist",
                "null": False,
                "visible": False,
                "visiblegrid": False,
                "editable": False,
            },
            {
                "name": "filesdef",
                "alias": "Files Def.",
                "type": "stringlist",
                "null": False,
                "visible": False,
                "visiblegrid": False,
                "editable": False,
            },
            {
                "name": "shaglobal",
                "alias": "SHA1 Global",
                "type": "string",
                "length": 255,
                "null": False,
                "visible": False,
                "visiblegrid": False,
                "editable": False,
            },
            {
                "name": "auxtxt",
                "alias": "Auxiliar Texto",
                "type": "stringlist",
                "visible": False,
                "visiblegrid": False,
                "editable": False,
            },
            {
                "name": "auxbin",
                "alias": "Auxiliar Binario",
                "type": "bytearray",
                "visible": False,
                "visiblegrid": False,
                "editable": False,
            },
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    id = sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True)
    actual = sqlalchemy.Column("actual", sqlalchemy.Boolean)
    fecha = sqlalchemy.Column("fecha", sqlalchemy.DateTime)
    hora = sqlalchemy.Column("hora", sqlalchemy.DateTime)
    nombre = sqlalchemy.Column("nombre", sqlalchemy.String(255))
    modulesdef = sqlalchemy.Column("modulesdef", sqlalchemy.String)
    filesdef = sqlalchemy.Column("filesdef", sqlalchemy.String)
    shaglobal = sqlalchemy.Column("shaglobal", sqlalchemy.String(255))
    auxtxt = sqlalchemy.Column("auxtxt", sqlalchemy.String)
    auxbin = sqlalchemy.Column("auxbin", sqlalchemy.LargeBinary)


# <--- Fields ---
