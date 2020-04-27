# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18
"""Flfiles_model module."""

from sqlalchemy.ext import declarative  # type: ignore [import] # noqa: F821
import sqlalchemy  # type: ignore [import] # noqa: F821


class Flfiles(declarative.declarative_base()):  # type: ignore [misc] # noqa: F821
    """Flfiles class."""

    __tablename__ = "flfiles"

    # --- Metadata --->
    legacy_metadata = {
        "name": "flfiles",
        "alias": "Ficheros de Texto",
        "fields": [
            {
                "name": "nombre",
                "alias": "Nombre",
                "pk": True,
                "type": "string",
                "length": 255,
                "regexp": "\w+\.(mtd|ts|ui|qs|qry|kut|xml|jrxml|svg)",  # noqa: W605
                "null": False,
            },
            {
                "name": "bloqueo",
                "alias": "Bloqueo",
                "type": "unlock",
                "null": False,
                "default": True,
            },
            {
                "name": "idmodulo",
                "alias": "Módulo",
                "type": "string",
                "length": 15,
                "relations": [
                    {"card": "M1", "table": "flmodules", "field": "idmodulo", "delC": True}
                ],
                "null": False,
            },
            {
                "name": "sha",
                "alias": "SHA1",
                "type": "string",
                "length": 255,
                "calculated": True,
                "editable": False,
            },
            {"name": "contenido", "alias": "Contenido", "type": "stringlist", "visiblegrid": False},
            {"name": "binario", "alias": "Binario", "type": "bytearray", "visiblegrid": False},
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
