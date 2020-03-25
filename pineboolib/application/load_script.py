"""Load_script module."""

from pineboolib.core.utils import logging
from .utils.path import _path

from typing import TYPE_CHECKING

from pineboolib.application.staticloader import pnmodulesstaticloader
from pineboolib import application

import xml.etree.ElementTree as ET
from importlib import machinery


import shutil
import time
import os

if TYPE_CHECKING:
    from pineboolib.qsa import formdbwidget
    from pineboolib.application import xmlaction

LOGGER = logging.get_logger(__name__)


def load_script(script_name: str, action_: "xmlaction.XMLAction") -> "formdbwidget.FormDBWidget":
    """
    Transform QS script into Python and starts it up.
    """

    LOGGER.warning("LOADING SCRIPT %s    ----->", script_name.upper())

    if script_name:
        script_name = script_name.replace(".qs", "")
        LOGGER.debug("Loading script %s for action %s", script_name, action_._name)
    else:
        LOGGER.info("No script to load for action %s", action_._name)

    script_loaded = None
    generate_static_flag_file = True

    if script_name:

        script_path_qs: str = _path("%s.qs" % script_name, False) or ""
        script_path_py: str = _path("%s.py" % script_name, False) or ""

        if script_path_qs:
            LOGGER.info(
                "Found QSA file (ALWAYS PARSE QSA: %s): %s",
                application.PROJECT.no_python_cache,
                script_path_qs,
            )
        else:
            LOGGER.info("QSA file not found.")

        if script_path_py:
            LOGGER.info("Found cached PY file : %s", script_path_py)
        else:
            LOGGER.info("PY file not found.")

        if application.PROJECT.no_python_cache:
            if not script_path_qs:
                LOGGER.warning(
                    "load_script: no_python_cache. Using %s. No candidate found for translation",
                    script_path_py,
                )
            else:
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
            if not script_path_py_static:
                script_path_qs_static = pnmodulesstaticloader.PNStaticLoader.content(
                    "%s.qs" % script_name, mng_modules.static_db_info_, True
                )  # Con True solo devuelve el path
            else:
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

            LOGGER.info("Loading script PY %s -> %s", script_name, script_path_py)
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

                if replace_static:

                    shutil.copy(script_path_qs_static, script_path_qs)  # Lo copiamos en tempdata
                    if os.path.exists(script_path_py):  # Borramos el py existente
                        os.remove(script_path_py)

                    xml_data = get_static_flag(script_path_qs, script_path_qs_static)
                    my_data = ET.tostring(xml_data, encoding="utf8", method="xml")
                    file_ = open(static_flag, "wb")
                    file_.write(my_data)
                else:
                    need_parse = False

            if need_parse:
                if os.path.exists(script_path_py):
                    LOGGER.info("Deleting older PY %s", script_path_py)
                    os.remove(script_path_py)

                if not application.PROJECT.parse_script_list([script_path_qs]):
                    if not os.path.exists(script_path_py):
                        LOGGER.error("SCRIPT_NAME: %s", script_name)
                        LOGGER.error("QSA_FILE PATH: %s", script_path_qs)
                        LOGGER.error("STATIC_LOAD_FILE PATH: %s", script_path_qs_static)
                        raise Exception("THE FILE %s DOESN'T CREATED!\n" % script_path_py)

            LOGGER.info("Loading script QS %s -> %s", script_name, script_path_py)
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
    LOGGER.warning("<-----   END LOADING SCRIPT %s", script_name.upper())
    return script_loaded.FormInternalObj(action_)  # type: ignore[attr-defined] # noqa: F821


def get_static_flag(database_path: str, static_path: str) -> "ET.Element":
    """Return static_info."""

    xml_data = ET.Element("data")
    xml_data.set("path_legacy", database_path)
    xml_data.set("path_remote", static_path)
    xml_data.set("last_modified_remote", str(time.ctime(os.path.getmtime(static_path))))
    return xml_data
