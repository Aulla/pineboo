"""Modules module."""

from PyQt6 import QtCore

from pineboolib.application.utils import path
from pineboolib.core.utils import logging, utils_base

import hashlib
import os
from typing import Optional, Any, TYPE_CHECKING

LOGGER = logging.get_logger(__name__)

if TYPE_CHECKING:
    from importlib.machinery import ModuleSpec


def text_to_module(source: str) -> Any:
    """Text to module function."""

    from pineboolib.application.parsers.parser_qsa import flscriptparse, postparse, pytnyzer
    from pineboolib.application import file, PROJECT
    from importlib import util
    import sys as python_sys

    source_bytes = source.encode()
    sha_ = hashlib.new("sha1", source_bytes).hexdigest()

    module_name = "anon_%s" % QtCore.QDateTime.currentDateTime().toString("ddMMyyyyhhmmsszzz")
    last_state_strict_mode = pytnyzer.STRICT_MODE
    pytnyzer.STRICT_MODE = False
    prog = flscriptparse.parse(source)
    if prog is None:
        raise ValueError("Failed to convert to Python")
    tree_data = flscriptparse.calctree(prog, alias_mode=0)
    ast = postparse.post_parse(tree_data)

    pytnyzer.STRICT_MODE = last_state_strict_mode
    db_name = PROJECT.conn_manager.mainConn().DBName()
    fileobj = file.File("anon", "%s.py" % module_name, "%s" % sha_, db_name=db_name)
    fileobjdir = os.path.dirname(path._dir("cache", fileobj.filekey))
    file_name = path._dir("cache", fileobj.filekey)
    if not os.path.isfile(file_name) or not os.path.getsize(
        file_name
    ):  # Borra si no existe el fichero o está vacio.
        if os.path.exists(fileobjdir):
            utils_base.empty_dir(fileobjdir)
        else:
            os.makedirs(fileobjdir)

    if os.path.exists(file_name):
        os.remove(file_name)

    file_ = open(file_name, "w", encoding="UTF-8")

    pytnyzer.write_python_file(file_, ast)
    file_.close()

    LOGGER.debug("Fichero generado %s" % file_name)

    module_path = "tempdata.%s" % (module_name)

    spec: Optional["ModuleSpec"] = util.spec_from_file_location(module_path, file_name)
    if spec and spec.loader is not None:
        module = util.module_from_spec(spec)
        python_sys.modules[spec.name] = module
        spec.loader.exec_module(module)  # type: ignore [attr-defined]
        return module
    else:
        raise Exception("Module named %s can't be loaded from %s" % (module_path, file_name))
