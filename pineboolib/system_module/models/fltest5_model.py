# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18
"""Fltest5_model module."""

import sqlalchemy  # type: ignore [import] # noqa: F821

from pineboolib.application.database.orm import basemodel


class Fltest5(basemodel.BaseModel):  # type: ignore [misc] # noqa: F821
    """Fltest5 class."""

    __tablename__ = "fltest5"

    # --- Metadata --->
    legacy_metadata = {
        "name": "fltest5",
        "alias": "Test table",
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
                "name": "idmodulo",
                "alias": "Id. del Módulo",
                "type": "string",
                "length": 15,
                "null": False,
            },
            {
                "name": "idarea",
                "alias": "Id. del Área",
                "type": "string",
                "length": 15,
                "relations": [{"card": "M1", "table": "fltest4", "field": "idarea", "delC": True}],
                "null": False,
            },
            {"name": "string_timestamp", "alias": "String timestamp", "type": "timestamp"},
            {"name": "uint_field", "alias": "Unsigned int field", "type": "uint"},
            {"name": "my_json", "alias": "json field", "type": "json"},
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    id = sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True)
    idmodulo = sqlalchemy.Column("idmodulo", sqlalchemy.String(15))
    idarea = sqlalchemy.Column("idarea", sqlalchemy.String(15))
    string_timestamp = sqlalchemy.Column("string_timestamp", sqlalchemy.DateTime)
    uint_field = sqlalchemy.Column("uint_field", sqlalchemy.BigInteger)
    my_json = sqlalchemy.Column("my_json", sqlalchemy.types.JSON)


# <--- Fields ---
