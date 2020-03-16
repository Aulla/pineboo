"""
SysBaseType for QSA.

Will be inherited at fllegacy.
"""

import platform
import traceback
import ast

from typing import Any, Dict, Optional, List, Union, cast

from PyQt5 import QtCore, QtWidgets, QtXml

from pineboolib.core import settings
from pineboolib.core import decorators
from pineboolib.core.utils.utils_base import ustr, filedir
from pineboolib.core.utils import logging

from pineboolib import application
from pineboolib.application import connections

from pineboolib.application.process import Process

LOGGER = logging.get_logger(__name__)


class SysBaseType(object):
    """
    Obtain useful data from the application.
    """

    time_user_ = QtCore.QDateTime.currentDateTime()

    @classmethod
    def nameUser(self) -> str:
        """Get current database user."""
        ret_ = None

        if application.PROJECT.DGI.use_alternative_credentials():
            ret_ = application.PROJECT.DGI.get_nameuser()
        else:
            ret_ = application.PROJECT.conn_manager.mainConn().user()

        return ret_ or ""

    @classmethod
    def interactiveGUI(self) -> str:
        """Check if running in GUI mode."""
        return application.PROJECT.DGI.interactiveGUI()

    @classmethod
    def isUserBuild(self) -> bool:
        """Check if this build is an user build."""
        return self.version().upper().find("USER") > -1

    @classmethod
    def isDeveloperBuild(self) -> bool:
        """Check if this build is a developer build."""
        return self.version().upper().find("DEVELOPER") > -1

    @classmethod
    def isNebulaBuild(self) -> bool:
        """Check if this build is a nebula build."""
        return self.version().upper().find("NEBULA") > -1

    @classmethod
    def isDebuggerMode(self) -> bool:
        """Check if running in debugger mode."""
        return bool(settings.CONFIG.value("application/isDebuggerMode", False))

    @classmethod
    @decorators.not_implemented_warn
    def isCloudMode(self) -> bool:
        """Check if running on cloud mode."""
        return False

    @classmethod
    def isDebuggerEnabled(self) -> bool:
        """Check if this debugger is on."""
        return bool(settings.CONFIG.value("application/dbadmin_enabled", False))

    @classmethod
    def isQuickBuild(self) -> bool:
        """Check if this build is a Quick build."""
        return not self.isDebuggerEnabled()

    @classmethod
    def isLoadedModule(self, modulename: str) -> bool:
        """Check if a module has been loaded."""
        return modulename in application.PROJECT.conn_manager.managerModules().listAllIdModules()

    @classmethod
    def osName(self) -> str:
        """
        Get operating system name.

        @return Código del sistema operativo (WIN32, LINUX, MACX)
        """
        if platform.system() == "Windows":
            return "WIN32"
        elif platform.system() == "Linux" or platform.system() == "Linux2":
            return "LINUX"
        elif platform.system() == "Darwin":
            return "MACX"
        else:
            return platform.system()

    @classmethod
    def nameBD(self) -> str:
        """Get database name."""
        return application.PROJECT.conn_manager.mainConn().DBName()

    @classmethod
    def toUnicode(self, val: str, format: str) -> str:
        """Convert string to unicode."""
        return val.encode(format).decode("utf-8", "replace")

    @classmethod
    def fromUnicode(self, val: str, format: str) -> str:
        """Convert from unicode to string."""
        return val.encode("utf-8").decode(format, "replace")

    @classmethod
    def Mr_Proper(self) -> None:
        """Cleanup database like Mr. Proper."""
        application.PROJECT.conn_manager.mainConn().Mr_Proper()

    @classmethod
    def installPrefix(self) -> str:
        """Get folder where app is installed."""
        return filedir("..")

    @classmethod
    def version(self) -> str:
        """Get version number as string."""
        return str(application.PROJECT.version)

    @classmethod
    def processEvents(self) -> None:
        """Process event loop."""
        return application.PROJECT.DGI.processEvents()

    @classmethod
    def write(self, encode_: str, dir_: str, contenido: str) -> None:
        """Write to file."""
        from pineboolib.application.types import File

        file_iso = File(dir_, encode_)
        file_iso.write(contenido)
        file_iso.close()

    @classmethod
    def cleanupMetaData(self, conn_name: str = "default") -> None:
        """Clean up metadata."""
        application.PROJECT.conn_manager.manager().cleanupMetaData()

    @classmethod
    def nameDriver(self, conn_name: str = "default") -> Any:
        """Get driver name."""
        return application.PROJECT.conn_manager.useConn(conn_name).driverName()

    @classmethod
    def nameHost(self, conn_name: str = "default") -> Any:
        """Get database host name."""
        return application.PROJECT.conn_manager.useConn(conn_name).host()

    @classmethod
    def addDatabase(self, *args: Any) -> bool:
        """Add a new database."""
        # def addDatabase(self, driver_name = None, db_name = None, db_user_name = None,
        #                 db_password = None, db_host = None, db_port = None, connName="default"):

        if len(args) == 1:
            conn_db = application.PROJECT.conn_manager.useConn(args[0])
            if not conn_db.isOpen():
                if (
                    conn_db._driver_name
                    and conn_db._driver_sql
                    and conn_db._driver_sql.loadDriver(conn_db._driver_name)
                ):
                    main_conn = application.PROJECT.conn_manager.mainConn()
                    conn_db._driver = conn_db._driver_sql.driver()
                    conn_db.conn = conn_db.conectar(
                        main_conn._db_name,
                        main_conn._db_host,
                        main_conn._db_port,
                        main_conn._db_user_name,
                        main_conn._db_password,
                    )
                    if conn_db.conn is False:
                        return False

                    conn_db._is_open = True

        else:
            conn_db = application.PROJECT.conn_manager.useConn(args[6])
            if not conn_db.isOpen():
                if conn_db._driver_sql is None:
                    raise Exception("driverSql not loaded!")
                conn_db._driver_name = args[0].lower()
                if conn_db._driver_name and conn_db._driver_sql.loadDriver(conn_db._driver_name):
                    conn_db.conn = conn_db.conectar(args[1], args[4], args[5], args[2], args[3])

                    if isinstance(conn_db.conn, bool):
                        return False

                    # conn_db.driver().db_ = conn_db
                    conn_db._is_open = True
                    # conn_db._dbAux = conn_db

        return True

    @classmethod
    def removeDatabase(self, conn_name: str = "default") -> Any:
        """Remove a database."""
        return application.PROJECT.conn_manager.removeConn(conn_name)

    @classmethod
    def idSession(self) -> str:
        """Get Session ID."""
        # FIXME: Code copied from flapplication.aqApp
        return self.time_user_.toString(QtCore.Qt.ISODate)

    @classmethod
    def reportChanges(self, changes: Dict[str, str] = {}):
        """Create a report for project changes."""
        ret = u""
        # DEBUG:: FOR-IN: ['key', 'changes']
        for key in changes:
            if key == u"size":
                continue
            chg = changes[key].split("@")
            ret += "Nombre: %s \n" % chg[0]
            ret += "Estado: %s \n" % chg[1]
            ret += "ShaOldTxt: %s \n" % chg[2]
            ret += "ShaNewTxt: %s \n" % chg[4]
            ret += u"###########################################\n"

        return ret

    @classmethod
    def diffXmlFilesDef(self, xml_old: QtXml.QDomNode, xml_new: QtXml.QDomNode) -> Dict[str, Any]:
        """Create a Diff for XML."""
        array_old = self.filesDefToArray(xml_old)
        array_new = self.filesDefToArray(xml_new)
        ret: Dict[str, Any] = {}
        size = 0
        # DEBUG:: FOR-IN: ['key', 'array_old']
        for key in array_old:
            if key not in array_new:
                info = [key, "del", array_old[key]["shatext"], array_old[key]["shabinary"], "", ""]
                ret[key] = "@".join(info)
                size += 1
        # DEBUG:: FOR-IN: ['key', 'array_new']

        for key in array_new:
            if key not in array_old:
                info = [key, "new", "", "", array_new[key]["shatext"], array_new[key]["shabinary"]]
                ret[key] = "@".join(info)
                size += 1
            else:
                if (
                    array_new[key]["shatext"] != array_old[key]["shatext"]
                    or array_new[key]["shabinary"] != array_old[key]["shabinary"]
                ):
                    info = [
                        key,
                        "mod",
                        array_old[key]["shatext"],
                        array_old[key]["shabinary"],
                        array_new[key]["shatext"],
                        array_new[key]["shabinary"],
                    ]
                    ret[key] = "@".join(info)
                    size += 1

        ret["size"] = size
        return ret

    @classmethod
    def filesDefToArray(self, xml: QtXml.QDomNode) -> Dict[str, Dict[str, str]]:
        """Convert Module MOD xml to array."""
        root = xml.firstChild()
        files = root.childNodes()
        ret = {}
        i = 0
        while i < len(files):
            item = files.item(i)
            fil = {
                "id": item.namedItem(u"name").toElement().text(),
                "module": item.namedItem(u"module").toElement().text(),
                "text": item.namedItem(u"text").toElement().text(),
                "shatext": item.namedItem(u"shatext").toElement().text(),
                "binary": item.namedItem(u"binary").toElement().text(),
                "shabinary": item.namedItem(u"shabinary").toElement().text(),
            }
            i += 1
            if len(fil["id"]) == 0:
                continue
            ret[fil["id"]] = fil

        return ret

    @classmethod
    def textPacking(self, ext: str = "") -> bool:
        """Determine if file is text."""
        return ext.endswith(
            (
                ".ui",
                ".qry",
                ".kut",
                ".jrxml",
                ".ar",
                ".mtd",
                ".ts",
                ".qs",
                ".py",
                ".xml",
                ".xpm",
                ".svg",
            )
        )

    @classmethod
    def binaryPacking(self, ext: str = "") -> bool:
        """Determine if file is binary."""
        return ext.endswith(".qs")

    @classmethod
    def infoMsgBox(self, msg: str = "") -> None:
        """Show information message box."""
        msg = ustr(msg)
        msg += u"\n"
        if self.interactiveGUI():
            # QtWidgets.QMessageBox.information(
            #    QtWidgets.QApplication.focusWidget(), "Eneboo", msg, QtWidgets.QMessageBox.Ok
            # )
            application.PROJECT.message_manager().send("msgBoxInfo", None, [msg])
        else:
            LOGGER.warning(ustr(u"INFO: ", msg))

    @classmethod
    def warnMsgBox(self, msg: str = "", *buttons: Any) -> None:
        """Show Warning message box."""
        new_list = []
        new_list.append("%s.\n" % ustr(msg))
        for button in buttons:
            new_list.append(button)

        if self.interactiveGUI():
            # QtWidgets.QMessageBox.warning(
            #    QtWidgets.QApplication.focusWidget(), "Eneboo", msg, QtWidgets.QMessageBox.Ok
            # )
            application.PROJECT.message_manager().send("msgBoxWarning", None, new_list)
        else:
            LOGGER.warning(ustr(u"WARN: ", msg))

    @classmethod
    def errorMsgBox(self, msg: str = None) -> None:
        """Show error message box."""
        msg = ustr(msg)
        msg += u"\n"
        if self.interactiveGUI():
            # QtWidgets.QMessageBox.critical(
            #    QtWidgets.QApplication.focusWidget(), "Eneboo", msg, QtWidgets.QMessageBox.Ok
            # )
            application.PROJECT.message_manager().send("msgBoxError", None, [msg])
        else:
            LOGGER.warning(ustr(u"ERROR: ", msg))

    @classmethod
    def translate(self, text: str, arg2: Optional[str] = None) -> str:
        """Translate text."""
        if arg2:
            return arg2
        return text

    @classmethod
    def _warnHtmlPopup(self, html: str, options: List) -> None:
        """Show a fancy html popup."""
        raise Exception("not implemented.")

    @classmethod
    def infoPopup(self, msg: Optional[str] = None) -> None:
        """Show information popup."""
        msg = ustr(msg)
        caption = self.translate(u"AbanQ Información")
        msg = msg.replace("\n", "<br>")
        msg_html = ustr(
            u'<img source="about.png" align="right">',
            u"<b><u>",
            caption,
            u"</u></b><br><br>",
            msg,
            u"<br>",
        )
        self._warnHtmlPopup(msg_html, [])

    @classmethod
    def warnPopup(self, msg: str = "") -> None:
        """Show warning popup."""
        msg = ustr(msg)
        msg = msg.replace("\n", "<br>")
        caption = self.translate(u"AbanQ Aviso")
        msg_html = ustr(
            u'<img source="bug.png" align="right">',
            u"<b><u>",
            caption,
            u"</u></b><br><br>",
            msg,
            u"<br>",
        )
        self._warnHtmlPopup(msg_html, [])

    @classmethod
    def errorPopup(self, msg: str = "") -> None:
        """Show error popup."""
        msg = ustr(msg)
        msg = msg.replace("\n", "<br>")
        caption = self.translate(u"AbanQ Error")
        msg_html = ustr(
            u'<img source="remove.png" align="right">',
            u"<b><u>",
            caption,
            u"</u></b><br><br>",
            msg,
            u"<br>",
        )
        self._warnHtmlPopup(msg_html, [])

    @classmethod
    def trTagText(self, tag_text: str = "") -> str:
        """Process QT_TRANSLATE_NOOP tags."""
        if not tag_text.startswith(u"QT_TRANSLATE_NOOP"):
            return tag_text
        txt = tag_text[len("QT_TRANSLATE_NOOP") + 1 :]
        txt = "[%s]" % txt[0 : len(txt) - 1]
        arr = ast.literal_eval(txt)  # FIXME: Don't use "ast.literal_eval"
        return self.translate(arr[0], arr[1])

    @classmethod
    def updatePineboo(self) -> None:
        """Execute auto-updater."""
        QtWidgets.QMessageBox.warning(
            QtWidgets.QApplication.focusWidget(),
            "Pineboo",
            self.translate(u"Funcionalidad no soportada aún en Pineboo."),
            QtWidgets.QMessageBox.Ok,
        )
        return

    @classmethod
    def setObjText(self, container: QtWidgets.QWidget, component: str, value: str = "") -> bool:
        """Set text to random widget."""
        object_ = self.testObj(container, component)
        if object_ is None:
            return False
        clase = object_.__class__.__name__

        if clase in ["QPushButton", "QToolButton"]:
            pass
        elif clase == u"QLabel":
            self.runObjMethod(container, component, u"text", value)
        elif clase == u"FLFieldDB":
            self.runObjMethod(container, component, u"setValue", value)
        else:
            return False
        return True

    @classmethod
    def disableObj(self, container: QtWidgets.QWidget, component: str) -> bool:
        """Disable random widget."""
        object_ = self.testObj(container, component)
        if not object_:
            return False

        clase = object_.__class__.__name__

        if clase in ["QToolButton", "QPushButton"]:
            self.runObjMethod(container, component, u"setEnabled", False)
        elif clase == u"FLFieldDB":
            self.runObjMethod(container, component, u"setDisabled", True)
        else:
            return False

        return True

    @classmethod
    def enableObj(self, container: QtWidgets.QWidget, component: str) -> bool:
        """Enable random widget."""
        object_ = self.testObj(container, component)
        if not object_:
            return False

        clase = object_.__class__.__name__

        if clase == u"QPushButton":
            pass
        elif clase == u"QToolButton":
            self.runObjMethod(container, component, u"setEnabled", True)
        elif clase == u"FLFieldDB":
            self.runObjMethod(container, component, u"setDisabled", False)
        else:
            return False
        return True

    @classmethod
    def filterObj(self, container: QtWidgets.QWidget, component: str, filter: str = "") -> bool:
        """Apply filter to random widget."""
        object_ = self.testObj(container, component)
        if object_ is None:
            return False

        clase = object_.__class__.__name__

        if clase == u"FLTableDB":
            pass
        elif clase == u"FLFieldDB":
            self.runObjMethod(container, component, u"setFilter", filter)
        else:
            return False

        return True

    @classmethod
    def testObj(
        self, container: QtWidgets.QWidget = None, component: str = ""
    ) -> Optional[QtWidgets.QWidget]:
        """Test if object does exist."""

        if not container or container is None:
            return None
        object_ = cast(QtWidgets.QWidget, container.findChild(QtWidgets.QWidget, component))
        if not object_:
            LOGGER.warning(ustr(component, u" no existe"))
            return None
        return object_

    @classmethod
    def testAndRun(
        self, container: QtWidgets.QWidget, component: str, method: str = "", param: Any = None
    ) -> bool:
        """Test and execute object."""
        object_ = self.testObj(container, component)
        if not object_:
            return False
        if not self.runObjMethod(container, component, method, param):
            return False
        return True

    @classmethod
    def runObjMethod(
        self, container: QtWidgets.QWidget, component: str, method: str, param: Any = None
    ) -> bool:
        """Execute method from object."""
        object_ = cast(QtWidgets.QWidget, container.findChild(QtWidgets.QWidget, component))
        attr = getattr(object_, method, None)
        if attr is not None:
            attr(param)
        else:
            LOGGER.warning(ustr(method, u" no existe"))

        return True

    @classmethod
    def connectSS(
        self, sender: QtWidgets.QWidget, signal: str, receiver: QtWidgets.QWidget, slot: str
    ) -> bool:
        """Connect signal to slot."""
        if not sender:
            return False
        connections.connect(sender, signal, receiver, slot)
        return True

    @classmethod
    def openUrl(self, url: Union[str, List[str]] = "") -> bool:
        """Open given URL in a browser."""
        if not url:
            return False

        if isinstance(url, List):
            url = url[0]

        os_name = self.osName()
        if os_name == "LINUX":
            if self.launchCommand([u"xdg-open", url]):
                return True
            elif self.launchCommand([u"gnome-open", url]):
                return True
            elif self.launchCommand([u"kfmclient openURL", url]):
                return True
            elif self.launchCommand([u"kfmclient exec", url]):
                return True
            elif self.launchCommand([u"firefox", url]):
                return True
            elif self.launchCommand([u"mozilla", url]):
                return True
            elif self.launchCommand([u"opera", url]):
                return True
            elif self.launchCommand([u"google-chrome", url]):
                return True
            return False

        elif os_name == u"WIN32":
            if url.startswith(u"mailto"):
                url = url.replace("&", "^&")
            return self.launchCommand([u"cmd.exe", u"/C", u"start", u"", url])

        elif os_name == u"MACX":
            return self.launchCommand([u"open", url])

        return False

    @classmethod
    def launchCommand(self, comando: Union[str, List[str]]) -> bool:
        """Execute a program."""
        try:
            proc = Process()
            proc.execute(comando)
            return True
        except Exception:
            LOGGER.error(traceback.format_exc())
            return False
