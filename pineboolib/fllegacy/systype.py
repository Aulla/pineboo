"""Systype module."""

import traceback
import os
import os.path
import sys
import re


from PyQt5 import QtCore, QtWidgets, QtGui, QtXml


from pineboolib.core.system import System
from pineboolib.core.utils import utils_base, logging

from pineboolib.core import settings, decorators

from pineboolib import application
from pineboolib.application import types, process

from pineboolib.application.database import pnsqlcursor, pnsqlquery
from pineboolib.application.database import utils as utils_db

from pineboolib.application.packager import pnunpacker
from pineboolib.application.qsatypes import sysbasetype


from .aqsobjects.aqs import AQS
from .aqsobjects import aqsql

from . import flutil
from . import flvar

from pineboolib.q3widgets.dialog import Dialog
from pineboolib.q3widgets.qbytearray import QByteArray
from pineboolib.q3widgets.messagebox import MessageBox
from pineboolib.q3widgets.qtextedit import QTextEdit
from pineboolib.q3widgets.qlabel import QLabel
from pineboolib.q3widgets.qdialog import QDialog
from pineboolib.q3widgets.qvboxlayout import QVBoxLayout
from pineboolib.q3widgets.qhboxlayout import QHBoxLayout
from pineboolib.q3widgets.qpushbutton import QPushButton
from pineboolib.q3widgets.filedialog import FileDialog

from typing import cast, Optional, List, Any, Dict, Callable, Union, TYPE_CHECKING
from pineboolib.fllegacy import flfielddb, fltabledb

if TYPE_CHECKING:
    from pineboolib.interfaces import iconnection, isqlcursor  # pragma: no cover
    from pineboolib.fllegacy import flformrecorddb, flformdb  # noqa: F401 # pragma: no cover


LOGGER = logging.get_logger(__name__)


class AQTimer(QtCore.QTimer):
    """AQTimer class."""

    pass


