"""Flmodules module."""
# -*- coding: utf-8 -*-
from pineboolib import logging
from pineboolib.qsa import qsa

from pineboolib.application.parsers.parser_qsa import postparse
import os
import pathlib
from typing import Union, TYPE_CHECKING


if TYPE_CHECKING:
    from PyQt6 import QtWidgets  # type: ignore[import] # pragma: no cover

LOGGER = logging.get_logger(__name__)


class FormInternalObj(qsa.FormDBWidget):
    """FormInternalObj class."""

    def init(self) -> None:
        """Init function."""
        btn_load = self.child("botonCargar")
        btn_export = self.child("botonExportar")
        self.module_connect(btn_load, "clicked()", self, "load_button_clicked")
        self.module_connect(btn_export, "clicked()", self, "expoort_button_clicked")
        cursor = self.cursor()
        if cursor.modeAccess() == cursor.Browse:
            btn_load.setEnabled(False)
            btn_export.setEnabled(False)

    def load_file_to_db(
        self,
        nombre: str,
        contenido: Union[str, bytes],
        log: "QtWidgets.QTextEdit",
        directorio: str,
    ) -> None:
        """Load a file into database."""
        if not qsa.util.isFLDefFile(contenido) and not nombre.endswith(  # type: ignore [arg-type]
            (
                ".mod",
                ".xpm",
                ".signatures",
                ".checksum",
                ".certificates",
                ".qs",
                ".ar",
                ".py",
                ".kut",
                ".jasper",
                ".jrxml",
            )
        ):
            return

        cursor_ficheros = qsa.FLSqlCursor("flfiles")
        cursor = self.cursor()

        binary = nombre.endswith(".jasper")
        cursor_ficheros.select(qsa.ustr("nombre = '", nombre, "'"))
        if not cursor_ficheros.first():
            if nombre.endswith(".ar"):
                if not self.load_ar(nombre, contenido, log, directorio):  # type: ignore [arg-type]
                    return
            log.append(qsa.util.translate("scripts", "- Cargando :: ") + nombre)
            cursor_ficheros.setModeAccess(cursor_ficheros.Insert)
            cursor_ficheros.refreshBuffer()
            cursor_ficheros.setValueBuffer("nombre", nombre)
            cursor_ficheros.setValueBuffer("idmodulo", cursor.valueBuffer("idmodulo"))
            if binary:
                cursor_ficheros.setValueBuffer(
                    "sha", qsa.util.sha1(contenido.decode(errors="replace"))  # type: ignore [union-attr]
                )
                cursor_ficheros.setValueBuffer("binario", contenido)
            else:
                cursor_ficheros.setValueBuffer("sha", qsa.util.sha1(contenido))
                cursor_ficheros.setValueBuffer("contenido", contenido)
            cursor_ficheros.commitBuffer()

        else:
            cursor_ficheros.setModeAccess(cursor_ficheros.Edit)
            cursor_ficheros.refreshBuffer()
            copy_content = cursor_ficheros.valueBuffer("contenido")
            copy_binario = cursor_ficheros.valueBuffer("binario")
            if (not binary and copy_content != contenido) or (
                binary
                and copy_binario.decode(errors="replace") != contenido.decode(errors="replace")  # type: ignore [union-attr]
            ):
                log.append(qsa.util.translate("scripts", "- Actualizando :: ") + nombre)
                cursor_ficheros.setModeAccess(cursor_ficheros.Insert)
                cursor_ficheros.refreshBuffer()
                this_date = qsa.Date()
                cursor_ficheros.setValueBuffer("nombre", nombre + qsa.parseString(this_date))
                cursor_ficheros.setValueBuffer("idmodulo", cursor.valueBuffer("idmodulo"))
                cursor_ficheros.setValueBuffer("contenido", copy_content)
                cursor_ficheros.setValueBuffer("binario", copy_binario)
                cursor_ficheros.commitBuffer()
                log.append(
                    qsa.util.translate("scripts", "- Backup :: ")
                    + nombre
                    + qsa.parseString(this_date)
                )
                cursor_ficheros.select(qsa.ustr("nombre = '", nombre, "'"))
                cursor_ficheros.first()
                cursor_ficheros.setModeAccess(cursor_ficheros.Edit)
                cursor_ficheros.refreshBuffer()
                cursor_ficheros.setValueBuffer("idmodulo", cursor.valueBuffer("idmodulo"))
                if binary:
                    cursor_ficheros.setValueBuffer(
                        "sha", qsa.util.sha1(contenido.decode(errors="replace"))  # type: ignore [union-attr]
                    )
                    cursor_ficheros.setValueBuffer("binario", contenido)
                else:
                    cursor_ficheros.setValueBuffer("sha", qsa.util.sha1(contenido))
                    cursor_ficheros.setValueBuffer("contenido", contenido)
                cursor_ficheros.commitBuffer()
                if nombre.endswith(".ar"):
                    self.load_ar(nombre, contenido, log, directorio)  # type: ignore [arg-type]

        # cursor_ficheros.close()

    def load_ar(
        self, nombre: str, contenido: str, log: "QtWidgets.QTextEdit", directorio: str
    ) -> bool:
        """Load AR reports."""
        if not qsa.sys.isLoadedModule("flar2kut"):
            return False
        if qsa.util.readSettingEntry("scripts/sys/conversionAr") != "true":
            return False
        log.append(qsa.util.translate("scripts", "Convirtiendo %s a kut") % (str(nombre)))
        contenido = qsa.sys.toUnicode(contenido, "UTF-8")
        contenido = qsa.from_project("flar2kut").iface.pub_ar2kut(contenido)
        nombre = qsa.ustr(qsa.parseString(nombre)[0 : len(nombre) - 3], ".kut")
        if contenido:
            local_encode = qsa.util.readSettingEntry("scripts/sys/conversionArENC", "ISO-8859-15")
            contenido = qsa.sys.fromUnicode(contenido, local_encode)
            self.load_file_to_db(nombre, contenido, log, directorio)
            log.append(qsa.util.translate("scripts", "Volcando a disco ") + nombre)
            qsa.FileStatic.write(qsa.Dir.cleanDirPath(qsa.ustr(directorio, "/", nombre)), contenido)

        else:
            log.append(qsa.util.translate("scripts", "Error de conversión"))
            return False

        return True

    def load_files(self, directorio: str, extension: str) -> None:
        """Load files into database."""

        log = self.child("log")
        if log is None:
            raise Exception("log is empty!.")

        extension = extension.replace("*", "")

        settings = qsa.FLSettings()
        parse_modules_on_load = settings.readBoolEntry("ebcomportamiento/parseModulesOnLoad", False)
        for root, dirs, files in os.walk(directorio):
            # print("*", root, dirs, files)
            root_dirs_list = pathlib.Path(root)
            for name in files:
                if name.endswith(extension):
                    if "test" in root_dirs_list.parts or name.startswith("test_"):
                        continue

                    path_ = os.path.join(root, name)

                    if parse_modules_on_load and name.endswith(".qs"):
                        file_py_path_ = "%s.py" % path_
                        if os.path.exists(file_py_path_):
                            os.remove(file_py_path_)

                        postparse.pythonify([path_])
                        if os.path.exists(file_py_path_):
                            value_py = qsa.File(file_py_path_, "UTF-8").read()
                            if not isinstance(value_py, str):
                                raise Exception("value_py must be string not bytes.")

                            self.load_file_to_db("%s.py" % name[-3], value_py, log, directorio)
                    if name.endswith(".jasper"):
                        file_ = open(path_, "rb")
                        value = file_.read()
                        file_.close()
                    else:
                        encode = "UTF-8" if path_.endswith((".ts", ".py")) else "ISO-8859-1"
                        try:
                            value = qsa.File(path_, encode).read()  # type: ignore [assignment]
                        except UnicodeDecodeError:
                            LOGGER.warning(
                                "The file %s has a incorrect encode (%s)" % (path_, encode)
                            )
                            encode = "UTF8" if encode == "ISO-8859-1" else "ISO-8859-1"
                            value = qsa.File(path_, encode).read()  # type: ignore [assignment]

                    self.load_file_to_db(name, value, log, directorio)
                    # qsa.sys.processEvents()

    def load_button_clicked(self) -> None:
        """Load a directory from file system."""
        directorio = qsa.FileDialog.getExistingDirectory(
            "", qsa.util.translate("scripts", "Elegir Directorio")
        )
        self.load_from_disk(directorio or "", True)

    def expoort_button_clicked(self) -> None:
        """Export a module to file system."""
        directorio = qsa.FileDialog.getExistingDirectory(
            "", qsa.util.translate("scripts", "Elegir Directorio")
        )
        self.export_to_disk(directorio or "")

    def accept_license(self, directorio: str) -> bool:
        """Accept license dialog."""
        path_licencia = qsa.Dir.cleanDirPath(qsa.ustr(directorio, "/COPYING"))
        if not qsa.FileStatic.exists(path_licencia):
            qsa.MessageBox.critical(
                qsa.util.translate(
                    "scripts",
                    qsa.ustr(
                        "El fichero ",
                        path_licencia,
                        " con la licencia del módulo no existe.\nEste fichero debe existir para poder aceptar la licencia que contiene.",
                    ),
                ),
                qsa.MessageBox.Ok,
            )
            return False
        licencia = qsa.FileStatic.read(path_licencia)
        dialog = qsa.Dialog()
        dialog.setWidth(600)
        dialog.caption = qsa.util.translate("scripts", "Acuerdo de Licencia.")
        # dialog.newTab(qsa.util.translate(u"scripts", u"Acuerdo de Licencia."))
        texto = qsa.TextEdit()
        texto.text = licencia
        dialog.add(texto)
        dialog.okButtonText = qsa.util.translate("scripts", "Sí, acepto este acuerdo de licencia.")
        dialog.cancelButtonText = qsa.util.translate(
            "scripts", "No, no acepto este acuerdo de licencia."
        )
        return True if dialog.exec() else False

    def load_from_disk(self, directorio: str, check_license: bool) -> None:
        """Load a folder from file system."""
        if directorio:
            if check_license:
                if not self.accept_license(directorio):
                    qsa.MessageBox.critical(
                        qsa.util.translate(
                            "scripts",
                            "Imposible cargar el módulo.\nLicencia del módulo no aceptada.",
                        ),
                        qsa.MessageBox.Ok,
                    )
                    return

            # qsa.sys.cleanupMetaData()
            qsa.sys.processEvents()
            if self.cursor().commitBuffer():
                id_mod_widget = self.child("idMod")
                if id_mod_widget is not None:
                    id_mod_widget.setDisabled(True)
                log = self.child("log")

                if log is None:
                    raise Exception("log is empty!.")

                log.text = ""
                self.setDisabled(True)

                extensiones = [
                    "xml",
                    "mod",
                    "signatures",
                    "certificates",
                    "checksum",
                    "ui",
                    "mtd",
                    "qs",
                    "py",
                    "qry",
                    "kut",
                    "ar",
                    "ts",
                    "jasper",
                    "jrxml",
                ]
                for extension in extensiones:
                    self.load_files(directorio, ".%s" % extension)

                log.append(qsa.util.translate("scripts", "* Carga finalizada."))
                self.setDisabled(False)
                tdb_lineas = self.child("lineas")
                if tdb_lineas is not None:
                    tdb_lineas.refresh()

    def file_type(self, nombre: str) -> str:
        """Return file type."""
        dot_pos = nombre.rfind(".")
        return nombre[dot_pos:]

    def export_to_disk(self, directorio: str) -> None:
        """Export a module to disk."""
        if directorio:
            tdb_lineas = self.child("lineas")
            if tdb_lineas is None:
                raise Exception("lineas control not found")

            cur_files = tdb_lineas.cursor()
            cur_modules = qsa.FLSqlCursor("flmodules")
            cur_areas = qsa.FLSqlCursor("flareas")
            if cur_files.size() != 0:
                dir = qsa.Dir()
                id_modulo = self.cursor().valueBuffer("idmodulo")
                log = self.child("log")
                if log is None:
                    raise Exception("Log control not found!.")

                log.text = ""
                directorio = qsa.Dir.cleanDirPath(qsa.ustr(directorio, "/", id_modulo))
                if not dir.fileExists(directorio):
                    dir.mkdir(directorio)
                if not dir.fileExists(qsa.ustr(directorio, "/forms")):
                    dir.mkdir(qsa.ustr(directorio, "/forms"))
                if not dir.fileExists(qsa.ustr(directorio, "/scripts")):
                    dir.mkdir(qsa.ustr(directorio, "/scripts"))
                if not dir.fileExists(qsa.ustr(directorio, "/queries")):
                    dir.mkdir(qsa.ustr(directorio, "/queries"))
                if not dir.fileExists(qsa.ustr(directorio, "/tables")):
                    dir.mkdir(qsa.ustr(directorio, "/tables"))
                if not dir.fileExists(qsa.ustr(directorio, "/reports")):
                    dir.mkdir(qsa.ustr(directorio, "/reports"))
                if not dir.fileExists(qsa.ustr(directorio, "/translations")):
                    dir.mkdir(qsa.ustr(directorio, "/translations"))
                cur_files.first()
                # file = None
                # tipo = None
                # contenido = ""
                self.setDisabled(True)
                s01_dowhile_1stloop = True
                while s01_dowhile_1stloop or cur_files.next():
                    s01_dowhile_1stloop = False
                    file_name = cur_files.valueBuffer("nombre")
                    tipo = self.file_type(file_name)
                    contenido = (
                        cur_files.valueBuffer("binario")
                        if tipo == ".jasper"
                        else cur_files.valueBuffer("contenido")
                    )

                    if contenido:
                        codec: str = ""
                        if tipo in [
                            ".xml",
                            ".mod",
                            ".xml",
                            ".signatures",
                            ".certificates",
                            ".checksum",
                            ".ui",
                            ".qs",
                            ".qry",
                            ".mtd",
                            ".kut",
                            ".jasper",
                            ".jrxml",
                        ]:
                            codec = "ISO-8859-1"
                        elif tipo in [".py", ".ts"]:
                            codec = "UTF-8"
                        else:
                            log.append(
                                qsa.util.translate(
                                    "scripts", qsa.ustr("* Omitiendo ", file_name, ".")
                                )
                            )
                            continue

                        sub_carpeta = ""
                        if tipo in (".py", ".qs"):
                            sub_carpeta = "scripts"
                        elif tipo == ".qry":
                            sub_carpeta = "queries"
                        elif tipo == ".mtd":
                            sub_carpeta = "tables"
                        elif tipo == ".ts":
                            sub_carpeta = "translations"
                        elif tipo == ".ui":
                            sub_carpeta = "forms"
                        elif tipo in (".kut", ".jasper", ".jrxml"):
                            sub_carpeta = "reports"

                        file_path = os.path.join(directorio, sub_carpeta, file_name)

                        if tipo == ".jasper":
                            file_ = open(file_path, "wb")
                            file_.write(contenido)
                            file_.close()
                        else:
                            qsa.sys.write(codec, file_path, contenido)
                        log.append(
                            qsa.util.translate("scripts", qsa.ustr("* Exportando ", file_name, "."))
                        )

                    # qsa.sys.processEvents()

                cur_modules.select(qsa.ustr("idmodulo = '", id_modulo, "'"))
                if cur_modules.first():
                    cur_areas.select(qsa.ustr("idarea = '", cur_modules.valueBuffer("idarea"), "'"))
                    cur_areas.first()
                    name_area = cur_areas.valueBuffer("descripcion")
                    if not qsa.FileStatic.exists(
                        qsa.ustr(directorio, "/", cur_modules.valueBuffer("idmodulo"), ".xpm")
                    ):
                        qsa.sys.write(
                            "ISO-8859-1",
                            qsa.ustr(directorio, "/", cur_modules.valueBuffer("idmodulo"), ".xpm"),
                            cur_modules.valueBuffer("icono"),
                        )
                        log.append(
                            qsa.util.translate(
                                "scripts",
                                qsa.ustr(
                                    "* Exportando ",
                                    cur_modules.valueBuffer("idmodulo"),
                                    ".xpm (Regenerado).",
                                ),
                            )
                        )
                    if not qsa.FileStatic.exists(
                        qsa.ustr(directorio, "/", cur_modules.valueBuffer("idmodulo"), ".mod")
                    ):
                        contenido = qsa.ustr(
                            "<!DOCTYPE MODULE>\n<MODULE>\n<name>",
                            cur_modules.valueBuffer("idmodulo"),
                            '</name>\n<alias>QT_TRANSLATE_NOOP("FLWidgetApplication","',
                            cur_modules.valueBuffer("descripcion"),
                            '")</alias>\n<area>',
                            cur_modules.valueBuffer("idarea"),
                            '</area>\n<name_area>QT_TRANSLATE_NOOP("FLWidgetApplication","',
                            name_area,
                            '")</name_area>\n<version>',
                            cur_modules.valueBuffer("version"),
                            "</version>\n<icon>",
                            cur_modules.valueBuffer("idmodulo"),
                            ".xpm</icon>\n<flversion>",
                            cur_modules.valueBuffer("version"),
                            "</flversion>\n<description>",
                            cur_modules.valueBuffer("idmodulo"),
                            "</description>\n</MODULE>",
                        )
                        qsa.sys.write(
                            "ISO-8859-1",
                            qsa.ustr(directorio, "/", cur_modules.valueBuffer("idmodulo"), ".mod"),
                            contenido,
                        )
                        log.append(
                            qsa.util.translate(
                                "scripts",
                                qsa.ustr(
                                    "* Generando ",
                                    cur_modules.valueBuffer("idmodulo"),
                                    ".mod (Regenerado).",
                                ),
                            )
                        )

                self.setDisabled(False)
                log.append(qsa.util.translate("scripts", "* Exportación finalizada."))
