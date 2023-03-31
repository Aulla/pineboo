"""Modules module."""

from PyQt5 import QtCore

from pineboolib.core import settings
from pineboolib.core.utils import logging

import os
from typing import Optional, Any, TYPE_CHECKING

LOGGER = logging.get_logger(__name__)

if TYPE_CHECKING:
    from importlib.machinery import ModuleSpec


def text_to_module(source: str) -> Any:
    """Text to module function."""

    from pineboolib.application.parsers.parser_qsa import flscriptparse, postparse, pytnyzer
    from importlib import util
    import sys as python_sys

    module_name = "anon_%s" % QtCore.QDateTime.currentDateTime().toString("ddMMyyyyhhmmsszzz")

    prog = flscriptparse.parse(source)
    if prog is None:
        raise ValueError("Failed to convert to Python")
    tree_data = flscriptparse.calctree(prog, alias_mode=0)
    ast = postparse.post_parse(tree_data)
    dest_filename = "%s/%s.py" % (
        settings.CONFIG.value("ebcomportamiento/temp_dir"),
        module_name,
    )

    if os.path.exists(dest_filename):
        os.remove(dest_filename)

    file_ = open(dest_filename, "w", encoding="UTF-8")

    pytnyzer.write_python_file(file_, ast)
    file_.close()

    LOGGER.debug("Fichero generado %s" % dest_filename)

    module_path = "tempdata.%s" % (module_name)

    spec: Optional["ModuleSpec"] = util.spec_from_file_location(module_path, dest_filename)
    if spec and spec.loader is not None:
        module = util.module_from_spec(spec)
        python_sys.modules[spec.name] = module
        spec.loader.exec_module(module)  # type: ignore [attr-defined]
        return module
    else:
        raise Exception("Module named %s can't be loaded from %s" % (module_path, dest_filename))
