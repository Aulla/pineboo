# -*- coding: utf-8 -*-
"""
Manage load and storage of Eneboo/Pineboo modules.

What are modules?
-------------------

Modules are the declaration of Pineboo source packages where all related functionality
is stored within. Its composed of a name and description; and they contain code, forms, etc.
"""

import os.path
from pineboolib.core.utils import logging

from pineboolib.core import parsetable
from .utils.path import _path

from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .file import File
    from pineboolib.core.utils.struct import TableStruct

LOGGER = logging.getLogger(__name__)


class Module(object):
    """Information about loaded modules."""

    def __init__(self, areaid: str, name: str, description: str, icon: str) -> None:
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
        self.tables: Dict[str, TableStruct] = {}
        self.loaded = False

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
        from .moduleactions import ModuleActions
        from pineboolib import application

        mng_modules = application.PROJECT.conn_manager.managerModules()

        path_xml = _path("%s.xml" % self.name)

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
            self.actions = ModuleActions(self, path_xml, self.name)
            self.actions.load()
        except Exception:
            LOGGER.exception("Al cargar módulo %s:", self.name)
            return False

        # TODO: Load Main Script:
        self.mainscript = None
        # /-----------------------

        for tablefile in self.files:
            if not tablefile.endswith(".mtd") or tablefile.find("alteredtable") > -1:
                continue

            contenido = mng_modules.contentCached(tablefile)
            name, ext = os.path.splitext(tablefile)
            #    # path = _path(tablefile)
            #    # if path is None:
            #    #    raise Exception("Cannot find %s" % tablefile)
            #    # try:
            #    #    contenido = str(open(path, "rb").read(), "ISO-8859-15")
            #    # except UnicodeDecodeError as e:
            #    #    self.logger.error("Error al leer el fichero %s %s", tablefile, e)
            #    #    continue
            try:
                if contenido is None:
                    continue
                self.tables[name] = parsetable.parse_table(name, contenido)
            except ValueError as exception:
                LOGGER.warning(
                    "No se pudo procesar. Se ignora tabla %s/%s (%s) ", self.name, name, exception
                )

        self.loaded = True
        return True
