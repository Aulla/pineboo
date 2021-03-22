"""Flreloadlast module."""
# -*- coding: utf-8 -*-
from pineboolib.qsa import qsa
import os


class FormInternalObj(qsa.FormDBWidget):
    """FormInternalObj class."""

    def _class_init(self) -> None:
        """Inicialize."""
        self = self

    def init(self) -> None:
        """Init function."""
        pass

    def main(self) -> None:
        """Entry function."""
        util = qsa.FLUtil()
        setting = "scripts/sys/modLastModule_%s" % qsa.sys.nameBD()
        last_module = util.readSettingEntry(setting)
        if not last_module:
            last_module = qsa.FileDialog.getOpenFileName(
                util.translate(u"scripts", u"Módulo a cargar (*.mod)"),
                util.translate(u"scripts", u"Módulo a cargar"),
            )
            if not last_module:
                return
            util.writeSettingEntry(setting, last_module)

        qsa.sys.processEvents()
        self.load_module(last_module)
        qsa.sys.reinit()

    def load_module(self, nombre_fichero: str) -> bool:
        """Load modules."""
        util = qsa.FLUtil()
        fichero = qsa.File(nombre_fichero, "iso-8859-15")
        modulo = None
        descripcion = None
        area = None
        area_description = None
        version = None
        icon_name = None
        # versionMinimaFL = None
        dependencias = qsa.Array()
        fichero.open(qsa.File.ReadOnly)
        file_ = fichero.read()
        module_xml = qsa.FLDomDocument()
        if module_xml.setContent(file_):
            module_node = module_xml.namedItem(u"MODULE")
            if module_node is None:
                qsa.MessageBox.critical(
                    util.translate(u"scripts", u"Error en la carga del fichero xml .mod"),
                    qsa.MessageBox.Ok,
                    qsa.MessageBox.NoButton,
                )
            modulo = module_node.namedItem(u"name").toElement().text()
            descripcion = module_node.namedItem(u"alias").toElement().text()
            area = module_node.namedItem(u"area").toElement().text()
            area_description = module_node.namedItem(u"areaname").toElement().text()
            version = module_node.namedItem(u"version").toElement().text()
            icon_name = module_node.namedItem(u"icon").toElement().text()
            # if module_node.namedItem(u"flversion"):
            #    versionMinimaFL = module_node.namedItem(u"flversion").toElement().text()
            if module_node.namedItem(u"dependencies") is not None:
                depend_node = module_xml.elementsByTagName(u"dependency")
                i = 0
                while i < len(depend_node):
                    dependencias[i] = depend_node.item(i).toElement().text()
                    i += 1
        else:
            if not isinstance(file_, str):
                raise Exception("data must be str, not bytes!!")
            file_array = file_.split(u"\n")
            modulo = self.get_value(file_array[0])
            descripcion = self.get_value(file_array[1])
            area = self.get_value(file_array[2]) or ""
            area_description = self.get_value(file_array[3])
            version = self.get_value(file_array[4])
            icon_name = self.get_value(file_array[5])

        descripcion = qsa.qt_translate_noop(descripcion or "", fichero.path or "", modulo or "")
        area_description = qsa.qt_translate_noop(
            area_description or "", fichero.path or "", modulo or ""
        )
        icon_file = qsa.File(qsa.ustr(fichero.path, u"/", icon_name))
        icon_file.open(qsa.File.ReadOnly)
        icono = icon_file.read()
        icon_file.close()

        if not util.sqlSelect(u"flareas", u"idarea", qsa.ustr(u"idarea = '", area, u"'")):
            if not util.sqlInsert(
                u"flareas", u"idarea,descripcion", qsa.ustr(area, u",", area_description)
            ):
                qsa.MessageBox.warning(
                    util.translate(u"scripts", u"Error al crear el área:\n") + area,
                    qsa.MessageBox.Ok,
                    qsa.MessageBox.NoButton,
                )
                return False
        recargar = util.sqlSelect(
            u"flmodules", u"idmodulo", qsa.ustr(u"idmodulo = '", modulo, u"'")
        )
        modules_cursor = qsa.FLSqlCursor(u"flmodules")
        if recargar:
            # WITH_START
            modules_cursor.select(qsa.ustr(u"idmodulo = '", modulo, u"'"))
            modules_cursor.first()
            modules_cursor.setModeAccess(modules_cursor.Edit)
            # WITH_END

        else:
            modules_cursor.setModeAccess(modules_cursor.Insert)

        # WITH_START
        modules_cursor.refreshBuffer()
        modules_cursor.setValueBuffer(u"idmodulo", modulo)
        modules_cursor.setValueBuffer(u"descripcion", descripcion)
        modules_cursor.setValueBuffer(u"idarea", area)
        modules_cursor.setValueBuffer(u"version", version)
        modules_cursor.setValueBuffer(u"icono", icono)
        modules_cursor.commitBuffer()
        # WITH_END
        # curSeleccion = qsa.FLSqlCursor(u"flmodules")
        modules_cursor.setMainFilter(qsa.ustr(u"idmodulo = '", modulo, u"'"))
        modules_cursor.editRecord(False)
        qsa.from_project("formRecordflmodules").cargarDeDisco(qsa.ustr(fichero.path, u"/"), False)
        qsa.from_project("formRecordflmodules").accept()
        setting = "scripts/sys/modLastModule_%s" % qsa.sys.nameBD()
        nombre_fichero = "%s" % os.path.abspath(nombre_fichero)
        qsa.util.writeSettingEntry(setting, nombre_fichero)
        qsa.sys.processEvents()

        return True

    def version_compare(self, ver_1: str = "", ver_2: str = "") -> int:
        """Compare versions."""

        if ver_1 and ver_2:

            list_1 = ver_1.split(u".")
            list_2 = ver_2.split(u".")

            for num, item in enumerate(list_1):
                if qsa.parseInt(item) > qsa.parseInt(list_2[num]):
                    return 1
                if qsa.parseInt(item) < qsa.parseInt(list_2[num]):
                    return 2
        return 0

    def get_value(self, linea: str) -> str:
        """Return value."""
        return linea


form = None  # pylint: disable=C0103
