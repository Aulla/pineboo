# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18

import sqlalchemy
from sqlalchemy.orm import relationship, validates
from pineboolib import application

BASE = application.PROJECT.conn_manager.mainConn().declarative_base()


class Fltest4(BASE):
    __tablename__ = "fltest4"

    # --- Metadata --->
    legacy_metadata = {
        "name": "fltest4",
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
            {
                "name": "idmodulo",
                "alias": "Id. del Mï¿œdulo",
                "type": "string",
                "length": 15,
                "relations": [{"card": "1M", "table": "fltest", "field": "id"}],
            },
            {
                "name": "other_field",
                "alias": "otro campo",
                "type": "string",
                "length": 15,
                "relations": [{"card": "1M", "table": "fltest1234567", "field": "id"}],
            },
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    id = sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True)
    idmodulo = sqlalchemy.Column("idmodulo", sqlalchemy.String(15))
    other_field = sqlalchemy.Column("other_field", sqlalchemy.String(15))


# <--- Fields ---
