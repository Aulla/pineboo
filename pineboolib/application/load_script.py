"""Load_script module."""

from pineboolib.core.utils import logging
from .utils.path import _path

from typing import Optional, TYPE_CHECKING

from pineboolib.application.staticloader import pnmodulesstaticloader
from pineboolib import application

import xml.etree.ElementTree as ET
from importlib import machinery
from sqlalchemy.ext import declarative

import shutil
import time
import os

if TYPE_CHECKING:
    from pineboolib.qsa import formdbwidget
    from pineboolib.application import xmlaction
    from sqlalchemy.ext.declarative import api  # noqa: F401

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

        # if script_path_qs:
        #    LOGGER.info("Found QSA file : %s", script_path_qs)
        # else:
        #    LOGGER.info("QSA file not found.")

        # if script_path_py:
        #    LOGGER.info("Found cached PY file : %s", script_path_py)
        # else:
        #    LOGGER.info("PY file not found.")

        if application.PROJECT.no_python_cache:
            # if not script_path_qs:
            #    LOGGER.warning(
            #        "load_script: no_python_cache. Using %s. No candidate found for translation",
            #        script_path_py,
            #    )
            # else:
            if script_path_qs:
                script_path_py = ""
        script_path_py_static: str = ""
        script_path_qs_static: str = ""
        static_flag = ""
        old_script_path_py = ""

        if script_path_qs:
            static_flag = "%s/static.xml" % os.path.dirname(script_path_qs)

        mng_modules = application.PROJECT.conn_manager.managerModules()
        if mng_modules.static_db_info_ and mng_modules.static_db_info_.enabled_:
            script_path_py_static = pnmodulesstaticloader.PNStaticLoader.content(
                "%s.py" % script_name, mng_modules.static_db_info_, True
            )  # Con True solo devuelve el path

            script_path_qs_static = pnmodulesstaticloader.PNStaticLoader.content(
                "%s.qs" % script_name, mng_modules.static_db_info_, True
            )  # Con True solo devuelve el path

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
                loader = machinery.SourceFileLoader(script_name, script_path_py)
                script_loaded = loader.load_module()  # type: ignore[call-arg] # noqa: F821
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
                    except Exception as error:
                        file_ = open(static_flag, "r", encoding="UTF8")
                        data = file_.read()
                        file_.close()

                        LOGGER.warning(
                            "A problem found reading %s data: %s. Forcing realoading",
                            static_flag,
                            data,
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
                    # LOGGER.info("Deleting older PY %s", script_path_py)
                    os.remove(script_path_py)

                # if settings.CONFIG.value("application/isDebuggerMode", False):
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
                        # LOGGER.error("SCRIPT_NAME: %s", script_name)
                        # LOGGER.error("QSA_FILE PATH: %s", script_path_qs)
                        # LOGGER.error("STATIC_LOAD_FILE PATH: %s", script_path_qs_static)
                        raise Exception("The file %s doesn't created\n" % script_path_py)

            # LOGGER.info("Loading script QS %s -> %s", script_name, script_path_py)
            try:
                loader = machinery.SourceFileLoader(script_name, script_path_py)
                script_loaded = loader.load_module()  # type: ignore[call-arg] # noqa: F821

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

    # script_loaded.form = script_loaded.FormInternalObj(action_)
    # LOGGER.info("<-----   END LOADING SCRIPT %s", script_name.upper())
    return script_loaded.FormInternalObj(action_)  # type: ignore[attr-defined] # noqa: F821


def load_model(script_name: str, script_path_py: str) -> Optional["type"]:
    """Return class from path."""

    # script_path_py = _path("%s.py" % script_name, False)
    model_class = None

    mng_modules = application.PROJECT.conn_manager.managerModules()
    if mng_modules.static_db_info_ and mng_modules.static_db_info_.enabled_:

        script_path_py_static = pnmodulesstaticloader.PNStaticLoader.content(
            "%s_model.py" % script_name, mng_modules.static_db_info_, True
        )  # Con True solo devuelve el path
        if script_path_py_static:
            script_path_py = script_path_py_static

    if script_path_py:
        class_name = "%s%s" % (script_name[0].upper(), script_name[1:])
        loader = machinery.SourceFileLoader("model.%s" % class_name, script_path_py)
        script_loaded = loader.load_module()  # type: ignore[call-arg] # noqa: F821
        module_class = getattr(script_loaded, class_name, None)
        if module_class:
            module_class.__metaclass__ = "Base"
            model_class = type(class_name, (module_class, declarative.declarative_base()), {})

    return model_class


def load_class(script_name):
    """Return class from path."""

    script_path_py = _path("%s.py" % script_name, False)
    class_loaded = None

    mng_modules = application.PROJECT.conn_manager.managerModules()
    if mng_modules.static_db_info_ and mng_modules.static_db_info_.enabled_:
        script_path_py_static = pnmodulesstaticloader.PNStaticLoader.content(
            "%s.py" % script_name, mng_modules.static_db_info_, True
        )  # Con True solo devuelve el path
        if script_path_py_static:
            script_path_py = script_path_py_static

    if script_path_py:
        try:
            loader = machinery.SourceFileLoader(script_name, script_path_py)
            script_loaded = loader.load_module()  # type: ignore[call-arg] # noqa: F821
            class_loaded = getattr(
                script_loaded, "%s%s" % (script_name[0].upper(), script_name[1:]), None
            )
        except Exception as error:
            LOGGER.error("Error loading class %s: %s", script_name, str(error))

    return class_loaded


def load_module(script_name):
    """Return class from path."""

    script_path_py = _path(script_name, False)
    script_loaded = None
    mng_modules = application.PROJECT.conn_manager.managerModules()
    if mng_modules.static_db_info_ and mng_modules.static_db_info_.enabled_:
        script_path_py_static = pnmodulesstaticloader.PNStaticLoader.content(
            "%s.py" % script_name, mng_modules.static_db_info_, True
        )  # Con True solo devuelve el path
        if script_path_py_static:
            script_path_py = script_path_py_static

    if script_path_py:
        try:
            loader = machinery.SourceFileLoader(script_name[:-3], script_path_py)
            script_loaded = loader.load_module()  # type: ignore[call-arg] # noqa: F821
            # class_loaded = getattr(
            #    script_loaded, "%s%s" % (script_name[0].upper(), script_name[1:]), None
            # )
        except Exception as error:
            LOGGER.error("Error loading module %s: %s", script_name, str(error), stack_info=True)

    return script_loaded


def get_static_flag(database_path: str, static_path: str) -> "ET.Element":
    """Return static_info."""

    xml_data = ET.Element("data")
    xml_data.set("path_legacy", database_path)
    xml_data.set("path_remote", static_path)
    xml_data.set("last_modified_remote", str(time.ctime(os.path.getmtime(static_path))))
    return xml_data
