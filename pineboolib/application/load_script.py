"""Load_script module."""

from importlib.machinery import ModuleSpec
from pineboolib.core.utils import logging
from .utils.path import _path

from typing import Optional, TYPE_CHECKING

from pineboolib.application.staticloader import pnmodulesstaticloader
from pineboolib.application.parsers.parser_mtd import pnmtdparser
from pineboolib import application

import xml.etree.ElementTree as ET
from importlib import util
from sqlalchemy.ext import declarative
from sqlalchemy import exc

import shutil
import time
import os

if TYPE_CHECKING:
    from pineboolib.qsa import formdbwidget  # pragma: no cover
    from pineboolib.application import xmlaction  # pragma: no cover
    from sqlalchemy.ext.declarative import api  # noqa: F401 # pragma: no cover
    from types import ModuleType  # pragma: no cover

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

    script_name = script_name.replace(".qs", "")
    LOGGER.debug("Loading script %s for action %s", script_name, action_._name)

    script_path_py: str = ""
    script_path_qs: str = ""
    script_loaded = None

    cached_script_path_qs: str = _path("%s.qs" % script_name, False) or ""
    # Busqueda en carpetas .py
    cached_script_path_py: str = _path("%s.py" % script_name, False) or ""
    if cached_script_path_qs and not cached_script_path_py:  # busqueda en carpetas .qs.py
        file_py = "%spy" % cached_script_path_qs[:-2]
        cached_script_path_py = file_py if os.path.exists(file_py) else ""

    if application.PROJECT.no_python_cache and cached_script_path_qs:  # Si no_python_cache
        cached_script_path_py = ""

    # carga estática
    static_flag = (
        "%s/static.xml" % os.path.dirname(cached_script_path_qs) if cached_script_path_qs else ""
    )
    script_path_qs_static = _static_file("%s.qs" % script_name)
    script_path_py_static = _static_file("%s.py" % script_name)

    # Primera opción carga estática.
    if script_path_py_static:
        script_path_py = script_path_py_static
    elif script_path_qs_static:
        script_path_qs = script_path_qs_static
    else:  # Segunda Caché
        if cached_script_path_py:
            script_path_py = cached_script_path_py
        elif cached_script_path_qs:
            script_path_qs = cached_script_path_qs

    if script_path_py:
        _remove(static_flag)

        if script_path_py_static and cached_script_path_py.find("system_module") == -1:
            if not cached_script_path_py:
                msg = (
                    "The %s.py file that does not exist in pineboo's cache is being overloaded."
                    % script_name
                )
                msg += "Check that the file exists in the flfiles table"
                LOGGER.exception(msg)
            # si es carga estática y no es módulo sistema lo marco
            static_flag = "%s/static.xml" % os.path.dirname(cached_script_path_py)
            _build_static_flag(static_flag, cached_script_path_py, script_path_py)

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
        script_path_py = "%spy" % cached_script_path_qs[:-2]  # Buscamos

        if script_path_qs_static:
            replace_static = True
            if os.path.exists(static_flag):
                replace_static = _resolve_flag(
                    static_flag, cached_script_path_qs, script_path_qs_static
                )
            if replace_static:
                shutil.copy(script_path_qs_static, cached_script_path_qs)  # Lo copiamos en tempdata
                _remove(script_path_py)
                _build_static_flag(static_flag, cached_script_path_qs, script_path_qs_static)
            else:
                need_parse = not os.path.exists(script_path_py)
        else:
            if os.path.exists(script_path_py) and not application.PROJECT.no_python_cache:
                need_parse = False

        if need_parse:
            _remove(script_path_py)
            application.PROJECT.message_manager().send(
                "status_help_msg", "send", ["Convirtiendo script... %s" % script_name]
            )

            LOGGER.info(
                "PARSE_SCRIPT (name : %s, use cache : %s, file: %s",
                script_name,
                not application.PROJECT.no_python_cache,
                cached_script_path_qs,
            )
            if not application.PROJECT.parse_script_list([cached_script_path_qs]):
                if not os.path.exists(script_path_py):
                    raise Exception("The file %s doesn't created\n" % script_path_py)

        try:
            script_loaded = _load(script_name, script_path_py, False)
        except Exception as error:
            _remove(script_path_py)
            _remove(static_flag)

            raise Exception(
                "ERROR al cargar script QS para la accion %s: %s" % (action_._name, str(error))
            )

    return _init_internal_obj(action_, script_loaded)


