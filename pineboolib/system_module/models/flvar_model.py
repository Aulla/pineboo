# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18
"""Flvar_model module."""

import sqlalchemy  # type: ignore [import] # noqa: F821

from pineboolib.application.database.orm import basemodel


class Flvar(basemodel.BaseModel):  # type: ignore [misc] # noqa: F821
    """Flvar class."""

    __tablename__ = "flvar"

    # --- Metadata --->
    legacy_metadata = {
        "name": "flvar",
        "alias": "Variables",
        "fields": [
            {
                "name": "id",
                "alias": "Identificador",
                "pk": True,
                "type": "serial",
                "null": False,
                "visiblegrid": False,
            },
            {
                "name": "idvar",
                "alias": "Identificador de la variable",
                "ck": True,
                "type": "string",
                "length": 30,
                "null": False,
            },
            {
                "name": "idsesion",
                "alias": "Identificador de la sesión",
                "ck": True,
                "type": "string",
                "length": 30,
                "null": False,
            },
            {
                "name": "valor",
                "alias": "Valor",
                "type": "stringlist",
                "null": False,
                "visiblegrid": False,
            },
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    id = sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True)
    idvar = sqlalchemy.Column("idvar", sqlalchemy.String(30))
    idsesion = sqlalchemy.Column("idsesion", sqlalchemy.String(30))
    valor = sqlalchemy.Column("valor", sqlalchemy.String)


# <--- Fields ---
