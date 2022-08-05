"""Systype module."""

import traceback
import os
import os.path
import sys
import re


from PyQt6 import QtCore, QtWidgets, QtGui, QtXml  # type: ignore[import]


from pineboolib.core.utils import utils_base, logging

from pineboolib.core import decorators, settings, translate

from pineboolib import application
from pineboolib.application import types, process

from pineboolib.application.database import pnsqlcursor, pnsqlquery, utils as utils_db


from pineboolib.application.packager import pnunpacker
from pineboolib.application.qsatypes import sysbasetype


from .aqsobjects import aqsql, aqs

from . import flutil
from . import flvar
from . import flfielddb
from . import fltabledb

from pineboolib.q3widgets import (
    qdialog,
    qlabel,
    qtextedit,
    qvboxlayout,
    qhboxlayout,
    qpushbutton,
    filedialog,
    dialog,
    qbytearray,
    messagebox,
)

from typing import cast, Optional, List, Any, Dict, Callable, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.interfaces import iconnection, isqlcursor  # pragma: no cover
    from pineboolib.fllegacy import flformrecorddb, flformdb  # noqa: F401 # pragma: no cover


LOGGER = logging.get_logger(__name__)


class AQTimer(QtCore.QTimer):
    """AQTimer class."""

    pass


class AQGlobalFunctionsClass(QtCore.QObject):
    """AQSGlobalFunction class."""

    functions_: Dict[str, Callable]
    mappers_: "QtCore.QSignalMapper"

    def __init__(self):
        """Initialize."""

        super().__init__()
        self.functions_ = {}
        self.mappers_ = QtCore.QSignalMapper()

    def set(self, function_name: str, global_function: Callable) -> None:
        """Set a new global function."""
        self.functions_[function_name] = global_function

    def get(self, function_name: str) -> Callable:
        """Return a global function specified by name."""

        return self.functions_[function_name]

    def exec_(self, function_name: str) -> None:
        """Execute a function specified by name."""

        fun = self.functions_[function_name]
        if fun is not None:
            fun()

    def mapConnect(self, obj: "QtWidgets.QWidget", signal: str, function_name: str) -> None:
        """Add conection to map."""

        self.mappers_.mappedString.connect(self.exec_)  # type: ignore
        sg_name = re.sub(r" *\(.*\)", "", signal)

        signal_ = getattr(obj, sg_name, None)
        if signal_ is not None:
            signal_.connect(self.mappers_.map)
            self.mappers_.setMapping(obj, function_name)


