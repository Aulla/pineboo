# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18

import sqlalchemy
from sqlalchemy.orm import relationship, validates
from pineboolib import application

BASE = application.PROJECT.conn_manager.mainConn().declarative_base()


class Flacos(BASE):
    __tablename__ = "flacos"

    # --- Metadata --->
    legacy_metadata = {
        "alias": "Objetos de Control de Acceso",
        "fields": [
            {
                "name": "idaco",
                "alias": "Identificador",
                "primarykey": True,
                "type": "serial",
                "visiblegrid": False,
            },
            {
                "name": "nombre",
                "alias": "Nombre",
                "compoundkey": True,
                "type": "string",
                "length": 100,
            },
            {
                "name": "permiso",
                "alias": "Permiso",
                "type": "string",
                "length": 50,
                "regexp": "[r-][w-]",
                "defaultvalue": "--",
            },
            {
                "name": "idac",
                "alias": "Control de Acceso",
                "compoundkey": True,
                "type": "uint",
                "visiblegrid": False,
            },
            {
                "name": "descripcion",
                "alias": "Descripción",
                "type": "string",
                "length": 100,
                "allownull": True,
            },
            {
                "name": "tipocontrol",
                "alias": "Control",
                "type": "string",
                "length": 30,
                "allownull": True,
                "defaultvalue": "Todos",
                "optionslist": [
                    "Botón",
                    "Campo",
                    "Tabla",
                    "Grupo de controles",
                    "Pestaña",
                    "Todos",
                ],
            },
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    idaco = sqlalchemy.Column("idaco", sqlalchemy.Integer, primary_key=True)
    nombre = sqlalchemy.Column("nombre", sqlalchemy.String(100))
    permiso = sqlalchemy.Column("permiso", sqlalchemy.String(50))
    idac = sqlalchemy.Column("idac", sqlalchemy.BigInteger)
    descripcion = sqlalchemy.Column("descripcion", sqlalchemy.String(100))
    tipocontrol = sqlalchemy.Column("tipocontrol", sqlalchemy.String(30))


# <--- Fields ---
