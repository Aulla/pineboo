# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18
"""Fserial_model module."""

import sqlalchemy

from pineboolib import application

BASE = application.PROJECT.conn_manager.mainConn().declarative_base()


class Flserial(BASE):
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