def _init_internal_obj(
    action_: "xmlaction.XMLAction", script_loaded: Optional["ModuleType"] = None
) -> "formdbwidget.FormDBWidget":
    """Return formDBWidget."""

    if script_loaded is None:
        from pineboolib.qsa import emptyscript

        script_loaded = emptyscript

    return script_loaded.FormInternalObj(action_)  # type: ignore[attr-defined] # noqa: F821


def _resolve_flag(static_flag: str, script: str, script_static: str) -> bool:
    """Return if replace."""

    result = True
    try:
        tree = ET.parse(static_flag)
        root = tree.getroot()
        if root.get("path_legacy") != script:
            pass
        elif root.get("last_modified_remote") != str(time.ctime(os.path.getmtime(script_static))):
            pass
        else:
            result = False
    except Exception:
        flag_file = open(static_flag, "r", encoding="UTF8")
        flag_data = flag_file.read()
        flag_file.close()
        LOGGER.warning(
            "A problem found reading %s data: %s. Forcing realoading", static_flag, flag_data
        )

    return result


def _build_static_flag(flag: str, script: str, static: str) -> None:
    """Build flag file."""

    _remove(flag)

    xml_data = get_static_flag(script, static)
    my_data = ET.tostring(xml_data, encoding="utf8", method="xml")

    file_ = open(flag, "wb")
    file_.write(my_data)


def _remove(file_name: str) -> None:
    """Remove file."""

    if os.path.exists(file_name):
        try:
            os.remove(file_name)
        except FileNotFoundError as error:  # noqa: F841
            LOGGER.warning("File %s exists but not found!!", file_name)


def load_model(script_name: str, script_path_py: str) -> Optional["type"]:
    """Return model_class from path."""

    model_class: Optional["type"] = None
    script_path_py = _resolve_script("%s_model.py" % script_name, script_path_py)
    if os.path.exists(script_path_py) and pnmtdparser.use_mtd_fields(script_path_py):
        script_path_py = pnmtdparser.populate_fields(script_path_py, "%s.mtd" % script_name)
        LOGGER.warning(
            "El model %s no contenía legacy_metadata. Se rellena con datos de %s.mtd",
            script_name,
            script_name,
        )

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
        else:
            LOGGER.warning(
                "No existe la clase %s dentro de %s. No se puede usar este orm."
                % (class_name, "%s_model.py" % script_name)
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

    return _load(script_name[:-3], script_path_py) if script_path_py else None


def _resolve_script(file_name, alternative: str = "") -> str:
    """Resolve script."""

    result = _static_file(file_name)
    if not result:
        result = alternative
        if not result:
            result = _path(file_name, False) or ""

    return result or ""


def _load(  # type: ignore [return] # noqa: F821, F723
    module_name: str, script_name: str, capture_error: bool = True
) -> "ModuleType":
    """Load modules."""

    if os.path.exists(script_name) and not os.access(script_name, os.R_OK):
        if capture_error:
            LOGGER.error("Permision denied for read %s file", script_name)
        else:
            raise PermissionError

    try:

        spec: Optional["ModuleSpec"] = util.spec_from_file_location(module_name, script_name)
        if spec and spec.loader is not None:
            module = util.module_from_spec(spec)
            spec.loader.exec_module(module)  # type: ignore [attr-defined]
            return module
        else:
            raise Exception("Module named %s can't be loaded from %s" % (module_name, script_name))

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
