"""Flfiles_dir module."""

import os
import hashlib
from typing import List, Any

from PyQt5.QtXml import QDomDocument
from PyQt5 import QtCore
from pineboolib.core.utils import logging


LOGGER = logging.get_logger(__name__)


class FlFiles(object):
    """FlFiles class."""

    _root_dir: str
    _areas: List[List[Any]]
    _modules: List[List[Any]]
    _files: List[List[Any]]

    def __init__(self, folder: str = "") -> None:
        """Initialize."""

        self._root_dir = folder
        self._areas = []
        self._modules = []
        self._files = []
        if os.path.exists(self._root_dir):
            self.build_data()
        else:
            LOGGER.warning("FLFILES_FOLDER: folder %s not found", self._root_dir)

    def areas(self) -> List[List[Any]]:
        """Return areas info."""

        return self._areas

    def modules(self) -> List[List[Any]]:
        """Return modules info."""

        return self._modules

    def files(self) -> List[List[Any]]:
        """Return files info."""

        return self._files

    def build_data(self) -> None:
        """Build data from a folder."""

        for root, subdirs, files in os.walk(self._root_dir):
            module_found = None
            for file_name in files:
                if file_name.endswith(".mod"):
                    module_found = file_name
                    break

            if module_found:
                self.process_module(file_name, root, subdirs, files)

    def process_module(
        self, module_file: str, root_folder: str, subdirs: List[str], files: List[str]
    ) -> None:
        """Process a module folder."""

        nombre_fichero = os.path.join(root_folder, module_file)
        # print("Buscando ...", nombre_fichero)
        fichero = open(nombre_fichero, "r", encoding="iso-8859-15")
        datos_module = fichero.read()
        xml_module = QDomDocument()

        if xml_module.setContent(datos_module):
            node_module = xml_module.namedItem(u"MODULE")
            modulo = node_module.namedItem(u"name").toElement().text()
            descripcion_modulo = node_module.namedItem(u"alias").toElement().text()
            area = node_module.namedItem(u"area").toElement().text()
            descripcion_area = node_module.namedItem(u"areaname").toElement().text()
            version = node_module.namedItem(u"version").toElement().text()
            nombre_icono = node_module.namedItem(u"icon").toElement().text()
            # if node_module.namedItem(u"flversion"):
            #    versionMinimaFL = node_module.namedItem(u"flversion").toElement().text()
            # if node_module.namedItem(u"dependencies") is not None:
            #    node_depend = xml_module.elementsByTagName(u"dependency")
            #    i = 0
            #    while i < len(node_depend):
            #        dependencias[i] = node_depend.item(i).toElement().text()
            #        i += 1

        descripcion_modulo = self.traducirCadena(descripcion_modulo, root_folder, modulo)
        descripcion_area = self.traducirCadena(descripcion_area, root_folder, modulo)
        datos_icono = None
        if os.path.exists(os.path.join(root_folder, nombre_icono)):
            fichero_icono = open(
                os.path.join(root_folder, nombre_icono), "r", encoding="ISO-8859-15"
            )
            datos_icono = fichero_icono.read()
            fichero_icono.close()

        if area not in [idarea for idarea, descripcion_area in self._areas]:
            self._areas.append([area, descripcion_area])

        if modulo not in [
            idmodulo
            for idarea, idmodulo, descripcion_modulo, icono_modulo, version_modulo in self._modules
        ]:
            self._modules.append([area, modulo, descripcion_modulo, datos_icono, version])

            self.process_files(root_folder, modulo)

    def process_files(self, root_folder: str, id_module: str) -> None:
        """Process folder files."""

        for root, subdirs, files in os.walk(root_folder):
            for file_name in files:
                if file_name.endswith((".pyc")):
                    continue

                if file_name not in [nombre for idmodule, nombre, sha, contenido in self._files]:
                    try:
                        fichero = open(
                            os.path.join(root, file_name),
                            "r",
                            encoding="UTF-8"
                            if file_name.endswith((".ts", ".py"))
                            else "ISO-8859-15",
                        )
                        # print("Guardando ...", os.path.join(root, file_name))
                        data = fichero.read()
                        byte_data = data.encode()
                        sha_ = hashlib.new("sha1", byte_data)
                        string_sha = str(sha_.hexdigest()).upper()
                        self._files.append([id_module, file_name, string_sha, data])
                    except Exception as error:
                        LOGGER.error("Error processing %s:%s", file_name, str(error))
                        return
                # else:
                #    LOGGER.warning("FLFILES_DIR: file %s already loaded, ignoring..." % file_name)

            for sub_dir in subdirs:
                self.process_files(os.path.join(root_folder, sub_dir), id_module)

    def traducirCadena(self, cadena: str, path: str, modulo: str) -> str:
        """Translate string."""

        if cadena.find(u"QT_TRANSLATE_NOOP") == -1:
            return cadena
        cadena_list = cadena[18:-1].split(",")
        cadena = cadena_list[1][1:-1]

        nombre_fichero = os.path.join(
            path, "translations", "%s.%s.ts" % (modulo, QtCore.QLocale().name()[:2])
        )
        if not os.path.exists(nombre_fichero):
            LOGGER.debug(
                "flreloadlast.traducirCadena: No se encuentra el fichero %s" % nombre_fichero
            )
            return cadena

        fichero = open(nombre_fichero, "r", encoding="ISO-8859-15")
        file_data = fichero.read()
        xml_translations = QDomDocument()
        if xml_translations.setContent(file_data):
            node_mess = xml_translations.elementsByTagName(u"message")
            for item in range(len(node_mess)):
                if node_mess.item(item).namedItem(u"source").toElement().text() == cadena:
                    traduccion = node_mess.item(item).namedItem(u"translation").toElement().text()
                    if traduccion:
                        cadena = traduccion
                        break

        return cadena
