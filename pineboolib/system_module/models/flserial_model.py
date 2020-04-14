# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18

import sqlalchemy
from sqlalchemy.orm import relationship, validates
from pineboolib import application

BASE = application.PROJECT.conn_manager.mainConn().declarative_base()


class Flserial(BASE):
    __tablename__ = "flserial"

    # --- Metadata --->
    legacy_metadata = {
        "name": "flserial",
        "alias": "Serie",
        "fields": [
            {"name": "serie", "alias": "Serie", "primarykey": True, "type": "serial"},
            {
                "name": "sha",
                "alias": "SHA1",
                "type": "string",
                "length": 255,
                "allownull": True,
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
