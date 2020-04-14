# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18

import sqlalchemy
from sqlalchemy.orm import relationship, validates
from pineboolib import application

BASE = application.PROJECT.conn_manager.mainConn().declarative_base()


class Flacls(BASE):
    __tablename__ = "flacls"

    # --- Metadata --->
    legacy_metadata = {
        "name": "flacls",
        "alias": "Listas de Control de Acceso",
        "fields": [
            {
                "name": "idacl",
                "alias": "Nombre",
                "primarykey": True,
                "type": "string",
                "length": 15,
                "relations": [{"card": "1M", "table": "flacs", "field": "idacl"}],
            },
            {
                "name": "descripcion",
                "alias": "Descripción",
                "type": "string",
                "length": 100,
                "allownull": True,
            },
            {"name": "instalada", "alias": "Instalada", "type": "bool", "allownull": True},
            {
                "name": "idgroupintro",
                "alias": "Grupo",
                "type": "string",
                "length": 30,
                "allownull": True,
            },
            {
                "name": "iduserintro",
                "alias": "Usuario",
                "type": "string",
                "length": 30,
                "allownull": True,
            },
            {
                "name": "prioridadgrupointro",
                "alias": "Prioridad por defecto",
                "type": "uint",
                "allownull": True,
                "defaultvalue": "2",
                "visiblegrid": False,
            },
            {
                "name": "prioridadusuariointro",
                "alias": "Prioridad por defecto(7)",
                "type": "uint",
                "allownull": True,
                "defaultvalue": "1",
                "visiblegrid": False,
            },
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    idacl = sqlalchemy.Column("idacl", sqlalchemy.String(15), primary_key=True)
    descripcion = sqlalchemy.Column("descripcion", sqlalchemy.String(100))
    instalada = sqlalchemy.Column("instalada", sqlalchemy.Boolean)
    idgroupintro = sqlalchemy.Column("idgroupintro", sqlalchemy.String(30))
    iduserintro = sqlalchemy.Column("iduserintro", sqlalchemy.String(30))
    prioridadgrupointro = sqlalchemy.Column("prioridadgrupointro", sqlalchemy.BigInteger)
    prioridadusuariointro = sqlalchemy.Column("prioridadusuariointro", sqlalchemy.BigInteger)


# <--- Fields ---