class SysType(sysbasetype.SysBaseType):
    """SysType class."""

    time_user_ = QtCore.QDateTime.currentDateTime()
    AQTimer = AQTimer
    AQGlobalFunctions = AQGlobalFunctionsClass()

    @classmethod
    def translate(cls, *args) -> str:
        """Translate a text."""

        group, text = (args[0], args[1]) if len(args) == 2 else ("scripts", args[0])

        if text == "MetaData":
            group, text = text, group

        return translate.translate(group, text.replace(" % ", " %% "))

    def printTextEdit(self, editor: "QtWidgets.QTextEdit"):
        """Print text from a textEdit."""

        application.PROJECT.aq_app.printTextEdit(editor)

    def diskCacheAbsDirPath(self) -> str:
        """Return Absolute disk cache path."""

        return os.path.abspath(application.PROJECT.tmpdir)

    def dialogGetFileImage(self) -> Optional[str]:
        """Show a file dialog and return a file name."""

        return application.PROJECT.aq_app.dialogGetFileImage()

    def toXmlReportData(self, qry: "pnsqlquery.PNSqlQuery") -> "QtXml.QDomDocument":
        """Return xml from a query."""

        return application.PROJECT.aq_app.toXmlReportData(qry)

    def showDocPage(self, url_: str) -> None:
        """Show externa file."""

        return application.PROJECT.aq_app.showDocPage(url_)

    def toPixmap(self, value_: str) -> "QtGui.QPixmap":
        """Create a QPixmap from a text."""

        return application.PROJECT.aq_app.toPixmap(value_)

    def setMultiLang(self, enable_: bool, lang_id_: str) -> None:
        """
        Change multilang status.

        @param enable, Boolean con el nuevo estado
        @param langid, Identificador del leguaje a activar
        """

        return application.PROJECT.aq_app.setMultiLang(enable_, lang_id_)

    def fromPixmap(self, pix_: "QtGui.QPixmap") -> str:
        """Return a text from a QPixmap."""

        return application.PROJECT.aq_app.fromPixmap(pix_)

    def popupWarn(self, msg_warn: str, script_calls: List[Any] = []) -> None:
        """Show a warning popup."""

        application.PROJECT.aq_app.popupWarn(msg_warn, script_calls)

    def openMasterForm(self, action_name_: str) -> None:
        """Open default form from a action."""

        if action_name_ in application.PROJECT.actions.keys():
            application.PROJECT.actions[action_name_].openDefaultForm()

    def scalePixmap(
        self, pix_: "QtGui.QPixmap", width_: int, height_: int, mode_: "QtCore.Qt.AspectRatioMode"
    ) -> "QtGui.QImage":
        """Return QImage scaled from a QPixmap."""

        return application.PROJECT.aq_app.scalePixmap(pix_, width_, height_, mode_)

    @classmethod
    def transactionLevel(cls) -> int:
        """Return transaction level."""

        return application.PROJECT.conn_manager.useConn("default").transactionLevel()

    @classmethod
    def installACL(cls, idacl) -> None:
        """Install a acl."""
        from pineboolib.application.acls import pnaccesscontrollists

        acl_ = pnaccesscontrollists.PNAccessControlLists()

        if acl_:
            acl_.install_acl(idacl)

    @classmethod
    def updateAreas(cls) -> None:
        """Update areas in mdi."""
        func_ = getattr(application.PROJECT.main_window, "initToolBox", None)
        if func_ is not None:
            func_()

    @classmethod
    def reinit(cls) -> None:
        """Call reinit script."""

        while application.PROJECT.aq_app._inicializing:
            application.PROJECT.app.processEvents()  # type: ignore [misc]

        application.PROJECT.aq_app.reinit()

    @classmethod
    def modMainWidget(cls, id_module_: str) -> Optional["QtWidgets.QWidget"]:
        """Set module MainWinget."""

        return application.PROJECT.aq_app.modMainWidget(id_module_)

    @classmethod
    def setCaptionMainWidget(cls, title: str) -> None:
        """Set caption in the main widget."""

        application.PROJECT.aq_app.setCaptionMainWidget(title)

    @staticmethod
    def execQSA(qsa_file=None, args=None) -> Any:
        """Execute a QS file."""

        try:
            with open(qsa_file, "r") as file_:
                fun = types.function("exec_qsa", file_.read())
                file_.close()
                return fun(args)
        except Exception:
            error = traceback.format_exc()
            LOGGER.warning(error)

        return None

    @staticmethod
    def dumpDatabase() -> None:
        """Launch dump database."""
        aq_dumper = AbanQDbDumper()
        aq_dumper.init()

    @staticmethod
    def terminateChecksLocks(cursor: "isqlcursor.ISqlCursor" = None) -> None:
        """Set check risk locks to False in a cursor."""
        if cursor is not None:
            cursor.checkRisksLocks(True)

    @classmethod
    def mvProjectXml(cls) -> "QtXml.QDomDocument":
        """Extract a module defition to a QDomDocument."""

        doc_ret_ = QtXml.QDomDocument()
        str_xml_ = utils_db.sql_select("flupdates", "modulesdef", "actual")
        if not str_xml_:
            return doc_ret_
        doc = QtXml.QDomDocument()
        if not doc.setContent(str_xml_):
            return doc_ret_
        str_xml_ = ""
        nodes = doc.childNodes()

        for number in range(len(nodes)):
            it_ = nodes.item(number)
            if it_.isComment():
                data = it_.toComment().data()
                if not data == "" and data.startswith("<mvproject "):
                    str_xml_ = data
                    break

        if str_xml_ == "":
            return doc_ret_
        doc_ret_.setContent(str_xml_)
        return doc_ret_

    @classmethod
    def mvProjectModules(cls) -> "types.Array":
        """Return modules defitions Dict."""
        ret = types.Array()
        doc = cls.mvProjectXml()
        mods = doc.elementsByTagName("module")
        for number in range(len(mods)):
            it_ = mods.item(number).toElement()
            mod = {"name": (it_.attribute("name")), "version": (it_.attribute("version"))}
            if len(mod["name"]) == 0:
                continue
            ret[mod["name"]] = mod

        return ret

    @classmethod
    def mvProjectExtensions(cls) -> "types.Array":
        """Return project extensions Dict."""

        ret = types.Array()
        doc = cls.mvProjectXml()
        exts = doc.elementsByTagName("extension")

        for number in range(len(exts)):
            it_ = exts.item(number).toElement()
            ext = {"name": (it_.attribute("name")), "version": (it_.attribute("version"))}
            if len(ext["name"]) == 0:
                continue
            ret[ext["name"]] = ext

        return ret

    @classmethod
    def calculateShaGlobal(cls) -> str:
        """Return sha global value."""

        value = ""
        qry = pnsqlquery.PNSqlQuery()
        qry.setSelect("sha")
        qry.setFrom("flfiles")
        if qry.exec_() and qry.first():
            value = utils_base.sha1(str(qry.value(0)))
            while qry.next():
                value = utils_base.sha1(value + str(qry.value(0)))
        else:
            value = utils_base.sha1("")

        return value

    def registerUpdate(self, input_: str = "") -> None:
        """Install a package."""

        if not input_:
            return
        unpacker = pnunpacker.PNUnpacker(input_)
        errors = unpacker.errorMessages()
        if len(errors) != 0:
            msg = self.translate("Hubo los siguientes errores al intentar cargar los módulos:")
            msg += "\n"
            for number in range(len(errors)):
                msg += utils_base.ustr(errors[number], "\n")

            self.errorMsgBox(msg)
            return

        unpacker.jump()
        unpacker.jump()
        unpacker.jump()
        now = str(types.Date())
        file_ = types.File(input_)
        file_name = file_.name
        modules_def = self.toUnicode(unpacker.getText(), "utf8")
        files_def = self.toUnicode(unpacker.getText(), "utf8")
        sha_global = self.calculateShaGlobal()
        aqsql.AQSql.update("flupdates", ["actual"], [False], "1=1")
        aqsql.AQSql.insert(
            "flupdates",
            ["fecha", "hora", "nombre", "modulesdef", "filesdef", "shaglobal"],
            [
                now[: now.find("T")],
                now[(len(now) - (8)) :],
                file_name,
                modules_def,
                files_def,
                sha_global,
            ],
        )

    def warnLocalChanges(self, changes: Optional[Dict[str, Any]] = None) -> bool:
        """Show local changes warning."""

        if changes is None:
            changes = self.localChanges()
        if changes["size"] == 0:
            return True
        diag = qdialog.QDialog()
        diag.caption = self.translate("Detectados cambios locales")
        diag.setModal(True)
        txt = ""
        txt += self.translate("¡¡ CUIDADO !! DETECTADOS CAMBIOS LOCALES\n\n")
        txt += self.translate("Se han detectado cambios locales en los módulos desde\n")
        txt += self.translate("la última actualización/instalación de un paquete de módulos.\n")
        txt += self.translate("Si continua es posible que estos cambios sean sobreescritos por\n")
        txt += self.translate("los cambios que incluye el paquete que quiere cargar.\n\n")
        txt += "\n\n"
        txt += self.translate("Registro de cambios")
        lay = qvboxlayout.QVBoxLayout(diag)
        # lay.setMargin(6)
        # lay.setSpacing(6)
        lbl = qlabel.QLabel(diag)
        lbl.setText(txt)
        lbl.setAlignment(cast(QtCore.Qt.AlignmentFlag, QtCore.Qt.AlignmentFlag.AlignTop))
        lay.addWidget(lbl)
        ted = qtextedit.QTextEdit(diag)
        ted.setTextFormat(qtextedit.QTextEdit.LogText)
        ted.setAlignment(
            cast(
                QtCore.Qt.AlignmentFlag,
                QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter,
            )
        )
        ted.append(self.reportChanges(changes))
        lay.addWidget(ted)
        lbl2 = qlabel.QLabel(diag)
        lbl2.setText(self.translate("¿Que desea hacer?"))
        lbl2.setAlignment(cast(QtCore.Qt.AlignmentFlag, QtCore.Qt.AlignmentFlag.AlignTop))
        lay.addWidget(lbl2)
        lay2 = qhboxlayout.QHBoxLayout()
        # lay2.setMargin(6)
        # lay2.setSpacing(6)
        lay.addLayout(lay2)
        push_button_cancel = qpushbutton.QPushButton(diag)
        push_button_cancel.setText(self.translate("Cancelar"))
        push_button_accept = qpushbutton.QPushButton(diag)
        push_button_accept.setText(self.translate("continue"))
        lay2.addWidget(push_button_cancel)
        lay2.addWidget(push_button_accept)
        push_button_accept.clicked.connect(diag.accept)  # type: ignore [attr-defined]
        push_button_cancel.clicked.connect(diag.reject)  # type: ignore [attr-defined]
        if not application.PROJECT.app.platformName() != "offscreen":
            return False if (diag.exec() == 0) else True
        else:
            return True

    def xmlFilesDefBd(self) -> "QtXml.QDomDocument":
        """Return a QDomDocument with files definition."""

        doc = QtXml.QDomDocument("files_def")
        root = doc.createElement("files")
        doc.appendChild(root)
        qry = pnsqlquery.PNSqlQuery()
        qry.setSelect("idmodulo,nombre,contenido")
        qry.setFrom("flfiles")
        if not qry.exec_():
            return doc
        sha_sum = ""
        sha_sum_txt = ""
        sha_sum_bin = ""
        while qry.next():
            id_module = str(qry.value(0))
            if id_module == "sys":
                continue
            file_name = str(qry.value(1))
            ba_ = qbytearray.QByteArray()
            ba_.string = self.fromUnicode(str(qry.value(2)), "iso-8859-15")
            sha = ba_.sha1()
            node_file = doc.createElement("file")
            root.appendChild(node_file)
            node = doc.createElement("module")
            node_file.appendChild(node)
            node_text = doc.createTextNode(id_module)
            node.appendChild(node_text)
            node = doc.createElement("name")
            node_file.appendChild(node)
            node_text = doc.createTextNode(file_name)
            node.appendChild(node_text)
            if self.textPacking(file_name):
                node = doc.createElement("text")
                node_file.appendChild(node)
                node_text = doc.createTextNode(file_name)
                node.appendChild(node_text)
                node = doc.createElement("shatext")
                node_file.appendChild(node)
                node_text = doc.createTextNode(sha)
                node.appendChild(node_text)
                ba_ = qbytearray.QByteArray()
                ba_.string = sha_sum + sha
                sha_sum = ba_.sha1()
                ba_ = qbytearray.QByteArray()
                ba_.string = sha_sum_txt + sha
                sha_sum_txt = ba_.sha1()

        qry = pnsqlquery.PNSqlQuery()
        qry.setSelect("idmodulo,icono")
        qry.setFrom("flmodules")
        if qry.exec_():
            while qry.next():
                id_module = str(qry.value(0))
                if id_module == "sys":
                    continue
                file_name = utils_base.ustr(id_module, ".xpm")
                ba_ = qbytearray.QByteArray()
                ba_.string = str(qry.value(1))
                sha = ba_.sha1()
                node_file = doc.createElement("file")
                root.appendChild(node_file)
                node = doc.createElement("module")
                node_file.appendChild(node)
                node_text = doc.createTextNode(id_module)
                node.appendChild(node_text)
                node = doc.createElement("name")
                node_file.appendChild(node)
                node_text = doc.createTextNode(file_name)
                node.appendChild(node_text)
                if self.textPacking(file_name):
                    node = doc.createElement("text")
                    node_file.appendChild(node)
                    node_text = doc.createTextNode(file_name)
                    node.appendChild(node_text)
                    node = doc.createElement("shatext")
                    node_file.appendChild(node)
                    node_text = doc.createTextNode(sha)
                    node.appendChild(node_text)
                    ba_ = qbytearray.QByteArray()
                    ba_.string = sha_sum + sha
                    sha_sum = ba_.sha1()
                    ba_ = qbytearray.QByteArray()
                    ba_.string = sha_sum_txt + sha
                    sha_sum_txt = ba_.sha1()

        node = doc.createElement("shasum")
        node.appendChild(doc.createTextNode(sha_sum))
        root.appendChild(node)
        node = doc.createElement("shasumtxt")
        node.appendChild(doc.createTextNode(sha_sum_txt))
        root.appendChild(node)
        node = doc.createElement("shasumbin")
        node.appendChild(doc.createTextNode(sha_sum_bin))
        root.appendChild(node)
        return doc

    def loadModules(self, input_: Optional[Any] = None, warning_bakup: bool = True) -> bool:
        """Load modules from a package."""

        if input_ is None:
            util = flutil.FLUtil()
            dir_ = types.Dir(self.installPrefix())
            dir_.setCurrent()
            setting = (
                "scripts/sys/lastDirPackages_%s"
                % application.PROJECT.conn_manager.mainConn().DBName()
            )

            last_path = util.readSettingEntry(setting)
            path_tuple = QtWidgets.QFileDialog.getOpenFileName(
                QtWidgets.QApplication.focusWidget(),
                self.translate("scripts", "Seleccionar Eneboo/Abanq Package"),
                last_path,
                "Eneboo Package (*.eneboopkg);;Abanq Package (*.abanq)",
            )
            input_ = path_tuple[0]
            if input_:
                util.writeSettingEntry(setting, os.path.dirname(input_))

        return self.loadAbanQPackage(input_, warning_bakup)

    def loadAbanQPackage(self, input_: str, warning_bakup: bool = True) -> bool:
        """Load and process a Abanq/Eneboo package."""

        if input_:

            if warning_bakup and self.interactiveGUI():
                txt = ""
                txt += self.translate(
                    "Asegúrese de tener una copia de seguridad de todos los datos\n"
                )
                txt += self.translate(
                    "y de que  no hay ningun otro  usuario conectado a la base de\n"
                )
                txt += self.translate("datos mientras se realiza la carga.\n\n")
                txt += "\n\n"
                txt += self.translate("¿Desea continuar?")

                if messagebox.MessageBox.Yes != messagebox.MessageBox.warning(
                    txt, messagebox.MessageBox.No, messagebox.MessageBox.Yes
                ):
                    return False

            changes = self.localChanges()
            if changes["size"]:
                if not self.warnLocalChanges(changes):
                    return False

            unpacker = pnunpacker.PNUnpacker(input_)
            errors = unpacker.errorMessages()
            if len(errors):
                msg = self.translate("Hubo los siguientes errores al intentar cargar los módulos:")
                msg += "\n"

                for number in range(len(errors)):
                    msg += utils_base.ustr(errors[number], "\n")
                self.errorMsgBox(msg)
                return False

            unpacker.jump()
            unpacker.jump()
            unpacker.jump()

            if self.loadModulesDef(unpacker):
                if self.loadFilesDef(unpacker):
                    self.registerUpdate(input_)
                    self.infoMsgBox(
                        self.translate("La carga de módulos se ha realizado con éxito.")
                    )
                    self.reinit()

                    tmp_var = flvar.FLVar()
                    tmp_var.set("mrproper", "dirty")
                    return True
                else:
                    self.errorMsgBox(
                        self.translate("No se ha podido realizar la carga de los módulos.")
                    )

        return False

    def loadFilesDef(self, document: "pnunpacker.PNUnpacker") -> bool:
        """Load files definition from a package to a QDomDocument."""

        files_definition = self.toUnicode(document.getText(), "utf8")
        doc = QtXml.QDomDocument()
        if not doc.setContent(files_definition):
            self.errorMsgBox(
                self.translate("Error XML al intentar cargar la definición de los ficheros.")
            )
            return False
        ok_ = True
        root = doc.firstChild()
        files = root.childNodes()
        flutil.FLUtil.createProgressDialog(self.translate("Registrando ficheros"), len(files))

        for number in range(len(files)):

            it_ = files.item(number)
            fil = {
                "id": it_.namedItem("name").toElement().text(),
                "skip": it_.namedItem("skip").toElement().text(),
                "module": it_.namedItem("module").toElement().text(),
                "text": it_.namedItem("text").toElement().text(),
                "shatext": it_.namedItem("shatext").toElement().text(),
                "binary": it_.namedItem("binary").toElement().text(),
                "shabinary": it_.namedItem("shabinary").toElement().text(),
            }
            flutil.FLUtil.setProgress(number)
            flutil.FLUtil.setLabelText(
                utils_base.ustr(self.translate("Registrando fichero"), " ", fil["id"])
            )
            if len(fil["id"]) == 0 or fil["skip"] == "true":
                continue
            if not self.registerFile(fil, document):
                self.errorMsgBox(
                    utils_base.ustr(self.translate("Error registrando el fichero"), " ", fil["id"])
                )
                ok_ = False
                break

        flutil.FLUtil.destroyProgressDialog()
        return ok_

    def registerFile(self, fil: Dict[str, Any], document: Any) -> bool:
        """Register a file in the database."""
        id_value: str = fil["id"]
        if id_value.endswith(".xpm"):
            cur = pnsqlcursor.PNSqlCursor("flmodules")
            if not cur.select(utils_base.ustr("idmodulo='", fil["module"], "'")) or not cur.first():
                return False

            cur.setModeAccess(aqsql.AQSql.Edit)
            cur.refreshBuffer()
            cur.setValueBuffer("icono", document.getText())
            return cur.commitBuffer()

        cur = pnsqlcursor.PNSqlCursor("flfiles")
        if not cur.select("nombre='%s'" % id_value):
            return False
        cur.setModeAccess((aqsql.AQSql.Edit if cur.first() else aqsql.AQSql.Insert))
        cur.refreshBuffer()
        cur.setValueBuffer("nombre", id_value)
        cur.setValueBuffer("idmodulo", fil["module"])
        cur.setValueBuffer("sha", fil["shatext"])
        if len(fil["text"]):
            encode = "iso-8859-15" if not id_value.endswith((".py")) else "UTF-8"
            try:
                cur.setValueBuffer(
                    "contenido",
                    self.toUnicode(document.getText(), encode)
                    if not id_value.endswith(".py")
                    else document.getText(),
                )
            except UnicodeEncodeError as error:
                LOGGER.error("The %s file does not have the correct encode (%s)", id_value, encode)
                raise error

        if len(fil["binary"]) > 0:
            document.getBinary()
        return cur.commitBuffer()

    def checkProjectName(self, project_name: str) -> bool:
        """Return if te project name is valid."""
        if not project_name:
            project_name = ""
        db_project_name = flutil.FLUtil.readDBSettingEntry("projectname") or ""

        if project_name == db_project_name:
            return True

        if project_name and not db_project_name:
            return flutil.FLUtil.writeDBSettingEntry("projectname", project_name)

        txt = ""
        txt += self.translate("¡¡ CUIDADO !! POSIBLE INCOHERENCIA EN LOS MÓDULOS\n\n")
        txt += self.translate("Está intentando cargar un proyecto o rama de módulos cuyo\n")
        txt += self.translate("nombre difiere del instalado actualmente en la base de datos.\n")
        txt += self.translate("Es posible que la estructura de los módulos que quiere cargar\n")
        txt += self.translate(
            "sea completamente distinta a la instalada actualmente, y si continua\n"
        )
        txt += self.translate(
            "podría dañar el código, datos y la estructura de tablas de Eneboo.\n\n"
        )

        txt += self.translate("- Nombre del proyecto instalado: %s\n") % (str(db_project_name))
        txt += self.translate("- Nombre del proyecto a cargar: %s\n\n") % (str(project_name))
        txt += "\n\n"

        if not self.interactiveGUI():
            LOGGER.warning(txt)
            return False
        txt += self.translate("¿Desea continuar?")
        return messagebox.MessageBox.Yes == messagebox.MessageBox.warning(
            txt,
            messagebox.MessageBox.No,
            messagebox.MessageBox.Yes,
            messagebox.MessageBox.NoButton,
            "Pineboo",
        )

    def loadModulesDef(self, document: "pnunpacker.PNUnpacker") -> bool:
        """Return QDomDocument with modules definition."""

        modules_definition = self.toUnicode(document.getText(), "utf8")
        doc = QtXml.QDomDocument()
        if not doc.setContent(modules_definition):
            self.errorMsgBox(
                self.translate("Error XML al intentar cargar la definición de los módulos.")
            )
            return False
        root = doc.firstChild()
        if not self.checkProjectName(root.toElement().attribute("projectname", "")):
            return False
        ok_ = True
        modules = root.childNodes()
        flutil.FLUtil.createProgressDialog(self.translate("Registrando módulos"), len(modules))
        for number in range(len(modules)):
            it_ = modules.item(number)
            mod = {
                "id": it_.namedItem("name").toElement().text(),
                "alias": self.trTagText(it_.namedItem("alias").toElement().text()),
                "area": it_.namedItem("area").toElement().text(),
                "areaname": self.trTagText(it_.namedItem("areaname").toElement().text()),
                "version": it_.namedItem("version").toElement().text(),
            }
            flutil.FLUtil.setProgress(number)
            flutil.FLUtil.setLabelText(
                utils_base.ustr(self.translate("Registrando módulo"), " ", mod["id"])
            )
            if not self.registerArea(mod) or not self.registerModule(mod):
                self.errorMsgBox(
                    utils_base.ustr(self.translate("Error registrando el módulo"), " ", mod["id"])
                )
                ok_ = False
                break

        flutil.FLUtil.destroyProgressDialog()
        return ok_

    def registerArea(self, modules: Dict[str, Any]) -> bool:
        """Return True if the area is created or False."""
        cur = pnsqlcursor.PNSqlCursor("flareas")
        if not cur.select(utils_base.ustr("idarea = '", modules["area"], "'")):
            return False
        cur.setModeAccess((aqsql.AQSql.Edit if cur.first() else aqsql.AQSql.Insert))
        cur.refreshBuffer()
        cur.setValueBuffer("idarea", modules["area"])
        cur.setValueBuffer("descripcion", modules["areaname"])
        return cur.commitBuffer()

    def registerModule(self, modules: Dict[str, Any]) -> bool:
        """Return True if the module is created or False."""

        cur = pnsqlcursor.PNSqlCursor("flmodules")
        if not cur.select(utils_base.ustr("idmodulo='", modules["id"], "'")):
            return False
        cur.setModeAccess((aqsql.AQSql.Edit if cur.first() else aqsql.AQSql.Insert))
        cur.refreshBuffer()
        cur.setValueBuffer("idmodulo", modules["id"])
        cur.setValueBuffer("idarea", modules["area"])
        cur.setValueBuffer("descripcion", modules["alias"])
        cur.setValueBuffer("version", modules["version"])
        return cur.commitBuffer()

    def questionMsgBox(
        self,
        msg: str,
        key_remember: str = "",
        txt_remember: str = "",
        force_show: bool = True,
        txt_caption: str = "Pineboo",
        txt_yes: str = "Sí",
        txt_no: str = "No",
    ) -> Any:
        """Return a messagebox result."""

        key = "QuestionMsgBox/"
        value_remember = False
        if key_remember:
            value_remember = settings.SETTINGS.value(key + key_remember)
            if value_remember and not force_show:
                return messagebox.MessageBox.Yes
        if not self.interactiveGUI():
            return True
        diag = qdialog.QDialog()
        diag.caption = txt_caption
        diag.setModal(True)
        lay = qvboxlayout.QVBoxLayout(diag)
        # lay.setMargin(6)
        lay.setSpacing(6)
        lay2 = qhboxlayout.QHBoxLayout(diag)
        # lay2.setMargin(6)
        lay2.setSpacing(6)
        label_pix = qlabel.QLabel(diag)
        pixmap = aqs.AQS.pixmap_fromMimeSource("help_index.png")
        if pixmap:
            label_pix.setPixmap(pixmap)
            label_pix.setAlignment(aqs.AQS.AlignTop)
        lay2.addWidget(label_pix)
        lbl = qlabel.QLabel(diag)
        lbl.setText(msg)
        lbl.setAlignment(cast(QtCore.Qt.AlignmentFlag, aqs.AQS.AlignTop | aqs.AQS.WordBreak))
        lay2.addWidget(lbl)
        lay3 = qhboxlayout.QHBoxLayout(diag)
        # lay3.setMargin(6)
        lay3.setSpacing(6)
        push_button_yes = qpushbutton.QPushButton(diag)
        push_button_yes.setText(txt_yes if txt_yes else self.translate("Sí"))
        push_button_no = qpushbutton.QPushButton(diag)
        push_button_no.setText(txt_no if txt_no else self.translate("No"))
        lay3.addWidget(push_button_yes)
        lay3.addWidget(push_button_no)
        push_button_yes.clicked.connect(diag.accept)  # type: ignore [attr-defined]
        push_button_no.clicked.connect(diag.reject)  # type: ignore [attr-defined]
        check_remember = None
        if key_remember and txt_remember:

            check_remember = QtWidgets.QCheckBox(txt_remember, diag)
            check_remember.setChecked(value_remember)
            lay.addWidget(check_remember)

        if not application.PROJECT.app.platformName() == "offscreen":
            return messagebox.MessageBox.Yes

        ret = messagebox.MessageBox.No if (diag.exec() == 0) else messagebox.MessageBox.Yes
        if check_remember is not None:
            settings.SETTINGS.set_value(key + key_remember, check_remember.isChecked())
        return ret

    def exportModules(self) -> None:
        """Export modules."""

        dir_base_path = filedialog.FileDialog.getExistingDirectory(types.Dir.home)
        if not dir_base_path:
            return
        data_base_name = application.PROJECT.conn_manager.mainConn()._db_name
        dir_base_path = types.Dir.cleanDirPath(
            utils_base.ustr(
                dir_base_path,
                "/modulos_exportados_",
                data_base_name[data_base_name.rfind("/") + 1 :],
            )
        )
        dir_ = types.Dir()
        if not dir_.fileExists(dir_base_path):
            try:
                dir_.mkdir(dir_base_path)
            except Exception:
                error = traceback.format_exc()
                self.errorMsgBox(utils_base.ustr("", error))
                return

        else:
            self.warnMsgBox(
                dir_base_path + self.translate(" ya existe,\ndebe borrarlo antes de continuar")
            )
            return

        qry = pnsqlquery.PNSqlQuery()
        qry.setSelect("idmodulo")
        qry.setFrom("flmodules")
        if not qry.exec_() or qry.size() == 0:
            return
        pos = 0
        flutil.FLUtil.createProgressDialog(self.translate("Exportando módulos"), qry.size() - 1)
        while qry.next():
            id_module = qry.value(0)
            if id_module == "sys":
                continue
            flutil.FLUtil.setLabelText(id_module)
            pos += 1
            flutil.FLUtil.setProgress(pos)
            try:
                self.exportModule(id_module, dir_base_path)
            except Exception:
                error = traceback.format_exc()
                flutil.FLUtil.destroyProgressDialog()
                self.errorMsgBox(utils_base.ustr("", error))
                return

        db_project_name = flutil.FLUtil.readDBSettingEntry("projectname")
        if not db_project_name:
            db_project_name = ""
        if not db_project_name == "":
            doc = QtXml.QDomDocument()
            tag = doc.createElement("mvproject")
            tag.toElement().setAttribute("name", db_project_name)
            doc.appendChild(tag)
            try:
                types.FileStatic.write(
                    utils_base.ustr(dir_base_path, "/mvproject.xml"), doc.toString(2)
                )
            except Exception:
                error = traceback.format_exc()
                flutil.FLUtil.destroyProgressDialog()
                self.errorMsgBox(utils_base.ustr("", error))
                return

        flutil.FLUtil.destroyProgressDialog()
        self.infoMsgBox(self.translate("Módulos exportados en:\n") + dir_base_path)

    def xmlModule(self, id_module: str) -> "QtXml.QDomDocument":
        """Return xml data from a module."""
        qry = pnsqlquery.PNSqlQuery()
        qry.setSelect("descripcion,idarea,version")
        qry.setFrom("flmodules")
        qry.setWhere(utils_base.ustr("idmodulo='", id_module, "'"))
        doc = QtXml.QDomDocument("MODULE")
        if not qry.exec_() or not qry.next():
            return doc

        tag_module = doc.createElement("MODULE")
        doc.appendChild(tag_module)
        tag = doc.createElement("name")
        tag.appendChild(doc.createTextNode(id_module))
        tag_module.appendChild(tag)
        translate_noop = 'QT_TRANSLATE_NOOP("Eneboo","%s")'
        tag = doc.createElement("alias")
        tag.appendChild(doc.createTextNode(translate_noop % qry.value(0)))
        tag_module.appendChild(tag)
        id_area = qry.value(1)
        tag = doc.createElement("area")
        tag.appendChild(doc.createTextNode(id_area))
        tag_module.appendChild(tag)
        area_name = utils_db.sql_select(
            "flareas", "descripcion", utils_base.ustr("idarea='", id_area, "'")
        )
        tag = doc.createElement("areaname")
        tag.appendChild(doc.createTextNode(translate_noop % area_name))
        tag_module.appendChild(tag)
        tag = doc.createElement("entryclass")
        tag.appendChild(doc.createTextNode(id_module))
        tag_module.appendChild(tag)
        tag = doc.createElement("version")
        tag.appendChild(doc.createTextNode(qry.value(2)))
        tag_module.appendChild(tag)
        tag = doc.createElement("icon")
        tag.appendChild(doc.createTextNode(utils_base.ustr(id_module, ".xpm")))
        tag_module.appendChild(tag)
        return doc

    def fileWriteIso(self, file_name: str, content: str) -> None:
        """Write data into a file with ISO-8859-15 encode."""

        file_iso = types.File(file_name, "ISO8859-15")
        file_iso.write(content.encode("ISO8859-15", "ignore"))
        file_iso.close()

    def fileWriteUtf8(self, file_name: str, content: str) -> None:
        """Write data into a file with UTF-8 encode."""

        file_utf = types.File(file_name, "UTF-8")
        file_utf.write(content)
        file_utf.close()

    def exportModule(self, id_module: str, dir_base_path: str) -> None:
        """Export a module to a directory."""

        dir_ = types.Dir()
        dir_path = types.Dir.cleanDirPath(utils_base.ustr(dir_base_path, "/", id_module))
        if not dir_.fileExists(dir_path):
            dir_.mkdir(dir_path)
        for name in ["/forms", "/scripts", "/queries", "/tables", "/reports", "/translations"]:
            if not dir_.fileExists("%s%s" % (dir_path, name)):
                dir_.mkdir("%s%s" % (dir_path, name))
        xml_module = self.xmlModule(id_module)
        self.fileWriteIso(utils_base.ustr(dir_path, "/", id_module, ".mod"), xml_module.toString(2))
        xpm_module = utils_db.sql_select(
            "flmodules", "icono", utils_base.ustr("idmodulo='", id_module, "'")
        )
        self.fileWriteIso(utils_base.ustr(dir_path, "/", id_module, ".xpm"), xpm_module)
        qry = pnsqlquery.PNSqlQuery()
        qry.setSelect("nombre,contenido")
        qry.setFrom("flfiles")
        qry.setWhere(utils_base.ustr("idmodulo='", id_module, "'"))
        if qry.exec_():
            while qry.next():
                name = qry.value(0)
                content = qry.value(1)
                type_ = name[name.rfind(".") :]
                if type_ == ".xml":
                    self.fileWriteIso(utils_base.ustr(dir_path, "/", name), content)
                elif type_ == ".ui":
                    self.fileWriteIso(utils_base.ustr(dir_path, "/forms/", name), content)
                elif type_ == ".qs":
                    self.fileWriteIso(utils_base.ustr(dir_path, "/scripts/", name), content)
                elif type_ == ".qry":
                    self.fileWriteIso(utils_base.ustr(dir_path, "/queries/", name), content)
                elif type_ == ".mtd":
                    self.fileWriteIso(utils_base.ustr(dir_path, "/tables/", name), content)
                elif type_ in (".kut", ".ar", ".jrxml", ".svg"):
                    self.fileWriteIso(utils_base.ustr(dir_path, "/reports/", name), content)
                elif type_ == ".ts":
                    self.fileWriteIso(utils_base.ustr(dir_path, "/translations/", name), content)
                elif type_ == ".py":
                    self.fileWriteUtf8(utils_base.ustr(dir_path, "/scripts/", name), content)

    def importModules(self, warning_bakup: bool = True) -> None:
        """Import modules from a directory."""

        if warning_bakup and self.interactiveGUI():
            txt = ""
            txt += self.translate("Asegúrese de tener una copia de seguridad de todos los datos\n")
            txt += self.translate("y de que  no hay ningun otro  usuario conectado a la base de\n")
            txt += self.translate("datos mientras se realiza la importación.\n\n")
            txt += self.translate("Obtenga soporte en")
            txt += " http://www.infosial.com\n(c) InfoSiAL S.L."
            txt += "\n\n"
            txt += self.translate("¿Desea continuar?")
            if messagebox.MessageBox.Yes != messagebox.MessageBox.warning(
                txt, messagebox.MessageBox.No, messagebox.MessageBox.Yes
            ):
                return

        key = utils_base.ustr("scripts/sys/modLastDirModules_", self.nameBD())
        dir_ant = settings.SETTINGS.value(key)

        dir_modules = filedialog.FileDialog.getExistingDirectory(
            str(dir_ant) if dir_ant else ".", self.translate("Directorio de Módulos")
        )
        if not dir_modules:
            return
        dir_modules = types.Dir.cleanDirPath(dir_modules)
        dir_modules = types.Dir.convertSeparators(dir_modules)
        QtCore.QDir.setCurrent(dir_modules)  # change current directory
        modified_files = self.selectModsDialog(flutil.FLUtil.findFiles(dir_modules, "*.mod", False))
        flutil.FLUtil.createProgressDialog(self.translate("Importando"), len(modified_files))
        flutil.FLUtil.setProgress(1)

        for number, value in enumerate(modified_files):
            flutil.FLUtil.setLabelText(value)
            flutil.FLUtil.setProgress(number)
            if not self.importModule(value):
                self.errorMsgBox(self.translate("Error al cargar el módulo:\n") + value)
                break

        flutil.FLUtil.destroyProgressDialog()
        flutil.FLUtil.writeSettingEntry(key, dir_modules)
        self.infoMsgBox(self.translate("Importación de módulos finalizada."))
        AQTimer.singleShot(0, self.reinit)  # type: ignore [arg-type] # noqa: F821

    def selectModsDialog(self, modified_files: List = []) -> "types.Array":
        """Select modules dialog."""

        dialog_ = dialog.Dialog()
        dialog_.okButtonText = self.translate("Aceptar")
        dialog_.cancelButtonText = self.translate("Cancelar")
        bgroup = QtWidgets.QGroupBox()
        bgroup.setTitle(self.translate("Seleccione módulos a importar"))
        dialog_.add(bgroup)
        res = types.Array()
        check_box = types.Array()

        for number, item in enumerate(modified_files):
            check_box[number] = QtWidgets.QCheckBox()

            check_box[number].text = item
            check_box[number].checked = True

        idx = 0
        if self.interactiveGUI() and dialog_.exec_():
            for number, item in enumerate(modified_files):
                if check_box[number].checked:
                    res[idx] = item
                    idx += 1

        return res

    def importModule(self, module_path: str) -> bool:
        """Import a module specified by name."""
        try:
            with open(module_path, "r", encoding="ISO8859-15") as file_module:
                content_module = file_module.read()
        except Exception:
            error = traceback.format_exc()
            self.errorMsgBox(utils_base.ustr(self.translate("Error leyendo fichero."), "\n", error))
            return False
        mod_folder = os.path.dirname(module_path)
        mod = None
        xml_module = QtXml.QDomDocument()
        if xml_module.setContent(content_module):
            node_module = xml_module.namedItem("MODULE")
            if not node_module:
                self.errorMsgBox(self.translate("Error en la carga del fichero xml .mod"))
                return False
            mod = {
                "id": (node_module.namedItem("name").toElement().text()),
                "alias": (self.trTagText(node_module.namedItem("alias").toElement().text())),
                "area": (node_module.namedItem("area").toElement().text()),
                "areaname": (self.trTagText(node_module.namedItem("areaname").toElement().text())),
                "version": (node_module.namedItem("version").toElement().text()),
            }
            if not self.registerArea(mod) or not self.registerModule(mod):
                self.errorMsgBox(
                    utils_base.ustr(self.translate("Error registrando el módulo"), " ", mod["id"])
                )
                return False

            for ext in [
                "*.xml",
                "*.ui",
                "*.qs",
                "*.py",
                "*.qry",
                "*.mtd",
                "*.kut",
                "*.ar",
                "*.jrxml",
                "*.svg",
                "*.ts",
            ]:
                if not self.importFiles(mod_folder, ext, mod["id"]):
                    return False

        else:
            self.errorMsgBox(self.translate("Error en la carga del fichero xml .mod"))
            return False

        return True

    def importFiles(self, dir_path_: str, ext: str, id_module_: str) -> bool:
        """Import files with a exension from a path."""
        ok_ = True
        util = flutil.FLUtil()
        list_files_ = util.findFiles(dir_path_, ext, False)
        util.createProgressDialog(self.translate("Importando"), len(list_files_))
        util.setProgress(1)

        for number, value in enumerate(list_files_):
            util.setLabelText(value)
            util.setProgress(number)
            if not self.importFile(value, id_module_):
                self.errorMsgBox(self.translate("Error al cargar :\n") + value)
                ok_ = False
                break

        util.destroyProgressDialog()
        return ok_

    def importFile(self, file_path_: str, id_module_: str) -> bool:
        """Import a file from a path."""
        file_ = types.File(file_path_)
        content = ""
        try:
            file_.open(types.File.ReadOnly)
            content = str(file_.read())
        except Exception:
            error = traceback.format_exc()
            self.errorMsgBox(utils_base.ustr(self.translate("Error leyendo fichero."), "\n", error))
            return False

        ok_ = True
        name: str = file_.name
        if (
            not flutil.FLUtil.isFLDefFile(content)
            and not name.endswith((".qs", ".py", ".ar", ".svg"))
        ) or name.endswith("untranslated.ts"):
            return ok_
        cur = pnsqlcursor.PNSqlCursor("flfiles")
        cur.select(utils_base.ustr("nombre = '%s'" % name))
        ba_ = qbytearray.QByteArray()
        ba_.string = content
        sha_count = ba_.sha1()
        copy_content = ""

        if cur.first():
            copy_content = cur.valueBuffer("contenido")
            cur.setModeAccess(aqsql.AQSql.Edit)
        else:
            cur.setModeAccess(aqsql.AQSql.Insert)

        if name.endswith(".ar"):
            if not self.importReportAr(file_path_, id_module_, content):
                return True

        cur.refreshBuffer()
        cur.setValueBuffer("nombre", name)
        cur.setValueBuffer("idmodulo", id_module_)
        cur.setValueBuffer("sha", sha_count)
        cur.setValueBuffer("contenido", content)
        ok_ = cur.commitBuffer()

        if ok_ and copy_content:
            date_ = str(types.Date())
            cur.setModeAccess(aqsql.AQSql.Insert)
            cur.refreshBuffer()
            cur.setValueBuffer("nombre", "%s%s" % (name, date_))
            cur.setValueBuffer("idmodulo", id_module_)
            cur.setValueBuffer("contenido", copy_content)
            ok_ = cur.commitBuffer()

        return ok_

    def importReportAr(self, file_path_: str, id_module_: str, content: str) -> bool:
        """Import a report file, convert and install."""

        from pineboolib.application.safeqsa import SafeQSA

        if (
            not self.isLoadedModule("flar2kut")
            or settings.SETTINGS.value("scripts/sys/conversionAr") != "true"
        ):
            return False

        content = self.toUnicode(content, "UTF-8")
        content = SafeQSA.root_module("flar2kut").iface.pub_ar2kut(content)
        file_path_ = utils_base.ustr(file_path_[0 : len(file_path_) - 3], ".kut")
        if content:
            local_encoding = settings.SETTINGS.value("scripts/sys/conversionArENC")
            if not local_encoding:
                local_encoding = "ISO-8859-15"
            content = self.fromUnicode(content, local_encoding)
            file_ = types.FileStatic()
            try:
                file_.write(file_path_, content)
            except Exception:
                error = traceback.format_exc()
                self.errorMsgBox(
                    utils_base.ustr(self.translate("Error escribiendo fichero."), "\n", error)
                )
                return False

            return self.importFile(file_path_, id_module_)

        return False

    def runTransaction(self, function: Callable, optional_params: Dict[str, Any]) -> Any:
        """Run a Transaction."""
        roll_back_: bool = False
        error_msg_: str = ""
        valor_: Any

        db_ = application.PROJECT.conn_manager.useConn("default")

        # Create Transaction.
        db_.transaction()
        db_._transaction_level += 1

        if self.interactiveGUI():
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)

        try:
            valor_ = function(optional_params)
            if "errorMsg" in optional_params:
                error_msg_ = optional_params["errorMsg"]

            if not valor_:
                roll_back_ = True

        except Exception:
            error = traceback.format_exc(limit=-6, chain=False)
            roll_back_ = True
            valor_ = False
            if error_msg_ == "":
                error_msg_ = self.translate("Error al ejecutar la función")
            raise Exception("%s: %s" % (error_msg_, error))

        db_._transaction_level -= 1

        if roll_back_:  # do RollBack
            if error_msg_ != "":
                self.warnMsgBox(error_msg_)

            db_.rollback()

        else:  # do Commit
            db_.commit()

        if self.interactiveGUI():
            aqs.AQS.Application_restoreOverrideCursor()

        return valor_

    @decorators.deprecated
    def qsaExceptions(self) -> None:
        """Return QSA exceptions found."""

        return
        # return application.PROJECT.conn_manager.qsaExceptions()

    def serverTime(self) -> str:
        """Return time from database."""
        conn = application.PROJECT.conn_manager.useConn("default")
        qry_result = conn.execute_query("SELECT current_time")
        result = ""
        if qry_result is not None:
            line = qry_result.fetchone()
            if line is not None:
                result = str(line[0])

        return result

    def localChanges(self) -> Dict[str, Any]:
        """Return xml with local changes."""
        ret = {}
        ret["size"] = 0
        str_xml_update = utils_db.quick_sql_select(
            "flupdates",
            "filesdef",
            "actual=%s"
            % application.PROJECT.conn_manager.default().formatValue("bool", True, False),
        )
        if not str_xml_update:
            return ret
        document_update = QtXml.QDomDocument()
        if not document_update.setContent(str_xml_update):
            self.errorMsgBox(
                self.translate("Error XML al intentar cargar la definición de los ficheros.")
            )
            return ret
        document_db = self.xmlFilesDefBd()

        return self.diffXmlFilesDef(document_db, document_update)

    @classmethod
    def interactiveGUI(cls) -> str:
        """Return interactiveGUI."""

        return application.PROJECT.conn_manager.mainConn().interactiveGUI()

    def getWidgetList(self, container: str, control_name: str) -> str:
        """Get widget list from a widget."""

        obj_class: Any = None
        if control_name == "FLFieldDB":

            obj_class = flfielddb.FLFieldDB
        elif control_name == "FLTableDB":

            obj_class = fltabledb.FLTableDB
        elif control_name == "Button":
            control_name = "QPushButton"

        if obj_class is None:
            obj_class = getattr(QtWidgets, control_name, None)

        if obj_class is None:
            raise Exception("obj_class is empty!")

        widget: Optional[Union["flformrecorddb.FLFormRecordDB", "flformdb.FLFormDB"]] = None
        action = None
        conn = application.PROJECT._conn_manager
        if conn is None:
            raise Exception("conn is empty!")

        if container[0:10] == "formRecord":
            action_ = container[10:]
            action = conn.manager().action(action_)
            if action.formRecord():
                widget = conn.managerModules().createFormRecord(action)
        elif container[0:10] == "formSearch":
            action_ = container[10:]
            action = conn.manager().action(action_)
            if action.form():
                widget = conn.managerModules().createForm(action)
        else:
            action_ = container[4:]
            action = conn.manager().action(action_)
            if action.form():
                widget = conn.managerModules().createForm(action)

        if widget is None:
            return ""

        object_list = widget.findChildren(obj_class)
        retorno_: str = ""
        for obj in object_list:
            name_ = obj.objectName()
            if name_ == "":
                continue

            if control_name == "FLFieldDB":
                field_table_ = cast(flfielddb.FLFieldDB, obj).tableName()
                if field_table_ and field_table_ != action.table():
                    continue
                retorno_ += "%s/%s*" % (name_, cast(flfielddb.FLFieldDB, obj).fieldName())
            elif control_name == "FLTableDB":
                retorno_ += "%s/%s*" % (name_, cast(fltabledb.FLTableDB, obj).tableName())
            elif control_name in ["QPushButton", "Button"]:
                if name_ in ["pushButtonDB", "pbAux", "qt_left_btn", "qt_right_btn"]:
                    continue
                retorno_ += "%s/%s*" % (name_, obj.objectName())
            else:
                if name_ in [
                    "textLabelDB",
                    "componentDB",
                    "tab_pages",
                    "editor",
                    "FrameFind",
                    "TextLabelSearch",
                    "TextLabelIn",
                    "lineEditSearch",
                    "in-combo",
                    "voidTable",
                ]:
                    continue
                if isinstance(obj, QtWidgets.QGroupBox):
                    retorno_ += "%s/%s*" % (name_, obj.title())
                else:
                    retorno_ += "%s/*" % (name_)

        return retorno_


