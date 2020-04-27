# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18
"""Fserial_model module."""

from sqlalchemy.ext import declarative  # type: ignore [import] # noqa: F821
import sqlalchemy  # type: ignore [import] # noqa: F821


class Flserial(declarative.declarative_base()):  # type: ignore [misc] # noqa: F821
    """Flserial class."""

    __tablename__ = "flserial"

    # --- Metadata --->
    legacy_metadata = {
        "name": "flserial",
        "alias": "Serie",
        "fields": [
            {"name": "serie", "alias": "Serie", "pk": True, "type": "serial", "null": False},
            {
                "name": "sha",
                "alias": "SHA1",
                "type": "string",
                "length": 255,
                "calculated": True,
                "editable": False,
            },
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    serie = sqlalchemy.Column("serie", sqlalchemy.Integer, primary_key=True)
    sha = sqlalchemy.Column("sha", sqlalchemy.String(255))


# <--- Fields ---
