# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18

import sqlalchemy
from sqlalchemy.orm import relationship, validates
from pineboolib import application

BASE = application.PROJECT.conn_manager.mainConn().declarative_base()


class Fltest2(BASE):
    __tablename__ = "fltest2"

    # --- Metadata --->
    legacy_metadata = {
        "alias": "Test table",
        "query": "fltest2",
        "fields": [
            {
                "name": "id",
                "alias": "ID",
                "primarykey": True,
                "type": "serial",
                "visiblegrid": False,
                "editable": False,
            },
            {"name": "string_field", "alias": "String field", "type": "string", "allownull": True},
            {"name": "date_field", "alias": "Date field", "type": "date", "allownull": True},
            {"name": "time_field", "alias": "Time field", "type": "time", "allownull": True},
            {
                "name": "double_field",
                "alias": "Double field",
                "type": "double",
                "allownull": True,
                "defaultvalue": "0",
                "partinteger": 6,
                "partdecimal": 2,
            },
            {"name": "bool_field", "alias": "Bool field", "type": "bool", "allownull": True},
            {
                "name": "uint_field",
                "alias": "Unsigned int field",
                "type": "uint",
                "allownull": True,
                "defaultvalue": "0",
            },
            {
                "name": "int_field",
                "alias": "Int field",
                "type": "int",
                "allownull": True,
                "defaultvalue": "0",
            },
            {"name": "bloqueo", "alias": "Bloqueo", "type": "unlock", "defaultvalue": "True"},
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    id = sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True)
    string_field = sqlalchemy.Column("string_field", sqlalchemy.String)
    date_field = sqlalchemy.Column("date_field", sqlalchemy.DateTime)
    time_field = sqlalchemy.Column("time_field", sqlalchemy.DateTime)
    double_field = sqlalchemy.Column("double_field", sqlalchemy.Numeric(6, 2))
    bool_field = sqlalchemy.Column("bool_field", sqlalchemy.Boolean)
    uint_field = sqlalchemy.Column("uint_field", sqlalchemy.BigInteger)
    int_field = sqlalchemy.Column("int_field", sqlalchemy.Integer)
    bloqueo = sqlalchemy.Column("bloqueo", sqlalchemy.Boolean)


# <--- Fields ---
