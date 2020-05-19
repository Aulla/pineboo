# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18
"""Fltest4_model module."""

from sqlalchemy.ext import declarative  # type: ignore [import] # noqa: F821
import sqlalchemy  # type: ignore [import] # noqa: F821

from pineboolib.application.database.orm import basemodel


class Fltest4(
    declarative.declarative_base(), basemodel.BaseModel  # type: ignore [misc] # noqa: F821
):
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
                "alias": "Id. del Módulo",
                "type": "string",
                "length": 15,
                "relations": [{"card": "1M", "table": "fltest", "field": "id"}],
            },
            {
                "name": "idarea",
                "alias": "Área",
                "type": "string",
                "length": 15,
                "relations": [{"card": "1M", "table": "fltest5", "field": "idarea"}],
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
    idarea = sqlalchemy.Column("idarea", sqlalchemy.String(15))
    other_field = sqlalchemy.Column("other_field", sqlalchemy.String(15))


# <--- Fields ---
