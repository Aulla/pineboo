"""Flmanagermodules module."""

# -*- coding: utf-8 -*-
from PyQt6 import QtWidgets, QtGui  # type: ignore[import]

from pineboolib.core import decorators
from pineboolib.core.utils import utils_base
from pineboolib.core import settings

from pineboolib.application.metadata import pnaction
from pineboolib.application.staticloader import pnmodulesstaticloader


from pineboolib.application.utils import path, xpm, convert_flaction


from pineboolib import application
from pineboolib.application.utils.path import _path


from . import flutil
from . import flformdb
from . import flformrecorddb

from pineboolib import logging

from typing import Union, List, Dict, Optional, cast, Any, TYPE_CHECKING
from watchdog import observers, events  # type: ignore [import] # noqa: F821
import os
import codecs

from xml.etree import ElementTree as ET

if TYPE_CHECKING:
    from pineboolib.application import xmlaction  # noqa: F401 # pragma: no cover
    from pineboolib.interfaces import iconnection, isqlcursor  # noqa : F401 # pragma: no cover


"""
Gestor de módulos.

Esta clase permite realizar las funciones básicas de manejo de ficheros
de texto que forman parte de los módulos de aplicación, utilizando como
soporte de almacenamiento la base de datos y el sistema de cachés de texto
para optimizar las lecturas.
Gestiona la carga y descarga de módulos. Mantiene cual es el módulo activo.
El módulo activo se puede establecer en cualquier momento con
FLManagerModules::setActiveIdModule().

Los módulos se engloban en áreas (FACTURACION, FINANCIERA, PRODUCCION, etc..) y
cada módulo tiene varios ficheros de texto XML y scripts. Toda la estructura de
módulos se almacena en las tablas flareas, flmodulos, flserial y flfiles, sirviendo esta
clase como interfaz para el manejo de dicha estructura en el entorno de trabajo
de AbanQ.

@author InfoSiAL S.L.
"""

LOGGER = logging.get_logger(__name__)


