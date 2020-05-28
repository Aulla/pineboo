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
from importlib import machinery

from sqlalchemy import exc  # type: ignore

from pineboolib import logging, application
from . import pnmtdparser

from typing import Any, List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.application.metadata import pntablemetadata

LOGGER = logging.get_logger(__name__)
PROCESSED: List[str] = []


def empty_base():
    """Cleanup sqlalchemy models."""

    if application.PROJECT.conn_manager is None:
        raise Exception("Project is not connected yet")

    # FIXME: Not a good idea to delete from other module
    if hasattr(application.PROJECT.conn_manager.mainConn().driver(), "_declarative_base"):
        del application.PROJECT.conn_manager.mainConn().driver()._declarative_base
    application.PROJECT.conn_manager.mainConn().driver()._declarative_base = None


def register_metadata_as_model(metadata: "pntablemetadata.PNTableMetaData") -> None:
    """Register a mtd as model."""

    from pineboolib.application import qsadictmodules
    name_ = metadata.name()

    if "%s_model" % name_ in PROCESSED or qsadictmodules.QSADictModules.from_project("%s_orm" % name_):
        LOGGER.warning("%s already exists as model" % name_)
        return
    else:
        LOGGER.warning("Parsing %s", name_)
        path_ = pnmtdparser.mtd_parse(metadata)
        
        loader = machinery.SourceFileLoader("model", path_)
        model_module = loader.load_module()  # type: ignore [call-arg] # noqa: F821
        model_class = getattr(model_module, "%s%s" % (name_[0].upper(), name_[1:]), None)
        if model_class is not None:
            qsadictmodules.QSADictModules.save_other("%s_orm" % name_, model_class)

        PROCESSED.append(name_)


def load_models() -> None:
    """Load all sqlAlchemy models."""
    # print("LOADING MODELS!!!")
    from pineboolib.application.qsadictmodules import QSADictModules

    if application.PROJECT.conn_manager is None:
        raise Exception("Project is not connected yet")

    # main_conn = application.PROJECT.conn_manager.mainConn()
    # db_name = main_conn.DBName()
    # print("Cargando modelos")
    # QSADictModules.save_other("Base", main_conn.declarative_base())
    # QSADictModules.save_other("session", main_conn.session())
    # QSADictModules.save_other("engine", main_conn.engine())

    models_: Dict[str, Any] = {}

    for action_name in application.PROJECT.actions:
        class_orm = application.PROJECT.actions[action_name]._class_orm
        if class_orm:
            path_class_orm = _path(class_orm, False)
            if not path_class_orm:
                LOGGER.warning(
                    "Se ha especificado un model (%s) en el action %s, pero el fichero no existe",
                    class_orm,
                    action_name,
                )
                continue
            if class_orm in PROCESSED:
                continue

            models_[class_orm] = path_class_orm
            # print("***", class_orm)
            PROCESSED.append(class_orm)

    for key in application.PROJECT.files.keys():
        file_ = application.PROJECT.files[key]
        if file_.filename.endswith("_model.py"):
            name = key[:-3]
            if name.endswith(".mtd_model"):
                name = "%s_model" % name[:-10]

            if name in PROCESSED:
                # LOGGER.warning(
                #    "Se está cargando el model %s, pero ya existe desde action. Omitido" % name
                # )
                continue
            else:
                # print("****", name)
                PROCESSED.append(name)
                models_[name] = file_.path()

    for mod_ in models_.keys():
        # if mod_ in processed:
        #    continue

        # print("Guardando", mod_, "como", "%s_orm" % mod_[:-6])
        try:
            loader = machinery.SourceFileLoader("model", models_[mod_])
            # print(1, mod_)
            model_module = loader.load_module()  # type: ignore [call-arg] # noqa: F821
            # print(2, model_module, "%s%s" % (mod_[0].upper(), mod_[1:-6]))
            model_class = getattr(model_module, "%s%s" % (mod_[0].upper(), mod_[1:-6]), None)
            if model_class is not None:
                # print(3)
                QSADictModules.save_other("%s_orm" % mod_[:-6], model_class)

        except exc.InvalidRequestError as error:
            LOGGER.warning(str(error))


# ===============================================================================
#
#     for action_name in application.PROJECT.actions:
#         table = application.PROJECT.actions[action_name]._table
#
#         if not table or table in tables_loaded:
#             continue
#
#         model_name = "%s%s" % (table[0].upper(), table[1:])
#         class_orm = application.PROJECT.actions[action_name]._class_orm
#         if _path(class_orm, False):
#             action_model = application.PROJECT.actions[action_name]._class_orm
#         else:
#             if class_orm:
#                 LOGGER.warning(
#                     "Se ha especificado un model (%s) en el action %s, pero el fichero no existe",
#                     application.PROJECT.actions[action_name]._class_orm,
#                     action_name,
#                 )
#             action_model = ""
#
#         if action_model:
#
#             model_path = _path("%s.py" % action_model)
#         else:
#             print("FIXME! buscar ruta carga model", action_name)
#             model_path = _path("%s_model.py" % table, False) or ""
#
#         if model_path:
#             try:
#                 loader = machinery.SourceFileLoader("model", model_path)
#                 model_module = loader.load_module()  # type: ignore [call-arg] # noqa: F821
#                 model_class = getattr(model_module, model_name, None)
#                 if model_class is not None:
#                     QSADictModules.save_other("%s_orm" % table, model_class)
#
#             except exc.InvalidRequestError as error:
#                 LOGGER.warning(str(error))
#
#             else:
#                 tables_loaded.append(table)
# ===============================================================================