class AbanQDbDumper(QtCore.QObject):
    """AbanqDbDumper class."""

    SEP_CSV = "\u00b6"
    db_: "iconnection.IConnection"
    _show_gui: bool
    _dir_base: str
    _file_name: str
    widget_: "QtWidgets.QDialog"
    _label_dir_base: "qlabel.QLabel"
    pushbutton_change_dir: "qpushbutton.QPushButton"
    _ted_log: "qtextedit.QTextEdit"
    pb_init_dump: "qpushbutton.QPushButton"
    state_: "types.Array"
    _fun_log: "Callable"
    proc_: "process.Process"

    def __init__(
        self,
        db_: Optional["iconnection.IConnection"] = None,
        dir_base: Optional[str] = None,
        show_gui: bool = True,
        fun_log: Optional[Callable] = None,
    ):
        """Inicialize."""

        super().__init__()

        self._fun_log = self.addLog if fun_log is None else fun_log  # type: ignore

        self.db_ = application.PROJECT.aq_app.db().mainConn() if db_ is None else db_
        self._show_gui = show_gui
        self._dir_base = types.Dir.home if dir_base is None else dir_base

        self._file_name = self.genFileName()
        self.encoding = sys.getdefaultencoding()
        self.state_ = types.Array()

    def init(self) -> None:
        """Inicialize dump dialog."""
        if self._show_gui:
            self.buildGui()
            self.widget_.exec()

    def buildGui(self) -> None:
        """Build a Dialog for database dump."""
        self.widget_ = QtWidgets.QDialog(application.PROJECT.main_window)
        self.widget_.setWindowTitle(SysType.translate("Copias de seguridad"))
        self.widget_.resize(800, 600)

        lay = qvboxlayout.QVBoxLayout(self.widget_)
        lay.setContentsMargins(6, 6, 6, 6)
        lay.setSpacing(6)

        frm = QtWidgets.QFrame(self.widget_)
        frm.setFrameShape(QtWidgets.QFrame.Shape.Box)
        frm.setLineWidth(1)
        frm.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)

        # lay_frame = qvboxlayout.QVBoxLayout(frm, 6, 6)
        lay_frame = qvboxlayout.QVBoxLayout(frm)
        lay_frame.setContentsMargins(6, 6, 6, 6)
        lay_frame.setSpacing(6)
        lbl = qlabel.QLabel(frm)
        lbl.setText(
            SysType.translate("Driver: %s")
            % (str(self.db_.driverNameToDriverAlias(self.db_.driverName())))
        )
        lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        lay_frame.addWidget(lbl)
        lbl = qlabel.QLabel(frm)
        lbl.setText(SysType.translate("Base de datos: %s") % (str(self.db_.database())))
        lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        lay_frame.addWidget(lbl)
        lbl = qlabel.QLabel(frm)
        lbl.setText(SysType.translate("Host: %s") % (str(self.db_.host())))
        lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        lay_frame.addWidget(lbl)
        lbl = qlabel.QLabel(frm)
        lbl.setText(SysType.translate("Puerto: %s") % (str(self.db_.port())))
        lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        lay_frame.addWidget(lbl)
        lbl = qlabel.QLabel(frm)
        lbl.setText(SysType.translate("Usuario: %s") % (str(self.db_.user())))
        lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        lay_frame.addWidget(lbl)
        lay_aux = qhboxlayout.QHBoxLayout()
        lay_frame.addLayout(lay_aux)
        self._label_dir_base = qlabel.QLabel(frm)
        self._label_dir_base.setText(
            SysType.translate("Directorio Destino: %s") % (str(self._dir_base))
        )
        self._label_dir_base.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
        lay_aux.addWidget(self._label_dir_base)
        self.pushbutton_change_dir = qpushbutton.QPushButton(SysType.translate("Cambiar"))
        self.pushbutton_change_dir.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Preferred
        )

        self.pushbutton_change_dir.clicked.connect(  # type: ignore [attr-defined]
            self.changeDirBase
        )
        lay_aux.addWidget(self.pushbutton_change_dir)
        lay.addWidget(frm)
        self.pb_init_dump = qpushbutton.QPushButton(SysType.translate("INICIAR COPIA"))
        self.pb_init_dump.clicked.connect(self.initDump)  # type: ignore [attr-defined]
        lay.addWidget(self.pb_init_dump)
        lbl = qlabel.QLabel(self.widget_)
        lbl.setText("Log:")
        lay.addWidget(lbl)
        self._ted_log = qtextedit.QTextEdit(self.widget_)
        self._ted_log.setTextFormat(qtextedit.QTextEdit.LogText)
        self._ted_log.setAlignment(
            cast(
                QtCore.Qt.AlignmentFlag,
                QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter,
            )
        )
        lay.addWidget(self._ted_log)

    def initDump(self) -> None:
        """Inicialize dump."""

        gui = self._show_gui and self.widget_ is not None
        if gui:
            self.widget_.setEnabled(False)
        self.dumpDatabase()
        if gui:
            self.widget_.setEnabled(True)
            SysType.infoMsgBox(self.state_.msg)
            if self.state_.ok:
                self.widget_.close()

    def genFileName(self) -> str:
        """Return a file name."""
        now = types.Date()
        time_stamp = str(now)
        reg_exp = ["-", ":"]
        # reg_exp.global_ = True
        for item in reg_exp:
            time_stamp = time_stamp.replace(item, "")

        file_name = "%s/dump_%s_%s" % (self._dir_base, self.db_.database(), time_stamp)
        file_name = types.Dir.cleanDirPath(file_name)
        file_name = types.Dir.convertSeparators(file_name)
        return file_name

    def changeDirBase(self, dir_: Optional[str] = None) -> None:
        """Change base dir."""

        dir_base_path = dir_
        if not dir_base_path:
            dir_base_path = filedialog.FileDialog.getExistingDirectory(self._dir_base)
            if not dir_base_path:
                return
        self._dir_base = dir_base_path
        if self._show_gui and self._label_dir_base is not None:
            self._label_dir_base.setText(
                SysType.translate("Directorio Destino: %s") % (str(self._dir_base))
            )
        self._file_name = self.genFileName()

    def addLog(self, msg: str) -> None:
        """Add a text to log."""

        if self._show_gui and self._ted_log is not None:
            self._ted_log.append(msg)
        else:
            LOGGER.warning(msg)

    def setState(self, ok_: int, msg: str) -> None:
        """Set state."""

        self.state_.ok = ok_
        self.state_.msg = msg

    def state(self) -> types.Array:
        """Return state."""

        return self.state_

    def launchProc(self, command: List[str]) -> str:
        """Return the result from a Launched command."""
        self.proc_ = process.Process()
        self.proc_.setProgram(command[0])
        self.proc_.setArguments(command[1:])

        self.proc_.readyReadStandardOutput.connect(self.readFromStdout)  # type: ignore [attr-defined]
        self.proc_.readyReadStandardError.connect(self.readFromStdout)  # type: ignore [attr-defined]

        self.proc_.start(QtCore.QIODeviceBase.OpenModeFlag.ReadOnly)

        while self.proc_.running:
            SysType.processEvents()

        return self.proc_.exitcode() == self.proc_.ExitStatus.NormalExit.value

    def readFromStdout(self) -> None:
        """Read data from stdOutput."""
        while self.proc_.canReadLine():
            text = self.proc_.readLine().decode(self.encoding)
            if text not in (None, ""):
                self._fun_log(text)

    def dumpDatabase(self) -> bool:
        """Dump database to target specified by sql driver class."""

        driver = self.db_.driverName()
        type_db = 0
        if driver.find("PSQL") > -1:
            type_db = 1
        elif driver.find("MYSQL") > -1:
            type_db = 2

        if type_db == 0:
            self.setState(
                False,
                SysType.translate("Este tipo de base de datos no soporta el volcado a disco."),
            )
            self._fun_log(self.state_.msg)
            self.dumpAllTablesToCsv()
            return False
        file = types.File(self._file_name)  # noqa
        try:
            if not os.path.exists(self._file_name):
                dir_ = types.Dir(self._file_name)  # noqa

        except Exception:
            error = traceback.format_exc()
            self.setState(False, utils_base.ustr("", error))
            self._fun_log(self.state_.msg)
            return False

        ok_ = True
        if type_db == 1:
            ok_ = self.dumpPostgreSQL()

        if type_db == 2:
            ok_ = self.dumpMySQL()

        if not ok_:
            self.dumpAllTablesToCsv()
        if not ok_:
            self.setState(
                False, SysType.translate("No se ha podido realizar la copia de seguridad.")
            )
            self._fun_log(self.state_.msg)
        else:
            self.setState(
                True,
                SysType.translate("Copia de seguridad realizada con éxito en:\n%s.sql")
                % (str(self._file_name)),
            )
            self._fun_log(self.state_.msg)

        return ok_

    def dumpPostgreSQL(self) -> bool:
        """Dump database to PostgreSql file."""

        from pineboolib.core import system as system_mod

        pg_dump: str = "pg_dump"
        command: List[str] = []
        file_name = "%s.sql" % self._file_name

        system_mod.System.setenv("PGPASSWORD", self.db_.returnword())

        if SysType.osName() == "WIN32":
            pg_dump += ".exe"

        command = [
            pg_dump,
            "-f",
            file_name,
            "-h",
            self.db_.host(),
            "-p",
            str(self.db_.port()),
            "-U",
            self.db_.user(),
            self.db_.database().DBName(),
        ]

        if not self.launchProc(command):
            self.setState(
                False,
                SysType.translate("No se ha podido volcar la base de datos a disco.\n")
                + SysType.translate("Es posible que no tenga instalada la herramienta ")
                + pg_dump,
            )
            self._fun_log(self.state_.msg)
            return False
        self.setState(True, "")
        return True

    def dumpMySQL(self) -> bool:
        """Dump database to MySql file."""

        my_dump: str = "mysqldump"
        command: List[str]
        file_name = utils_base.ustr(self._file_name, ".sql")

        if SysType.osName() == "WIN32":
            my_dump += ".exe"
        command = [
            my_dump,
            "-v",
            utils_base.ustr("--result-file=", file_name),
            utils_base.ustr("--host=", self.db_.host()),
            utils_base.ustr("--port=", self.db_.port()),
            utils_base.ustr("--password=", self.db_.returnword()),
            utils_base.ustr("--user=", self.db_.user()),
            str(self.db_.database()),
        ]

        if not self.launchProc(command):
            self.setState(
                False,
                SysType.translate("No se ha podido volcar la base de datos a disco.\n")
                + SysType.translate("Es posible que no tenga instalada la herramienta ")
                + my_dump,
            )
            self._fun_log(self.state_.msg)
            return False
        self.setState(True, "")
        return True

    def dumpTableToCsv(self, table: str, dir_base: str) -> bool:
        """Dump a table to a CSV."""

        file_name = utils_base.ustr(dir_base, table, ".csv")
        file_ = types.File(file_name)
        if not file_.open(types.File.WriteOnly):
            return False
        ts_ = QtCore.QTextStream(file_.ioDevice())
        # ts_.setCodec(aqs.AQS.TextCodec_codecForName(u"utf8"))
        qry = pnsqlquery.PNSqlQuery()
        qry.setSelect(utils_base.ustr(table, ".*"))
        qry.setFrom(table)
        if not qry.exec_():
            return False

        rec = str("%s" % self.SEP_CSV).join(qry.fieldList())

        ts_.device().write(utils_base.ustr(rec, "\n").encode())
        # ts.opIn(utils_base.ustr(rec, u"\n"))
        flutil.FLUtil.createProgressDialog(
            SysType.translate("Haciendo copia en CSV de ") + table, qry.size()
        )
        pos = 0
        while qry.next():
            values = []
            for field_name in qry.fieldList():
                values.append(str(qry.value(field_name)))

            rec = str("%s" % self.SEP_CSV).join(values)

            ts_.device().write(utils_base.ustr(rec, "\n").encode())
            pos += 1
            flutil.FLUtil.setProgress(pos)

        file_.close()
        flutil.FLUtil.destroyProgressDialog()
        return True

    def dumpAllTablesToCsv(self) -> bool:
        """Dump all tables to a csv files."""
        tables = self.db_.tables(aqsql.AQSql.TableType.Tables)
        dir_ = types.Dir(self._file_name)
        dir_.mkdir()
        dir_base = types.Dir.convertSeparators(utils_base.ustr(self._file_name, "/"))
        # i = 0
        # while_pass = True
        for table_ in tables:
            self.dumpTableToCsv(table_, dir_base)
        return True
