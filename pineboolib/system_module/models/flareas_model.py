# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18
"""FLareas_model module."""

from pineboolib.application.database.orm import basemodel

import sqlalchemy


class Flareas(basemodel.BaseModel):  # type: ignore [misc] # noqa: F821
    """Flareas class."""

    __tablename__ = "flareas"

    # --- Metadata --->
    legacy_metadata = {
        "name": "flareas",
        "alias": "Áreas",
        "fields": [
            {
                "name": "bloqueo",
                "alias": "Bloqueo",
                "type": "unlock",
                "null": False,
                "default": True,
            },
            {
                "name": "idarea",
                "alias": "Área",
                "pk": True,
                "type": "string",
                "length": 15,
                "relations": [{"card": "1M", "table": "flmodules", "field": "idarea"}],
                "null": False,
            },
            {
                "name": "descripcion",
                "alias": "Descripción",
                "type": "string",
                "length": 100,
                "null": False,
            },
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    bloqueo = sqlalchemy.Column("bloqueo", sqlalchemy.Boolean)
    idarea = sqlalchemy.Column("idarea", sqlalchemy.String(15), primary_key=True)
    descripcion = sqlalchemy.Column("descripcion", sqlalchemy.String(100))

    # <--- Fields ---
