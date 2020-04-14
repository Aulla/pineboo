# -*- coding: utf-8 -*-
"""
Create and register sqlAlchemy models in QSA tree.

Para llamar a uno de estos se puede hacer desde cualquier script de la siguiente manera

from pineboolib.qsa import *

cli = Clientes() <- Este es un modelo disponible, nombre del mtd existente y comenzando en Mayuscula.

También es posible recargar estos modelos creados a raiz de los mtds. Se puede crear por ejemplo
(tempdata)/cache/nombre_de_bd/models/Clientes_model.py. Esta librería sobrecargará en el arbol qsa la previa por defecto.

Un ejemplo sería:

    from pineboolib.qsa import *
    from sqlalchemy.orm import reconstructor

    class Clientes(Clientes):
        @reconstructor

        def init(self):
            print("Inicializado", self.nombre)


        def saluda(self):
            print("Hola", self.nombre)


Ejemplo de uso:
    from pineboolib.qsa import *

    session = aqApp.session()

    for instance in session.query(Clientes).order_by(Clientes.codcliente):
        instance.saluda()

"""
from pineboolib.application.utils.path import _path
from pineboolib.core.utils.utils_base import filedir
from pineboolib.core import settings
from importlib import machinery

from sqlalchemy import String, exc  # type: ignore

import importlib
import traceback
import sys
import os
from pineboolib import logging, application

from typing import Any, List

LOGGER = logging.get_logger(__name__)


def empty_base():
    """Cleanup sqlalchemy models."""

    if application.PROJECT.conn_manager is None:
        raise Exception("Project is not connected yet")

    # FIXME: Not a good idea to delete from other module
    del application.PROJECT.conn_manager.mainConn().driver().declarative_base_
    application.PROJECT.conn_manager.mainConn().driver().declarative_base_ = None


def load_models() -> None:
    """Load all sqlAlchemy models."""
    from pineboolib.application.qsadictmodules import QSADictModules

    if application.PROJECT.conn_manager is None:
        raise Exception("Project is not connected yet")

    main_conn = application.PROJECT.conn_manager.mainConn()

    # db_name = main_conn.DBName()
    # print("Cargando modelos")
    # QSADictModules.save_other("Base", main_conn.declarative_base())
    # QSADictModules.save_other("session", main_conn.session())
    # QSADictModules.save_other("engine", main_conn.engine())

    tables_loaded: List[str] = []

    for action_name in application.PROJECT.actions:
        table = application.PROJECT.actions[action_name]._table

        if not table or table in tables_loaded:
            continue

        model_name = "%s%s" % (table[0].upper(), table[1:])
        class_orm = application.PROJECT.actions[action_name]._class_orm
        if _path(class_orm, False):
            action_model = application.PROJECT.actions[action_name]._class_orm
        else:
            if class_orm:
                LOGGER.warning(
                    "Se ha especificado un model (%s) en el action %s, pero el fichero no existe",
                    application.PROJECT.actions[action_name]._class_orm,
                    action_name,
                )
            action_model = ""

        if action_model:

            model_path = _path("%s.py" % action_model)
        else:
            print("FIXME! buscar ruta carga model", action_name)
            model_path = _path("%s_model.py" % table, False) or ""

        if model_path:
            try:
                loader = machinery.SourceFileLoader("model", model_path)
                model_module = loader.load_module()  # type: ignore [call-arg] # noqa: F821
                model_class = getattr(model_module, model_name, None)
                if model_class is not None:
                    QSADictModules.save_other("%s_orm" % table, model_class)

            except exc.InvalidRequestError as error:
                LOGGER.warning(str(error))

            else:
                tables_loaded.append(table)


Calculated = String
