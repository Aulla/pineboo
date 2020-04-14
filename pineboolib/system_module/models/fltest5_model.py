# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18

import sqlalchemy
from sqlalchemy.orm import relationship, validates
from pineboolib import application

BASE = application.PROJECT.conn_manager.mainConn().declarative_base()


class Fltest5(BASE):
    __tablename__ = "fltest5"

    # --- Metadata --->
    legacy_metadata = {
        "alias": "Test table",
        "fields": [
            {
                "name": "id",
                "alias": "ID",
                "primarykey": True,
                "type": "serial",
                "visiblegrid": False,
                "editable": False,
            },
            {"name": "idmodulo", "alias": "Id. del Mï¿œdulo", "type": "string", "length": 15},
            {
                "name": "string_timestamp",
                "alias": "String timestamp",
                "type": "timestamp",
                "allownull": True,
            },
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    id = sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True)
    idmodulo = sqlalchemy.Column("idmodulo", sqlalchemy.String(15))
    string_timestamp = sqlalchemy.Column("string_timestamp", sqlalchemy.DateTime)


# <--- Fields ---
