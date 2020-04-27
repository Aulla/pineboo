# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18
"""Flusers_model module."""

from sqlalchemy.ext import declarative  # type: ignore [import] # noqa: F821
import sqlalchemy  # type: ignore [import] # noqa: F821


class Flusers(declarative.declarative_base()):  # type: ignore [misc] # noqa: F821
    """Fusers class."""

    __tablename__ = "flusers"

    # --- Metadata --->
    legacy_metadata = {
        "name": "flusers",
        "alias": "Usuarios",
        "fields": [
            {
                "name": "iduser",
                "alias": "Nombre",
                "pk": True,
                "type": "string",
                "length": 30,
                "relations": [{"card": "1M", "table": "flacs", "field": "iduser"}],
                "null": False,
            },
            {
                "name": "idgroup",
                "alias": "Grupo",
                "type": "string",
                "length": 30,
                "relations": [{"card": "M1", "table": "flgroups", "field": "idgroup"}],
                "null": False,
            },
            {"name": "descripcion", "alias": "Descripción", "type": "string", "length": 100},
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    iduser = sqlalchemy.Column("iduser", sqlalchemy.String(30), primary_key=True)
    idgroup = sqlalchemy.Column("idgroup", sqlalchemy.String(30))
    descripcion = sqlalchemy.Column("descripcion", sqlalchemy.String(100))


# <--- Fields ---
