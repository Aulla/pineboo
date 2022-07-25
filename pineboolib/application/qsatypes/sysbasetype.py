"""
SysBaseType for QSA.

Will be inherited at fllegacy.
"""

import platform
import traceback
import ast

from typing import Any, Dict, Optional, List, Union

from PyQt6 import QtWidgets, QtXml, QtCore

from pineboolib.core import settings, decorators
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

    @classmethod
    def nameUser(cls) -> str:
        """Get current database user."""

        ret_ = (
            application.PROJECT.DGI.get_nameuser()
            if application.PROJECT.DGI.use_alternative_credentials()
            else application.PROJECT.conn_manager.mainConn().user()
        )

        return ret_ or ""

    # @classmethod
    # def interactiveGUI(cls) -> str:
    #    """Check if running in GUI mode."""
    #    return application.PROJECT.DGI.interactiveGUI()

    @classmethod
    def isUserBuild(cls) -> bool:
        """Check if this build is an user build."""
        return cls.version().upper().find("USER") > -1

    @classmethod
    def isDeveloperBuild(cls) -> bool:
        """Check if this build is a developer build."""
        return cls.version().upper().find("DEVELOPER") > -1

    @classmethod
    def isNebulaBuild(cls) -> bool:
        """Check if this build is a nebula build."""
        return cls.version().upper().find("NEBULA") > -1

    @classmethod
    def isDebuggerMode(cls) -> bool:
        """Check if running in debugger mode."""
        return bool(settings.CONFIG.value("application/isDebuggerMode", False))

    @classmethod
    @decorators.not_implemented_warn
    def isCloudMode(cls) -> bool:
        """Check if running on cloud mode."""
        return False

    @classmethod
    def isDebuggerEnabled(cls) -> bool:
        """Check if this debugger is on."""
        return bool(application.PROJECT._db_admin_mode)

    @classmethod
    def isQuickBuild(cls) -> bool:
        """Check if this build is a Quick build."""
        return not cls.isDebuggerEnabled()

    @classmethod
    def isLoadedModule(cls, modulename: str) -> bool:
        """Check if a module has been loaded."""
        return modulename in application.PROJECT.conn_manager.managerModules().listAllIdModules()

    @classmethod
    def osName(cls) -> str:
        """
        Get operating system name.

        @return Código del sistema operativo (WIN32, LINUX, MACX)
        """
        if platform.system() == "Windows":
            return "WIN32"
        elif platform.system() in ["Linux", "Linux2"]:
            return "LINUX"
        elif platform.system() == "Darwin":
            return "MACX"
        else:
            return platform.system()

    @classmethod
    def nameBD(cls) -> str:
        """Get database name."""
        return application.PROJECT.conn_manager.mainConn().DBName()

    @classmethod
    def toUnicode(cls, val: str, format_encode: str) -> str:
        """Convert string to unicode."""
        return val.encode(format_encode, "replace").decode("utf-8", "replace")

    @classmethod
    def fromUnicode(cls, val: str, format_encode: str) -> str:
        """Convert from unicode to string."""
        return val.encode("utf-8", "replace").decode(format_encode, "replace")

    @classmethod
    def Mr_Proper(cls) -> None:
        """Cleanup database like Mr. Proper."""
        application.PROJECT.conn_manager.mainConn().Mr_Proper()

    @classmethod
    def installPrefix(cls) -> str:
        """Get folder where app is installed."""
        return filedir("..")

    @classmethod
    def version(cls) -> str:
        """Get version number as string."""
        return str(application.PROJECT.load_version())

    @classmethod
    def processEvents(cls) -> None:
        """Process event loop."""
        QtWidgets.QApplication.processEvents()

    @classmethod
    def write(cls, encode_: str, dir_: str, contenido: str) -> None:
        """Write to file."""
        from pineboolib.application.types import File

        file_iso = File(dir_, encode_)
        file_iso.write(contenido)
        file_iso.close()

    @classmethod
    def cleanupMetaData(cls, conn_name: str = "default") -> None:
        """Clean up metadata."""
        application.PROJECT.conn_manager.manager().cleanupMetaData()

    @classmethod
    def nameDriver(cls, conn_name: str = "default") -> str:
        """Get driver name."""
        return application.PROJECT.conn_manager.useConn(conn_name).driverName()

    @classmethod
    def nameHost(cls, conn_name: str = "default") -> str:
        """Get database host name."""
        return application.PROJECT.conn_manager.useConn(conn_name).host()

    @classmethod
    def addDatabase(
        cls,
        driver_or_conn: str,
        db_name: str = "",
        db_user: str = "",
        db_pw: str = "",
        db_host: str = "",
        db_port: int = 0,
        conn_name: str = "",
    ) -> bool:
        """Add a new database."""

        mng_ = application.PROJECT.conn_manager
        conn_db = None
        new_conn = False

        if not db_name:
            conn_db = mng_.useConn(driver_or_conn)
        else:
            if not conn_name:
                raise Exception(
                    "Invalid connection data. conn_name: %s, driver_name: %s, database_name: %s, user_name: %s, db_host: %s, port: %s"
                    % (conn_name, driver_or_conn, db_name, db_user, db_host, db_port)
                )
            new_conn = True
            conn_db = mng_.useConn(conn_name, db_name)

        if not conn_db.isOpen():
            conn_db_name = db_name
            conn_db_host = db_host
            conn_db_port = db_port
            conn_db_user = db_user
            conn_db_pass = db_pw

            if new_conn:
                conn_db._driver_name = driver_or_conn.lower()
            else:
                main_conn = mng_.mainConn()
                conn_db_name = main_conn._db_name
                conn_db_host = main_conn._db_host
                conn_db_port = main_conn._db_port
                conn_db_user = main_conn._db_user_name
                conn_db_pass = main_conn._db_password

            if mng_._drivers_sql_manager.loadDriver(conn_db._driver_name):
                conn_db.conn = conn_db.conectar(
                    conn_db_name, conn_db_host, conn_db_port, conn_db_user, conn_db_pass
                )

                if isinstance(conn_db.conn, bool):
                    return False

                conn_db._is_open = True

        else:
            LOGGER.warning("addDatabase: '%s' connection is already open", conn_name)

        return True

    @classmethod
    def removeDatabase(cls, conn_name: str = "default") -> bool:
        """Remove a database."""
        return application.PROJECT.conn_manager.removeConn(conn_name)

    @classmethod
    def idSession(cls) -> str:
        """Get Session ID."""

        # FIXME: Code copied from flapplication.aqApp
        return application.ID_SESSION

    @classmethod
    def reportChanges(cls, changes: Dict[str, str] = {}):
        """Create a report for project changes."""
        ret = ""
        # DEBUG:: FOR-IN: ['key', 'changes']
        for key in changes.keys():
            if key == "size":
                continue
            chg = changes[key].split("@")
            ret += "Nombre: %s \n" % chg[0]
            ret += "Estado: %s \n" % chg[1]
            ret += "ShaOldTxt: %s \n" % chg[2]
            ret += "ShaNewTxt: %s \n" % chg[3]
            ret += "###########################################\n"

        return ret

    @classmethod
    def diffXmlFilesDef(
        cls, xml_old: "QtXml.QDomNode", xml_new: "QtXml.QDomNode"
    ) -> Dict[str, Any]:
        """Create a Diff for XML."""
        array_old = cls.filesDefToArray(xml_old)
        array_new = cls.filesDefToArray(xml_new)
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
    def filesDefToArray(cls, xml: "QtXml.QDomNode") -> Dict[str, Dict[str, str]]:
        """Convert Module MOD xml to array."""
        root = xml.firstChild()
        files = root.childNodes()
        ret = {}
        i = 0
        while i < len(files):
            item = files.item(i)
            fil = {
                "id": item.namedItem("name").toElement().text(),
                "module": item.namedItem("module").toElement().text(),
                "text": item.namedItem("text").toElement().text(),
                "shatext": item.namedItem("shatext").toElement().text(),
                "binary": item.namedItem("binary").toElement().text(),
                "shabinary": item.namedItem("shabinary").toElement().text(),
            }
            i += 1
            if len(fil["id"]) == 0:
                continue
            ret[fil["id"]] = fil

        return ret

    @classmethod
    def textPacking(cls, ext: str = "") -> bool:
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
    def binaryPacking(cls, ext: str = "") -> bool:
        """Determine if file is binary."""
        return ext.endswith(".qs")

    @classmethod
    def infoMsgBox(cls, msg: str = "") -> None:
        """Show information message box."""
        msg = ustr(msg)
        msg += "\n"
        application.PROJECT.message_manager().send("msgBoxInfo", None, [msg])

    @classmethod
    def warnMsgBox(cls, msg: str = "", *buttons: Any) -> None:
        """Show Warning message box."""
        new_list = []
        new_list.append("%s.\n" % ustr(msg))
        for button in buttons:
            new_list.append(button)

        application.PROJECT.message_manager().send("msgBoxWarning", None, new_list)

    @classmethod
    def errorMsgBox(cls, msg: str = None) -> None:
        """Show error message box."""
        msg = ustr(msg)
        msg += "\n"

        application.PROJECT.message_manager().send("msgBoxError", None, [msg])

    @classmethod
    def translate(cls, text: str, arg2: Optional[str] = None) -> str:
        """Translate text."""
        if arg2:
            return arg2
        return text

    @classmethod
    def _warnHtmlPopup(cls, html: str, options: List) -> None:
        """Show a fancy html popup."""
        raise Exception("not implemented.")

    @classmethod
    def infoPopup(cls, msg: Optional[str] = None) -> None:
        """Show information popup."""
        msg = ustr(msg)
        caption = cls.translate("AbanQ Información")
        msg = msg.replace("\n", "<br>")
        msg_html = ustr(
            '<img source="about.png" align="right">',
            "<b><u>",
            caption,
            "</u></b><br><br>",
            msg,
            "<br>",
        )
        cls._warnHtmlPopup(msg_html, [])

    @classmethod
    def warnPopup(cls, msg: str = "") -> None:
        """Show warning popup."""
        msg = ustr(msg)
        msg = msg.replace("\n", "<br>")
        caption = cls.translate("AbanQ Aviso")
        msg_html = ustr(
            '<img source="bug.png" align="right">',
            "<b><u>",
            caption,
            "</u></b><br><br>",
            msg,
            "<br>",
        )
        cls._warnHtmlPopup(msg_html, [])

    @classmethod
    def errorPopup(cls, msg: str = "") -> None:
        """Show error popup."""
        msg = ustr(msg)
        msg = msg.replace("\n", "<br>")
        caption = cls.translate("AbanQ Error")
        msg_html = ustr(
            '<img source="remove.png" align="right">',
            "<b><u>",
            caption,
            "</u></b><br><br>",
            msg,
            "<br>",
        )
        cls._warnHtmlPopup(msg_html, [])

    @classmethod
    def trTagText(cls, tag_text: str = "") -> str:
        """Process QT_TRANSLATE_NOOP tags."""
        if not tag_text.startswith("QT_TRANSLATE_NOOP"):
            return tag_text
        txt = tag_text[len("QT_TRANSLATE_NOOP") + 1 :]
        txt = "[%s]" % txt[0 : len(txt) - 1]
        arr = ast.literal_eval(txt)  # FIXME: Don't use "ast.literal_eval"
        return cls.translate(arr[0], arr[1])

    @classmethod
    def updatePineboo(cls) -> None:
        """Execute auto-updater."""
        QtWidgets.QMessageBox.warning(
            QtWidgets.QApplication.focusWidget(),
            "Pineboo",
            cls.translate("Funcionalidad no soportada aún en Pineboo."),
            QtWidgets.QMessageBox.StandardButton.Ok,
        )
        return

    @classmethod
    def setObjText(cls, container: "QtWidgets.QWidget", component: str, value: str = "") -> bool:
        """Set text to random widget."""
        object_ = cls.testObj(container, component)
        if object_ is None:
            return False
        clase = object_.__class__.__name__

        if clase in ["QPushButton", "QToolButton"]:
            pass
        elif clase == "QLabel":
            cls.runObjMethod(container, component, "text", value)
        elif clase == "FLFieldDB":
            cls.runObjMethod(container, component, "setValue", value)
        else:
            return False
        return True

    @classmethod
    def disableObj(cls, container: "QtWidgets.QWidget", component: str) -> bool:
        """Disable random widget."""
        object_ = cls.testObj(container, component)
        if not object_:
            return False

        clase = object_.__class__.__name__

        if clase in ["QToolButton", "QPushButton"]:
            cls.runObjMethod(container, component, "setEnabled", False)
        elif clase == "FLFieldDB":
            cls.runObjMethod(container, component, "setDisabled", True)
        else:
            return False

        return True

    @classmethod
    def enableObj(cls, container: "QtWidgets.QWidget", component: str) -> bool:
        """Enable random widget."""
        object_ = cls.testObj(container, component)
        if not object_:
            return False

        clase = object_.__class__.__name__

        if clase == "QPushButton":
            pass
        elif clase == "QToolButton":
            cls.runObjMethod(container, component, "setEnabled", True)
        elif clase == "FLFieldDB":
            cls.runObjMethod(container, component, "setDisabled", False)
        else:
            return False
        return True

    @classmethod
    def filterObj(cls, container: QtWidgets.QWidget, component: str, filter: str = "") -> bool:
        """Apply filter to random widget."""
        object_ = cls.testObj(container, component)
        if object_ is None:
            return False

        clase = object_.__class__.__name__

        if clase == "FLTableDB":
            pass
        elif clase == "FLFieldDB":
            cls.runObjMethod(container, component, "setFilter", filter)
        else:
            return False

        return True

    @classmethod
    def testObj(
        cls, container: Optional["QtWidgets.QWidget"] = None, component: str = ""
    ) -> Optional[Union["QtCore.QObject", "QtWidgets.QWidget"]]:
        """Test if object does exist."""

        object_ = None
        if container is not None:
            object_ = container.findChild(QtWidgets.QWidget, component)
            if object_ is None:
                child_fun = getattr(container, "child", None)  # type: ignore [unreachable]
                if child_fun is not None:
                    object_ = child_fun(component)

            if object_ is None:
                LOGGER.warning(  # type: ignore [unreachable]
                    "%s no existe en %s", component, container
                )
        return object_

    @classmethod
    def testAndRun(
        cls, container: "QtWidgets.QWidget", component: str, method: str = "", param: Any = None
    ) -> bool:
        """Test and execute object."""
        object_ = cls.testObj(container, component)
        if not object_:
            return False
        if not cls.runObjMethod(container, component, method, param):
            return False
        return True

    @classmethod
    def runObjMethod(
        cls, container: "QtWidgets.QWidget", component: str, method: str, param: Any = None
    ) -> bool:
        """Execute method from object."""
        object_ = cls.testObj(container, component)
        attr = getattr(object_, method, None)
        if attr is not None:
            attr(param)
        else:
            LOGGER.warning("%s no existe en %s", method, component)

        return True

    @classmethod
    def connectSS(
        cls, sender: "QtWidgets.QWidget", signal: str, receiver: "QtWidgets.QWidget", slot: str
    ) -> bool:
        """Connect signal to slot."""
        if not sender:
            return False
        connections.connect(sender, signal, receiver, slot)
        return True

    @classmethod
    def openUrl(cls, url: Union[str, List[str]] = "") -> bool:
        """Open given URL in a browser."""
        if not url:
            return False

        if isinstance(url, List):
            url = url[0]

        os_name = cls.osName()
        if os_name == "LINUX":
            if cls.launchCommand(["xdg-open", url]):
                return True
            elif cls.launchCommand(["gnome-open", url]):
                return True
            elif cls.launchCommand(["kfmclient openURL", url]):
                return True
            elif cls.launchCommand(["kfmclient exec", url]):
                return True
            elif cls.launchCommand(["firefox", url]):
                return True
            elif cls.launchCommand(["mozilla", url]):
                return True
            elif cls.launchCommand(["opera", url]):
                return True
            elif cls.launchCommand(["google-chrome", url]):
                return True
            return False

        elif os_name == "WIN32":
            if url.startswith("mailto"):
                url = url.replace("&", "^&")
            return cls.launchCommand(["cmd.exe", "/C", "start", "", url])

        elif os_name == "MACX":
            return cls.launchCommand(["open", url])

        return False

    @classmethod
    def launchCommand(cls, comando: Union[str, List[str]]) -> bool:
        """Execute a program."""
        try:
            proc = Process()
            proc.execute(comando)
            return True
        except Exception:
            LOGGER.error(traceback.format_exc())
            return False
