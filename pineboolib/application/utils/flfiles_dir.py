"""Flfiles_dir module."""

import os
import hashlib
from typing import List

from PyQt6 import QtXml  # type: ignore[import]
from pineboolib.core.utils import logging, utils_base


LOGGER = logging.get_logger(__name__)


class FlFiles(object):
    """FlFiles class."""

    _root_dir: str
    _areas: List[List[str]]
    _modules: List[List[str]]
    _files: List[List[str]]

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

    def areas(self) -> List[List[str]]:
        """Return areas info."""

        return self._areas

    def modules(self) -> List[List[str]]:
        """Return modules info."""

        return self._modules

    def files(self) -> List[List[str]]:
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
        try:
            fichero = open(nombre_fichero, "r", encoding="iso-8859-15")
            datos_module = fichero.read()
            fichero.close()
        except Exception as error:
            LOGGER.error("Error processing %s:%s", nombre_fichero, str(error))
            return
        xml_module = QtXml.QDomDocument()
        descripcion_modulo: str
        if xml_module.setContent(datos_module):
            node_module = xml_module.namedItem("MODULE")
            modulo = node_module.namedItem("name").toElement().text()
            descripcion_modulo = node_module.namedItem("alias").toElement().text()
            area = node_module.namedItem("area").toElement().text()
            descripcion_area = node_module.namedItem("areaname").toElement().text()
            version = node_module.namedItem("version").toElement().text()
            nombre_icono = node_module.namedItem("icon").toElement().text()
            # if node_module.namedItem(u"flversion"):
            #    versionMinimaFL = node_module.namedItem(u"flversion").toElement().text()
            # if node_module.namedItem(u"dependencies") is not None:
            #    node_depend = xml_module.elementsByTagName(u"dependency")
            #    i = 0
            #    while i < len(node_depend):
            #        dependencias[i] = node_depend.item(i).toElement().text()
            #        i += 1

        descripcion_modulo = utils_base.qt_translate_noop(descripcion_modulo, root_folder, modulo)
        descripcion_area = utils_base.qt_translate_noop(descripcion_area, root_folder, modulo)
        datos_icono: str = ""
        if os.path.exists(os.path.join(root_folder, nombre_icono)):
            try:
                fichero_icono = open(
                    os.path.join(root_folder, nombre_icono), "r", encoding="ISO-8859-15"
                )
                datos_icono = fichero_icono.read()
                fichero_icono.close()
            except Exception as error:
                LOGGER.error("Error processing %s:%s", nombre_icono, str(error))
                return

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

            break  # despues de los subdirs salimos...
