# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18

import sqlalchemy
from sqlalchemy.orm import relationship, validates
from pineboolib import application

BASE = application.PROJECT.conn_manager.mainConn().declarative_base()


class Flacs(BASE):
    __tablename__ = "flacs"

    # --- Metadata --->
    legacy_metadata = {
        "name": "flacs",
        "alias": "Reglas de Control de Acceso",
        "fields": [
            {
                "name": "idac",
                "alias": "Identificador",
                "primarykey": True,
                "type": "serial",
                "relations": [{"card": "1M", "table": "flacos", "field": "idac"}],
                "visiblegrid": False,
            },
            {"name": "prioridad", "alias": "Prioridad", "type": "uint"},
            {
                "name": "tipo",
                "alias": "Tipo",
                "compoundkey": True,
                "type": "string",
                "length": 30,
                "defaultvalue": "mainwindow",
                "optionslist": ["mainwindow", "form", "table"],
            },
            {
                "name": "nombre",
                "alias": "Nombre",
                "compoundkey": True,
                "type": "string",
                "length": 50,
            },
            {
                "name": "iduser",
                "alias": "Usuario",
                "compoundkey": True,
                "type": "string",
                "length": 30,
                "allownull": True,
            },
            {
                "name": "idgroup",
                "alias": "Grupo",
                "compoundkey": True,
                "type": "string",
                "length": 30,
                "allownull": True,
            },
            {
                "name": "permiso",
                "alias": "Permiso Global",
                "type": "string",
                "length": 50,
                "regexp": "[r-][w-]",
                "allownull": True,
            },
            {
                "name": "idacl",
                "alias": "Lista de Control de Acceso",
                "type": "string",
                "length": 15,
            },
            {
                "name": "descripcion",
                "alias": "Descripción",
                "type": "string",
                "length": 100,
                "allownull": True,
            },
            {"name": "degrupo", "alias": "Aplicar a un grupo", "type": "bool"},
            {"name": "idarea", "alias": "Área", "type": "string", "length": 15, "allownull": True},
            {
                "name": "idmodule",
                "alias": "Módulo",
                "type": "string",
                "length": 15,
                "allownull": True,
            },
            {
                "name": "tipoform",
                "alias": "Formulario",
                "type": "string",
                "length": 30,
                "defaultvalue": "Maestro",
                "optionslist": ["Maestro", "Edición", "Búsqueda"],
            },
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    idac = sqlalchemy.Column("idac", sqlalchemy.Integer, primary_key=True)
    prioridad = sqlalchemy.Column("prioridad", sqlalchemy.BigInteger)
    tipo = sqlalchemy.Column("tipo", sqlalchemy.String(30))
    nombre = sqlalchemy.Column("nombre", sqlalchemy.String(50))
    iduser = sqlalchemy.Column("iduser", sqlalchemy.String(30))
    idgroup = sqlalchemy.Column("idgroup", sqlalchemy.String(30))
    permiso = sqlalchemy.Column("permiso", sqlalchemy.String(50))
    idacl = sqlalchemy.Column("idacl", sqlalchemy.String(15))
    descripcion = sqlalchemy.Column("descripcion", sqlalchemy.String(100))
    degrupo = sqlalchemy.Column("degrupo", sqlalchemy.Boolean)
    idarea = sqlalchemy.Column("idarea", sqlalchemy.String(15))
    idmodule = sqlalchemy.Column("idmodule", sqlalchemy.String(15))
    tipoform = sqlalchemy.Column("tipoform", sqlalchemy.String(30))


# <--- Fields ---
