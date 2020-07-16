# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18
"""Flmodules_model module."""

import sqlalchemy  # type: ignore [import] # noqa: F821

from pineboolib.application.database.orm import basemodel


class Flmodules(basemodel.BaseModel):  # type: ignore [misc] # noqa: F821
    """Flmodules class."""

    __tablename__ = "flmodules"

    # --- Metadata --->
    legacy_metadata = {
        "name": "flmodules",
        "alias": "Módulos",
        "fields": [
            {
                "name": "bloqueo",
                "alias": "Bloqueo",
                "type": "unlock",
                "null": False,
                "default": True,
            },
            {
                "name": "idmodulo",
                "alias": "Id. del Módulo",
                "pk": True,
                "type": "string",
                "length": 15,
                "relations": [{"card": "1M", "table": "flfiles", "field": "idmodulo"}],
                "null": False,
            },
            {
                "name": "idarea",
                "alias": "Id. del Área",
                "type": "string",
                "length": 15,
                "relations": [{"card": "M1", "table": "flareas", "field": "idarea"}],
                "null": False,
                "visiblegrid": False,
            },
            {
                "name": "descripcion",
                "alias": "Descripción",
                "type": "string",
                "length": 100,
                "null": False,
            },
            {
                "name": "version",
                "alias": "Versión",
                "type": "string",
                "length": 3,
                "regexp": "[0-9]\\.[0-9]",  # noqa: W605
                "null": False,
                "default": "0.0",
                "editable": False,
            },
            {"name": "icono", "alias": "Icono", "type": "pixmap"},
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
