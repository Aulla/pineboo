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
from pineboolib.core.settings import config
from importlib import machinery

from sqlalchemy import String  # type: ignore

import importlib
import traceback
import sys
import os
from pineboolib import logging

from typing import Any

logger = logging.getLogger("PNORMModelsFactory")

# processed_: List[str] = []


def base_model(name: str) -> Any:
    """Import and return sqlAlchemy model for given table name."""
    # print("Base", name)
    from pineboolib.application import project

    if project.conn_manager is None:
        raise Exception("Project is not connected yet")

    path = _path("%s.mtd" % name, False)
    if path is None:
        return None
    if path.find("system_module/tables") > -1:
        path = path.replace(
            "system_module/tables",
            "%s/cache/%s/sys/file.mtd"
            % (config.value("ebcomportamiento/temp_dir"), project.conn_manager.mainConn().DBName()),
        )
    if path:
        path = "%s_model.py" % path[:-4]
        if os.path.exists(path):
            try:

                # FIXME: load_module is deprecated!
                # https://docs.python.org/3/library/importlib.html#importlib.machinery.SourceFileLoader.load_module
                loader = machinery.SourceFileLoader(name, path)
                return loader.load_module()  # type: ignore
            except Exception as exc:
                logger.warning("Error recargando model base:\n%s\n%s", exc, traceback.format_exc())
                pass

    return None


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
    from pineboolib.application import project

    db_name = project.conn_manager.mainConn().DBName()

    module = None
    file_path = filedir(
        config.value("ebcomportamiento/temp_dir"),
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
            logger.warning("Error cargando módulo:\n%s\n%s", exc, traceback.format_exc())
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
    from pineboolib.application import project

    if project.conn_manager is None:
        raise Exception("Project is not connected yet")

    # FIXME: Not a good idea to delete from other module
    del project.conn_manager.mainConn().driver().declarative_base_
    project.conn_manager.mainConn().driver().declarative_base_ = None


def load_models() -> None:
    """Load all sqlAlchemy models."""

    from pineboolib.application.qsadictmodules import QSADictModules
    from pineboolib.application import project

    if project.conn_manager is None:
        raise Exception("Project is not connected yet")

    main_conn = project.conn_manager.mainConn()

    db_name = main_conn.DBName()
    tables = main_conn.tables()

    QSADictModules.save_other("Base", main_conn.declarative_base())
    QSADictModules.save_other("session", main_conn.session())
    QSADictModules.save_other("engine", main_conn.engine())

    for t in tables:
        try:
            mod = base_model(t)
        except Exception:
            mod = None

        if mod is not None:
            model_name = "%s%s" % (t[0].upper(), t[1:])
            class_ = getattr(mod, model_name, None)
            if class_ is not None:
                QSADictModules.save_other(model_name, class_)

    for root, dirs, files in os.walk(
        filedir(config.value("ebcomportamiento/temp_dir"), "cache", db_name, "models")
    ):
        for nombre in files:  # Buscamos los presonalizados
            if nombre.endswith("pyc"):
                continue
            nombre = nombre.replace("_model.py", "")
            mod = load_model(nombre)
            if mod is not None:
                model_name = "%s%s" % (nombre[0].upper(), nombre[1:])

                class_ = getattr(mod, model_name, None)
                if class_ is not None:
                    QSADictModules.save_other(model_name, class_)


Calculated = String
