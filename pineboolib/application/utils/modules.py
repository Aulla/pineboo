"""Modules module."""


from pineboolib.core.utils import logging

import hashlib
import os
from typing import Optional, Any, TYPE_CHECKING

LOGGER = logging.get_logger(__name__)

if TYPE_CHECKING:
    from importlib.machinery import ModuleSpec


def text_to_module(source: str, file_name: str = "anon", lang="qs") -> Any:
    """Text to module function."""

    from pineboolib.application.parsers.parser_qsa import flscriptparse, postparse, pytnyzer
    from pineboolib.application import file, PROJECT
    from importlib import util
    import sys as python_sys

    db_name = PROJECT.conn_manager.mainConn().DBName()
    source_bytes = source.encode()
    sha_ = hashlib.new("sha1", source_bytes).hexdigest()
    module_name = "%s" % (file_name)
    fileobj = file.File("anon", "%s.py" % module_name, sha_, db_name=db_name)
    file_name = fileobj.path()

    if not os.path.isfile(file_name) or not os.path.getsize(
        file_name
    ):  # Si no existe el fichero o está vacio.
        file_dir = os.path.dirname(file_name)
        if not os.path.exists(file_dir):  # Si no existe la carpeta la crea
            os.makedirs(file_dir)
        elif os.path.exists(file_name):  # Si existe la carpeta borra el archivo erroneo
            os.remove(file_name)
        if lang == "qs":
            prog = flscriptparse.parse(source)
            if prog is None:
                raise ValueError("Failed to convert to Python")
            tree_data = flscriptparse.calctree(prog, alias_mode=0)
            ast = postparse.post_parse(tree_data)

            file_ = open(file_name, "w", encoding="UTF-8")

            pytnyzer.write_python_file(file_, ast)
            file_.close()
        else:
            file_ = open(file_name, "w", encoding="UTF-8")
            file_.write(source)
            file_.close()

        LOGGER.debug("Nuevo módulo anónimo generado -> %s " % file_name)
    else:
        LOGGER.debug("Usando módulo anónimo ya existente -> %s" % file_name)

    module_path = "tempdata.%s" % (module_name)

    spec: Optional["ModuleSpec"] = util.spec_from_file_location(module_path, file_name)
    if spec and spec.loader is not None:
        module = util.module_from_spec(spec)
        python_sys.modules[spec.name] = module
        spec.loader.exec_module(module)  # type: ignore [attr-defined]
        return module
    else:
        raise Exception("Module named %s can't be loaded from %s" % (module_path, file_name))
