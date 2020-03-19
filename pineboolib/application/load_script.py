"""Load_script module."""

from pineboolib.core.utils import logging
from .utils.path import _path
from pineboolib.qsa import emptyscript

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
    # print("load_script", script_name)
    if script_name:
        script_name = script_name.replace(".qs", "")
        LOGGER.debug("Loading script %s for action %s", script_name, action_._name)
    else:
        LOGGER.info("No script to load for action %s", action_._name)

    script_loaded = emptyscript

    script_path_py: str = ""
    script_path_py_static: str = ""
    script_path_qs: str = ""
    script_path_qs_static: str = ""

    if script_name:

        script_path_qs = _path("%s.qs" % script_name, False) or ""
        script_path_py = _path("%s.py" % script_name, False) or ""

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
                script_path_py = script_path_py_static

        if script_path_py:
            LOGGER.info("Loading script PY %s . . . ", script_name)
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

            static_flag = "%s/static.xml" % os.path.dirname(script_path_qs)
            script_path_py = "%spy" % script_path_qs[:-2]

            if script_path_qs_static:
                static_flag = "%s/static.xml" % os.path.dirname(script_path_qs)
                replace_static = True
                if os.path.exists(static_flag):
                    tree = ET.parse(static_flag)
                    root = tree.getroot()
                    if root.get("path_legacy") != script_path_qs:
                        replace_static = True
                    elif root.get("date_static") != str(
                        time.ctime(os.path.getmtime(script_path_qs_static))
                    ):
                        replace_static = True
                    else:
                        replace_static = False

                if replace_static:

                    shutil.copy(script_path_qs_static, script_path_qs)  # Lo copiamos en tempdata
                    if os.path.exists(script_path_py):  # Borramos el py existente
                        os.remove(script_path_py)

                    if application.PROJECT.parse_script_list([script_path_qs]):

                        if not os.path.exists(script_path_py):
                            raise Exception(
                                "El fichero convertido con carga estática %s no existe, pero el parser dice que todo está ok"
                                % script_path_py
                            )

                        xml_data = get_static_flag(script_path_qs, script_path_qs_static)
                        my_data = ET.tostring(xml_data, encoding="utf8", method="xml")
                        file_ = open(static_flag, "wb")
                        file_.write(my_data)
            else:
                if not application.PROJECT.parse_script_list([script_path_qs]):
                    if not os.path.exists(script_path_py):
                        raise Exception(
                            "El fichero convertido %s no existe, pero el parser dice que todo está ok"
                            % script_path_py
                        )

            LOGGER.warning("Loading script QS %s . . . ", script_name)
            try:
                if os.path.exists(script_path_py):
                    loader = machinery.SourceFileLoader(script_name, script_path_py)
                    script_loaded = loader.load_module()  # type: ignore[call-arg] # noqa: F821
                else:
                    LOGGER.warning("The file %s does not exists!", script_path_py, stack_info=True)

            except Exception as error:
                LOGGER.exception(
                    "ERROR al cargar script QS para la accion %s: %s", action_._name, str(error)
                )

                if os.path.exists(script_path_py):
                    os.remove(script_path_py)

    # script_loaded.form = script_loaded.FormInternalObj(action_)
    return script_loaded.FormInternalObj(action_)


def get_static_flag(database_path: str, static_path: str) -> "ET.Element":
    """Return static_info."""

    xml_data = ET.Element("data")
    xml_data.set("path_legacy", database_path)
    xml_data.set("date_static", str(time.ctime(os.path.getmtime(static_path))))
    return xml_data
