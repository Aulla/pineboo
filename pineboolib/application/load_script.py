"""Load_script module."""

from pineboolib.core.utils import logging
from .utils.path import _path

from typing import Optional, TYPE_CHECKING


from pineboolib.application.staticloader import pnmodulesstaticloader
from pineboolib import application

import xml.etree.ElementTree as ET
from importlib import machinery
from sqlalchemy.ext import declarative
from sqlalchemy import exc

import shutil
import time
import os

if TYPE_CHECKING:
    from pineboolib.qsa import formdbwidget
    from pineboolib.application import xmlaction
    from sqlalchemy.ext.declarative import api  # noqa: F401
    from types import ModuleType

LOGGER = logging.get_logger(__name__)


def load_script(script_name: str, action_: "xmlaction.XMLAction") -> "formdbwidget.FormDBWidget":
    """
    Transform QS script into Python and starts it up.
    """

    # LOGGER.info(
    #    "LOADING SCRIPT %s (ALWAYS PARSE QSA: %s) ----->",
    #    script_name.upper(),
    #    application.PROJECT.no_python_cache,
    # )
    if script_name:
        script_name = script_name.replace(".qs", "")
        LOGGER.debug("Loading script %s for action %s", script_name, action_._name)
    else:
        LOGGER.info("No script to load for action %s", action_._name)

    script_loaded = None
    generate_static_flag_file = True

    if script_name:

        script_path_qs: str = _path("%s.qs" % script_name, False) or ""
        script_path_py = _path("%s.py" % script_name, False) or ""  # Busqueda en carpetas .py

        if script_path_qs and not script_path_py:  # busqueda en carpetas .qs.py
            script_path_py = (
                "%spy" % script_path_qs[:-2] if os.path.exists("%spy" % script_path_qs[:-2]) else ""
            )

        if application.PROJECT.no_python_cache:
            if script_path_qs:
                script_path_py = ""

        script_path_py_static: str = ""
        script_path_qs_static: str = ""
        static_flag = ""
        old_script_path_py = ""

        if script_path_qs:
            static_flag = "%s/static.xml" % os.path.dirname(script_path_qs)

        script_path_py_static = _static_file("%s.py" % script_name)
        script_path_qs_static = _static_file("%s.qs" % script_name)

        if script_path_qs_static and not script_path_py_static:

            script_path_py = ""

        elif script_path_py_static:
            old_script_path_py = script_path_py
            script_path_py = script_path_py_static

        if script_path_py:
            if os.path.exists(static_flag):
                os.remove(static_flag)

            if old_script_path_py:  # si es carga estática lo marco:
                if old_script_path_py.find("system_module") > -1:
                    generate_static_flag_file = False

                static_flag = "%s/static.xml" % os.path.dirname(old_script_path_py)
                if os.path.exists(static_flag):
                    os.remove(static_flag)

                if generate_static_flag_file:
                    xml_data = get_static_flag(old_script_path_py, script_path_py)
                    my_data = ET.tostring(xml_data, encoding="utf8", method="xml")
                    file_ = open(static_flag, "wb")
                    file_.write(my_data)

            # LOGGER.info("Loading script PY %s -> %s", script_name, script_path_py)
            if not os.path.isfile(script_path_py):
                raise IOError
            try:
                script_loaded = _load(script_name, script_path_py, False)
            except Exception:
                LOGGER.exception("ERROR al cargar script PY para la accion %s:", action_._name)

        elif script_path_qs:
            if not os.path.isfile(script_path_qs):
                raise IOError

            need_parse = True
            script_path_py = "%spy" % script_path_qs[:-2]

            if script_path_qs_static:
                replace_static = True
                if os.path.exists(static_flag):
                    try:
                        tree = ET.parse(static_flag)
                        root = tree.getroot()
                        if root.get("path_legacy") != script_path_qs:
                            replace_static = True
                        elif root.get("last_modified_remote") != str(
                            time.ctime(os.path.getmtime(script_path_qs_static))
                        ):
                            replace_static = True
                        else:
                            replace_static = False
                    except Exception:
                        flag_file = open(static_flag, "r", encoding="UTF8")
                        flag_data = flag_file.read()
                        flag_file.close()

                        LOGGER.warning(
                            "A problem found reading %s data: %s. Forcing realoading",
                            static_flag,
                            flag_data,
                        )

                        replace_static = True

                if replace_static:
                    shutil.copy(script_path_qs_static, script_path_qs)  # Lo copiamos en tempdata
                    if os.path.exists(script_path_py):  # Borramos el py existente
                        os.remove(script_path_py)

                    xml_data = get_static_flag(script_path_qs, script_path_qs_static)
                    my_data = ET.tostring(xml_data, encoding="utf8", method="xml")
                    file_ = open(static_flag, "wb")
                    file_.write(my_data)
                else:
                    need_parse = not os.path.exists(script_path_py)
            else:
                if os.path.exists(script_path_py) and not application.PROJECT.no_python_cache:
                    need_parse = False

            if need_parse:
                if os.path.exists(script_path_py):
                    os.remove(script_path_py)

                application.PROJECT.message_manager().send(
                    "status_help_msg", "send", ["Convirtiendo script... %s" % script_name]
                )

                LOGGER.info(
                    "PARSE_SCRIPT (name : %s, use cache : %s, file: %s",
                    script_name,
                    not application.PROJECT.no_python_cache,
                    script_path_qs,
                )
                if not application.PROJECT.parse_script_list([script_path_qs]):
                    if not os.path.exists(script_path_py):
                        raise Exception("The file %s doesn't created\n" % script_path_py)

            try:
                script_loaded = _load(script_name, script_path_py, False)
            except Exception as error:
                if os.path.exists(script_path_py):
                    os.remove(script_path_py)
                if os.path.exists(static_flag):
                    os.remove(static_flag)

                raise Exception(
                    "ERROR al cargar script QS para la accion %s: %s" % (action_._name, str(error))
                )

    if script_loaded is None:
        from pineboolib.qsa import emptyscript

        script_loaded = emptyscript

    return script_loaded.FormInternalObj(action_)  # type: ignore[attr-defined] # noqa: F821


