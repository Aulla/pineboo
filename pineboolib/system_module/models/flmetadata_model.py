# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18
"""FLmetadata_model module."""

import sqlalchemy  # type: ignore [import] # noqa: F821

from pineboolib.application.database.orm import basemodel


class Flmetadata(basemodel.BaseModel):  # type: ignore [misc] # noqa: F821
    """Flmetadata class."""

    __tablename__ = "flmetadata"

    # --- Metadata --->
    legacy_metadata = {
        "name": "flmetadata",
        "alias": "Metadatos",
        "fields": [
            {
                "name": "tabla",
                "alias": "Nombre de la tabla",
                "pk": True,
                "type": "string",
                "length": 255,
                "null": False,
            },
            {"name": "xml", "alias": "Descripción XML", "type": "stringlist", "visiblegrid": False},
            {"name": "bloqueo", "alias": "Tabla bloqueada", "type": "bool"},
            {"name": "seq", "alias": "Secuencia", "type": "uint", "null": False},
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    tabla = sqlalchemy.Column("tabla", sqlalchemy.String(255), primary_key=True)
    xml = sqlalchemy.Column("xml", sqlalchemy.String)
    bloqueo = sqlalchemy.Column("bloqueo", sqlalchemy.Boolean)
    seq = sqlalchemy.Column("seq", sqlalchemy.BigInteger)


# <--- Fields ---