class FLManagerModules(object):
    """FLManagerModules class."""

    """
    Mantiene el identificador del módulo activo.
    """
    active_id_module_: str

    """
    Mantiene la clave sha correspondiente a la version de los módulos cargados localmente
    """
    sha_local_: Optional[str]

    """
    Diccionario de claves de ficheros, para optimizar lecturas
    """
    dict_key_files_: Dict[str, str]

    """
    Diccionario de identificadores de modulo de ficheros, para optimizar lecturas
    """
    dict_module_files_: Dict[str, str]

    """
    Uso interno.
    Informacion para la carga estatica desde el disco local
    """
    static_db_info_: "pnmodulesstaticloader.AQStaticBdInfo"
    _file_watcher: "observers.Observer"
    root_dir_: str
    scripts_dir_: str
    tables_dir_: str
    forms_dir_: str
    reports_dir_: str
    queries_dir_: str
    trans_dir_: str
    _files_cached: Dict[str, str]

    def __init__(self, db: "iconnection.IConnection") -> None:
        """Inicialize."""

        if db is None:
            raise ValueError("Database is required")
        self.conn_ = db

        self.commonInit()
        self.active_id_module_ = ""
        self.active_id_area_ = ""
        self.sha_local_ = ""
        self._files_cached = {}
        self.dict_key_files_ = {}

        self.dict_module_files_ = {}

    def commonInit(self) -> None:
        """Run common init."""

        self.static_db_info_ = pnmodulesstaticloader.AQStaticBdInfo(self.conn_)
        self._file_watcher = observers.Observer()
        flfiles_folder = application.PROJECT.USE_FLFILES_FOLDER

        if self.static_db_info_.enabled_ or flfiles_folder:
            num_folders = 0
            LOGGER.warning("STATIC LOAD IS ENABLED!")
            event_handler = events.FileSystemEventHandler()

            if flfiles_folder and application.USE_FLFILES_FOLDER_AS_STATIC_LOAD:
                LOGGER.warning("USING FLFILES_FOLDER AS STATIC LOAD FOLDER!")
                num_folders += 1 if self.addFolder(flfiles_folder, event_handler) else 0
            else:
                self.static_db_info_.readSettings()
                for dir_path in self.static_db_info_.dirs_:
                    LOGGER.warning("STATIC LOAD: %s IS %s", dir_path.path_, dir_path.active_)
                    if dir_path.active_:
                        num_folders += 1 if self.addFolder(dir_path.path_, event_handler) else 0

            if num_folders > 0:
                event_handler.on_any_event = self.static_db_info_.msg_static_changed

                self._file_watcher.start()
                LOGGER.warning("STATIC LOAD IS WORKING")

    def addFolder(self, folder: str, event_handler) -> bool:
        """Add folder."""

        if os.path.exists(folder):
            self._file_watcher.schedule(event_handler, folder, recursive=True)
        else:
            LOGGER.warning("STATIC LOAD: %s FOLDER DOESN'T EXISTS !" % folder)
            return False

        return True

    def reloadStaticLoader(self) -> None:
        """Reload static loader."""
        pnmodulesstaticloader.SHOW_REINIT_MESSAGE = True
        if hasattr(self, "_file_watcher"):
            self._file_watcher.stop()
            del self._file_watcher
        del self.static_db_info_

        self.commonInit()

    def finish(self) -> None:
        """Run tasks when closing the module."""

        del self.dict_module_files_
        self.dict_module_files_ = {}

        del self.static_db_info_
        self.static_db_info_ = pnmodulesstaticloader.AQStaticBdInfo(self.conn_)

        self.writeState()
        del self.dict_key_files_
        self.dict_key_files_ = {}

        del self._files_cached
        self._files_cached = {}

    def content(self, file_name: str) -> str:
        """
        Get the contents of a file stored in the database.

        This method looks for the content of the requested file in the
        database, exactly in the flfiles table, if you can't find it
        Try to get it from the file system.

        @param file_name File name.
        @return QString with the contents of the file or empty in case of error.
        """

        result_conn = (
            self.conn_.connManager()
            .dbAux()
            .execute_query(
                "SELECT contenido FROM flfiles WHERE nombre='%s' AND NOT sha = ''" % file_name
            )
        )
        if result_conn is not None:
            ret = result_conn.first()
            if ret is not None:
                return ret[0]

        return ""

    @decorators.not_implemented_warn
    def byteCodeToStr(self, file_name: str) -> str:
        """
        Get the contents of a script file.

        Get the contents of a script file, processing it to change the connections it contains,
        so that at the end of the execution of the connected function the test script resumes.
        It also performs code formatting processes to optimize it.

        @param file_name File name.
        @return QString with the contents of the file or empty in case of error.
        """
        return ""

    @decorators.not_implemented_warn
    def contentCode(self, file_name: str) -> str:
        """
        Return the contents of a script file.

        Return the contents of a script file processing it to change the connections it contains,
        so that at the end of the execution of the connected function the test script resumes.
        It also performs code formatting processes to optimize it.

        @param file_name File name.
        @return QString with the contents of the file or empty in case of error.
        """
        return ""

    def contentFS(self, path_name: str, utf8: bool = False) -> str:
        """
        Return the contents of a file stored in the file system.

        @param path_name Path and file name in the file system
        @return QString with the contents of the file or empty in case of error.
        """
        encode_ = "UTF-8" if utf8 else "ISO-8859-15"

        try:
            return str(open(path_name, "rb").read(), encode_)
        except Exception:
            LOGGER.warning("Error trying to read %r", path_name, exc_info=True)
            return ""

    def contentCached(self, file_name: str, sha_key=None) -> Optional[str]:
        """
        Get the contents of a file, using the memory and disk cache.

        This method first looks for the content of the requested file in the
        Internal cache, if not, you get it with the FLManagerModules :: content () method.

        @param file_name File name.
        @return QString with the contents of the file or None in case of error.
        """

        sys_table: bool = (
            self.conn_.connManager().manager().isSystemTable(file_name)
            if file_name.endswith(".mtd")
            else False
        )

        data = ""

        if not sys_table and self.static_db_info_ and self.static_db_info_.enabled_:
            data = self.contentStatic(file_name)

        if not data:
            if file_name in self._files_cached.keys():
                data = self._files_cached[file_name]
            else:
                path_file = _path(file_name, False)
                if path_file is not None and os.path.exists(path_file):
                    file_encode = "UTF8" if file_name.endswith((".ts", ".py")) else "ISO-8859-15"

                    file_ = codecs.open(path_file, "r", file_encode)
                    data = file_.read()
                    file_.close()

                elif not application.PROJECT.USE_FLFILES_FOLDER:  # load from database
                    data = self.content(file_name)

        if data:
            self._files_cached[file_name] = data

        return data

    def setContent(self, file_name: str, id_module: str, content: str) -> None:
        """
        Store the contents of a file in a given module.

        @param file_name File name.
        @param id_module Identifier of the module to which the file will be associated
        @param content File content.
        """

        from pineboolib.application.database import pnsqlcursor

        format_val = (
            self.conn_.connManager()
            .manager()
            .formatAssignValue("nombre", "string", file_name, True)
        )
        format_val2 = (
            self.conn_.connManager()
            .manager()
            .formatAssignValue("idmodulo", "string", id_module, True)
        )

        cursor = pnsqlcursor.PNSqlCursor("flfiles", True, "dbAux")
        cursor.setActivatedCheckIntegrity(False)
        cursor.select("%s AND %s" % (format_val, format_val2))

        if cursor.first():
            cursor.setModeAccess(cursor.Edit)
            cursor.refreshBuffer()
        else:
            cursor.setModeAccess(cursor.Insert)
            cursor.refreshBuffer()
            cursor.setValueBuffer("nombre", file_name)
            cursor.setValueBuffer("idmodulo", id_module)

        cursor.setValueBuffer("contenido", content)
        cursor.setValueBuffer("sha", flutil.FLUtil().sha1(content))
        cursor.commitBuffer()

    @staticmethod
    def createUI(
        file_name: str,
        connection: Optional["iconnection.IConnection"] = None,
        parent: Optional["QtWidgets.QWidget"] = None,
    ) -> Optional["QtWidgets.QWidget"]:
        """
        Create a form from its description file.

        Use the FLManagerModules :: contentCached () method to get the XML text it describes the formula.

        @param file_name Name of the file that contains the description of the form.
        @param parent. Parent widget
        @return QWidget corresponding to the built form.
        """

        if ".ui" not in file_name:
            file_name += ".ui"

        form_path = file_name if os.path.exists(file_name) else path._path(file_name, False)
        conn_manager = application.PROJECT.conn_manager

        if "main_conn" in conn_manager.connections_dict.keys():
            mng_modules = conn_manager.managerModules()
            if mng_modules.static_db_info_ and mng_modules.static_db_info_.enabled_:
                static_path = mng_modules.contentStatic(file_name, True)
                if static_path:
                    form_path = static_path

        if not form_path:
            # raise AttributeError("File %r not found in project" % n)
            LOGGER.warning("createUI: No se encuentra el fichero %s", file_name)

            return None

        tree = utils_base.load2xml(form_path)

        if not tree:
            return parent or QtWidgets.QWidget()

        root_ = tree.getroot()

        ui_version = root_.get("version") or "1.0"
        wid = root_.find("widget")
        geometry = []

        if wid is not None:
            for prop in wid.findall("property"):
                if prop.get("name") == "geometry":
                    geometry.append(
                        prop.find("rect")  # type: ignore [union-attr] # noqa: F821
                        .find("width")  # type: ignore [union-attr] # noqa: F821
                        .text
                    )
                    geometry.append(
                        prop.find("rect")  # type: ignore [union-attr] # noqa: F821
                        .find("height")  # type: ignore [union-attr] # noqa: F821
                        .text
                    )
                    break

        if parent is None:

            if wid is None:
                raise Exception("No parent provided and also no <widget> found")
            xclass = wid.get("class")

            if xclass is None:
                raise Exception("class was expected")

            if ui_version < "4.0":
                if xclass == "QMainWindow":
                    from pineboolib.q3widgets import qmainwindow

                    parent = qmainwindow.QMainWindow()
                elif xclass in ["QDialog", "QWidget"]:
                    from pineboolib.q3widgets import qdialog

                    parent = qdialog.QDialog()
            else:
                if xclass == "QMainWindow":
                    parent = QtWidgets.QMainWindow()
                elif xclass in ["QDialog", "QWidget"]:
                    parent = QtWidgets.QDialog()

            if parent is None:
                raise Exception("xclass not found %s" % xclass)

        LOGGER.info("Procesando %s (v%s)", file_name, ui_version)
        if ui_version < "4.0":
            from pineboolib.application.parsers.parser_ui import qt3ui

            qt3ui.load_ui(form_path, parent)
        else:
            from PyQt6 import uic  # type: ignore

            qt_widgets_path = utils_base.filedir("plugins/custom_widgets")
            if qt_widgets_path not in uic.widgetPluginPath:
                LOGGER.info("Añadiendo path %s a uic.widgetPluginPath", qt_widgets_path)
                uic.widgetPluginPath.append(qt_widgets_path)

            uic.loadUi(form_path, parent)

        if geometry[0]:
            form_parent: Any = parent
            if parent.parent() is not None:
                form_parent = parent.parent()
            form_parent.resize(
                int(geometry[0]), int(geometry[1])  # type: ignore [arg-type] # noqa: F821
            )
        return parent

    def createForm(
        self,
        action: Union["pnaction.PNAction", "xmlaction.XMLAction"],
        connector: Optional["iconnection.IConnection"] = None,
        parent: Optional["QtWidgets.QWidget"] = None,
        name: Optional[str] = None,
    ) -> "flformdb.FLFormDB":
        """
        Create the master form of an action from its description file.

        Use the FLManagerModules :: createUI () method to get the built form.

        @param to FLAction Object.
        @return QWidget corresponding to the built form.
        """

        if not isinstance(action, pnaction.PNAction):
            action = convert_flaction.convert_to_flaction(action)

        if action is None:
            raise Exception("action is empty!.")

        # if parent is None:
        #    from pineboolib.fllegacy import flapplication

        #    parent = flapplication.aqApp.mainWidget()

        return flformdb.FLFormDB(action, parent, load=True)

    def createFormRecord(
        self,
        action: Union["pnaction.PNAction", "xmlaction.XMLAction"],
        connector: Optional["iconnection.IConnection"] = None,
        parent_or_cursor: Optional[Union["isqlcursor.ISqlCursor", "QtWidgets.QWidget"]] = None,
        name: Optional[str] = None,
    ) -> "flformrecorddb.FLFormRecordDB":
        """
        Create the record editing form of an action from its description file.

        @param action. Action
        @param connector. Connector used
        @param parent_or_cursor. Cursor or parent of the form
        @param name. FormRecord name
        """

        LOGGER.trace("createFormRecord: init")

        # Falta implementar conector y name
        if not isinstance(action, pnaction.PNAction):
            LOGGER.trace("createFormRecord: convert2FLAction")

            action = convert_flaction.convert_to_flaction(action)

        if action is None:
            raise Exception("action is empty!")

        LOGGER.trace("createFormRecord: load FormRecordDB")
        return flformrecorddb.FLFormRecordDB(action, parent_or_cursor, load=False)

    def setActiveIdModule(self, id_module: str = "") -> None:
        """
        Set the active module.

        It also automatically establishes the area corresponding to the module,
        since a module can only belong to a single area.

        @param id_module Module identifier
        """

        self.active_id_module_ = (
            id_module if id_module in application.PROJECT.modules.keys() else ""
        )

    def activeIdArea(self) -> str:
        """
        Return the area of the active module.

        @return Area identifier
        """

        return (
            application.PROJECT.modules[self.active_id_module_].areaid
            if self.active_id_module_ in application.PROJECT.modules
            else ""
        )

    def activeIdModule(self) -> str:
        """
        Return the active module.

        @return Module identifier
        """

        return self.active_id_module_

    def listIdAreas(self) -> List[str]:
        """
        Return the list of area identifiers loaded in the system.

        @return List of area identifiers
        """

        return list(application.PROJECT.areas.keys())

    def listIdModules(self, id_area: str) -> List[str]:
        """
        Return the list of module identifiers loaded into the system of a given area.

        @param id_area Identifier of the area from which you want to get the modules list
        @return List of module identifiers
        """

        return [
            key
            for key in application.PROJECT.modules.keys()
            if application.PROJECT.modules[key].areaid == id_area
        ]

    def listAllIdModules(self) -> List[str]:
        """
        Return the list of identifiers of all modules loaded in the system.

        @return List of module identifiers
        """

        return [key for key in application.PROJECT.modules.keys()]

    def idAreaToDescription(self, id_area: str = "") -> str:
        """
        Return the description of an area from its identifier.

        @param id_area Area identifier.
        @return Area description text, if found or idA if not found.
        """

        return (
            application.PROJECT.areas[id_area].descripcion
            if id_area in application.PROJECT.areas.keys()
            else ""
        )

    def idModuleToDescription(self, id_module: str = "") -> str:
        """
        Return the description of a module from its identifier.

        @param id_module Module identifier.
        @return Module description text, if found or idM if not found.
        """

        return (
            application.PROJECT.modules[id_module].description
            if id_module in application.PROJECT.modules.keys()
            else ""
        )

    def iconModule(self, id_module: str) -> "QtGui.QPixmap":
        """
        To obtain the icon associated with a module.

        @param id_moule Identifier of the module from which to obtain the icon
        @return QPixmap with the icon
        """

        return (
            QtGui.QPixmap(xpm.cache_xpm(application.PROJECT.modules[id_module].icon))
            if id_module in application.PROJECT.modules.keys()
            else QtGui.QPixmap()
        )

    def versionModule(self, id_module: str) -> str:
        """
        Return the version of a module.

        @param id_module Identifier of the module whose version you want to know
        @return Chain with version
        """

        return (
            application.PROJECT.modules[id_module].version
            if id_module in application.PROJECT.modules.keys()
            else id_module
        )

    def shaLocal(self) -> Optional[str]:
        """
        To obtain the local sha key.

        @return Sha key of the locally loaded modules version
        """

        return self.sha_local_

    def shaGlobal(self) -> str:
        """
        To get the global sha key.

        @return Sha key of the globally loaded modules version
        """

        if not self.conn_.connManager().dbAux():
            return ""

        from pineboolib.application.database import pnsqlquery

        qry = pnsqlquery.PNSqlQuery(None, "dbAux")
        qry.setForwardOnly(True)
        qry.exec_("SELECT sha FROM flserial")
        if qry.lastError is None:
            return "error"

        return str(qry.value(0)) if qry.next() else ""

    def setShaLocalFromGlobal(self) -> None:
        """
        Set the value of the local sha key with that of the global one.
        """

        self.sha_local_ = self.shaGlobal()

    def shaOfFile(self, file_name: str) -> str:
        """
        Get the sha key associated with a stored file.

        @param file_name File name
        @return Key sh associated with the files
        """
        ret_ = ""
        if not self.conn_.connManager().manager().isSystemTable(file_name):
            if file_name in application.PROJECT.files.keys():
                ret_ = application.PROJECT.files[file_name].sha or ""

        return ret_

    def loadKeyFiles(self) -> None:
        """
        Load the sha1 keys of the files into the key dictionary.
        """

        self.dict_key_files_ = {}
        self.dict_module_files_ = {}

        from pineboolib.application.database import pnsqlquery

        qry = pnsqlquery.PNSqlQuery(None, "dbAux")
        # qry.setForwardOnly(True)
        qry.exec_("SELECT nombre, sha, idmodulo FROM flfiles")

        while qry.next():
            name = str(qry.value(0))
            self.dict_key_files_[name] = str(qry.value(1))
            self.dict_module_files_[name.upper()] = str(qry.value(2))

    @decorators.deprecated
    def loadAllIdModules(self) -> None:
        """
        Load the list of all module identifiers.
        """

        # =======================================================================
        # self.dict_info_mods_ = {}
        # for id_module in application.PROJECT.modules.keys():
        #     info_module_ = pninfomod.PNInfoMod()
        #     info_module_.id_modulo = id_module
        #     info_module_.id_area = application.PROJECT.modules[id_module].areaid
        #     info_module_.descripcion = application.PROJECT.modules[id_module].description
        #     info_module_.version = ""
        #     info_module_.icono = application.PROJECT.modules[id_module].icon
        #     info_module_.area_descripcion = application.PROJECT.areas[
        #         application.PROJECT.modules[id_module].areaid
        #     ].descripcion
        #     self.dict_info_mods_[info_module_.id_modulo.upper()] = info_module_
        # =======================================================================

    @decorators.deprecated
    def loadIdAreas(self) -> None:
        """
        Load the list of all area identifiers.
        """

        pass
        # for key in application.PROJECT.areas.keys():
        #    self.dict_areas[key] = application.PROJECT.areas[key].descripcion

    @decorators.not_implemented_warn
    def checkSignatures(self):
        """
        Check the signatures for a given module.
        """

        pass

    def idModuleOfFile(self, name: str = "") -> str:
        """
        Return the identifier of the module to which a given file belongs.

        @param n File name including extension
        @return Identifier of the module to which the file belongs
        """
        if name.endswith(".mtd"):
            if application.PROJECT.conn_manager.manager().isSystemTable(name):
                return "sys"
            elif "%s_model.py" % name[:-4] in application.PROJECT.files.keys():
                return application.PROJECT.files["%s_model.py" % name[:-4]].module

        elif name in application.PROJECT.files.keys():
            return application.PROJECT.files[name].module
        else:
            LOGGER.warning(
                "Can't found %s ** %s", name, application.PROJECT.files.keys(), stack_info=True
            )

        return ""

    def writeState(self) -> None:
        """
        Save the status of the module system.
        """

        id_db = "noDB"
        db_aux = self.conn_.connManager().dbAux()
        if db_aux:
            id_db = "%s%s%s%s%s" % (
                db_aux.database(),
                db_aux.host(),
                db_aux.user(),
                db_aux.driverName(),
                db_aux.port(),
            )

        if self.active_id_area_ is None:
            self.active_id_area_ = ""

        if self.active_id_module_ is None:
            self.active_id_module_ = ""

        if self.sha_local_ is None:
            raise ValueError("sha_local_ is empty!")

        settings.SETTINGS.setValue("Modules/activeIdModule/%s" % id_db, self.active_id_module_)
        settings.SETTINGS.setValue("Modules/activeIdArea/%s" % id_db, self.active_id_area_)
        settings.SETTINGS.setValue("Modules/shaLocal/%s" % id_db, self.sha_local_)

    def readState(self) -> None:
        """
        Read the module system status.
        """
        db_aux = self.conn_.connManager().dbAux()

        if db_aux:
            id_db = "%s%s%s%s%s" % (
                db_aux.database(),
                db_aux.host(),
                db_aux.user(),
                db_aux.driverName(),
                db_aux.port(),
            )

            self.active_id_module_ = settings.SETTINGS.value(
                "Modules/activeIdModule/%s" % id_db, None
            )
            self.active_id_area_ = settings.SETTINGS.value("Modules/activeIdArea/%s" % id_db, None)
            self.sha_local_ = settings.SETTINGS.value("Modules/shaLocal/%s" % id_db, None)

            if (
                self.active_id_module_ is None
                or self.active_id_module_ not in self.listAllIdModules()
            ):
                self.active_id_module_ = ""

    def contentStatic(self, file_name: str, only_path: bool = False) -> str:
        """
        Return the contents of a file by static loading from the local disk.

        @param file_name File name.
        @return String with the contents of the file or None in case of error.
        """

        str_ret = pnmodulesstaticloader.PNStaticLoader.content(
            file_name, self.static_db_info_, only_path
        )
        if str_ret:
            mng = application.PROJECT.conn_manager.manager()
            text_ = ""
            util = flutil.FLUtil()
            sha = util.sha1(str_ret)
            if file_name in self.dict_key_files_.keys():
                text_ = self.dict_key_files_[file_name]

            if text_ == sha:
                return ""

            elif self.dict_key_files_ and file_name.find(".qs") > -1:
                self.dict_key_files_[file_name] = sha

            if file_name.endswith(".mtd"):
                mtd = mng.metadata(ET.fromstring(str_ret), True)

                if mtd is not None and not mtd.isQuery():
                    conn_ = application.PROJECT.conn_manager.useConn("dbaux")
                    if not conn_.existsTable(mtd.name()):
                        conn_.createTable(mtd)
                    elif conn_.canRegenTables():
                        conn_.regenTable(mtd.name(), mtd)

        return str_ret

    def staticLoaderSetup(self) -> None:
        """
        Display dialog box to configure static load from local disk.
        """
        ui_ = cast(
            QtWidgets.QDialog,
            self.createUI(utils_base.filedir("./application/staticloader/ui/static_loader.ui")),
        )
        pnmodulesstaticloader.PNStaticLoader.setup(self.static_db_info_, ui_)
