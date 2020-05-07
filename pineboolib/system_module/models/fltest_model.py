# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18
"""Fltest_model module."""

from sqlalchemy.ext import declarative  # type: ignore [import] # noqa: F821
import sqlalchemy  # type: ignore [import] # noqa: F821

from pineboolib.application.database.orm import basemodel


class Fltest(
    declarative.declarative_base(), basemodel.BaseModel  # type: ignore [misc] # noqa: F821
):
    """FLtest class."""

    __tablename__ = "fltest"

    # --- Metadata --->
    legacy_metadata = {
        "name": "fltest",
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
            {"name": "string_field", "alias": "String field", "type": "string"},
            {"name": "date_field", "alias": "Date field", "type": "date"},
            {"name": "time_field", "alias": "Time field", "type": "time"},
            {
                "name": "double_field",
                "alias": "Double field",
                "type": "double",
                "default": 0,
                "partI": 6,
                "partD": 2,
            },
            {"name": "bool_field", "alias": "Bool field", "type": "bool"},
            {"name": "uint_field", "alias": "Unsigned int field", "type": "uint", "default": 0},
            {
                "name": "bloqueo",
                "alias": "Bloqueo",
                "type": "unlock",
                "null": False,
                "default": True,
            },
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    id = sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True)
    string_field = sqlalchemy.Column("string_field", sqlalchemy.String)
    date_field = sqlalchemy.Column("date_field", sqlalchemy.Date)
    time_field = sqlalchemy.Column("time_field", sqlalchemy.Time)
    double_field = sqlalchemy.Column("double_field", sqlalchemy.Float)
    bool_field = sqlalchemy.Column("bool_field", sqlalchemy.Boolean)
    uint_field = sqlalchemy.Column("uint_field", sqlalchemy.BigInteger)
    bloqueo = sqlalchemy.Column("bloqueo", sqlalchemy.Boolean)


# <--- Fields ---
