# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18
"""Flseqs_model module."""

import sqlalchemy  # type: ignore [import] # noqa: F821

from pineboolib.application.database.orm import basemodel


class Flseqs(basemodel.BaseModel):  # type: ignore [misc] # noqa: F821
    """Flseqs class."""

    __tablename__ = "flseqs"

    # --- Metadata --->
    legacy_metadata = {
        "name": "flseqs",
        "alias": "Secuencias",
        "fields": [
            {
                "name": "tabla",
                "alias": "Nombre de la tabla",
                "pk": True,
                "type": "string",
                "length": 255,
                "null": False,
            },
            {
                "name": "campo",
                "alias": "Nombre del campo",
                "ck": True,
                "type": "string",
                "length": 255,
                "null": False,
            },
            {"name": "seq", "alias": "Secuencia", "type": "uint", "null": False},
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    tabla = sqlalchemy.Column("tabla", sqlalchemy.String(255), primary_key=True)
    campo = sqlalchemy.Column("campo", sqlalchemy.String(255))
    seq = sqlalchemy.Column("seq", sqlalchemy.BigInteger)


# <--- Fields ---
