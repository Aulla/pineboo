# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18
"""FLlarge_model module."""

import sqlalchemy  # type: ignore [import] # noqa: F821

from pineboolib.application.database.orm import basemodel


class Fllarge(basemodel.BaseModel):  # type: ignore [misc] # noqa: F821
    """Fllarge class."""

    __tablename__ = "fllarge"

    # --- Metadata --->
    legacy_metadata = {
        "name": "fllarge",
        "alias": "Ficheros de gran tamaño",
        "fields": [
            {
                "name": "refkey",
                "alias": "Clave de Referencia",
                "pk": True,
                "type": "string",
                "length": 100,
                "null": False,
            },
            {"name": "sha1", "alias": "Hash Sha1", "type": "string", "length": 50},
            {"name": "contenido", "alias": "Contenido", "type": "stringlist", "visiblegrid": False},
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    refkey = sqlalchemy.Column("refkey", sqlalchemy.String(100), primary_key=True)
    sha1 = sqlalchemy.Column("sha1", sqlalchemy.String(50))
    contenido = sqlalchemy.Column("contenido", sqlalchemy.String)


# <--- Fields ---
