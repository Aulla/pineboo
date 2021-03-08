"""Flmodules module."""
# -*- coding: utf-8 -*-
from pineboolib import logging
from pineboolib.qsa import qsa

from pineboolib.application.parsers.parser_qsa import postparse
import os

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from PyQt5 import QtWidgets  # pragma: no cover

LOGGER = logging.get_logger(__name__)


class FormInternalObj(qsa.FormDBWidget):
    """FormInternalObj class."""

    def _class_init(self) -> None:
        """Inicialize."""
        pass

    def init(self) -> None:
        """Init function."""
        btn_load = self.child(u"botonCargar")
        btn_export = self.child(u"botonExportar")
        self.module_connect(btn_load, u"clicked()", self, u"botonCargar_clicked")
        self.module_connect(btn_export, u"clicked()", self, u"botonExportar_clicked")
        cursor = self.cursor()
        if cursor.modeAccess() == cursor.Browse:
            btn_load.setEnabled(False)
            btn_export.setEnabled(False)

    def cargarFicheroEnBD(
        self, nombre: str, contenido: str, log: "QtWidgets.QTextEdit", directorio: str
    ) -> None:
        """Load a file into database."""
        if not qsa.util.isFLDefFile(contenido) and not nombre.endswith(
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
            )
        ):
            return

        cursor_ficheros = qsa.FLSqlCursor(u"flfiles")
        cursor = self.cursor()

        cursor_ficheros.select(qsa.ustr(u"nombre = '", nombre, u"'"))
        if not cursor_ficheros.first():
            if nombre.endswith(u".ar"):
                if not self.cargarAr(nombre, contenido, log, directorio):
                    return
            log.append(qsa.util.translate(u"scripts", u"- Cargando :: ") + nombre)
            cursor_ficheros.setModeAccess(cursor_ficheros.Insert)
            cursor_ficheros.refreshBuffer()
            cursor_ficheros.setValueBuffer(u"nombre", nombre)
            cursor_ficheros.setValueBuffer(u"idmodulo", cursor.valueBuffer(u"idmodulo"))
            cursor_ficheros.setValueBuffer(u"sha", qsa.util.sha1(contenido))
            cursor_ficheros.setValueBuffer(u"contenido", contenido)
            cursor_ficheros.commitBuffer()

        else:
            cursor_ficheros.setModeAccess(cursor_ficheros.Edit)
            cursor_ficheros.refreshBuffer()
            contenidoCopia = cursor_ficheros.valueBuffer(u"contenido")
            if contenidoCopia != contenido:
                log.append(qsa.util.translate(u"scripts", u"- Actualizando :: ") + nombre)
                cursor_ficheros.setModeAccess(cursor_ficheros.Insert)
                cursor_ficheros.refreshBuffer()
                this_date = qsa.Date()
                cursor_ficheros.setValueBuffer(u"nombre", nombre + qsa.parseString(this_date))
                cursor_ficheros.setValueBuffer(u"idmodulo", cursor.valueBuffer(u"idmodulo"))
                cursor_ficheros.setValueBuffer(u"contenido", contenidoCopia)
                cursor_ficheros.commitBuffer()
                log.append(
                    qsa.util.translate(u"scripts", u"- Backup :: ")
                    + nombre
                    + qsa.parseString(this_date)
                )
                cursor_ficheros.select(qsa.ustr(u"nombre = '", nombre, u"'"))
                cursor_ficheros.first()
                cursor_ficheros.setModeAccess(cursor_ficheros.Edit)
                cursor_ficheros.refreshBuffer()
                cursor_ficheros.setValueBuffer(u"idmodulo", cursor.valueBuffer(u"idmodulo"))
                cursor_ficheros.setValueBuffer(u"sha", qsa.util.sha1(contenido))
                cursor_ficheros.setValueBuffer(u"contenido", contenido)
                cursor_ficheros.commitBuffer()
                if nombre.endswith(u".ar"):
                    self.cargarAr(nombre, contenido, log, directorio)

        # cursor_ficheros.close()

    def cargarAr(
        self, nombre: str, contenido: str, log: "QtWidgets.QTextEdit", directorio: str
    ) -> bool:
        """Load AR reports."""
        if not qsa.sys.isLoadedModule(u"flar2kut"):
            return False
        if qsa.util.readSettingEntry(u"scripts/sys/conversionAr") != u"true":
            return False
        log.append(qsa.util.translate(u"scripts", u"Convirtiendo %s a kut") % (str(nombre)))
        contenido = qsa.sys.toUnicode(contenido, u"UTF-8")
        contenido = qsa.from_project("flar2kut").iface.pub_ar2kut(contenido)
        nombre = qsa.ustr(qsa.parseString(nombre)[0 : len(nombre) - 3], u".kut")
        if contenido:
            local_encode = qsa.util.readSettingEntry(u"scripts/sys/conversionArENC", "ISO-8859-15")
            contenido = qsa.sys.fromUnicode(contenido, local_encode)
            self.cargarFicheroEnBD(nombre, contenido, log, directorio)
            log.append(qsa.util.translate(u"scripts", u"Volcando a disco ") + nombre)
            qsa.FileStatic.write(
                qsa.Dir.cleanDirPath(qsa.ustr(directorio, u"/", nombre)), contenido
            )

        else:
            log.append(qsa.util.translate(u"scripts", u"Error de conversión"))
            return False

        return True

    def cargarFicheros(self, directorio: str, extension: str) -> None:
        """Load files into database."""
        dir = qsa.Dir(directorio)
        ficheros = dir.entryList(extension, qsa.Dir.Files)
        log = self.child(u"log")
        if log is None:
            raise Exception("log is empty!.")
        settings = qsa.FLSettings()
        for fichero in ficheros:
            path_ = qsa.Dir.cleanDirPath(qsa.ustr(directorio, u"/", fichero))
            if settings.readBoolEntry("ebcomportamiento/parseModulesOnLoad", False):
                file_py_path_ = "%s.py" % path_
                if os.path.exists(file_py_path_):
                    os.remove(file_py_path_)
                if path_.endswith(".qs"):
                    postparse.pythonify([path_])
                if os.path.exists(file_py_path_):
                    value_py = qsa.File(file_py_path_).read()
                    if not isinstance(value_py, str):
                        raise Exception("value_py must be string not bytes.")

                    self.cargarFicheroEnBD("%s.py" % fichero[-3], value_py, log, directorio)

            encode = "UTF-8" if path_.endswith((".ts", ".py")) else "ISO-8859-1"
            try:
                value = qsa.File(path_, encode).read()
            except UnicodeDecodeError:
                LOGGER.warning("The file %s has a incorrect encode (%s)" % (path_, encode))
                encode = "UTF8" if encode == "ISO-8859-1" else "ISO-8859-1"
                value = qsa.File(path_, encode).read()

            if not isinstance(value, str):
                raise Exception("value must be string not bytes.")

            self.cargarFicheroEnBD(fichero, value, log, directorio)
            # qsa.sys.processEvents()

    def botonCargar_clicked(self) -> None:
        """Load a directory from file system."""
        directorio = qsa.FileDialog.getExistingDirectory(
            u"", qsa.util.translate(u"scripts", u"Elegir Directorio")
        )
        self.cargarDeDisco(directorio or "", True)

    def botonExportar_clicked(self) -> None:
        """Export a module to file system."""
        directorio = qsa.FileDialog.getExistingDirectory(
            u"", qsa.util.translate(u"scripts", u"Elegir Directorio")
        )
        self.exportarADisco(directorio or "")

    def aceptarLicenciaDelModulo(self, directorio: str) -> bool:
        """Accept license dialog."""
        path_licencia = qsa.Dir.cleanDirPath(qsa.ustr(directorio, u"/COPYING"))
        if not qsa.FileStatic.exists(path_licencia):
            qsa.MessageBox.critical(
                qsa.util.translate(
                    u"scripts",
                    qsa.ustr(
                        u"El fichero ",
                        path_licencia,
                        u" con la licencia del módulo no existe.\nEste fichero debe existir para poder aceptar la licencia que contiene.",
                    ),
                ),
                qsa.MessageBox.Ok,
            )
            return False
        licencia = qsa.FileStatic.read(path_licencia)
        dialog = qsa.Dialog()
        dialog.setWidth(600)
        dialog.caption = qsa.util.translate(u"scripts", u"Acuerdo de Licencia.")
        # dialog.newTab(qsa.util.translate(u"scripts", u"Acuerdo de Licencia."))
        texto = qsa.TextEdit()
        texto.text = licencia
        dialog.add(texto)
        dialog.okButtonText = qsa.util.translate(
            u"scripts", u"Sí, acepto este acuerdo de licencia."
        )
        dialog.cancelButtonText = qsa.util.translate(
            u"scripts", u"No, no acepto este acuerdo de licencia."
        )
        if dialog.exec_():
            return True
        else:
            return False

    def cargarDeDisco(self, directorio: str, check_license: bool) -> None:
        """Load a folder from file system."""
        if directorio:
            if check_license:
                if not self.aceptarLicenciaDelModulo(directorio):
                    qsa.MessageBox.critical(
                        qsa.util.translate(
                            u"scripts",
                            u"Imposible cargar el módulo.\nLicencia del módulo no aceptada.",
                        ),
                        qsa.MessageBox.Ok,
                    )
                    return

            # qsa.sys.cleanupMetaData()
            qsa.sys.processEvents()
            if self.cursor().commitBuffer():

                id_mod_widget = self.child(u"idMod")
                if id_mod_widget is not None:
                    id_mod_widget.setDisabled(True)
                log = self.child(u"log")

                if log is None:
                    raise Exception("log is empty!.")

                log.text = u""
                self.setDisabled(True)
                self.cargarFicheros(qsa.ustr(directorio, u"/"), u"*.xml")
                self.cargarFicheros(qsa.ustr(directorio, u"/"), u"*.mod")
                self.cargarFicheros(qsa.ustr(directorio, u"/"), u"*.xpm")
                self.cargarFicheros(qsa.ustr(directorio, u"/"), u"*.signatures")
                self.cargarFicheros(qsa.ustr(directorio, u"/"), u"*.certificates")
                self.cargarFicheros(qsa.ustr(directorio, u"/"), u"*.checksum")
                self.cargarFicheros(qsa.ustr(directorio, u"/forms/"), u"*.ui")
                self.cargarFicheros(qsa.ustr(directorio, u"/tables/"), u"*.mtd")
                self.cargarFicheros(qsa.ustr(directorio, u"/scripts/"), u"*.qs")
                self.cargarFicheros(qsa.ustr(directorio, u"/scripts/"), u"*.py")
                self.cargarFicheros(qsa.ustr(directorio, u"/queries/"), u"*.qry")
                self.cargarFicheros(qsa.ustr(directorio, u"/reports/"), u"*.kut")
                self.cargarFicheros(qsa.ustr(directorio, u"/reports/"), u"*.ar")
                self.cargarFicheros(qsa.ustr(directorio, u"/translations/"), u"*.ts")

                log.append(qsa.util.translate(u"scripts", u"* Carga finalizada."))
                self.setDisabled(False)
                tdb_lineas = self.child(u"lineas")
                if tdb_lineas is not None:
                    tdb_lineas.refresh()

    def tipoDeFichero(self, nombre: str) -> str:
        """Return file type."""
        dot_pos = nombre.rfind(u".")
        return nombre[dot_pos:]

    def exportarADisco(self, directorio: str) -> None:
        """Export a module to disk."""
        if directorio:
            tdb_lineas = self.child(u"lineas")
            if tdb_lineas is None:
                raise Exception("lineas control not found")

            curFiles = tdb_lineas.cursor()
            cur_modules = qsa.FLSqlCursor(u"flmodules")
            cursorAreas = qsa.FLSqlCursor(u"flareas")
            if curFiles.size() != 0:
                dir = qsa.Dir()
                idModulo = self.cursor().valueBuffer(u"idmodulo")
                log = self.child(u"log")
                if log is None:
                    raise Exception("Log control not found!.")

                log.text = u""
                directorio = qsa.Dir.cleanDirPath(qsa.ustr(directorio, u"/", idModulo))
                if not dir.fileExists(directorio):
                    dir.mkdir(directorio)
                if not dir.fileExists(qsa.ustr(directorio, u"/forms")):
                    dir.mkdir(qsa.ustr(directorio, u"/forms"))
                if not dir.fileExists(qsa.ustr(directorio, u"/scripts")):
                    dir.mkdir(qsa.ustr(directorio, u"/scripts"))
                if not dir.fileExists(qsa.ustr(directorio, u"/queries")):
                    dir.mkdir(qsa.ustr(directorio, u"/queries"))
                if not dir.fileExists(qsa.ustr(directorio, u"/tables")):
                    dir.mkdir(qsa.ustr(directorio, u"/tables"))
                if not dir.fileExists(qsa.ustr(directorio, u"/reports")):
                    dir.mkdir(qsa.ustr(directorio, u"/reports"))
                if not dir.fileExists(qsa.ustr(directorio, u"/translations")):
                    dir.mkdir(qsa.ustr(directorio, u"/translations"))
                curFiles.first()
                # file = None
                # tipo = None
                # contenido = ""
                self.setDisabled(True)
                s01_dowhile_1stloop = True
                while s01_dowhile_1stloop or curFiles.next():
                    s01_dowhile_1stloop = False
                    file_name = curFiles.valueBuffer(u"nombre")
                    tipo = self.tipoDeFichero(file_name)
                    contenido = curFiles.valueBuffer(u"contenido")
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
                        ]:
                            codec = "ISO-8859-1"
                        elif tipo in [".py", ".ts"]:
                            codec = "UTF-8"
                        else:
                            log.append(
                                qsa.util.translate(
                                    u"scripts", qsa.ustr(u"* Omitiendo ", file_name, u".")
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
                        elif tipo == ".kut":
                            sub_carpeta = "reports"

                        qsa.sys.write(
                            codec, qsa.ustr(directorio, "/%s/" % sub_carpeta, file_name), contenido
                        )
                        log.append(
                            qsa.util.translate(
                                u"scripts", qsa.ustr(u"* Exportando ", file_name, u".")
                            )
                        )

                    # qsa.sys.processEvents()

                cur_modules.select(qsa.ustr(u"idmodulo = '", idModulo, u"'"))
                if cur_modules.first():
                    cursorAreas.select(
                        qsa.ustr(u"idarea = '", cur_modules.valueBuffer(u"idarea"), u"'")
                    )
                    cursorAreas.first()
                    name_area = cursorAreas.valueBuffer(u"descripcion")
                    if not qsa.FileStatic.exists(
                        qsa.ustr(directorio, u"/", cur_modules.valueBuffer(u"idmodulo"), u".xpm")
                    ):
                        qsa.sys.write(
                            u"ISO-8859-1",
                            qsa.ustr(
                                directorio, u"/", cur_modules.valueBuffer(u"idmodulo"), u".xpm"
                            ),
                            cur_modules.valueBuffer(u"icono"),
                        )
                        log.append(
                            qsa.util.translate(
                                u"scripts",
                                qsa.ustr(
                                    u"* Exportando ",
                                    cur_modules.valueBuffer(u"idmodulo"),
                                    u".xpm (Regenerado).",
                                ),
                            )
                        )
                    if not qsa.FileStatic.exists(
                        qsa.ustr(directorio, u"/", cur_modules.valueBuffer(u"idmodulo"), u".mod")
                    ):
                        contenido = qsa.ustr(
                            u"<!DOCTYPE MODULE>\n<MODULE>\n<name>",
                            cur_modules.valueBuffer(u"idmodulo"),
                            u'</name>\n<alias>QT_TRANSLATE_NOOP("FLWidgetApplication","',
                            cur_modules.valueBuffer(u"descripcion"),
                            u'")</alias>\n<area>',
                            cur_modules.valueBuffer(u"idarea"),
                            u'</area>\n<name_area>QT_TRANSLATE_NOOP("FLWidgetApplication","',
                            name_area,
                            u'")</name_area>\n<version>',
                            cur_modules.valueBuffer(u"version"),
                            u"</version>\n<icon>",
                            cur_modules.valueBuffer(u"idmodulo"),
                            u".xpm</icon>\n<flversion>",
                            cur_modules.valueBuffer(u"version"),
                            u"</flversion>\n<description>",
                            cur_modules.valueBuffer(u"idmodulo"),
                            u"</description>\n</MODULE>",
                        )
                        qsa.sys.write(
                            u"ISO-8859-1",
                            qsa.ustr(
                                directorio, u"/", cur_modules.valueBuffer(u"idmodulo"), u".mod"
                            ),
                            contenido,
                        )
                        log.append(
                            qsa.util.translate(
                                u"scripts",
                                qsa.ustr(
                                    u"* Generando ",
                                    cur_modules.valueBuffer(u"idmodulo"),
                                    u".mod (Regenerado).",
                                ),
                            )
                        )

                self.setDisabled(False)
                log.append(qsa.util.translate(u"scripts", u"* Exportación finalizada."))


form = None
