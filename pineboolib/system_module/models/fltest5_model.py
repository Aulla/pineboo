# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18
"""Fltest5_model module."""

import sqlalchemy

from sqlalchemy.ext import declarative  # type: ignore [import] # noqa: F821

BASE = declarative.declarative_base()


class Fltest5(BASE):
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
                "alias": "Id. del Mï¿œdulo",
                "type": "string",
                "length": 15,
                "null": False,
            },
            {"name": "string_timestamp", "alias": "String timestamp", "type": "timestamp"},
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    id = sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True)
    idmodulo = sqlalchemy.Column("idmodulo", sqlalchemy.String(15))
    string_timestamp = sqlalchemy.Column("string_timestamp", sqlalchemy.DateTime)


# <--- Fields ---