class AQGlobalFunctionsClass(QtCore.QObject):
    """AQSGlobalFunction class."""

    functions_ = types.Array()
    mappers_: QtCore.QSignalMapper

    def __init__(self):
        """Initialize."""

        super().__init__()
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

    def mapConnect(self, obj: QtWidgets.QWidget, signal: str, function_name: str) -> None:
        """Add conection to map."""

        self.mappers_.mapped[str].connect(self.exec_)  # type: ignore
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

        from pineboolib.core import translate

        group = args[0] if len(args) == 2 else "scripts"
        text = args[1] if len(args) == 2 else args[0]

        if text == "MetaData":
            group, text = text, group

        text = text.replace(" % ", " %% ")

        return translate.translate(group, text)

    def printTextEdit(self, editor: QtWidgets.QTextEdit):
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

    def toPixmap(self, value_: str) -> QtGui.QPixmap:
        """Create a QPixmap from a text."""

        return application.PROJECT.aq_app.toPixmap(value_)

    def setMultiLang(self, enable_: bool, lang_id_: str) -> None:
        """
        Change multilang status.

        @param enable, Boolean con el nuevo estado
        @param langid, Identificador del leguaje a activar
        """

        return application.PROJECT.aq_app.setMultiLang(enable_, lang_id_)

    def fromPixmap(self, pix_: QtGui.QPixmap) -> str:
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
        self, pix_: QtGui.QPixmap, width_: int, height_: int, mode_: QtCore.Qt.AspectRatioMode
    ) -> QtGui.QImage:
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
            QtWidgets.QApplication.processEvents()

        application.PROJECT.aq_app.reinit()

    @classmethod
    def modMainWidget(cls, id_module_: str) -> Optional[QtWidgets.QWidget]:
        """Set module MainWinget."""

        return application.PROJECT.aq_app.modMainWidget(id_module_)

    @classmethod
    def setCaptionMainWidget(cls, title: str) -> None:
        """Set caption in the main widget."""

        application.PROJECT.aq_app.setCaptionMainWidget(title)

    @staticmethod
    def execQSA(qsa_file=None, args=None) -> Any:
        """Execute a QS file."""
        from pineboolib.application import types

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
    def mvProjectXml(cls) -> QtXml.QDomDocument:
        """Extract a module defition to a QDomDocument."""

        doc_ret_ = QtXml.QDomDocument()
        str_xml_ = utils_db.sql_select(u"flupdates", u"modulesdef", "actual")
        if not str_xml_:
            return doc_ret_
        doc = QtXml.QDomDocument()
        if not doc.setContent(str_xml_):
            return doc_ret_
        str_xml_ = u""
        nodes = doc.childNodes()

        for number in range(len(nodes)):
            it_ = nodes.item(number)
            if it_.isComment():
                data = it_.toComment().data()
                if not data == "" and data.startswith(u"<mvproject "):
                    str_xml_ = data
                    break

        if str_xml_ == "":
            return doc_ret_
        doc_ret_.setContent(str_xml_)
        return doc_ret_

    @classmethod
    def mvProjectModules(cls) -> types.Array:
        """Return modules defitions Dict."""
        ret = types.Array()
        doc = cls.mvProjectXml()
        mods = doc.elementsByTagName(u"module")
        for number in range(len(mods)):
            it_ = mods.item(number).toElement()
            mod = {"name": (it_.attribute(u"name")), "version": (it_.attribute(u"version"))}
            if len(mod["name"]) == 0:
                continue
            ret[mod["name"]] = mod

        return ret

    @classmethod
    def mvProjectExtensions(cls) -> types.Array:
        """Return project extensions Dict."""

        ret = types.Array()
        doc = cls.mvProjectXml()
        exts = doc.elementsByTagName(u"extension")

        for number in range(len(exts)):
            it_ = exts.item(number).toElement()
            ext = {"name": (it_.attribute(u"name")), "version": (it_.attribute(u"version"))}
            if len(ext["name"]) == 0:
                continue
            ret[ext["name"]] = ext

        return ret

    @classmethod
    def calculateShaGlobal(cls) -> str:
        """Return sha global value."""

        value = ""
        qry = pnsqlquery.PNSqlQuery()
        qry.setSelect(u"sha")
        qry.setFrom(u"flfiles")
        if qry.exec_() and qry.first():
            value = utils_base.sha1(str(qry.value(0)))
            while qry.next():
                value = utils_base.sha1(value + str(qry.value(0)))
        else:
            value = utils_base.sha1("")

        return value

    def registerUpdate(self, input_: Any = None) -> None:
        """Install a package."""

        if not input_:
            return
        unpacker = pnunpacker.PNUnpacker(input_)
        errors = unpacker.errorMessages()
        if len(errors) != 0:
            msg = self.translate(u"Hubo los siguientes errores al intentar cargar los módulos:")
            msg += u"\n"
            for number in range(len(errors)):
                msg += utils_base.ustr(errors[number], u"\n")

            self.errorMsgBox(msg)
            return

        unpacker.jump()
        unpacker.jump()
        unpacker.jump()
        now = str(types.Date())
        file_ = types.File(input_)
        file_name = file_.name
        modules_def = self.toUnicode(unpacker.getText(), u"utf8")
        files_def = self.toUnicode(unpacker.getText(), u"utf8")
        sha_global = self.calculateShaGlobal()
        aqsql.AQSql.update(u"flupdates", [u"actual"], [False], "1=1")
        aqsql.AQSql.insert(
            u"flupdates",
            [u"fecha", u"hora", u"nombre", u"modulesdef", u"filesdef", u"shaglobal"],
            [
                now[: now.find("T")],
                str(now)[(len(str(now)) - (8)) :],
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
        diag = QDialog()
        diag.caption = self.translate(u"Detectados cambios locales")
        diag.setModal(True)
        txt = u""
        txt += self.translate(u"¡¡ CUIDADO !! DETECTADOS CAMBIOS LOCALES\n\n")
        txt += self.translate(u"Se han detectado cambios locales en los módulos desde\n")
        txt += self.translate(u"la última actualización/instalación de un paquete de módulos.\n")
        txt += self.translate(u"Si continua es posible que estos cambios sean sobreescritos por\n")
        txt += self.translate(u"los cambios que incluye el paquete que quiere cargar.\n\n")
        txt += u"\n\n"
        txt += self.translate(u"Registro de cambios")
        lay = QVBoxLayout(diag)
        # lay.setMargin(6)
        # lay.setSpacing(6)
        lbl = QLabel(diag)
        lbl.setText(txt)
        lbl.setAlignment(cast(QtCore.Qt.Alignment, QtCore.Qt.AlignTop))
        lay.addWidget(lbl)
        ted = QTextEdit(diag)
        ted.setTextFormat(QTextEdit.LogText)
        ted.setAlignment(cast(QtCore.Qt.Alignment, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter))
        ted.append(self.reportChanges(changes))
        lay.addWidget(ted)
        lbl2 = QLabel(diag)
        lbl2.setText(self.translate("¿Que desea hacer?"))
        lbl2.setAlignment(cast(QtCore.Qt.Alignment, QtCore.Qt.AlignTop))
        lay.addWidget(lbl2)
        lay2 = QHBoxLayout()
        # lay2.setMargin(6)
        # lay2.setSpacing(6)
        lay.addLayout(lay2)
        push_button_cancel = QPushButton(diag)
        push_button_cancel.setText(self.translate(u"Cancelar"))
        push_button_accept = QPushButton(diag)
        push_button_accept.setText(self.translate(u"continue"))
        lay2.addWidget(push_button_cancel)
        lay2.addWidget(push_button_accept)
        application.connections.connect(push_button_accept, "clicked()", diag, "accept()")
        application.connections.connect(push_button_cancel, "clicked()", diag, "reject()")
        if not application.PROJECT.app.platformName() != "offscreen":
            return False if (diag.exec_() == 0) else True
        else:
            return True

    def xmlFilesDefBd(self) -> QtXml.QDomDocument:
        """Return a QDomDocument with files definition."""

        doc = QtXml.QDomDocument(u"files_def")
        root = doc.createElement(u"files")
        doc.appendChild(root)
        qry = pnsqlquery.PNSqlQuery()
        qry.setSelect(u"idmodulo,nombre,contenido")
        qry.setFrom(u"flfiles")
        if not qry.exec_():
            return doc
        sha_sum = u""
        sha_sum_txt = u""
        sha_sum_bin = u""
        while qry.next():
            id_module = str(qry.value(0))
            if id_module == u"sys":
                continue
            file_name = str(qry.value(1))
            ba_ = QByteArray()
            ba_.string = self.fromUnicode(str(qry.value(2)), u"iso-8859-15")
            sha = ba_.sha1()
            node_file = doc.createElement(u"file")
            root.appendChild(node_file)
            node = doc.createElement(u"module")
            node_file.appendChild(node)
            node_text = doc.createTextNode(id_module)
            node.appendChild(node_text)
            node = doc.createElement(u"name")
            node_file.appendChild(node)
            node_text = doc.createTextNode(file_name)
            node.appendChild(node_text)
            if self.textPacking(file_name):
                node = doc.createElement(u"text")
                node_file.appendChild(node)
                node_text = doc.createTextNode(file_name)
                node.appendChild(node_text)
                node = doc.createElement(u"shatext")
                node_file.appendChild(node)
                node_text = doc.createTextNode(sha)
                node.appendChild(node_text)
                ba_ = QByteArray()
                ba_.string = sha_sum + sha
                sha_sum = ba_.sha1()
                ba_ = QByteArray()
                ba_.string = sha_sum_txt + sha
                sha_sum_txt = ba_.sha1()

        qry = pnsqlquery.PNSqlQuery()
        qry.setSelect(u"idmodulo,icono")
        qry.setFrom(u"flmodules")
        if qry.exec_():
            while qry.next():
                id_module = str(qry.value(0))
                if id_module == u"sys":
                    continue
                file_name = utils_base.ustr(id_module, u".xpm")
                ba_ = QByteArray()
                ba_.string = str(qry.value(1))
                sha = ba_.sha1()
                node_file = doc.createElement(u"file")
                root.appendChild(node_file)
                node = doc.createElement(u"module")
                node_file.appendChild(node)
                node_text = doc.createTextNode(id_module)
                node.appendChild(node_text)
                node = doc.createElement(u"name")
                node_file.appendChild(node)
                node_text = doc.createTextNode(file_name)
                node.appendChild(node_text)
                if self.textPacking(file_name):
                    node = doc.createElement(u"text")
                    node_file.appendChild(node)
                    node_text = doc.createTextNode(file_name)
                    node.appendChild(node_text)
                    node = doc.createElement(u"shatext")
                    node_file.appendChild(node)
                    node_text = doc.createTextNode(sha)
                    node.appendChild(node_text)
                    ba_ = QByteArray()
                    ba_.string = sha_sum + sha
                    sha_sum = ba_.sha1()
                    ba_ = QByteArray()
                    ba_.string = sha_sum_txt + sha
                    sha_sum_txt = ba_.sha1()

        node = doc.createElement(u"shasum")
        node.appendChild(doc.createTextNode(sha_sum))
        root.appendChild(node)
        node = doc.createElement(u"shasumtxt")
        node.appendChild(doc.createTextNode(sha_sum_txt))
        root.appendChild(node)
        node = doc.createElement(u"shasumbin")
        node.appendChild(doc.createTextNode(sha_sum_bin))
        root.appendChild(node)
        return doc

    def loadModules(self, input_: Optional[Any] = None, warning_bakup: bool = True) -> bool:
        """Load modules from a package."""
        ret_ = False

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
                self.translate(u"scripts", u"Seleccionar Eneboo/Abanq Package"),
                last_path,
                "Eneboo Package (*.eneboopkg);;Abanq Package (*.abanq)",
            )
            input_ = path_tuple[0]
            if input_:
                util.writeSettingEntry(setting, os.path.dirname(input_))

        if input_:

            ret_ = self.loadAbanQPackage(input_, warning_bakup)

        return ret_

    def loadAbanQPackage(self, input_: str, warning_bakup: bool = True) -> bool:
        """Load and process a Abanq/Eneboo package."""
        ok_ = False

        txt = u""
        txt += self.translate(u"Asegúrese de tener una copia de seguridad de todos los datos\n")
        txt += self.translate(u"y de que  no hay ningun otro  usuario conectado a la base de\n")
        txt += self.translate(u"datos mientras se realiza la carga.\n\n")
        txt += u"\n\n"
        txt += self.translate(u"¿Desea continuar?")

        if warning_bakup and self.interactiveGUI():
            if MessageBox.Yes != MessageBox.warning(txt, MessageBox.No, MessageBox.Yes):
                return False

        if input_:
            ok_ = True
            changes = self.localChanges()
            if changes["size"] != 0:
                if not self.warnLocalChanges(changes):
                    return False
            if ok_:
                unpacker = pnunpacker.PNUnpacker(input_)
                errors = unpacker.errorMessages()
                if len(errors) != 0:
                    msg = self.translate(
                        u"Hubo los siguientes errores al intentar cargar los módulos:"
                    )
                    msg += u"\n"

                    for number in range(len(errors)):
                        msg += utils_base.ustr(errors[number], u"\n")
                    self.errorMsgBox(msg)
                    ok_ = False

                unpacker.jump()
                unpacker.jump()
                unpacker.jump()
                if ok_:
                    ok_ = self.loadModulesDef(unpacker)
                if ok_:
                    ok_ = self.loadFilesDef(unpacker)

            if not ok_:
                self.errorMsgBox(
                    self.translate(u"No se ha podido realizar la carga de los módulos.")
                )
            else:
                self.registerUpdate(input_)
                self.infoMsgBox(self.translate(u"La carga de módulos se ha realizado con éxito."))
                self.reinit()

                tmp_var = flvar.FLVar()
                tmp_var.set(u"mrproper", u"dirty")

        return ok_

    def loadFilesDef(self, document: Any) -> bool:
        """Load files definition from a package to a QDomDocument."""

        files_definition = self.toUnicode(document.getText(), u"utf8")
        doc = QtXml.QDomDocument()
        if not doc.setContent(files_definition):
            self.errorMsgBox(
                self.translate(u"Error XML al intentar cargar la definición de los ficheros.")
            )
            return False
        ok_ = True
        root = doc.firstChild()
        files = root.childNodes()
        flutil.FLUtil.createProgressDialog(self.translate(u"Registrando ficheros"), len(files))

        for number in range(len(files)):

            it_ = files.item(number)
            fil = {
                "id": it_.namedItem(u"name").toElement().text(),
                "skip": it_.namedItem(u"skip").toElement().text(),
                "module": it_.namedItem(u"module").toElement().text(),
                "text": it_.namedItem(u"text").toElement().text(),
                "shatext": it_.namedItem(u"shatext").toElement().text(),
                "binary": it_.namedItem(u"binary").toElement().text(),
                "shabinary": it_.namedItem(u"shabinary").toElement().text(),
            }
            flutil.FLUtil.setProgress(number)
            flutil.FLUtil.setLabelText(
                utils_base.ustr(self.translate(u"Registrando fichero"), u" ", fil["id"])
            )
            if len(fil["id"]) == 0 or fil["skip"] == u"true":
                continue
            if not self.registerFile(fil, document):
                self.errorMsgBox(
                    utils_base.ustr(
                        self.translate(u"Error registrando el fichero"), u" ", fil["id"]
                    )
                )
                ok_ = False
                break

        flutil.FLUtil.destroyProgressDialog()
        return ok_

    def registerFile(self, fil: Dict[str, Any], document: Any) -> bool:
        """Register a file in the database."""

        if fil["id"].endswith(u".xpm"):
            cur = pnsqlcursor.PNSqlCursor(u"flmodules")
            if not cur.select(utils_base.ustr(u"idmodulo='", fil["module"], u"'")):
                return False
            if not cur.first():
                return False
            cur.setModeAccess(aqsql.AQSql.Edit)
            cur.refreshBuffer()
            cur.setValueBuffer(u"icono", document.getText())
            return cur.commitBuffer()

        cur = pnsqlcursor.PNSqlCursor(u"flfiles")
        if not cur.select(utils_base.ustr(u"nombre='", fil["id"], u"'")):
            return False
        cur.setModeAccess((aqsql.AQSql.Edit if cur.first() else aqsql.AQSql.Insert))
        cur.refreshBuffer()
        cur.setValueBuffer(u"nombre", fil["id"])
        cur.setValueBuffer(u"idmodulo", fil["module"])
        cur.setValueBuffer(u"sha", fil["shatext"])
        if len(fil["text"]) > 0:
            encode = "iso-8859-15" if not fil["id"].endswith((".py")) else "UTF-8"
            try:
                if not fil["id"].endswith((".py")):
                    cur.setValueBuffer(u"contenido", self.toUnicode(document.getText(), encode))
                else:
                    cur.setValueBuffer(u"contenido", document.getText())
            except UnicodeEncodeError as error:
                LOGGER.error("The %s file does not have the correct encode (%s)", fil["id"], encode)
                raise error

        if len(fil["binary"]) > 0:
            document.getBinary()
        return cur.commitBuffer()

    def checkProjectName(self, project_name: str) -> bool:
        """Return if te project name is valid."""
        if not project_name:
            project_name = u""
        db_project_name = flutil.FLUtil.readDBSettingEntry(u"projectname") or ""

        txt = u""
        txt += self.translate(u"¡¡ CUIDADO !! POSIBLE INCOHERENCIA EN LOS MÓDULOS\n\n")
        txt += self.translate(u"Está intentando cargar un proyecto o rama de módulos cuyo\n")
        txt += self.translate(u"nombre difiere del instalado actualmente en la base de datos.\n")
        txt += self.translate(u"Es posible que la estructura de los módulos que quiere cargar\n")
        txt += self.translate(
            u"sea completamente distinta a la instalada actualmente, y si continua\n"
        )
        txt += self.translate(
            u"podría dañar el código, datos y la estructura de tablas de Eneboo.\n\n"
        )

        if project_name == db_project_name:
            return True

        if project_name and not db_project_name:
            return flutil.FLUtil.writeDBSettingEntry(u"projectname", project_name)

        txt += self.translate(u"- Nombre del proyecto instalado: %s\n") % (str(db_project_name))
        txt += self.translate(u"- Nombre del proyecto a cargar: %s\n\n") % (str(project_name))
        txt += u"\n\n"

        if not self.interactiveGUI():
            LOGGER.warning(txt)
            return False
        txt += self.translate(u"¿Desea continuar?")
        return MessageBox.Yes == MessageBox.warning(
            txt, MessageBox.No, MessageBox.Yes, MessageBox.NoButton, u"Pineboo"
        )

    def loadModulesDef(self, document: Any) -> bool:
        """Return QDomDocument with modules definition."""

        modules_definition = self.toUnicode(document.getText(), u"utf8")
        doc = QtXml.QDomDocument()
        if not doc.setContent(modules_definition):
            self.errorMsgBox(
                self.translate(u"Error XML al intentar cargar la definición de los módulos.")
            )
            return False
        root = doc.firstChild()
        if not self.checkProjectName(root.toElement().attribute(u"projectname", u"")):
            return False
        ok_ = True
        modules = root.childNodes()
        flutil.FLUtil.createProgressDialog(self.translate(u"Registrando módulos"), len(modules))
        for number in range(len(modules)):
            it_ = modules.item(number)
            mod = {
                "id": it_.namedItem(u"name").toElement().text(),
                "alias": self.trTagText(it_.namedItem(u"alias").toElement().text()),
                "area": it_.namedItem(u"area").toElement().text(),
                "areaname": self.trTagText(it_.namedItem(u"areaname").toElement().text()),
                "version": it_.namedItem(u"version").toElement().text(),
            }
            flutil.FLUtil.setProgress(number)
            flutil.FLUtil.setLabelText(
                utils_base.ustr(self.translate(u"Registrando módulo"), u" ", mod["id"])
            )
            if not self.registerArea(mod) or not self.registerModule(mod):
                self.errorMsgBox(
                    utils_base.ustr(self.translate(u"Error registrando el módulo"), u" ", mod["id"])
                )
                ok_ = False
                break

        flutil.FLUtil.destroyProgressDialog()
        return ok_

    def registerArea(self, modules: Dict[str, Any]) -> bool:
        """Return True if the area is created or False."""
        cur = pnsqlcursor.PNSqlCursor(u"flareas")
        if not cur.select(utils_base.ustr(u"idarea = '", modules["area"], u"'")):
            return False
        cur.setModeAccess((aqsql.AQSql.Edit if cur.first() else aqsql.AQSql.Insert))
        cur.refreshBuffer()
        cur.setValueBuffer(u"idarea", modules["area"])
        cur.setValueBuffer(u"descripcion", modules["areaname"])
        return cur.commitBuffer()

    def registerModule(self, modules: Dict[str, Any]) -> bool:
        """Return True if the module is created or False."""

        cur = pnsqlcursor.PNSqlCursor(u"flmodules")
        if not cur.select(utils_base.ustr(u"idmodulo='", modules["id"], u"'")):
            return False
        cur.setModeAccess((aqsql.AQSql.Edit if cur.first() else aqsql.AQSql.Insert))
        cur.refreshBuffer()
        cur.setValueBuffer(u"idmodulo", modules["id"])
        cur.setValueBuffer(u"idarea", modules["area"])
        cur.setValueBuffer(u"descripcion", modules["alias"])
        cur.setValueBuffer(u"version", modules["version"])
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

        key = u"QuestionMsgBox/"
        value_remember = False
        if key_remember:
            value_remember = settings.SETTINGS.value(key + key_remember)
            if value_remember and not force_show:
                return MessageBox.Yes
        if not self.interactiveGUI():
            return True
        diag = QDialog()
        diag.caption = txt_caption
        diag.setModal(True)
        lay = QVBoxLayout(diag)
        # lay.setMargin(6)
        lay.setSpacing(6)
        lay2 = QHBoxLayout(diag)
        # lay2.setMargin(6)
        lay2.setSpacing(6)
        label_pix = QLabel(diag)
        pixmap = AQS.pixmap_fromMimeSource(u"help_index.png")
        if pixmap:
            label_pix.setPixmap(pixmap)
            label_pix.setAlignment(AQS.AlignTop)
        lay2.addWidget(label_pix)
        lbl = QLabel(diag)
        lbl.setText(msg)
        lbl.setAlignment(cast(QtCore.Qt.Alignment, AQS.AlignTop | AQS.WordBreak))
        lay2.addWidget(lbl)
        lay3 = QHBoxLayout(diag)
        # lay3.setMargin(6)
        lay3.setSpacing(6)
        push_button_yes = QPushButton(diag)
        push_button_yes.setText(txt_yes if txt_yes else self.translate(u"Sí"))
        push_button_no = QPushButton(diag)
        push_button_no.setText(txt_no if txt_no else self.translate(u"No"))
        lay3.addWidget(push_button_yes)
        lay3.addWidget(push_button_no)
        application.connections.connect(push_button_yes, u"clicked()", diag, u"accept()")
        application.connections.connect(push_button_no, u"clicked()", diag, u"reject()")
        check_remember = None
        if key_remember and txt_remember:
            # from pineboolib.q3widgets.qcheckbox import QCheckBox

            check_remember = QtWidgets.QCheckBox(txt_remember, diag)
            check_remember.setChecked(value_remember)
            lay.addWidget(check_remember)

        if not application.PROJECT.app.platformName() == "offscreen":
            return MessageBox.Yes

        ret = MessageBox.No if (diag.exec_() == 0) else MessageBox.Yes
        if check_remember is not None:
            settings.SETTINGS.set_value(key + key_remember, check_remember.isChecked())
        return ret

    def exportModules(self) -> None:
        """Export modules."""

        dir_base_path = FileDialog.getExistingDirectory(types.Dir.home)
        if not dir_base_path:
            return
        data_base_name = application.PROJECT.conn_manager.mainConn()._db_name
        dir_base_path = types.Dir.cleanDirPath(
            utils_base.ustr(
                dir_base_path,
                u"/modulos_exportados_",
                data_base_name[data_base_name.rfind(u"/") + 1 :],
            )
        )
        dir_ = types.Dir()
        if not dir_.fileExists(dir_base_path):
            try:
                dir_.mkdir(dir_base_path)
            except Exception:
                error = traceback.format_exc()
                self.errorMsgBox(utils_base.ustr(u"", error))
                return

        else:
            self.warnMsgBox(
                dir_base_path + self.translate(u" ya existe,\ndebe borrarlo antes de continuar")
            )
            return

        qry = pnsqlquery.PNSqlQuery()
        qry.setSelect(u"idmodulo")
        qry.setFrom(u"flmodules")
        if not qry.exec_() or qry.size() == 0:
            return
        pos = 0
        flutil.FLUtil.createProgressDialog(self.translate(u"Exportando módulos"), qry.size() - 1)
        while qry.next():
            id_module = qry.value(0)
            if id_module == u"sys":
                continue
            flutil.FLUtil.setLabelText(id_module)
            pos += 1
            flutil.FLUtil.setProgress(pos)
            try:
                self.exportModule(id_module, dir_base_path)
            except Exception:
                error = traceback.format_exc()
                flutil.FLUtil.destroyProgressDialog()
                self.errorMsgBox(utils_base.ustr(u"", error))
                return

        db_project_name = flutil.FLUtil.readDBSettingEntry(u"projectname")
        if not db_project_name:
            db_project_name = u""
        if not db_project_name == "":
            doc = QtXml.QDomDocument()
            tag = doc.createElement(u"mvproject")
            tag.toElement().setAttribute(u"name", db_project_name)
            doc.appendChild(tag)
            try:
                types.FileStatic.write(
                    utils_base.ustr(dir_base_path, u"/mvproject.xml"), doc.toString(2)
                )
            except Exception:
                error = traceback.format_exc()
                flutil.FLUtil.destroyProgressDialog()
                self.errorMsgBox(utils_base.ustr(u"", error))
                return

        flutil.FLUtil.destroyProgressDialog()
        self.infoMsgBox(self.translate(u"Módulos exportados en:\n") + dir_base_path)

    def xmlModule(self, id_module: str) -> QtXml.QDomDocument:
        """Return xml data from a module."""
        qry = pnsqlquery.PNSqlQuery()
        qry.setSelect(u"descripcion,idarea,version")
        qry.setFrom(u"flmodules")
        qry.setWhere(utils_base.ustr(u"idmodulo='", id_module, u"'"))
        doc = QtXml.QDomDocument(u"MODULE")
        if not qry.exec_() or not qry.next():
            return doc

        tag_module = doc.createElement(u"MODULE")
        doc.appendChild(tag_module)
        tag = doc.createElement(u"name")
        tag.appendChild(doc.createTextNode(id_module))
        tag_module.appendChild(tag)
        translate_noop = u'QT_TRANSLATE_NOOP("Eneboo","%s")'
        tag = doc.createElement(u"alias")
        tag.appendChild(doc.createTextNode(translate_noop % qry.value(0)))
        tag_module.appendChild(tag)
        id_area = qry.value(1)
        tag = doc.createElement(u"area")
        tag.appendChild(doc.createTextNode(id_area))
        tag_module.appendChild(tag)
        area_name = utils_db.sql_select(
            u"flareas", u"descripcion", utils_base.ustr(u"idarea='", id_area, u"'")
        )
        tag = doc.createElement(u"areaname")
        tag.appendChild(doc.createTextNode(translate_noop % area_name))
        tag_module.appendChild(tag)
        tag = doc.createElement(u"entryclass")
        tag.appendChild(doc.createTextNode(id_module))
        tag_module.appendChild(tag)
        tag = doc.createElement(u"version")
        tag.appendChild(doc.createTextNode(qry.value(2)))
        tag_module.appendChild(tag)
        tag = doc.createElement(u"icon")
        tag.appendChild(doc.createTextNode(utils_base.ustr(id_module, u".xpm")))
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
        dir_path = types.Dir.cleanDirPath(utils_base.ustr(dir_base_path, u"/", id_module))
        if not dir_.fileExists(dir_path):
            dir_.mkdir(dir_path)
        for name in ["/forms", "/scripts", "/queries", "/tables", "/reports", "/translations"]:
            if not dir_.fileExists("%s%s" % (dir_path, name)):
                dir_.mkdir("%s%s" % (dir_path, name))
        xml_module = self.xmlModule(id_module)
        self.fileWriteIso(
            utils_base.ustr(dir_path, u"/", id_module, u".mod"), xml_module.toString(2)
        )
        xpm_module = utils_db.sql_select(
            u"flmodules", u"icono", utils_base.ustr(u"idmodulo='", id_module, u"'")
        )
        self.fileWriteIso(utils_base.ustr(dir_path, u"/", id_module, u".xpm"), xpm_module)
        qry = pnsqlquery.PNSqlQuery()
        qry.setSelect(u"nombre,contenido")
        qry.setFrom(u"flfiles")
        qry.setWhere(utils_base.ustr(u"idmodulo='", id_module, u"'"))
        if not qry.exec_() or qry.size() == 0:
            return
        while qry.next():
            name = qry.value(0)
            content = qry.value(1)
            type_ = name[(len(name) - (len(name) - name.rfind(u"."))) :]
            if type_ == ".xml":
                self.fileWriteIso(utils_base.ustr(dir_path, u"/", name), content)
            elif type_ == ".ui":
                self.fileWriteIso(utils_base.ustr(dir_path, u"/forms/", name), content)
            elif type_ == ".qs":
                self.fileWriteIso(utils_base.ustr(dir_path, u"/scripts/", name), content)
            elif type_ == ".qry":
                self.fileWriteIso(utils_base.ustr(dir_path, u"/queries/", name), content)
            elif type_ == ".mtd":
                self.fileWriteIso(utils_base.ustr(dir_path, u"/tables/", name), content)
            elif type_ in (".kut", ".ar", ".jrxml", ".svg"):
                self.fileWriteIso(utils_base.ustr(dir_path, u"/reports/", name), content)
            elif type_ == ".ts":
                self.fileWriteIso(utils_base.ustr(dir_path, u"/translations/", name), content)
            elif type_ == ".py":
                self.fileWriteUtf8(utils_base.ustr(dir_path, u"/scripts/", name), content)

    def importModules(self, warning_bakup: bool = True) -> None:
        """Import modules from a directory."""

        if warning_bakup and self.interactiveGUI():
            txt = u""
            txt += self.translate(u"Asegúrese de tener una copia de seguridad de todos los datos\n")
            txt += self.translate(u"y de que  no hay ningun otro  usuario conectado a la base de\n")
            txt += self.translate(u"datos mientras se realiza la importación.\n\n")
            txt += self.translate(u"Obtenga soporte en")
            txt += u" http://www.infosial.com\n(c) InfoSiAL S.L."
            txt += u"\n\n"
            txt += self.translate(u"¿Desea continuar?")
            if MessageBox.Yes != MessageBox.warning(txt, MessageBox.No, MessageBox.Yes):
                return

        key = utils_base.ustr(u"scripts/sys/modLastDirModules_", self.nameBD())
        dir_ant = settings.SETTINGS.value(key)

        dir_modules = FileDialog.getExistingDirectory(
            str(dir_ant) if dir_ant else ".", self.translate(u"Directorio de Módulos")
        )
        if not dir_modules:
            return
        dir_modules = types.Dir.cleanDirPath(dir_modules)
        dir_modules = types.Dir.convertSeparators(dir_modules)
        QtCore.QDir.setCurrent(dir_modules)  # change current directory
        modified_files = self.selectModsDialog(
            flutil.FLUtil.findFiles(dir_modules, u"*.mod", False)
        )
        flutil.FLUtil.createProgressDialog(self.translate(u"Importando"), len(modified_files))
        flutil.FLUtil.setProgress(1)

        for number, value in enumerate(modified_files):
            flutil.FLUtil.setLabelText(value)
            flutil.FLUtil.setProgress(number)
            if not self.importModule(value):
                self.errorMsgBox(self.translate(u"Error al cargar el módulo:\n") + value)
                break

        flutil.FLUtil.destroyProgressDialog()
        flutil.FLUtil.writeSettingEntry(key, dir_modules)
        self.infoMsgBox(self.translate(u"Importación de módulos finalizada."))
        AQTimer.singleShot(0, self.reinit)  # type: ignore [arg-type] # noqa: F821

    def selectModsDialog(self, modified_files: List = []) -> types.Array:
        """Select modules dialog."""

        dialog = Dialog()
        dialog.okButtonText = self.translate(u"Aceptar")
        dialog.cancelButtonText = self.translate(u"Cancelar")
        bgroup = QtWidgets.QGroupBox()
        bgroup.setTitle(self.translate(u"Seleccione módulos a importar"))
        dialog.add(bgroup)
        res = types.Array()
        check_box = types.Array()

        for number, item in enumerate(modified_files):
            check_box[number] = QtWidgets.QCheckBox()

            check_box[number].text = item
            check_box[number].checked = True

        idx = 0
        if self.interactiveGUI() and dialog.exec_():
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
            self.errorMsgBox(
                utils_base.ustr(self.translate(u"Error leyendo fichero."), u"\n", error)
            )
            return False
        mod_folder = os.path.dirname(module_path)
        mod = None
        xml_module = QtXml.QDomDocument()
        if xml_module.setContent(content_module):
            node_module = xml_module.namedItem(u"MODULE")
            if not node_module:
                self.errorMsgBox(self.translate(u"Error en la carga del fichero xml .mod"))
                return False
            mod = {
                "id": (node_module.namedItem(u"name").toElement().text()),
                "alias": (self.trTagText(node_module.namedItem(u"alias").toElement().text())),
                "area": (node_module.namedItem(u"area").toElement().text()),
                "areaname": (self.trTagText(node_module.namedItem(u"areaname").toElement().text())),
                "version": (node_module.namedItem(u"version").toElement().text()),
            }
            if not self.registerArea(mod) or not self.registerModule(mod):
                self.errorMsgBox(
                    utils_base.ustr(self.translate(u"Error registrando el módulo"), u" ", mod["id"])
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
            self.errorMsgBox(self.translate(u"Error en la carga del fichero xml .mod"))
            return False

        return True

    def importFiles(self, dir_path_: str, ext: str, id_module_: str) -> bool:
        """Import files with a exension from a path."""
        ok_ = True
        util = flutil.FLUtil()
        list_files_ = util.findFiles(dir_path_, ext, False)
        util.createProgressDialog(self.translate(u"Importando"), len(list_files_))
        util.setProgress(1)

        for number, value in enumerate(list_files_):
            util.setLabelText(value)
            util.setProgress(number)
            if not self.importFile(value, id_module_):
                self.errorMsgBox(self.translate(u"Error al cargar :\n") + value)
                ok_ = False
                break

        util.destroyProgressDialog()
        return ok_

    def importFile(self, file_path_: str, id_module_: str) -> bool:
        """Import a file from a path."""
        file_ = types.File(file_path_)
        content = u""
        try:
            file_.open(types.File.ReadOnly)  # type: ignore [arg-type]
            content = str(file_.read())
        except Exception:
            error = traceback.format_exc()
            self.errorMsgBox(
                utils_base.ustr(self.translate(u"Error leyendo fichero."), u"\n", error)
            )
            return False

        ok_ = True
        name = file_.name
        if (
            not flutil.FLUtil.isFLDefFile(content)
            and not name.endswith((".qs", ".py", ".ar", ".svg"))
        ) or name.endswith(u"untranslated.ts"):
            return ok_
        cur = pnsqlcursor.PNSqlCursor(u"flfiles")
        cur.select(utils_base.ustr(u"nombre = '", name, u"'"))
        ba_ = QByteArray()
        ba_.string = content

        if not cur.first():
            if name.endswith(u".ar"):
                if not self.importReportAr(file_path_, id_module_, content):
                    return True
            cur.setModeAccess(aqsql.AQSql.Insert)
            cur.refreshBuffer()
            cur.setValueBuffer(u"nombre", name)
            cur.setValueBuffer(u"idmodulo", id_module_)
            cur.setValueBuffer(u"sha", ba_.sha1())
            cur.setValueBuffer(u"contenido", content)
            ok_ = cur.commitBuffer()

        else:
            cur.setModeAccess(aqsql.AQSql.Edit)
            cur.refreshBuffer()

            sha_count = ba_.sha1()
            if cur.valueBuffer(u"sha") != sha_count:
                copy_content = cur.valueBuffer(u"contenido")
                cur.setModeAccess(aqsql.AQSql.Insert)
                cur.refreshBuffer()
                date_ = types.Date()
                cur.setValueBuffer(u"nombre", name + str(date_))
                cur.setValueBuffer(u"idmodulo", id_module_)
                cur.setValueBuffer(u"contenido", copy_content)
                cur.commitBuffer()
                cur.select(utils_base.ustr(u"nombre = '", name, u"'"))
                cur.first()
                cur.setModeAccess(aqsql.AQSql.Edit)
                cur.refreshBuffer()
                cur.setValueBuffer(u"idmodulo", id_module_)
                cur.setValueBuffer(u"sha", sha_count)
                cur.setValueBuffer(u"contenido", content)
                ok_ = cur.commitBuffer()
                if name.endswith(u".ar"):
                    if not self.importReportAr(file_path_, id_module_, content):
                        return True

        return ok_

    def importReportAr(self, file_path_: str, id_module_: str, content: str) -> bool:
        """Import a report file, convert and install."""

        from pineboolib.application.safeqsa import SafeQSA

        if not self.isLoadedModule(u"flar2kut"):
            return False
        if settings.SETTINGS.value(u"scripts/sys/conversionAr") != u"true":
            return False
        content = self.toUnicode(content, u"UTF-8")
        content = SafeQSA.root_module("flar2kut").iface.pub_ar2kut(content)
        file_path_ = utils_base.ustr(file_path_[0 : len(file_path_) - 3], u".kut")
        if content:
            local_encoding = settings.SETTINGS.value(u"scripts/sys/conversionArENC")
            if not local_encoding:
                local_encoding = u"ISO-8859-15"
            content = self.fromUnicode(content, local_encoding)
            file_ = types.FileStatic()
            try:
                file_.write(file_path_, content)
            except Exception:
                error = traceback.format_exc()
                self.errorMsgBox(
                    utils_base.ustr(self.translate(u"Error escribiendo fichero."), u"\n", error)
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
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

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
            AQS.Application_restoreOverrideCursor()

        return valor_

    def search_git_updates(self, url: str) -> None:
        """Search updates of pineboo."""

        if not os.path.exists(utils_base.filedir("../.git")):
            return

        if not url:
            url = settings.SETTINGS.value(
                "ebcomportamiento/git_updates_repo", "https://github.com/Aulla/pineboo.git"
            )

        command = "git status %s" % url

        pro = process.Process()
        pro.execute(command)
        if pro.stdout is None:
            return
        # print("***", pro.stdout)

        if pro.stdout.find("git pull") > -1:
            if MessageBox.Yes != MessageBox.warning(
                "Hay nuevas actualizaciones disponibles para Pineboo. ¿Desea actualizar?",
                MessageBox.No,
                MessageBox.Yes,
            ):
                return

            pro.execute("git pull %s" % url)

            MessageBox.information(
                "Pineboo se va a reiniciar ahora",
                MessageBox.Ok,
                MessageBox.NoButton,
                MessageBox.NoButton,
                u"Eneboo",
            )
            # os.execl(executable, os.path.abspath(__file__)) #FIXME

    def qsaExceptions(self):
        """Return QSA exceptions found."""

        return application.PROJECT.conn_manager.qsaExceptions()

    @decorators.not_implemented_warn
    def serverTime(self) -> str:
        """Return time from database."""

        # FIXME: QSqlSelectCursor is not defined. Was an internal of Qt3.3
        return ""
        # db = aqApp.db().db()
        # sql = u"select current_time"
        # ahora = None
        # q = QSqlSelectCursor(sql, db)
        # if q.isActive() and q.next():
        #     ahora = q.value(0)
        # return ahora

    def localChanges(self) -> Dict[str, Any]:
        """Return xml with local changes."""
        ret = {}
        ret[u"size"] = 0
        str_xml_update = utils_db.sql_select("flupdates", "filesdef", "actual='true'")
        if not str_xml_update:
            return ret
        document_update = QtXml.QDomDocument()
        if not document_update.setContent(str_xml_update):
            self.errorMsgBox(
                self.translate(u"Error XML al intentar cargar la definición de los ficheros.")
            )
            return ret
        document_db = self.xmlFilesDefBd()
        ret = self.diffXmlFilesDef(document_db, document_update)
        return ret

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

    SEP_CSV = u"\u00b6"
    db_: "iconnection.IConnection"
    _show_gui: bool
    _dir_base: str
    _file_name: str
    widget_: QDialog
    _label_dir_base: QLabel
    pushbutton_change_dir: QPushButton
    _ted_log: QTextEdit
    pb_init_dump: QPushButton
    state_: types.Array
    _fun_log: Callable
    proc_: process.Process

    def __init__(
        self,
        db_: Optional["iconnection.IConnection"] = None,
        dir_base: Optional[str] = None,
        show_gui: bool = True,
        fun_log: Optional[Callable] = None,
    ):
        """Inicialize."""

        self._fun_log = self.addLog if fun_log is None else fun_log  # type: ignore

        self.db_ = application.PROJECT.aq_app.db() if db_ is None else db_
        self._show_gui = show_gui
        self._dir_base = types.Dir.home if dir_base is None else dir_base

        self._file_name = self.genFileName()
        self.encoding = sys.getdefaultencoding()
        self.state_ = types.Array()

    def init(self) -> None:
        """Inicialize dump dialog."""
        if self._show_gui:
            self.buildGui()
            self.widget_.exec_()

    def buildGui(self) -> None:
        """Build a Dialog for database dump."""
        self.widget_ = QDialog()
        self.widget_.caption = SysType.translate(u"Copias de seguridad")
        self.widget_.setModal(True)
        self.widget_.resize(800, 600)
        # lay = QVBoxLayout(self.widget_, 6, 6)
        lay = QVBoxLayout(self.widget_)
        frm = QtWidgets.QFrame(self.widget_)
        frm.setFrameShape(QtWidgets.QFrame.Box)
        frm.setLineWidth(1)
        frm.setFrameShadow(QtWidgets.QFrame.Plain)

        # lay_frame = QVBoxLayout(frm, 6, 6)
        lay_frame = QVBoxLayout(frm)
        lbl = QLabel(frm)
        lbl.setText(
            SysType.translate(u"Driver: %s")
            % (str(self.db_.driverNameToDriverAlias(self.db_.driverName())))
        )
        lbl.setAlignment(QtCore.Qt.AlignTop)
        lay_frame.addWidget(lbl)
        lbl = QLabel(frm)
        lbl.setText(SysType.translate(u"Base de datos: %s") % (str(self.db_.database())))
        lbl.setAlignment(QtCore.Qt.AlignTop)
        lay_frame.addWidget(lbl)
        lbl = QLabel(frm)
        lbl.setText(SysType.translate(u"Host: %s") % (str(self.db_.host())))
        lbl.setAlignment(QtCore.Qt.AlignTop)
        lay_frame.addWidget(lbl)
        lbl = QLabel(frm)
        lbl.setText(SysType.translate(u"Puerto: %s") % (str(self.db_.port())))
        lbl.setAlignment(QtCore.Qt.AlignTop)
        lay_frame.addWidget(lbl)
        lbl = QLabel(frm)
        lbl.setText(SysType.translate(u"Usuario: %s") % (str(self.db_.user())))
        lbl.setAlignment(QtCore.Qt.AlignTop)
        lay_frame.addWidget(lbl)
        lay_aux = QHBoxLayout()
        lay_frame.addLayout(lay_aux)
        self._label_dir_base = QLabel(frm)
        self._label_dir_base.setText(
            SysType.translate(u"Directorio Destino: %s") % (str(self._dir_base))
        )
        self._label_dir_base.setAlignment(QtCore.Qt.AlignVCenter)
        lay_aux.addWidget(self._label_dir_base)
        self.pushbutton_change_dir = QPushButton(SysType.translate(u"Cambiar"), frm)
        self.pushbutton_change_dir.setSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred
        )
        application.connections.connect(
            self.pushbutton_change_dir, u"clicked()", self, u"changeDirBase()"
        )
        lay_aux.addWidget(self.pushbutton_change_dir)
        lay.addWidget(frm)
        self.pb_init_dump = QPushButton(SysType.translate(u"INICIAR COPIA"), self.widget_)
        application.connections.connect(self.pb_init_dump, u"clicked()", self, u"initDump()")
        lay.addWidget(self.pb_init_dump)
        lbl = QLabel(self.widget_)
        lbl.setText("Log:")
        lay.addWidget(lbl)
        self._ted_log = QTextEdit(self.widget_)
        self._ted_log.setTextFormat(QTextEdit.LogText)
        self._ted_log.setAlignment(
            cast(QtCore.Qt.Alignment, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        )
        lay.addWidget(self._ted_log)

    def initDump(self) -> None:
        """Inicialize dump."""

        gui = self._show_gui and self.widget_ is not None
        if gui:
            self.widget_.enable = False
        self.dumpDatabase()
        if gui:
            self.widget_.enable = True
            if self.state_.ok:
                SysType.infoMsgBox(self.state_.msg)
                self.widget_.close()
            else:
                SysType.errorMsgBox(self.state_.msg)

    def genFileName(self) -> str:
        """Return a file name."""
        now = types.Date()
        time_stamp = str(now)
        reg_exp = ["-", ":"]
        # reg_exp.global_ = True
        for item in reg_exp:
            time_stamp = time_stamp.replace(item, u"")

        file_name = "%s/dump_%s_%s" % (self._dir_base, self.db_.database(), time_stamp)
        file_name = types.Dir.cleanDirPath(file_name)
        file_name = types.Dir.convertSeparators(file_name)
        return file_name

    def changeDirBase(self, dir_: Optional[str] = None) -> None:
        """Change base dir."""
        dir_base_path = dir_
        if not dir_base_path:
            dir_base_path = FileDialog.getExistingDirectory(self._dir_base)
            if not dir_base_path:
                return
        self._dir_base = dir_base_path
        if self._show_gui and self._label_dir_base is not None:
            self._label_dir_base.setText(
                SysType.translate(u"Directorio Destino: %s") % (str(self._dir_base))
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
        # FIXME: Mejorar lectura linea a linea
        cast(
            QtCore.pyqtSignal, self.proc_.readyReadStandardOutput
        ).connect(  # type: ignore [attr-defined]
            self.readFromStdout
        )
        cast(
            QtCore.pyqtSignal, self.proc_.readyReadStandardError
        ).connect(  # type: ignore [attr-defined]
            self.readFromStderr
        )
        self.proc_.start()

        while self.proc_.running:
            SysType.processEvents()

        return self.proc_.exitcode() == self.proc_.normalExit

    def readFromStdout(self) -> None:
        """Read data from stdOutput."""

        text = (
            self.proc_.readLine()  # type: ignore[attr-defined] # noqa : F821
            .data()
            .decode(self.encoding)
        )
        if text not in (None, ""):
            self._fun_log(text)

    def readFromStderr(self) -> None:
        """Read data from stdError."""

        text = (
            self.proc_.readLine()  # type: ignore[attr-defined] # noqa : F821
            .data()
            .decode(self.encoding)
        )
        if text not in (None, ""):
            self._fun_log(text)

    def dumpDatabase(self) -> bool:
        """Dump database to target specified by sql driver class."""

        driver = self.db_.driverName()
        type_db = 0
        if driver.find("PSQL") > -1:
            type_db = 1
        else:
            if driver.find("MYSQL") > -1:
                type_db = 2

        if type_db == 0:
            self.setState(
                False,
                SysType.translate(u"Este tipo de base de datos no soporta el volcado a disco."),
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
            self.setState(False, utils_base.ustr(u"", error))
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
                False, SysType.translate(u"No se ha podido realizar la copia de seguridad.")
            )
            self._fun_log(self.state_.msg)
        else:
            self.setState(
                True,
                SysType.translate(u"Copia de seguridad realizada con éxito en:\n%s.sql")
                % (str(self._file_name)),
            )
            self._fun_log(self.state_.msg)

        return ok_

    def dumpPostgreSQL(self) -> bool:
        """Dump database to PostgreSql file."""

        pg_dump: str = u"pg_dump"
        command: List[str]
        file_name = "%s.sql" % self._file_name

        if SysType.osName() == u"WIN32":
            pg_dump += u".exe"
            System.setenv(u"PGPASSWORD", self.db_.returnword())
            command = [
                pg_dump,
                u"-f",
                file_name,
                u"-h",
                self.db_.host() or "",
                u"-p",
                str(self.db_.port() or 0),
                u"-U",
                self.db_.user() or "",
                str(self.db_.database()),
            ]
        else:
            System.setenv(u"PGPASSWORD", self.db_.returnword())
            command = [
                pg_dump,
                u"-v",
                u"-f",
                file_name,
                u"-h",
                self.db_.host() or "",
                u"-p",
                str(self.db_.port() or 0),
                u"-U",
                self.db_.user() or "",
                str(self.db_.database()),
            ]

        if not self.launchProc(command):
            self.setState(
                False,
                SysType.translate(u"No se ha podido volcar la base de datos a disco.\n")
                + SysType.translate(u"Es posible que no tenga instalada la herramienta ")
                + pg_dump,
            )
            self._fun_log(self.state_.msg)
            return False
        self.setState(True, u"")
        return True

    def dumpMySQL(self) -> bool:
        """Dump database to MySql file."""

        my_dump: str = u"mysqldump"
        command: List[str]
        file_name = utils_base.ustr(self._file_name, u".sql")

        if SysType.osName() == u"WIN32":
            my_dump += u".exe"
            command = [
                my_dump,
                u"-v",
                utils_base.ustr(u"--result-file=", file_name),
                utils_base.ustr(u"--host=", self.db_.host()),
                utils_base.ustr(u"--port=", self.db_.port()),
                utils_base.ustr(u"--password=", self.db_.returnword()),
                utils_base.ustr(u"--user=", self.db_.user()),
                str(self.db_.database()),
            ]
        else:
            command = [
                my_dump,
                u"-v",
                utils_base.ustr(u"--result-file=", file_name),
                utils_base.ustr(u"--host=", self.db_.host()),
                utils_base.ustr(u"--port=", self.db_.port()),
                utils_base.ustr(u"--password=", self.db_.returnword()),
                utils_base.ustr(u"--user=", self.db_.user()),
                str(self.db_.database()),
            ]

        if not self.launchProc(command):
            self.setState(
                False,
                SysType.translate(u"No se ha podido volcar la base de datos a disco.\n")
                + SysType.translate(u"Es posible que no tenga instalada la herramienta ")
                + my_dump,
            )
            self._fun_log(self.state_.msg)
            return False
        self.setState(True, u"")
        return True

    def dumpTableToCsv(self, table: str, dir_base: str) -> bool:
        """Dump a table to a CSV."""

        file_name = utils_base.ustr(dir_base, table, u".csv")
        file_ = types.File(file_name)
        if not file_.open(types.File.WriteOnly):  # type: ignore [arg-type]
            return False
        ts_ = QtCore.QTextStream(file_.ioDevice())
        ts_.setCodec(AQS.TextCodec_codecForName(u"utf8"))
        qry = pnsqlquery.PNSqlQuery()
        qry.setSelect(utils_base.ustr(table, u".*"))
        qry.setFrom(table)
        if not qry.exec_():
            return False

        rec = str("%s" % self.SEP_CSV).join(qry.fieldList())

        ts_.device().write(utils_base.ustr(rec, u"\n").encode())
        # ts.opIn(utils_base.ustr(rec, u"\n"))
        flutil.FLUtil.createProgressDialog(
            SysType.translate(u"Haciendo copia en CSV de ") + table, qry.size()
        )
        pos = 0
        while qry.next():
            values = []
            for field_name in qry.fieldList():
                values.append(str(qry.value(field_name)))

            rec = str("%s" % self.SEP_CSV).join(values)

            ts_.device().write(utils_base.ustr(rec, u"\n").encode())
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
        dir_base = types.Dir.convertSeparators(utils_base.ustr(self._file_name, u"/"))
        # i = 0
        # while_pass = True
        for table_ in tables:
            self.dumpTableToCsv(table_, dir_base)
        return True
