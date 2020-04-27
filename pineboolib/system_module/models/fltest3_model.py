# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18
"""Fltest3_model module."""

from sqlalchemy.ext import declarative  # type: ignore [import] # noqa: F821
import sqlalchemy  # type: ignore [import] # noqa: F821


class Fltest3(declarative.declarative_base()):  # type: ignore [misc] # noqa: F821
    """Fltest3 class."""

    __tablename__ = "fltest3"

    # --- Metadata --->
    legacy_metadata = {
        "name": "fltest3",
        "alias": "Test table",
        "fields": [
            {
                "name": "counter",
                "alias": "Contador",
                "pk": True,
                "type": "string",
                "length": 6,
                "null": False,
                "counter": True,
                "visiblegrid": False,
                "editable": False,
            },
            {"name": "string_field", "alias": "String field", "type": "string", "default": ""},
            {
                "name": "timezone_field",
                "alias": "TimeZone field",
                "type": "timestamp",
                "null": False,
                "default": "",
            },
            {
                "name": "bool_field",
                "alias": "Bool field",
                "type": "bool",
                "null": False,
                "default": False,
            },
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    counter = sqlalchemy.Column("counter", sqlalchemy.String(6), primary_key=True)
    string_field = sqlalchemy.Column("string_field", sqlalchemy.String)
    timezone_field = sqlalchemy.Column("timezone_field", sqlalchemy.DateTime)
    bool_field = sqlalchemy.Column("bool_field", sqlalchemy.Boolean)


# <--- Fields ---
