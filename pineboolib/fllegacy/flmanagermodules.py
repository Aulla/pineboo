"""Flmanagermodules module."""

# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets

import os
from pineboolib import logging

from pineboolib.core import decorators
from pineboolib.core.utils.utils_base import filedir

from . import flaction
from . import flmodulesstaticloader

from pineboolib.application.database.pnsqlquery import PNSqlQuery


from typing import Union, List, Dict, Any, Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from pineboolib.application.xmlaction import XMLAction  # noqa: F401
    from pineboolib.application.database.pnconnection import PNConnection  # noqa: F401
    from pineboolib.application.database.pnsqlcursor import PNSqlCursor  # noqa: F401
    from PyQt5.QtGui import QPixmap  # noqa: F401


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

logger = logging.getLogger(__name__)


class FLInfoMod(object):
    """FLInfoMod class."""

    idModulo: str
    idArea: str
    descripcion: str
    version: str
    icono: str
    areaDescripcion: str


class FLManagerModules(object):
    """FLManagerModules class."""

    """
    Mantiene el identificador del area a la que pertenece el módulo activo.
    """

    activeIdArea_: Optional[str]

    """
    Mantiene el identificador del módulo activo.
    """
    activeIdModule_: Optional[str]

    """
    Mantiene la clave sha correspondiente a la version de los módulos cargados localmente
    """
    shaLocal_: Optional[str]

    """
    Diccionario de claves de ficheros, para optimizar lecturas
    """
    dictKeyFiles: Dict[str, str]

    """
    Lista de todos los identificadores de módulos cargados, para optimizar lecturas
    """
    listAllIdModules_: List[str]

    """
    Lista de todas los identificadores de areas cargadas, para optimizar lecturas
    """
    listIdAreas_: List[str]

    """
    Diccionario con información de los módulos
    """
    dictInfoMods: Dict[str, FLInfoMod]

    """
    Diccionario de identificadores de modulo de ficheros, para optimizar lecturas
    """
    dictModFiles: Dict[str, str]

    """
    Uso interno.
    Informacion para la carga estatica desde el disco local
    """
    staticBdInfo_: flmodulesstaticloader.AQStaticBdInfo

    root_dir_: str
    scripts_dir_: str
    tables_dir_: str
    forms_dir_: str
    reports_dir_: str
    queries_dir_: str
    trans_dir_: str
    filesCached_: Dict[str, str]

    def __init__(self, db: "PNConnection") -> None:
        """Inicialize."""

        super(FLManagerModules, self).__init__()
        if db is None:
            raise ValueError("Database is required")
        self.conn_ = db

        self.staticBdInfo_ = flmodulesstaticloader.AQStaticBdInfo(self.conn_)
        self.activeIdModule_ = None
        self.activeIdArea_ = None
        self.shaLocal_ = ""
        self.filesCached_ = {}
        self.dictKeyFiles = {}
        self.listAllIdModules_ = []
        self.listIdAreas_ = []
        self.dictInfoMods = {}
        self.dictModFiles = {}

    # """
    # Acciones de inicialización del sistema de módulos.
    # """
    # @decorators.NotImplementedWarn
    # def init(self):
    #    pass

    def finish(self) -> None:
        """Run tasks when closing the module."""

        if self.listAllIdModules_:
            del self.listAllIdModules_
            self.listAllIdModules_ = []

        if self.listIdAreas_:
            del self.listIdAreas_
            self.listIdAreas_ = []

        if self.dictInfoMods:
            del self.dictInfoMods
            self.dictInfoMods = {}

        if self.dictModFiles:
            del self.dictModFiles
            self.dictModFiles = {}

        if self.staticBdInfo_:
            del self.staticBdInfo_

        if self.dictKeyFiles:
            self.writeState()
            del self.dictKeyFiles
            self.dictKeyFiles = {}

        del self

    def content(self, file_name: str) -> Optional[str]:
        """
        Get the contents of a file stored in the database.

        This method looks for the content of the requested file in the
        database, exactly in the flfiles table, if you can't find it
        Try to get it from the file system.

        @param file_name File name.
        @return QString with the contents of the file or empty in case of error.
        """

        cursor = self.conn_.dbAux().execute_query(
            "SELECT contenido FROM flfiles WHERE nombre='%s' AND NOT sha = ''" % file_name
        )

        for contenido in cursor:
            return contenido[0]

        return None

    @decorators.NotImplementedWarn
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

    @decorators.NotImplementedWarn
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
            logger.warn("Error trying to read %r", path_name, exc_info=True)
            return ""

    def contentCached(self, file_name: str, shaKey=None) -> Optional[str]:
        """
        Get the contents of a file, using the memory and disk cache.

        This method first looks for the content of the requested file in the
        Internal cache, if not, you get it with the FLManagerModules :: content () method.

        @param file_name File name.
        @return QString with the contents of the file or None in case of error.
        """
        not_sys_table = file_name[0:3] != "sys" and not self.conn_.manager().isSystemTable(
            file_name
        )
        if not_sys_table and self.staticBdInfo_ and self.staticBdInfo_.enabled_:
            str_ret = self.contentStatic(file_name)
            if str_ret:
                return str_ret

        if file_name in self.filesCached_.keys():
            return self.filesCached_[file_name]

        data = None
        modId = None
        name_ = file_name[: file_name.index(".")]
        ext_ = file_name[file_name.index(".") + 1 :]
        type_ = None
        if ext_ == "kut":
            type_ = "reports/"
        elif ext_ == "qs":
            type_ = "scritps/"
        elif ext_ == "mtd":
            type_ = "tables/"
        elif ext_ == "ui":
            type_ = "forms/"
        elif ext_ == "qry":
            type_ = "queries/"
        elif ext_ == "ts":
            type_ = "translations/"
        elif ext_ == "xml":
            type_ = ""

        if not shaKey and not self.conn_.manager().isSystemTable(name_):

            cursor = self.conn_.execute_query(
                "SELECT sha FROM flfiles WHERE nombre='%s'" % file_name
            )

            for contenido in cursor:
                shaKey = contenido[0]

        if self.conn_.manager().isSystemTable(name_):
            modId = "sys"
        else:
            modId = self.conn_.managerModules().idModuleOfFile(file_name)

        from pineboolib.application import project

        if not project._DGI:
            raise Exception("DGI not loaded")

        if project.DGI.alternative_content_cached():
            data = project.DGI.content_cached(
                project.tmpdir, self.conn_.DBName(), modId, ext_, name_, shaKey
            )
            if data is not None:
                return data

        if data is None:
            """Ruta por defecto"""
            if os.path.exists(
                "%s/cache/%s/%s/file.%s/%s"
                % (project.tmpdir, self.conn_.DBName(), modId, ext_, name_)
            ):
                utf8_ = True if ext_ == "kut" else False
                data = self.contentFS(
                    "%s/cache/%s/%s/file.%s/%s/%s.%s"
                    % (project.tmpdir, self.conn_.DBName(), modId, ext_, name_, shaKey, ext_),
                    utf8_,
                )

        if data is None:
            if os.path.exists(filedir("../share/pineboo/%s%s.%s" % (type_, name_, ext_))):
                data = self.contentFS(filedir("../share/pineboo/%s%s.%s" % (type_, name_, ext_)))
            else:
                data = self.content(file_name)

        if data:
            self.filesCached_[file_name] = data
        return data

    def setContent(self, file_name: str, id_module: str, content: str) -> None:
        """
        Store the contents of a file in a given module.

        @param file_name File name.
        @param id_module Identifier of the module to which the file will be associated
        @param content File content.
        """

        if not self.conn_.dbAux():
            return

        format_val = self.conn_.manager().formatAssignValue("nombre", "string", file_name, True)
        format_val2 = self.conn_.managere().formatAssignValue("idmodulo", "string", id_module, True)

        from pineboolib.fllegacy.flsqlcursor import FLSqlCursor
        from pineboolib.fllegacy.flutil import FLUtil

        cursor = FLSqlCursor("flfiles", True, self.conn_.dbAux())
        cursor.select("%s AND %s" % (format_val, format_val2))

        if cursor.first():
            cursor.setModeAccess(cursor.Edit)
            cursor.refreshBufer()
        else:
            cursor.setModeAccess(cursor.Insert)
            cursor.refreshBufer()
            cursor.setValueBuffer("nombre", file_name)
            cursor.setValueBuffer("idmodulo", id_module)

        cursor.setValueBuffer("contenido", content)
        cursor.setValueBuffer("sha", FLUtil().sha1(content))
        cursor.commitBuffer()

    @staticmethod
    def createUI(
        file_name: str,
        connection: Optional["PNConnection"] = None,
        parent: Optional["QtWidgets.QWidget"] = None,
    ) -> "QtWidgets.QWidget":
        """
        Create a form from its description file.

        Use the FLManagerModules :: contentCached () method to get the XML text it describes the formula.

        @param file_name Name of the file that contains the description of the form.
        @param parent. Parent widget
        @return QWidget corresponding to the built form.
        """

        from pineboolib.application.utils.path import _path
        from pineboolib.application.parsers.qt3uiparser import dgi_qt3ui

        from pineboolib.core.utils.utils_base import filedir, load2xml

        from pineboolib import qt3_widgets

        if ".ui" not in file_name:
            file_name += ".ui"

        form_path = file_name if os.path.exists(file_name) else _path(file_name)

        if form_path is None:
            # raise AttributeError("File %r not found in project" % n)
            logger.debug("createUI: No se encuentra el fichero %s", file_name)

            return QtWidgets.QWidget()

        tree = load2xml(form_path)

        if not tree:
            return parent or QtWidgets.QWidget()

        root_ = tree.getroot()

        UIVersion = root_.get("version")
        if UIVersion is None:
            UIVersion = "1.0"
        if parent is None:
            wid = root_.find("widget")
            if wid is None:
                raise Exception("No parent provided and also no <widget> found")
            xclass = wid.get("class")
            if xclass is None:
                raise Exception("class was expected")
            parent = None
            if xclass == "QMainWindow":
                parent = qt3_widgets.qmainwindow.QMainWindow()
            if xclass == "QDialog":
                parent = qt3_widgets.qdialog.QDialog()

            if parent is None:
                raise Exception("xclass not found %s" % xclass)

        if hasattr(parent, "widget"):
            w_ = parent.widget
        else:
            w_ = parent

        logger.info("Procesando %s (v%s)", file_name, UIVersion)
        if UIVersion < "4.0":
            dgi_qt3ui.loadUi(form_path, w_)
        else:
            from PyQt5 import uic  # type: ignore

            qtWidgetPlugings = filedir("../qtdesigner-plugins")
            if qtWidgetPlugings not in uic.widgetPluginPath:
                logger.info("Añadiendo path %s a uic.widgetPluginPath", qtWidgetPlugings)
                uic.widgetPluginPath.append(qtWidgetPlugings)
            uic.loadUi(form_path, w_)

        return w_

    def createForm(
        self,
        action: Union["flaction.FLAction", "XMLAction"],
        connector: Optional["PNConnection"] = None,
        parent: Optional["QtWidgets.QWidget"] = None,
        name: Optional[str] = None,
    ) -> "QtWidgets.QWidget":
        """
        Create the master form of an action from its description file.

        Use the FLManagerModules :: createUI () method to get the built form.

        @param to FLAction Object.
        @return QWidget corresponding to the built form.
        """
        from . import flformdb

        if not isinstance(action, flaction.FLAction):
            from pineboolib.application.utils.convert_flaction import convert2FLAction

            action = convert2FLAction(action)

        if action is None:
            raise Exception("action is empty!.")

        if parent is None:
            raise Exception("parent is empty!.")

        return flformdb.FLFormDB(parent, action, load=True)

    def createFormRecord(
        self,
        action: Union["flaction.FLAction", "XMLAction"],
        connector: Optional["PNConnection"] = None,
        parent_or_cursor: Optional[Union["PNSqlCursor", "QtWidgets.QWidget"]] = None,
        name: Optional[str] = None,
    ) -> "QtWidgets.QWidget":
        """
        Create the record editing form of an action from its description file.

        @param action. Action
        @param connector. Connector used
        @param parent_or_cursor. Cursor or parent of the form
        @param name. FormRecord name
        """

        logger.trace("createFormRecord: init")
        from . import flformrecorddb

        # Falta implementar conector y name
        if not isinstance(action, flaction.FLAction):
            logger.trace("createFormRecord: convert2FLAction")
            from pineboolib.application.utils.convert_flaction import convert2FLAction

            action = convert2FLAction(action)

        if action is None:
            raise Exception("action is empty!")

        # if parent_or_cursor is None:
        #    raise Exception("parent_or_cursor is empty!.")

        logger.trace("createFormRecord: load FormRecordDB")
        return flformrecorddb.FLFormRecordDB(parent_or_cursor, action, load=False)

    def setActiveIdModule(self, id_module: Optional[str] = None) -> None:
        """
        Set the active module.

        It also automatically establishes the area corresponding to the module,
        since a module can only belong to a single area.

        @param id_module Module identifier
        """

        if id_module is None or not self.dictInfoMods:
            self.activeIdArea_ = None
            self.activeIdModule_ = None
            return

        if id_module.upper() in self.dictInfoMods.keys():
            im = self.dictInfoMods[id_module.upper()]
            self.activeIdArea_ = im.idArea
            self.activeIdModule_ = id_module

    def activeIdArea(self) -> Optional[str]:
        """
        Return the area of ​​the active module.

        @return Area identifier
        """
        return self.activeIdArea_

    def activeIdModule(self) -> Optional[str]:
        """
        Return the active module.

        @return Module identifier
        """

        return self.activeIdModule_

    def listIdAreas(self) -> List[str]:
        """
        Return the list of area identifiers loaded in the system.

        @return List of area identifiers
        """

        if self.listIdAreas_:
            return self.listIdAreas_

        ret: List[str] = []
        if not self.conn_.dbAux():
            return ret

        q = PNSqlQuery(None, self.conn_.dbAux())
        q.setForwardOnly(True)
        q.exec_("SELECT idarea FROM flareas WHERE idarea <> 'sys'")
        while q.next():
            ret.append(str(q.value(0)))

        ret.append("sys")

        return ret

    def listIdModules(self, id_area: str) -> List[str]:
        """
        Return the list of module identifiers loaded into the system of a given area.

        @param id_area Identifier of the area from which you want to get the modules list
        @return List of module identifiers
        """

        list_: List[str] = []
        for mod in self.dictInfoMods.keys():
            if self.dictInfoMods[mod].idArea == id_area:
                list_.append(self.dictInfoMods[mod].idModulo)

        return list_

    def listAllIdModules(self) -> List[str]:
        """
        Return the list of identifiers of all modules loaded in the system.

        @return List of module identifiers
        """

        if self.listAllIdModules_:
            return self.listAllIdModules_

        ret: List[str] = []
        if not self.conn_.dbAux():
            return ret

        ret.append("sys")
        q = PNSqlQuery(None, self.conn_.dbAux())
        q.setForwardOnly(True)
        q.exec_("SELECT idmodulo FROM flmodules WHERE idmodulo <> 'sys'")
        while q.next():
            ret.append(str(q.value(0)))

        return ret

    def idAreaToDescription(self, id_area: Optional[str] = None) -> str:
        """
        Return the description of an area from its identifier.

        @param id_area Area identifier.
        @return Area description text, if found or idA if not found.
        """

        if id_area is None:
            return ""

        for areaObj in self.dictInfoMods.values():
            if areaObj.idArea and areaObj.idArea.upper() == id_area.upper():
                return areaObj.areaDescripcion

        return ""

    def idModuleToDescription(self, id_module: str) -> str:
        """
        Return the description of a module from its identifier.

        @param id_module Module identifier.
        @return Module description text, if found or idM if not found.
        """

        mod_obj = self.dictInfoMods[id_module.upper()]

        return getattr(mod_obj, "descripcion", id_module)

    def iconModule(self, id_module: str) -> "QPixmap":
        """
        To obtain the icon associated with a module.

        @param id_moule Identifier of the module from which to obtain the icon
        @return QPixmap with the icon
        """
        from PyQt5.QtGui import QPixmap

        pix = QPixmap()
        mod_obj = self.dictInfoMods.get(id_module.upper(), None)
        mod_icono = getattr(mod_obj, "icono", None)
        if mod_icono is not None:
            from pineboolib.application.utils import xpm

            pix = QPixmap(xpm.cacheXPM(mod_icono))

        return pix

    def versionModule(self, id_module: str) -> str:
        """
        Return the version of a module.

        @param id_module Identifier of the module whose version you want to know
        @return Chain with version
        """

        if not self.dictInfoMods:
            return id_module

        info_module = self.dictInfoMods[id_module.upper()]

        if info_module is not None:
            return info_module.version
        else:
            return id_module

    def shaLocal(self) -> Optional[str]:
        """
        To obtain the local sha key.

        @return Sha key of the locally loaded modules version
        """

        return self.shaLocal_

    def shaGlobal(self) -> str:
        """
        To get the global sha key.

        @return Sha key of the globally loaded modules version
        """

        if not self.conn_.dbAux():
            return ""

        q = PNSqlQuery(None, self.conn_.dbAux())
        q.setForwardOnly(True)
        q.exec_("SELECT sha FROM flserial")
        if q.lastError is None:
            return "error"

        if q.next():
            return str(q.value(0))
        else:
            return ""

    def setShaLocalFromGlobal(self) -> None:
        """
        Set the value of the local sha key with that of the global one.
        """

        self.shaLocal_ = self.shaGlobal()

    def shaOfFile(self, file_name: str) -> Optional[str]:
        """
        Get the sha key associated with a stored file.

        @param file_name File name
        @return Key sh associated with the files
        """

        if not file_name[:3] == "sys" and not self.conn_.manager().isSystemTable(file_name):
            formatVal = self.conn_.manager().formatAssignValue("nombre", "string", file_name, True)
            q = PNSqlQuery(None, self.conn_.dbAux())
            # q.setForwardOnly(True)
            q.exec_("SELECT sha FROM flfiles WHERE %s" % formatVal)
            if q.next():
                return str(q.value(0))

        return None

    def loadKeyFiles(self) -> None:
        """
        Load the sha1 keys of the files into the key dictionary.
        """

        self.dictKeyFiles = {}
        self.dictModFiles = {}
        q = PNSqlQuery(None, self.conn_.dbAux())
        # q.setForwardOnly(True)
        q.exec_("SELECT nombre, sha, idmodulo FROM flfiles")
        name = None
        while q.next():
            name = str(q.value(0))
            self.dictKeyFiles[name] = str(q.value(1))
            self.dictModFiles[name.upper()] = str(q.value(2))

    def loadAllIdModules(self) -> None:
        """
        Load the list of all module identifiers.
        """

        self.listAllIdModules_ = []
        self.listAllIdModules_.append("sys")
        self.dictInfoMods = {}

        q = PNSqlQuery(None, self.conn_.dbAux())
        q.setTablesList("flmodules,flareas")
        q.setSelect(
            "idmodulo,flmodules.idarea,flmodules.descripcion,version,icono,flareas.descripcion"
        )
        q.setFrom("flmodules left join flareas on flmodules.idarea = flareas.idarea")
        q.setWhere("1 = 1")
        q.setForwardOnly(True)
        q.exec_()
        # q.exec_("SELECT idmodulo,flmodules.idarea,flmodules.descripcion,version,icono,flareas.descripcion "
        #        "FROM flmodules left join flareas on flmodules.idarea = flareas.idarea")

        sysModuleFound = False
        while q.next():
            infoMod = FLInfoMod()
            infoMod.idModulo = str(q.value(0))
            infoMod.idArea = str(q.value(1))
            infoMod.descripcion = str(q.value(2))
            infoMod.version = str(q.value(3))
            infoMod.icono = str(q.value(4))
            infoMod.areaDescripcion = str(q.value(5))
            self.dictInfoMods[infoMod.idModulo.upper()] = infoMod

            if not infoMod.idModulo == "sys":
                self.listAllIdModules_.append(infoMod.idModulo)
            else:
                sysModuleFound = True

        if not sysModuleFound:
            infoMod = FLInfoMod()
            infoMod.idModulo = "sys"
            infoMod.idArea = "sys"
            infoMod.descripcion = "Administracion"
            infoMod.version = "0.0"
            infoMod.icono = self.contentFS("%s/%s" % (filedir("../share/pineboo"), "/sys.xpm"))
            infoMod.areaDescripcion = "Sistema"
            self.dictInfoMods[infoMod.idModulo.upper()] = infoMod

    def loadIdAreas(self) -> None:
        """
        Load the list of all area identifiers.
        """

        self.listIdAreas_ = []
        q = PNSqlQuery(None, self.conn_.dbAux())
        # q.setForwardOnly(True)
        q.exec_("SELECT idarea from flareas WHERE idarea <> 'sys'")
        while q.next():
            self.listIdAreas_.append(str(q.value(0)))

        if "sys" not in self.listIdAreas_:
            self.listIdAreas_.append("sys")

    @decorators.NotImplementedWarn
    def checkSignatures(self):
        """
        Check the signatures for a given module.
        """

        pass

    def idModuleOfFile(self, name: Union[str]) -> Any:
        """
        Return the identifier of the module to which a given file belongs.

        @param n File name including extension
        @return Identifier of the module to which the file belongs
        """

        if not isinstance(name, str):
            n = str(name.toString())
        else:
            n = name

        from pineboolib.application import project

        if n.endswith(".mtd") and project._DGI:
            if n[: n.find(".mtd")] in project.DGI.sys_mtds() or n == "flfiles.mtd":
                return "sys"

        cursor = self.conn_.execute_query("SELECT idmodulo FROM flfiles WHERE nombre='%s'" % n)

        for idmodulo in cursor:
            return idmodulo[0]

    def writeState(self) -> None:
        """
        Save the status of the module system.
        """

        idDB = "noDB"
        if self.conn_.dbAux():
            db_aux = self.conn_.dbAux()
            idDB = "%s%s%s%s%s" % (
                db_aux.database(),
                db_aux.host(),
                db_aux.user(),
                db_aux.driverName(),
                db_aux.port(),
            )

        from pineboolib.core.settings import settings

        if self.activeIdArea_ is None:
            raise ValueError("activeIdArea_ is empty!")

        if self.activeIdModule_ is None:
            raise ValueError("activeIdModule_ is empty!")

        if self.shaLocal_ is None:
            raise ValueError("shaLocal_ is empty!")

        settings.setValue("Modules/activeIdModule/%s" % idDB, self.activeIdModule_)
        settings.setValue("Modules/activeIdArea/%s" % idDB, self.activeIdArea_)
        settings.setValue("Modules/shaLocal/%s" % idDB, self.shaLocal_)

    def readState(self) -> None:
        """
        Read the module system status.
        """
        if not self.conn_.dbAux():
            return

        db_aux = self.conn_.dbAux()

        idDB = "%s%s%s%s%s" % (
            db_aux.database(),
            db_aux.host(),
            db_aux.user(),
            db_aux.driverName(),
            db_aux.port(),
        )

        from pineboolib.core.settings import settings

        self.activeIdModule_ = settings.value("Modules/activeIdModule/%s" % idDB, None)
        self.activeIdArea_ = settings.value("Modules/activeIdArea/%s" % idDB, None)
        self.shaLocal_ = settings.value("Modules/shaLocal/%s" % idDB, None)

        if self.activeIdModule_ is None or self.activeIdModule_ not in self.listAllIdModules():
            self.setActiveIdModule(None)

    def contentStatic(self, file_name: str) -> Optional[str]:
        """
        Return the contents of a file by static loading from the local disk.

        @param file_name File name.
        @return String with the contents of the file or None in case of error.
        """

        str_ret = flmodulesstaticloader.FLStaticLoader.content(file_name, self.staticBdInfo_)
        if str_ret is not None:
            from pineboolib.fllegacy.flutil import FLUtil

            s = ""
            util = FLUtil()
            sha = util.sha1(str_ret)
            if file_name in self.dictKeyFiles.keys():
                s = self.dictKeyFiles[file_name]

            if s == sha:
                return None

            elif self.dictKeyFiles and file_name.find(".qs") > -1:
                self.dictKeyFiles[file_name] = sha

            if file_name.endswith(".mtd"):
                from PyQt5.QtXml import QDomDocument  # type: ignore

                doc = QDomDocument(file_name)
                if util.domDocumentSetContent(doc, str_ret):
                    mng = self.conn_.manager()
                    docElem = doc.documentElement()
                    mtd = mng.metadata(docElem, True)

                    if not mtd or mtd.isQuery():
                        return str_ret

                    if not mng.existsTable(mtd.name()):
                        mng.createTable(mng)
                    elif self.conn_.canRegenTables():
                        self.conn_.regenTable(mtd.name(), mtd)

        return str_ret

    def staticLoaderSetup(self) -> None:
        """
        Display dialog box to configure static load from local disk.
        """
        ui = self.createUI(filedir("../share/pineboo/forms/FLStaticLoaderUI.ui"))
        flmodulesstaticloader.FLStaticLoader.setup(self.staticBdInfo_, ui)
