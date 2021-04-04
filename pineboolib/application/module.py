# -*- coding: utf-8 -*-
"""
Manage load and storage of Eneboo/Pineboo modules.

What are modules?
-------------------

Modules are the declaration of Pineboo source packages where all related functionality
is stored within. Its composed of a name and description; and they contain code, forms, etc.
"""


from pineboolib import logging

from .utils import path
from . import moduleactions

from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .file import File  # pragma: no cover
    from pineboolib.core.utils.struct import TableStruct  # pragma: no cover

LOGGER = logging.get_logger(__name__)


class Module(object):
    """Information about loaded modules."""

    def __init__(self, areaid: str, name: str, description: str, icon: str, version: str) -> None:
        """
        Create module instance.

        @param areaid. Area Identifier
        @param name. Module name
        @param description. Module Description
        @param icon. Module Icon
        """
        self.areaid = areaid
        self.name = name
        self.description = description  # En python2 era .decode(UTF-8)
        self.icon = icon
        self.files: Dict[str, "File"] = {}
        self.tables: Dict[str, "TableStruct"] = {}
        self.loaded = False
        self.version = version

    def add_project_file(self, fileobj: "File") -> None:
        """
        Add files to project array.

        @param fileobj. File object with file information
        """
        self.files[fileobj.filename] = fileobj

    def load(self) -> bool:
        """
        Load actions belonging to this module.

        @return Boolean True if ok, False if there are problems.
        """

        from pineboolib import application

        mng_modules = application.PROJECT.conn_manager.managerModules()

        path_xml = path._path("%s.xml" % self.name)

        if mng_modules.static_db_info_ and mng_modules.static_db_info_.enabled_:
            ret_xml = mng_modules.contentStatic(
                "%s.xml" % self.name, True
            )  # Con True solo devuelve el path
            if ret_xml:
                path_xml = ret_xml

        # pathui = _path("%s.ui" % self.name)
        if path_xml is None:
            LOGGER.error("módulo %s: fichero XML no existe", self.name)
            return False
        # if pathui is None:
        #    self.logger.error("módulo %s: fichero UI no existe", self.name)
        #    return False
        try:
            self.actions = moduleactions.ModuleActions(self, path_xml, self.name)
            self.actions.load()
        except Exception:
            LOGGER.exception("Al cargar módulo %s:", self.name)
            return False

        # TODO: Load Main Script:
        self.mainscript = None

        self.loaded = True
        return True
