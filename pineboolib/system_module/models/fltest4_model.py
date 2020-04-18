# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18
"""Fltest4_model module."""

import sqlalchemy

from sqlalchemy.ext import declarative  # type: ignore [import] # noqa: F821

BASE = declarative.declarative_base()


class Fltest4(BASE):
    """Fltest4 class."""

    __tablename__ = "fltest4"

    # --- Metadata --->
    legacy_metadata = {
        "name": "fltest4",
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
                "relations": [{"card": "1M", "table": "fltest", "field": "id"}],
                "null": False,
            },
            {
                "name": "other_field",
                "alias": "otro campo",
                "type": "string",
                "length": 15,
                "relations": [{"card": "1M", "table": "fltest1234567", "field": "id"}],
                "null": False,
            },
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    id = sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True)
    idmodulo = sqlalchemy.Column("idmodulo", sqlalchemy.String(15))
    other_field = sqlalchemy.Column("other_field", sqlalchemy.String(15))


# <--- Fields ---
