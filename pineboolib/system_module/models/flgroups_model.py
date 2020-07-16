# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18
"""Flgroups_model module."""

from pineboolib.application.database.orm import basemodel

import sqlalchemy  # type: ignore [import] # noqa: F821


class Flgroups(basemodel.BaseModel):  # type: ignore [misc] # noqa: F821
    """Flgroups class."""

    __tablename__ = "flgroups"

    # --- Metadata --->
    legacy_metadata = {
        "name": "flgroups",
        "alias": "Grupos de Usuarios",
        "fields": [
            {
                "name": "idgroup",
                "alias": "Nombre",
                "pk": True,
                "type": "string",
                "length": 30,
                "relations": [
                    {"card": "1M", "table": "flusers", "field": "idgroup"},
                    {"card": "1M", "table": "flacs", "field": "idgroup"},
                ],
                "null": False,
            },
            {"name": "descripcion", "alias": "Descripción", "type": "string", "length": 100},
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    idgroup = sqlalchemy.Column("idgroup", sqlalchemy.String(30), primary_key=True)
    descripcion = sqlalchemy.Column("descripcion", sqlalchemy.String(100))


# <--- Fields ---
