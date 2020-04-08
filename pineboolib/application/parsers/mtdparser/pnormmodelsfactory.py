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

# processed_: List[str] = []


def base_model(name: str) -> Any:
    """Import and return sqlAlchemy model for given table name."""
    # print("Base", name)

    if application.PROJECT.conn_manager is None:
        raise Exception("Project is not connected yet")

    path = _path("%s.mtd" % name, False)
    if path is None:
        return None
    if path.find("system_module/tables") > -1:
        path = "%s/cache/%s/sys/file.mtd%s" % (
            settings.CONFIG.value("ebcomportamiento/temp_dir"),
            application.PROJECT.conn_manager.mainConn().DBName(),
            path[path.find("system_module/tables") + 20 :],
        )

    if path:
        path = "%s_model.py" % path[:-4]
        if not os.path.exists(path):
            path = ""
            # try:

            # FIXME: load_module is deprecated!
            # https://docs.python.org/3/library/importlib.html#importlib.machinery.SourceFileLoader.load_module
            #    loader = machinery.SourceFileLoader(name, path)
            #    return loader.load_module()  # type: ignore
            # except Exception as exc:
            #    LOGGER.warning("Error recargando model base:\n%s\n%s", exc, traceback.format_exc())
            #    pass
    return path
    # return None


def load_model(nombre):
    """Import and return sqlAlchemy model for given table name."""

    if nombre is None:
        return

    # if nombre in processed_:
    #    return None

    # processed_.append(nombre)

    # nombre_qsa = nombre.replace("_model", "")
    # model_name = nombre_qsa[0].upper() + nombre_qsa[1:]
    # mod = getattr(qsa_dict_modules, model_name, None)
    # if mod is None:
    #    mod = base_model(nombre)
    #    if mod:
    #        setattr(qsa_dict_modules, model_name, mod)  # NOTE: Use application.qsadictmodules

    db_name = application.PROJECT.conn_manager.mainConn().DBName()

    module = None
    file_path = filedir(
        settings.CONFIG.value("ebcomportamiento/temp_dir"),
        "cache",
        db_name,
        "models",
        "%s_model.py" % nombre,
    )
    if os.path.exists(file_path):

        module_path = "%s_model" % (nombre)
        # if module_path in sys.modules:
        #    # print("Recargando", module_path)
        #    try:
        #        module = importlib.reload(sys.modules[module_path])
        #    except Exception as exc:
        #        logger.warning("Error recargando módulo:\n%s\n%s", exc, traceback.format_exc())
        #        pass
        # else:
        # print("Cargando", module_path)
        try:
            spec = importlib.util.spec_from_file_location(module_path, file_path)  # type: ignore
            module = importlib.util.module_from_spec(spec)  # type: ignore
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
        except Exception as exc:
            LOGGER.warning("Error cargando módulo:\n%s\n%s", exc, traceback.format_exc())
            pass
            # models_[nombre] = mod

    # if mod:
    #    setattr(qsa_dict_modules, model_name, mod)

    # print(3, nombre, mod)
    return module

    # if mod is not None:
    #    setattr(qsa_dict_modules,  model_name, mod)


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

    QSADictModules.save_other("Base", main_conn.declarative_base())
    QSADictModules.save_other("session", main_conn.session())
    QSADictModules.save_other("engine", main_conn.engine())

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
            model_path = base_model(table)

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
