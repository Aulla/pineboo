# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18
"""Flsetting_model module."""

import sqlalchemy

from sqlalchemy.ext import declarative  # type: ignore [import] # noqa: F821

BASE = declarative.declarative_base()


class Flsettings(BASE):
    """Flsetting class."""

    __tablename__ = "flsettings"

    # --- Metadata --->
    legacy_metadata = {
        "name": "flsettings",
        "alias": "Configuración global",
        "fields": [
            {
                "name": "flkey",
                "alias": "Clave",
                "pk": True,
                "type": "string",
                "length": 30,
                "null": False,
            },
            {"name": "valor", "alias": "Valor", "type": "stringlist", "visiblegrid": False},
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    flkey = sqlalchemy.Column("flkey", sqlalchemy.String(30), primary_key=True)
    valor = sqlalchemy.Column("valor", sqlalchemy.String)


# <--- Fields ---
