# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18
"""Fltest5_model module."""

from sqlalchemy.ext import declarative  # type: ignore [import] # noqa: F821
import sqlalchemy  # type: ignore [import] # noqa: F821


class Fltest5(declarative.declarative_base()):  # type: ignore [misc] # noqa: F821
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
            {"name": "string_timestamp", "alias": "String timestamp", "type": "timestamp"},
            {"name": "uint_field", "alias": "Unsigned int field", "type": "uint"},
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    id = sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True)
    idmodulo = sqlalchemy.Column("idmodulo", sqlalchemy.String(15))
    string_timestamp = sqlalchemy.Column("string_timestamp", sqlalchemy.DateTime)
    uint_field = sqlalchemy.Column("uint_field", sqlalchemy.BigInteger)


# <--- Fields ---
