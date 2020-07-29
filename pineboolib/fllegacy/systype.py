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
    from pineboolib.interfaces import iconnection, isqlcursor
    from pineboolib.fllegacy import flformrecorddb, flformdb  # noqa: F401


LOGGER = logging.get_logger(__name__)


class AQTimer(QtCore.QTimer):
    """AQTimer class."""

    pass


class AQGlobalFunctions_class(QtCore.QObject):
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

        fn = self.functions_[function_name]
        if fn is not None:
            fn()

    def mapConnect(self, obj: QtWidgets.QWidget, signal: str, function_name: str) -> None:
        """Add conection to map."""

        self.mappers_.mapped[str].connect(self.exec_)  # type: ignore
        sg_name = re.sub(r" *\(.*\)", "", signal)

        sg = getattr(obj, sg_name, None)
        if sg is not None:
            sg.connect(self.mappers_.map)
            self.mappers_.setMapping(obj, function_name)


class SysType(sysbasetype.SysBaseType):
    """SysType class."""

    time_user_ = QtCore.QDateTime.currentDateTime()
    AQTimer = AQTimer
    AQGlobalFunctions = AQGlobalFunctions_class()

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
        self, pix_: QtGui.QPixmap, w_: int, h_: int, mode_: QtCore.Qt.AspectRatioMode
    ) -> QtGui.QImage:
        """Return QImage scaled from a QPixmap."""

        return application.PROJECT.aq_app.scalePixmap(pix_, w_, h_, mode_)

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
    def execQSA(fileQSA=None, args=None) -> Any:
        """Execute a QS file."""
        from pineboolib.application import types

        try:
            with open(fileQSA, "r") as file:
                fn = types.function("exec_qsa", file.read())
                return fn(args)
        except Exception:
            e = traceback.format_exc()
            LOGGER.warning(e)
            return None

    @staticmethod
    def dumpDatabase() -> None:
        """Launch dump database."""
        aqDumper = AbanQDbDumper()
        aqDumper.init()

    @staticmethod
    def terminateChecksLocks(sqlCursor: "isqlcursor.ISqlCursor" = None) -> None:
        """Set check risk locks to False in a cursor."""
        if sqlCursor is not None:
            sqlCursor.checkRisksLocks(True)

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

    @classmethod
    def warnLocalChanges(cls, changes: Optional[Dict[str, Any]] = None) -> bool:
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
        pbCancel = QPushButton(diag)
        pbCancel.setText(self.translate(u"Cancelar"))
        pbAccept = QPushButton(diag)
        pbAccept.setText(self.translate(u"continue"))
        lay2.addWidget(pbCancel)
        lay2.addWidget(pbAccept)
        application.connections.connect(pbAccept, "clicked()", diag, "accept()")
        application.connections.connect(pbCancel, "clicked()", diag, "reject()")
        if not application.PROJECT.app.platformName() != "offscreen":
            return False if (diag.exec_() == 0) else True
        else:
            return True

    @classmethod
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
        shaSum = u""
        shaSumTxt = u""
        shaSumBin = u""
        while qry.next():
            idMod = str(qry.value(0))
            if idMod == u"sys":
                continue
            fName = str(qry.value(1))
            ba = QByteArray()
            ba.string = self.fromUnicode(str(qry.value(2)), u"iso-8859-15")
            sha = ba.sha1()
            nf = doc.createElement(u"file")
            root.appendChild(nf)
            ne = doc.createElement(u"module")
            nf.appendChild(ne)
            nt = doc.createTextNode(idMod)
            ne.appendChild(nt)
            ne = doc.createElement(u"name")
            nf.appendChild(ne)
            nt = doc.createTextNode(fName)
            ne.appendChild(nt)
            if self.textPacking(fName):
                ne = doc.createElement(u"text")
                nf.appendChild(ne)
                nt = doc.createTextNode(fName)
                ne.appendChild(nt)
                ne = doc.createElement(u"shatext")
                nf.appendChild(ne)
                nt = doc.createTextNode(sha)
                ne.appendChild(nt)
                ba = QByteArray()
                ba.string = shaSum + sha
                shaSum = ba.sha1()
                ba = QByteArray()
                ba.string = shaSumTxt + sha
                shaSumTxt = ba.sha1()

        qry = pnsqlquery.PNSqlQuery()
        qry.setSelect(u"idmodulo,icono")
        qry.setFrom(u"flmodules")
        if qry.exec_():
            while qry.next():
                idMod = str(qry.value(0))
                if idMod == u"sys":
                    continue
                fName = utils_base.ustr(idMod, u".xpm")
                ba = QByteArray()
                ba.string = str(qry.value(1))
                sha = ba.sha1()
                nf = doc.createElement(u"file")
                root.appendChild(nf)
                ne = doc.createElement(u"module")
                nf.appendChild(ne)
                nt = doc.createTextNode(idMod)
                ne.appendChild(nt)
                ne = doc.createElement(u"name")
                nf.appendChild(ne)
                nt = doc.createTextNode(fName)
                ne.appendChild(nt)
                if self.textPacking(fName):
                    ne = doc.createElement(u"text")
                    nf.appendChild(ne)
                    nt = doc.createTextNode(fName)
                    ne.appendChild(nt)
                    ne = doc.createElement(u"shatext")
                    nf.appendChild(ne)
                    nt = doc.createTextNode(sha)
                    ne.appendChild(nt)
                    ba = QByteArray()
                    ba.string = shaSum + sha
                    shaSum = ba.sha1()
                    ba = QByteArray()
                    ba.string = shaSumTxt + sha
                    shaSumTxt = ba.sha1()

        ns = doc.createElement(u"shasum")
        ns.appendChild(doc.createTextNode(shaSum))
        root.appendChild(ns)
        ns = doc.createElement(u"shasumtxt")
        ns.appendChild(doc.createTextNode(shaSumTxt))
        root.appendChild(ns)
        ns = doc.createElement(u"shasumbin")
        ns.appendChild(doc.createTextNode(shaSumBin))
        root.appendChild(ns)
        return doc

    @classmethod
    def loadModules(self, input_: Optional[Any] = None, warnBackup: bool = True) -> bool:
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

            ret_ = self.loadAbanQPackage(input_, warnBackup)

        return ret_

    @classmethod
    def loadAbanQPackage(self, input_: str, warnBackup: bool = True) -> bool:
        """Load and process a Abanq/Eneboo package."""
        ok_ = False

        txt = u""
        txt += self.translate(u"Asegúrese de tener una copia de seguridad de todos los datos\n")
        txt += self.translate(u"y de que  no hay ningun otro  usuario conectado a la base de\n")
        txt += self.translate(u"datos mientras se realiza la carga.\n\n")
        txt += u"\n\n"
        txt += self.translate(u"¿Desea continuar?")

        if warnBackup and self.interactiveGUI():
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

    @classmethod
    def loadFilesDef(self, un: Any) -> bool:
        """Load files definition from a package to a QDomDocument."""

        filesDef = self.toUnicode(un.getText(), u"utf8")
        doc = QtXml.QDomDocument()
        if not doc.setContent(filesDef):
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
            if not self.registerFile(fil, un):
                self.errorMsgBox(
                    utils_base.ustr(
                        self.translate(u"Error registrando el fichero"), u" ", fil["id"]
                    )
                )
                ok_ = False
                break

        flutil.FLUtil.destroyProgressDialog()
        return ok_

    @classmethod
    def registerFile(self, fil: Dict[str, Any], un: Any) -> bool:
        """Register a file in the database."""

        if fil["id"].endswith(u".xpm"):
            cur = pnsqlcursor.PNSqlCursor(u"flmodules")
            if not cur.select(utils_base.ustr(u"idmodulo='", fil["module"], u"'")):
                return False
            if not cur.first():
                return False
            cur.setModeAccess(aqsql.AQSql.Edit)
            cur.refreshBuffer()
            cur.setValueBuffer(u"icono", un.getText())
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
                    cur.setValueBuffer(u"contenido", self.toUnicode(un.getText(), encode))
                else:
                    cur.setValueBuffer(u"contenido", un.getText())
            except UnicodeEncodeError as error:
                LOGGER.error("The %s file does not have the correct encode (%s)", fil["id"], encode)
                raise error

        if len(fil["binary"]) > 0:
            un.getBinary()
        return cur.commitBuffer()

    @classmethod
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

    @classmethod
    def loadModulesDef(self, un: Any) -> bool:
        """Return QDomDocument with modules definition."""

        modulesDef = self.toUnicode(un.getText(), u"utf8")
        doc = QtXml.QDomDocument()
        if not doc.setContent(modulesDef):
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

    @classmethod
    def registerArea(self, mod: Dict[str, Any]) -> bool:
        """Return True if the area is created or False."""
        cur = pnsqlcursor.PNSqlCursor(u"flareas")
        if not cur.select(utils_base.ustr(u"idarea = '", mod["area"], u"'")):
            return False
        cur.setModeAccess((aqsql.AQSql.Edit if cur.first() else aqsql.AQSql.Insert))
        cur.refreshBuffer()
        cur.setValueBuffer(u"idarea", mod["area"])
        cur.setValueBuffer(u"descripcion", mod["areaname"])
        return cur.commitBuffer()

    @classmethod
    def registerModule(self, mod: Dict[str, Any]) -> bool:
        """Return True if the module is created or False."""

        cur = pnsqlcursor.PNSqlCursor(u"flmodules")
        if not cur.select(utils_base.ustr(u"idmodulo='", mod["id"], u"'")):
            return False
        cur.setModeAccess((aqsql.AQSql.Edit if cur.first() else aqsql.AQSql.Insert))
        cur.refreshBuffer()
        cur.setValueBuffer(u"idmodulo", mod["id"])
        cur.setValueBuffer(u"idarea", mod["area"])
        cur.setValueBuffer(u"descripcion", mod["alias"])
        cur.setValueBuffer(u"version", mod["version"])
        return cur.commitBuffer()

    def questionMsgBox(
        self,
        msg: str,
        keyRemember: str = "",
        txtRemember: str = "",
        forceShow: bool = True,
        txtCaption: str = "Pineboo",
        txtYes: str = "Sí",
        txtNo: str = "No",
    ) -> Any:
        """Return a messagebox result."""

        key = u"QuestionMsgBox/"
        valRemember = False
        if keyRemember:
            valRemember = settings.SETTINGS.value(key + keyRemember)
            if valRemember and not forceShow:
                return MessageBox.Yes
        if not self.interactiveGUI():
            return True
        diag = QDialog()
        diag.caption = txtCaption
        diag.setModal(True)
        lay = QVBoxLayout(diag)
        # lay.setMargin(6)
        lay.setSpacing(6)
        lay2 = QHBoxLayout(diag)
        # lay2.setMargin(6)
        lay2.setSpacing(6)
        lblPix = QLabel(diag)
        pixmap = AQS.pixmap_fromMimeSource(u"help_index.png")
        if pixmap:
            lblPix.setPixmap(pixmap)
            lblPix.setAlignment(AQS.AlignTop)
        lay2.addWidget(lblPix)
        lbl = QLabel(diag)
        lbl.setText(msg)
        lbl.setAlignment(cast(QtCore.Qt.Alignment, AQS.AlignTop | AQS.WordBreak))
        lay2.addWidget(lbl)
        lay3 = QHBoxLayout(diag)
        # lay3.setMargin(6)
        lay3.setSpacing(6)
        pbYes = QPushButton(diag)
        pbYes.setText(txtYes if txtYes else self.translate(u"Sí"))
        pbNo = QPushButton(diag)
        pbNo.setText(txtNo if txtNo else self.translate(u"No"))
        lay3.addWidget(pbYes)
        lay3.addWidget(pbNo)
        application.connections.connect(pbYes, u"clicked()", diag, u"accept()")
        application.connections.connect(pbNo, u"clicked()", diag, u"reject()")
        chkRemember = None
        if keyRemember and txtRemember:
            # from pineboolib.q3widgets.qcheckbox import QCheckBox

            chkRemember = QtWidgets.QCheckBox(txtRemember, diag)
            chkRemember.setChecked(valRemember)
            lay.addWidget(chkRemember)

        if not application.PROJECT.app.platformName() == "offscreen":
            return MessageBox.Yes

        ret = MessageBox.No if (diag.exec_() == 0) else MessageBox.Yes
        if chkRemember is not None:
            settings.SETTINGS.set_value(key + keyRemember, chkRemember.isChecked())
        return ret

    @classmethod
    def exportModules(self) -> None:
        """Export modules."""

        dirBasePath = FileDialog.getExistingDirectory(types.Dir.home)
        if not dirBasePath:
            return
        dataBaseName = application.PROJECT.conn_manager.mainConn()._db_name
        dirBasePath = types.Dir.cleanDirPath(
            utils_base.ustr(
                dirBasePath, u"/modulos_exportados_", dataBaseName[dataBaseName.rfind(u"/") + 1 :]
            )
        )
        dir = types.Dir()
        if not dir.fileExists(dirBasePath):
            try:
                dir.mkdir(dirBasePath)
            except Exception:
                e = traceback.format_exc()
                self.errorMsgBox(utils_base.ustr(u"", e))
                return

        else:
            self.warnMsgBox(
                dirBasePath + self.translate(u" ya existe,\ndebe borrarlo antes de continuar")
            )
            return

        qry = pnsqlquery.PNSqlQuery()
        qry.setSelect(u"idmodulo")
        qry.setFrom(u"flmodules")
        if not qry.exec_() or qry.size() == 0:
            return
        p = 0
        flutil.FLUtil.createProgressDialog(self.translate(u"Exportando módulos"), qry.size() - 1)
        while qry.next():
            idMod = qry.value(0)
            if idMod == u"sys":
                continue
            flutil.FLUtil.setLabelText(idMod)
            p += 1
            flutil.FLUtil.setProgress(p)
            try:
                self.exportModule(idMod, dirBasePath)
            except Exception:
                e = traceback.format_exc()
                flutil.FLUtil.destroyProgressDialog()
                self.errorMsgBox(utils_base.ustr(u"", e))
                return

        dbProName = flutil.FLUtil.readDBSettingEntry(u"projectname")
        if not dbProName:
            dbProName = u""
        if not dbProName == "":
            doc = QtXml.QDomDocument()
            tag = doc.createElement(u"mvproject")
            tag.toElement().setAttribute(u"name", dbProName)
            doc.appendChild(tag)
            try:
                types.FileStatic.write(
                    utils_base.ustr(dirBasePath, u"/mvproject.xml"), doc.toString(2)
                )
            except Exception:
                e = traceback.format_exc()
                flutil.FLUtil.destroyProgressDialog()
                self.errorMsgBox(utils_base.ustr(u"", e))
                return

        flutil.FLUtil.destroyProgressDialog()
        self.infoMsgBox(self.translate(u"Módulos exportados en:\n") + dirBasePath)

    @classmethod
    def xmlModule(self, idMod: str) -> QtXml.QDomDocument:
        """Return xml data from a module."""
        qry = pnsqlquery.PNSqlQuery()
        qry.setSelect(u"descripcion,idarea,version")
        qry.setFrom(u"flmodules")
        qry.setWhere(utils_base.ustr(u"idmodulo='", idMod, u"'"))
        doc = QtXml.QDomDocument(u"MODULE")
        if not qry.exec_() or not qry.next():
            return doc

        tagMod = doc.createElement(u"MODULE")
        doc.appendChild(tagMod)
        tag = doc.createElement(u"name")
        tag.appendChild(doc.createTextNode(idMod))
        tagMod.appendChild(tag)
        trNoop = u'QT_TRANSLATE_NOOP("Eneboo","%s")'
        tag = doc.createElement(u"alias")
        tag.appendChild(doc.createTextNode(trNoop % qry.value(0)))
        tagMod.appendChild(tag)
        idArea = qry.value(1)
        tag = doc.createElement(u"area")
        tag.appendChild(doc.createTextNode(idArea))
        tagMod.appendChild(tag)
        areaName = utils_db.sql_select(
            u"flareas", u"descripcion", utils_base.ustr(u"idarea='", idArea, u"'")
        )
        tag = doc.createElement(u"areaname")
        tag.appendChild(doc.createTextNode(trNoop % areaName))
        tagMod.appendChild(tag)
        tag = doc.createElement(u"entryclass")
        tag.appendChild(doc.createTextNode(idMod))
        tagMod.appendChild(tag)
        tag = doc.createElement(u"version")
        tag.appendChild(doc.createTextNode(qry.value(2)))
        tagMod.appendChild(tag)
        tag = doc.createElement(u"icon")
        tag.appendChild(doc.createTextNode(utils_base.ustr(idMod, u".xpm")))
        tagMod.appendChild(tag)
        return doc

    @classmethod
    def fileWriteIso(self, file_name: str, content: str) -> None:
        """Write data into a file with ISO-8859-15 encode."""

        fileISO = types.File(file_name, "ISO8859-15")
        fileISO.write(content.encode("ISO8859-15", "ignore"))

        fileISO.close()

    @classmethod
    def fileWriteUtf8(self, file_name: str, content: str) -> None:
        """Write data into a file with UTF-8 encode."""

        fileUTF = types.File(file_name, "UTF-8")
        fileUTF.write(content)
        fileUTF.close()

    @classmethod
    def exportModule(self, idMod: str, dirBasePath: str) -> None:
        """Export a module to a directory."""

        dir = types.Dir()
        dirPath = types.Dir.cleanDirPath(utils_base.ustr(dirBasePath, u"/", idMod))
        if not dir.fileExists(dirPath):
            dir.mkdir(dirPath)
        if not dir.fileExists(utils_base.ustr(dirPath, u"/forms")):
            dir.mkdir(utils_base.ustr(dirPath, u"/forms"))
        if not dir.fileExists(utils_base.ustr(dirPath, u"/scripts")):
            dir.mkdir(utils_base.ustr(dirPath, u"/scripts"))
        if not dir.fileExists(utils_base.ustr(dirPath, u"/queries")):
            dir.mkdir(utils_base.ustr(dirPath, u"/queries"))
        if not dir.fileExists(utils_base.ustr(dirPath, u"/tables")):
            dir.mkdir(utils_base.ustr(dirPath, u"/tables"))
        if not dir.fileExists(utils_base.ustr(dirPath, u"/reports")):
            dir.mkdir(utils_base.ustr(dirPath, u"/reports"))
        if not dir.fileExists(utils_base.ustr(dirPath, u"/translations")):
            dir.mkdir(utils_base.ustr(dirPath, u"/translations"))
        xmlMod = self.xmlModule(idMod)
        self.fileWriteIso(utils_base.ustr(dirPath, u"/", idMod, u".mod"), xmlMod.toString(2))
        xpmMod = utils_db.sql_select(
            u"flmodules", u"icono", utils_base.ustr(u"idmodulo='", idMod, u"'")
        )
        self.fileWriteIso(utils_base.ustr(dirPath, u"/", idMod, u".xpm"), xpmMod)
        qry = pnsqlquery.PNSqlQuery()
        qry.setSelect(u"nombre,contenido")
        qry.setFrom(u"flfiles")
        qry.setWhere(utils_base.ustr(u"idmodulo='", idMod, u"'"))
        if not qry.exec_() or qry.size() == 0:
            return
        while qry.next():
            name = qry.value(0)
            content = qry.value(1)
            type_ = name[(len(name) - (len(name) - name.rfind(u"."))) :]
            if type_ == ".xml":
                self.fileWriteIso(utils_base.ustr(dirPath, u"/", name), content)
            elif type_ == ".ui":
                self.fileWriteIso(utils_base.ustr(dirPath, u"/forms/", name), content)
            elif type_ == ".qs":
                self.fileWriteIso(utils_base.ustr(dirPath, u"/scripts/", name), content)
            elif type_ == ".qry":
                self.fileWriteIso(utils_base.ustr(dirPath, u"/queries/", name), content)
            elif type_ == ".mtd":
                self.fileWriteIso(utils_base.ustr(dirPath, u"/tables/", name), content)
            elif type_ in (".kut", ".ar", ".jrxml", ".svg"):
                self.fileWriteIso(utils_base.ustr(dirPath, u"/reports/", name), content)
            elif type_ == ".ts":
                self.fileWriteIso(utils_base.ustr(dirPath, u"/translations/", name), content)
            elif type_ == ".py":
                self.fileWriteUtf8(utils_base.ustr(dirPath, u"/scripts/", name), content)

    @classmethod
    def importModules(self, warnBackup: bool = True) -> None:
        """Import modules from a directory."""

        if warnBackup and self.interactiveGUI():
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
        dirAnt = settings.SETTINGS.value(key)

        dir_modules = FileDialog.getExistingDirectory(
            str(dirAnt) if dirAnt else ".", self.translate(u"Directorio de Módulos")
        )
        if not dir_modules:
            return
        dir_modules = types.Dir.cleanDirPath(dir_modules)
        dir_modules = types.Dir.convertSeparators(dir_modules)
        QtCore.QDir.setCurrent(dir_modules)  # change current directory
        listFilesMod = self.selectModsDialog(flutil.FLUtil.findFiles(dir_modules, u"*.mod", False))
        flutil.FLUtil.createProgressDialog(self.translate(u"Importando"), len(listFilesMod))
        flutil.FLUtil.setProgress(1)

        for number, value in enumerate(listFilesMod):
            flutil.FLUtil.setLabelText(value)
            flutil.FLUtil.setProgress(number)
            if not self.importModule(value):
                self.errorMsgBox(self.translate(u"Error al cargar el módulo:\n") + value)
                break

        flutil.FLUtil.destroyProgressDialog()
        flutil.FLUtil.writeSettingEntry(key, dir_modules)
        self.infoMsgBox(self.translate(u"Importación de módulos finalizada."))
        AQTimer.singleShot(0, self.reinit)  # type: ignore [arg-type] # noqa: F821

    @classmethod
    def selectModsDialog(self, listFilesMod: List = []) -> types.Array:
        """Select modules dialog."""

        dialog = Dialog()
        dialog.okButtonText = self.translate(u"Aceptar")
        dialog.cancelButtonText = self.translate(u"Cancelar")
        bgroup = QtWidgets.QGroupBox()
        bgroup.setTitle(self.translate(u"Seleccione módulos a importar"))
        dialog.add(bgroup)
        res = types.Array()
        cB = types.Array()
        i = 0
        while_pass = True
        while i < len(listFilesMod):
            if not while_pass:
                i += 1
                while_pass = True
                continue
            while_pass = False
            cB[i] = QtWidgets.QCheckBox()
            # bgroup.add(cB[i])
            cB[i].text = listFilesMod[i]
            cB[i].checked = True
            i += 1
            while_pass = True
            try:
                i < len(listFilesMod)
            except Exception:
                break

        idx = 0
        if self.interactiveGUI() and dialog.exec_():
            i = 0
            while_pass = True
            while i < len(listFilesMod):
                if not while_pass:
                    i += 1
                    while_pass = True
                    continue
                while_pass = False
                if cB[i].checked:
                    res[idx] = listFilesMod[i]
                    idx += 1
                i += 1
                while_pass = True
                try:
                    i < len(listFilesMod)
                except Exception:
                    break

        return res

    @classmethod
    def importModule(self, modPath: str) -> bool:
        """Import a module specified by name."""
        try:
            with open(modPath, "r", encoding="ISO8859-15") as fileMod:
                contentMod = fileMod.read()
        except Exception:
            e = traceback.format_exc()
            self.errorMsgBox(utils_base.ustr(self.translate(u"Error leyendo fichero."), u"\n", e))
            return False
        mod_folder = os.path.dirname(modPath)
        mod = None
        xmlMod = QtXml.QDomDocument()
        if xmlMod.setContent(contentMod):
            nodeMod = xmlMod.namedItem(u"MODULE")
            if not nodeMod:
                self.errorMsgBox(self.translate(u"Error en la carga del fichero xml .mod"))
                return False
            mod = {
                "id": (nodeMod.namedItem(u"name").toElement().text()),
                "alias": (self.trTagText(nodeMod.namedItem(u"alias").toElement().text())),
                "area": (nodeMod.namedItem(u"area").toElement().text()),
                "areaname": (self.trTagText(nodeMod.namedItem(u"areaname").toElement().text())),
                "version": (nodeMod.namedItem(u"version").toElement().text()),
            }
            if not self.registerArea(mod) or not self.registerModule(mod):
                self.errorMsgBox(
                    utils_base.ustr(self.translate(u"Error registrando el módulo"), u" ", mod["id"])
                )
                return False
            if not self.importFiles(mod_folder, u"*.xml", mod["id"]):
                return False
            if not self.importFiles(mod_folder, u"*.ui", mod["id"]):
                return False
            if not self.importFiles(mod_folder, u"*.qs", mod["id"]):
                return False
            if not self.importFiles(mod_folder, u"*.py", mod["id"]):
                return False
            if not self.importFiles(mod_folder, u"*.qry", mod["id"]):
                return False
            if not self.importFiles(mod_folder, u"*.mtd", mod["id"]):
                return False
            if not self.importFiles(mod_folder, u"*.kut", mod["id"]):
                return False
            if not self.importFiles(mod_folder, u"*.ar", mod["id"]):
                return False
            if not self.importFiles(mod_folder, u"*.jrxml", mod["id"]):
                return False
            if not self.importFiles(mod_folder, u"*.svg", mod["id"]):
                return False
            if not self.importFiles(mod_folder, u"*.ts", mod["id"]):
                return False

        else:
            self.errorMsgBox(self.translate(u"Error en la carga del fichero xml .mod"))
            return False

        return True

    @classmethod
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

    @classmethod
    def importFile(self, file_path_: str, id_module_: str) -> bool:
        """Import a file from a path."""
        file = types.File(file_path_)
        content = u""
        try:
            file.open(types.File.ReadOnly)
            content = str(file.read())
        except Exception:
            e = traceback.format_exc()
            self.errorMsgBox(utils_base.ustr(self.translate(u"Error leyendo fichero."), u"\n", e))
            return False

        ok_ = True
        name = file.name
        if (
            not flutil.FLUtil.isFLDefFile(content)
            and not name.endswith(u".qs")
            and not name.endswith(u".py")
            and not name.endswith(u".ar")
            and not name.endswith(u".svg")
        ) or name.endswith(u"untranslated.ts"):
            return ok_
        cur = pnsqlcursor.PNSqlCursor(u"flfiles")
        cur.select(utils_base.ustr(u"nombre = '", name, u"'"))
        ba = QByteArray()
        ba.string = content

        if not cur.first():
            if name.endswith(u".ar"):
                if not self.importReportAr(file_path_, id_module_, content):
                    return True
            cur.setModeAccess(aqsql.AQSql.Insert)
            cur.refreshBuffer()
            cur.setValueBuffer(u"nombre", name)
            cur.setValueBuffer(u"idmodulo", id_module_)
            cur.setValueBuffer(u"sha", ba.sha1())
            cur.setValueBuffer(u"contenido", content)
            ok_ = cur.commitBuffer()

        else:
            cur.setModeAccess(aqsql.AQSql.Edit)
            cur.refreshBuffer()

            shaCnt = ba.sha1()
            if cur.valueBuffer(u"sha") != shaCnt:
                contenidoCopia = cur.valueBuffer(u"contenido")
                cur.setModeAccess(aqsql.AQSql.Insert)
                cur.refreshBuffer()
                d = types.Date()
                cur.setValueBuffer(u"nombre", name + str(d))
                cur.setValueBuffer(u"idmodulo", id_module_)
                cur.setValueBuffer(u"contenido", contenidoCopia)
                cur.commitBuffer()
                cur.select(utils_base.ustr(u"nombre = '", name, u"'"))
                cur.first()
                cur.setModeAccess(aqsql.AQSql.Edit)
                cur.refreshBuffer()
                cur.setValueBuffer(u"idmodulo", id_module_)
                cur.setValueBuffer(u"sha", shaCnt)
                cur.setValueBuffer(u"contenido", content)
                ok_ = cur.commitBuffer()
                if name.endswith(u".ar"):
                    if not self.importReportAr(file_path_, id_module_, content):
                        return True

        return ok_

    @classmethod
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
            localEnc = settings.SETTINGS.value(u"scripts/sys/conversionArENC")
            if not localEnc:
                localEnc = u"ISO-8859-15"
            content = self.fromUnicode(content, localEnc)
            f = types.FileStatic()
            try:
                f.write(file_path_, content)
            except Exception:
                e = traceback.format_exc()
                self.errorMsgBox(
                    utils_base.ustr(self.translate(u"Error escribiendo fichero."), u"\n", e)
                )
                return False

            return self.importFile(file_path_, id_module_)

        return False

    @classmethod
    def runTransaction(self, f: Callable, oParam: Dict[str, Any]) -> Any:
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
            valor_ = f(oParam)
            if "errorMsg" in oParam:
                error_msg_ = oParam["errorMsg"]

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

    @classmethod
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

    @classmethod
    def qsaExceptions(self):
        """Return QSA exceptions found."""

        return application.PROJECT.conn_manager.qsaExceptions()

    @classmethod
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

    @classmethod
    def localChanges(self) -> Dict[str, Any]:
        """Return xml with local changes."""
        ret = {}
        ret[u"size"] = 0
        strXmlUpt = utils_db.sql_select("flupdates", "filesdef", "actual='true'")
        if not strXmlUpt:
            return ret
        docUpt = QtXml.QDomDocument()
        if not docUpt.setContent(strXmlUpt):
            self.errorMsgBox(
                self.translate(u"Error XML al intentar cargar la definición de los ficheros.")
            )
            return ret
        docBd = self.xmlFilesDefBd()
        ret = self.diffXmlFilesDef(docBd, docUpt)
        return ret

    @classmethod
    def interactiveGUI(self):
        """Return interactiveGUI."""

        return application.PROJECT.conn_manager.mainConn().interactiveGUI()

    @classmethod
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
        a = None
        conn = application.PROJECT._conn_manager
        if conn is None:
            raise Exception("conn is empty!")

        if container[0:10] == "formRecord":
            action_ = container[10:]
            a = conn.manager().action(action_)
            if a.formRecord():
                widget = conn.managerModules().createFormRecord(a)
        elif container[0:10] == "formSearch":
            action_ = container[10:]
            a = conn.manager().action(action_)
            if a.form():
                widget = conn.managerModules().createForm(a)
        else:
            action_ = container[4:]
            a = conn.manager().action(action_)
            if a.form():
                widget = conn.managerModules().createForm(a)

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
                if field_table_ and field_table_ != a.table():
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
    showGui_: bool
    dirBase_: str
    fileName_: str
    w_: QDialog
    lblDirBase_: QLabel
    pbChangeDir_: QPushButton
    tedLog_: QTextEdit
    pbInitDump_: QPushButton
    state_: types.Array
    funLog_: Callable
    proc_: process.Process

    def __init__(
        self,
        db: Optional["iconnection.IConnection"] = None,
        dirBase: Optional[str] = None,
        showGui: bool = True,
        fun_log: Optional[Callable] = None,
    ):
        """Inicialize."""

        self.funLog_ = self.addLog if fun_log is None else fun_log  # type: ignore

        self.db_ = application.PROJECT.aq_app.db() if db is None else db
        self.showGui_ = showGui
        self.dirBase_ = types.Dir.home if dirBase is None else dirBase

        self.fileName_ = self.genFileName()
        self.encoding = sys.getdefaultencoding()
        self.state_ = types.Array()

    def init(self) -> None:
        """Inicialize dump dialog."""
        if self.showGui_:
            self.buildGui()
            self.w_.exec_()

    def buildGui(self) -> None:
        """Build a Dialog for database dump."""
        self.w_ = QDialog()
        self.w_.caption = SysType.translate(u"Copias de seguridad")
        self.w_.setModal(True)
        self.w_.resize(800, 600)
        # lay = QVBoxLayout(self.w_, 6, 6)
        lay = QVBoxLayout(self.w_)
        frm = QtWidgets.QFrame(self.w_)
        frm.setFrameShape(QtWidgets.QFrame.Box)
        frm.setLineWidth(1)
        frm.setFrameShadow(QtWidgets.QFrame.Plain)

        # layFrm = QVBoxLayout(frm, 6, 6)
        layFrm = QVBoxLayout(frm)
        lbl = QLabel(frm)
        lbl.setText(
            SysType.translate(u"Driver: %s")
            % (str(self.db_.driverNameToDriverAlias(self.db_.driverName())))
        )
        lbl.setAlignment(QtCore.Qt.AlignTop)
        layFrm.addWidget(lbl)
        lbl = QLabel(frm)
        lbl.setText(SysType.translate(u"Base de datos: %s") % (str(self.db_.database())))
        lbl.setAlignment(QtCore.Qt.AlignTop)
        layFrm.addWidget(lbl)
        lbl = QLabel(frm)
        lbl.setText(SysType.translate(u"Host: %s") % (str(self.db_.host())))
        lbl.setAlignment(QtCore.Qt.AlignTop)
        layFrm.addWidget(lbl)
        lbl = QLabel(frm)
        lbl.setText(SysType.translate(u"Puerto: %s") % (str(self.db_.port())))
        lbl.setAlignment(QtCore.Qt.AlignTop)
        layFrm.addWidget(lbl)
        lbl = QLabel(frm)
        lbl.setText(SysType.translate(u"Usuario: %s") % (str(self.db_.user())))
        lbl.setAlignment(QtCore.Qt.AlignTop)
        layFrm.addWidget(lbl)
        layAux = QHBoxLayout()
        layFrm.addLayout(layAux)
        self.lblDirBase_ = QLabel(frm)
        self.lblDirBase_.setText(
            SysType.translate(u"Directorio Destino: %s") % (str(self.dirBase_))
        )
        self.lblDirBase_.setAlignment(QtCore.Qt.AlignVCenter)
        layAux.addWidget(self.lblDirBase_)
        self.pbChangeDir_ = QPushButton(SysType.translate(u"Cambiar"), frm)
        self.pbChangeDir_.setSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred
        )
        application.connections.connect(self.pbChangeDir_, u"clicked()", self, u"changeDirBase()")
        layAux.addWidget(self.pbChangeDir_)
        lay.addWidget(frm)
        self.pbInitDump_ = QPushButton(SysType.translate(u"INICIAR COPIA"), self.w_)
        application.connections.connect(self.pbInitDump_, u"clicked()", self, u"initDump()")
        lay.addWidget(self.pbInitDump_)
        lbl = QLabel(self.w_)
        lbl.setText("Log:")
        lay.addWidget(lbl)
        self.tedLog_ = QTextEdit(self.w_)
        self.tedLog_.setTextFormat(QTextEdit.LogText)
        self.tedLog_.setAlignment(
            cast(QtCore.Qt.Alignment, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        )
        lay.addWidget(self.tedLog_)

    def initDump(self) -> None:
        """Inicialize dump."""

        gui = self.showGui_ and self.w_ is not None
        if gui:
            self.w_.enable = False
        self.dumpDatabase()
        if gui:
            self.w_.enable = True
            if self.state_.ok:
                SysType.infoMsgBox(self.state_.msg)
                self.w_.close()
            else:
                SysType.errorMsgBox(self.state_.msg)

    def genFileName(self) -> str:
        """Return a file name."""
        now = types.Date()
        timeStamp = str(now)
        regExp = ["-", ":"]
        # regExp.global_ = True
        for rE in regExp:
            timeStamp = timeStamp.replace(rE, u"")

        fileName = "%s/dump_%s_%s" % (self.dirBase_, self.db_.database(), timeStamp)
        fileName = types.Dir.cleanDirPath(fileName)
        fileName = types.Dir.convertSeparators(fileName)
        return fileName

    def changeDirBase(self, dir_: Optional[str] = None) -> None:
        """Change base dir."""
        dirBasePath = dir_
        if not dirBasePath:
            dirBasePath = FileDialog.getExistingDirectory(self.dirBase_)
            if not dirBasePath:
                return
        self.dirBase_ = dirBasePath
        if self.showGui_ and self.lblDirBase_ is not None:
            self.lblDirBase_.setText(
                SysType.translate(u"Directorio Destino: %s") % (str(self.dirBase_))
            )
        self.fileName_ = self.genFileName()

    def addLog(self, msg: str) -> None:
        """Add a text to log."""

        if self.showGui_ and self.tedLog_ is not None:
            self.tedLog_.append(msg)
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
        cast(QtCore.pyqtSignal, self.proc_.readyReadStandardOutput).connect(self.readFromStdout)
        cast(QtCore.pyqtSignal, self.proc_.readyReadStandardError).connect(self.readFromStderr)
        self.proc_.start()

        while self.proc_.running:
            SysType.processEvents()

        return self.proc_.exitcode() == self.proc_.normalExit

    def readFromStdout(self) -> None:
        """Read data from stdOutput."""

        t = (
            self.proc_.readLine()  # type: ignore[attr-defined] # noqa : F821
            .data()
            .decode(self.encoding)
        )
        if t not in (None, ""):
            self.funLog_(t)

    def readFromStderr(self) -> None:
        """Read data from stdError."""

        t = (
            self.proc_.readLine()  # type: ignore[attr-defined] # noqa : F821
            .data()
            .decode(self.encoding)
        )
        if t not in (None, ""):
            self.funLog_(t)

    def dumpDatabase(self) -> bool:
        """Dump database to target specified by sql driver class."""

        driver = self.db_.driverName()
        typeBd = 0
        if driver.find("PSQL") > -1:
            typeBd = 1
        else:
            if driver.find("MYSQL") > -1:
                typeBd = 2

        if typeBd == 0:
            self.setState(
                False,
                SysType.translate(u"Este tipo de base de datos no soporta el volcado a disco."),
            )
            self.funLog_(self.state_.msg)
            self.dumpAllTablesToCsv()
            return False
        file = types.File(self.fileName_)  # noqa
        try:
            if not os.path.exists(self.fileName_):
                dir_ = types.Dir(self.fileName_)  # noqa

        except Exception:
            e = traceback.format_exc()
            self.setState(False, utils_base.ustr(u"", e))
            self.funLog_(self.state_.msg)
            return False

        ok_ = True
        if typeBd == 1:
            ok_ = self.dumpPostgreSQL()

        if typeBd == 2:
            ok_ = self.dumpMySQL()

        if not ok_:
            self.dumpAllTablesToCsv()
        if not ok_:
            self.setState(
                False, SysType.translate(u"No se ha podido realizar la copia de seguridad.")
            )
            self.funLog_(self.state_.msg)
        else:
            self.setState(
                True,
                SysType.translate(u"Copia de seguridad realizada con éxito en:\n%s.sql")
                % (str(self.fileName_)),
            )
            self.funLog_(self.state_.msg)

        return ok_

    def dumpPostgreSQL(self) -> bool:
        """Dump database to PostgreSql file."""

        pgDump: str = u"pg_dump"
        command: List[str]
        fileName = "%s.sql" % self.fileName_
        db = self.db_
        if SysType.osName() == u"WIN32":
            pgDump += u".exe"
            System.setenv(u"PGPASSWORD", db.returnword())
            command = [
                pgDump,
                u"-f",
                fileName,
                u"-h",
                db.host() or "",
                u"-p",
                str(db.port() or 0),
                u"-U",
                db.user() or "",
                str(db.database()),
            ]
        else:
            System.setenv(u"PGPASSWORD", db.returnword())
            command = [
                pgDump,
                u"-v",
                u"-f",
                fileName,
                u"-h",
                db.host() or "",
                u"-p",
                str(db.port() or 0),
                u"-U",
                db.user() or "",
                str(db.database()),
            ]

        if not self.launchProc(command):
            self.setState(
                False,
                SysType.translate(u"No se ha podido volcar la base de datos a disco.\n")
                + SysType.translate(u"Es posible que no tenga instalada la herramienta ")
                + pgDump,
            )
            self.funLog_(self.state_.msg)
            return False
        self.setState(True, u"")
        return True

    def dumpMySQL(self) -> bool:
        """Dump database to MySql file."""

        myDump: str = u"mysqldump"
        command: List[str]
        fileName = utils_base.ustr(self.fileName_, u".sql")
        db = self.db_
        if SysType.osName() == u"WIN32":
            myDump += u".exe"
            command = [
                myDump,
                u"-v",
                utils_base.ustr(u"--result-file=", fileName),
                utils_base.ustr(u"--host=", db.host()),
                utils_base.ustr(u"--port=", db.port()),
                utils_base.ustr(u"--password=", db.returnword()),
                utils_base.ustr(u"--user=", db.user()),
                str(db.database()),
            ]
        else:
            command = [
                myDump,
                u"-v",
                utils_base.ustr(u"--result-file=", fileName),
                utils_base.ustr(u"--host=", db.host()),
                utils_base.ustr(u"--port=", db.port()),
                utils_base.ustr(u"--password=", db.returnword()),
                utils_base.ustr(u"--user=", db.user()),
                str(db.database()),
            ]

        if not self.launchProc(command):
            self.setState(
                False,
                SysType.translate(u"No se ha podido volcar la base de datos a disco.\n")
                + SysType.translate(u"Es posible que no tenga instalada la herramienta ")
                + myDump,
            )
            self.funLog_(self.state_.msg)
            return False
        self.setState(True, u"")
        return True

    def dumpTableToCsv(self, table: str, dirBase: str) -> bool:
        """Dump a table to a CSV."""

        fileName = utils_base.ustr(dirBase, table, u".csv")
        file = types.File(fileName)
        if not file.open(types.File.WriteOnly):
            return False
        ts = QtCore.QTextStream(file.ioDevice())
        ts.setCodec(AQS.TextCodec_codecForName(u"utf8"))
        qry = pnsqlquery.PNSqlQuery()
        qry.setSelect(utils_base.ustr(table, u".*"))
        qry.setFrom(table)
        if not qry.exec_():
            return False

        rec = str("%s" % self.SEP_CSV).join(qry.fieldList())

        ts.device().write(utils_base.ustr(rec, u"\n").encode())
        # ts.opIn(utils_base.ustr(rec, u"\n"))
        flutil.FLUtil.createProgressDialog(
            SysType.translate(u"Haciendo copia en CSV de ") + table, qry.size()
        )
        p = 0
        while qry.next():
            values = []
            for field_name in qry.fieldList():
                values.append(str(qry.value(field_name)))

            rec = str("%s" % self.SEP_CSV).join(values)

            ts.device().write(utils_base.ustr(rec, u"\n").encode())
            p += 1
            flutil.FLUtil.setProgress(p)

        file.close()
        flutil.FLUtil.destroyProgressDialog()
        return True

    def dumpAllTablesToCsv(self) -> bool:
        """Dump all tables to a csv files."""
        fileName = self.fileName_
        tables = self.db_.tables(aqsql.AQSql.TableType.Tables)
        dir_ = types.Dir(fileName)
        dir_.mkdir()
        dirBase = types.Dir.convertSeparators(utils_base.ustr(fileName, u"/"))
        # i = 0
        # while_pass = True
        for table_ in tables:
            self.dumpTableToCsv(table_, dirBase)
        return True
