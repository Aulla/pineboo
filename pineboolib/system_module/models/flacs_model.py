# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18
"""Flacs_model module."""

import sqlalchemy

from pineboolib import application

BASE = application.PROJECT.conn_manager.mainConn().declarative_base()


class Flacs(BASE):
    """Flacs class."""

    __tablename__ = "flacs"

    # --- Metadata --->
    legacy_metadata = {
        "name": "flacs",
        "alias": "Reglas de Control de Acceso",
        "fields": [
            {
                "name": "idac",
                "alias": "Identificador",
                "pk": True,
                "type": "serial",
                "relations": [{"card": "1M", "table": "flacos", "field": "idac"}],
                "null": False,
                "visiblegrid": False,
            },
            {"name": "prioridad", "alias": "Prioridad", "type": "uint", "null": False},
            {
                "name": "tipo",
                "alias": "Tipo",
                "ck": True,
                "type": "string",
                "length": 30,
                "null": False,
                "default": "mainwindow",
                "optionslist": ["mainwindow", "form", "table"],
            },
            {
                "name": "nombre",
                "alias": "Nombre",
                "ck": True,
                "type": "string",
                "length": 50,
                "null": False,
            },
            {
                "name": "iduser",
                "alias": "Usuario",
                "ck": True,
                "type": "string",
                "length": 30,
                "relations": [{"card": "M1", "table": "flusers", "field": "iduser"}],
            },
            {
                "name": "idgroup",
                "alias": "Grupo",
                "ck": True,
                "type": "string",
                "length": 30,
                "relations": [{"card": "M1", "table": "flgroups", "field": "idgroup"}],
            },
            {
                "name": "permiso",
                "alias": "Permiso Global",
                "type": "string",
                "length": 50,
                "regexp": "[r-][w-]",
            },
            {
                "name": "idacl",
                "alias": "Lista de Control de Acceso",
                "type": "string",
                "length": 15,
                "relations": [{"card": "M1", "table": "flacls", "field": "idacl", "delC": True}],
                "null": False,
            },
            {"name": "descripcion", "alias": "Descripción", "type": "string", "length": 100},
            {"name": "degrupo", "alias": "Aplicar a un grupo", "type": "bool", "null": False},
            {
                "name": "idarea",
                "alias": "Área",
                "type": "string",
                "length": 15,
                "relations": [{"card": "M1", "table": "flareas", "field": "idarea"}],
            },
            {
                "name": "idmodule",
                "alias": "Módulo",
                "type": "string",
                "length": 15,
                "relations": [{"card": "M1", "table": "flmodules", "field": "idmodulo"}],
                "associated": {"with": "idarea", "by": "idarea"},
            },
            {
                "name": "tipoform",
                "alias": "Formulario",
                "type": "string",
                "length": 30,
                "null": False,
                "default": "Maestro",
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