def load_model(script_name: str, script_path_py: str) -> Optional["type"]:
    """Return class from path."""

    # script_path_py = _path("%s.py" % script_name, False)
    model_class = None
    script_path_py = _resolve_script("%s_model.py" % script_name)

    if script_path_py:
        class_name = "%s%s" % (script_name[0].upper(), script_name[1:])
        script_loaded = _load("model.%s" % class_name, script_path_py)
        module_class = getattr(script_loaded, class_name, None)
        if module_class:
            module_class.__metaclass__ = "Base"
            try:
                model_class = type(class_name, (module_class, declarative.declarative_base()), {})
            except exc.ArgumentError:
                LOGGER.warning(
                    "Error in %s model. Please check columns and make sure exists a primaryKey column"
                    % script_name
                )

    return model_class


def load_class(script_name: str):
    """Return class from path."""

    class_loaded = None
    script_path_py = _resolve_script("%s.py" % script_name)

    if script_path_py:
        class_name = "%s%s" % (script_name[0].upper(), script_name[1:])
        script_loaded = _load(script_name, script_path_py)
        try:
            class_loaded = getattr(script_loaded, class_name, None)
        except Exception as error:
            LOGGER.error("Error loading class %s: %s", script_name, str(error))

    return class_loaded


def load_module(script_name: str) -> Optional["ModuleType"]:
    """Return class from path."""

    script_path_py = _resolve_script(script_name)
    if script_path_py:
        return _load(script_name[:-3], script_path_py)

    return None


def _resolve_script(file_name) -> str:
    """Resolve script."""

    static = _static_file(file_name)
    result = static if static else _path(file_name, False)
    return result or ""


def _load(  # type: ignore [return] # noqa: F821
    module_name: str, script_name: str, capture_error: bool = True
) -> "ModuleType":
    """Load modules."""

    try:
        loader = machinery.SourceFileLoader(module_name, script_name)
        return loader.load_module()  # type: ignore[call-arg] # noqa: F821

    except Exception as error:
        if capture_error:
            LOGGER.error("Error loading module %s: %s", script_name, str(error), stack_info=True)
        else:
            raise error


def _static_file(file_name: str) -> str:
    """Return static file."""

    result = ""
    mng_modules = application.PROJECT.conn_manager.managerModules()
    if mng_modules.static_db_info_ and mng_modules.static_db_info_.enabled_:
        result = pnmodulesstaticloader.PNStaticLoader.content(
            file_name, mng_modules.static_db_info_, True
        )  # Con True solo devuelve el path

    return result


def get_static_flag(database_path: str, static_path: str) -> "ET.Element":
    """Return static_info."""

    xml_data = ET.Element("data")
    xml_data.set("path_legacy", database_path)
    xml_data.set("path_remote", static_path)
    xml_data.set("last_modified_remote", str(time.ctime(os.path.getmtime(static_path))))
    return xml_data
