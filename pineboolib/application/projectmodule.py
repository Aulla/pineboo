"""
Project Module.
"""
import os
from optparse import Values
from pathlib import Path

import multiprocessing

from typing import List, Optional, Any, Dict, Callable, TYPE_CHECKING


# from pineboolib.fllegacy.flaccesscontrollists import FLAccessControlLists # FIXME: Not allowed yet
from PyQt5 import QtWidgets

from pineboolib.core.utils import logging, utils_base
from pineboolib.core.utils.struct import AreaStruct
from pineboolib.core import exceptions, settings, message_manager, decorators
from .database import pnconnectionmanager
from .database import utils as db_utils
from .utils import path, xpm, flfiles_dir
from . import module, file


from .parsers.parser_mtd import pnmtdparser, pnormmodelsfactory
from .parsers import parser_qsa


if TYPE_CHECKING:
    from pineboolib.interfaces import dgi_schema, imainwindow  # noqa: F401 # pragma: no cover
    from .database import pnconnection  # pragma: no cover
    from . import xmlaction, pnapplication  # noqa: F401 # pragma: no cover


LOGGER = logging.get_logger(__name__)


class Project(object):
    """
    Singleton for the whole application.

    Can be accessed with pineboolib.project from anywhere.
    """

    _conn_manager: Optional["pnconnectionmanager.PNConnectionManager"]

    _app: Optional[QtWidgets.QApplication] = None
    _aq_app: Optional["pnapplication.PNApplication"] = None
    # _conn: Optional["PNConnection"] = None  # Almacena la conexión principal a la base de datos
    debug_level = 100
    options: Values

    main_window: Optional["imainwindow.IMainWindow"] = None
    acl_ = None
    dgi: Optional["dgi_schema.dgi_schema"] = None
    delete_cache: bool = False
    parse_project: bool
    path = None
    _splash = None
    sql_drivers_manager = None
    timer_ = None
    no_python_cache: bool
    _msg_mng = None
    alternative_folder: Optional[str]
    _session_func_: Optional[Callable]

    areas: Dict[str, AreaStruct]
    files: Dict[str, Any]
    tables: Dict[str, Any]
    actions: Dict[str, "xmlaction.XMLAction"]
    translator_: List[Any]
    modules: Dict[str, "module.Module"]
    pending_conversion_list: List[str]
    USE_FLFILES_FOLDER: str = ""

    def __init__(self) -> None:
        """Initialize."""
        # self._conn = None
        self.dgi = None
        self.tree = None
        self.root = None
        self.alternative_folder = None
        self.apppath = ""
        self.tmpdir = settings.CONFIG.value("ebcomportamiento/temp_dir", "")
        self.parser = None
        # self.main_form_name: Optional[str] = None
        self.delete_cache = False
        self.parse_project = True
        self.no_python_cache = False
        self.translator_ = []  # FIXME: Add proper type
        self.actions = {}  # FIXME: Add proper type
        # self.tables = {}  # FIXME: Add proper type
        self.files = {}  # FIXME: Add proper type
        self.areas = {}
        self.modules = {}
        self.options = Values()
        if not self.tmpdir:
            self.tmpdir = utils_base.filedir("%s/Pineboo/tempdata" % Path.home())
            settings.CONFIG.set_value("ebcomportamiento/temp_dir", self.tmpdir)

        if not os.path.exists(self.tmpdir):
            try:
                Path(self.tmpdir).mkdir(parents=True, exist_ok=True)
            except Exception as error:
                LOGGER.error("Error creating %s folder : %s", self.tmpdir, str(error))
                return

        if not os.access(self.tmpdir, os.W_OK):
            LOGGER.error("%s folder is not writable!. Please change permissions!", self.tmpdir)
            return

        self._conn_manager = None
        self._session_func_ = None
        LOGGER.debug("Initializing connection manager for the application.PROJECT %s", self)
        self.pending_conversion_list = []

    @property
    def app(self) -> QtWidgets.QApplication:
        """Retrieve current Qt Application or throw error."""
        if self._app is None:
            raise Exception("No application set")
        return self._app

    def set_app(self, app: QtWidgets.QApplication):
        """Set Qt Application."""
        self._app = app

    @property
    def aq_app(self) -> "pnapplication.PNApplication":
        """Retrieve current Qt Application or throw error."""
        if self._aq_app is None:
            from pineboolib.application import pnapplication

            self._aq_app = pnapplication.PNApplication()
        return self._aq_app

    def set_aq_app(self, aq_app: "pnapplication.PNApplication") -> None:
        """Set Qt Application."""
        self._aq_app = aq_app

    @property
    def conn_manager(self) -> "pnconnectionmanager.PNConnectionManager":
        """Retrieve current connection or throw."""
        if self._conn_manager is None:
            self._conn_manager = pnconnectionmanager.PNConnectionManager()

        return self._conn_manager

    @property
    def DGI(self) -> "dgi_schema.dgi_schema":
        """Retrieve current DGI or throw."""
        if self.dgi is None:
            raise Exception("Project is not initialized")
        return self.dgi

    def init_conn(self, connection: "pnconnection.PNConnection") -> bool:
        """Initialize project with a connection."""
        # if self._conn is not None:
        #    del self._conn
        #    self._conn = None

        result = self.conn_manager.setMainConn(connection)

        if result:
            self.apppath = utils_base.filedir("..")

            self.delete_cache = settings.CONFIG.value("ebcomportamiento/deleteCache", False)
            self.parse_project = settings.CONFIG.value("ebcomportamiento/parseProject", True)
            if not self.no_python_cache:
                self.no_python_cache = settings.CONFIG.value(
                    "ebcomportamiento/noPythonCache", False
                )

        return result

    def init_dgi(self, dgi: "dgi_schema.dgi_schema") -> None:
        """Load and associate the defined DGI onto this project."""
        # FIXME: Actually, DGI should be loaded here, or kind of.

        self.dgi = dgi

        self._msg_mng = message_manager.Manager(dgi)

        self.dgi.extraProjectInit()

    def load_modules(self) -> None:
        """Load all modules."""
        for module_name, mod_obj in self.modules.items():
            mod_obj.load()

    def load_orm(self) -> None:
        """Load Orm objects."""

        # from pineboolib.application.parsers.mtdparser import pnmtdparser, pnormmodelsfactory

        # print("FIXME parse solo no existentes! y todos los mtd")
        # for action_name in self.actions:
        #    pnmtdparser.mtd_parse(self.actions[action_name])
        conn = self.conn_manager.mainConn()
        db_name = conn.DBName()

        for key in list(self.files.keys()):
            file_ = self.files[key]
            if file_.filename.endswith(".mtd"):

                if "%s_model.py" % file_.filename[:-4] in self.files.keys():
                    LOGGER.warning(
                        "Ya existe un model para %s.mtd (%s), no se convertirá a model.",
                        file_.filename[:-4],
                        self.files["%s_model.py" % file_.filename[:-4]].path(),
                    )
                    continue
                dest_file = pnmtdparser.mtd_parse(file_.filename, file_.path())

                if dest_file:
                    self.files["%s_model.py" % file_.filename[:-4]] = file.File(
                        file_.module,
                        "%s_model.py" % file_.path(),
                        basedir=file_.basedir,
                        sha=file_.sha,
                        db_name=db_name,
                    )

                    self.files["%s_model.py" % file_.filename[:-4]].filekey = (
                        "%s_model.py" % file_.filekey
                    )

        self.message_manager().send("splash", "showMessage", ["Cargando objetos ..."])
        LOGGER.warning("Loading ORMS ...")
        pnormmodelsfactory.load_models()

    def load_classes(self) -> None:
        """Load class files into qsa tree."""

        # print("* loading_classes")
        for key in list(self.files.keys()):
            if not key.endswith(".py"):
                continue

            if len(key) > 5 and key[0:5] == "test_":
                continue

            db_utils.process_file_class(self.files[key])

    def setDebugLevel(self, level: int) -> None:
        """
        Set debug level for application.

        @param q Número con el nivel espeficicado
        ***DEPRECATED***
        """
        self.debug_level = level
        # self.dgi.pnqt3ui.Options.DEBUG_LEVEL = q

    # def acl(self) -> Optional[FLAccessControlLists]:
    #     """
    #     Retorna si hay o no acls cargados
    #     @return Objeto acl_
    #     """
    #     return self.acl_
    def acl(self):
        """Return loaded ACL."""
        raise exceptions.CodeDoesNotBelongHereException("ACL Does not belong to PROJECT. Go away.")

    def run(self) -> bool:
        """Run project. Connects to DB and loads data."""
        from .parsers.parser_qsa import PARSER_QSA_VERSION

        LOGGER.info("RUN: Loading project data.")

        self.pending_conversion_list = []

        self.actions = {}
        self.files = {}
        self.areas = {}
        self.modules = {}

        if self.dgi is None:
            raise Exception("DGI not loaded")

        conn = self.conn_manager.mainConn()
        db_name = conn.DBName()
        delete_cache = self.delete_cache
        cache_ver = PARSER_QSA_VERSION
        if not os.path.exists(path._dir("cache")):
            cache_path = path._dir("cache")
            path_build: List[str] = []
            try:
                LOGGER.info("RUN: Checking if cache folder exists (%s)", cache_path)
                for folder in os.path.split(cache_path):
                    path_build.append(folder)
                    if not os.path.exists(os.path.join(*path_build)):
                        os.mkdir(os.path.join(*path_build))
            except Exception as error:
                raise Exception("Error building cache folder (%s) : %s" % (path_build, error))

        if os.path.exists(path._dir("cache/%s" % db_name)):
            if not os.path.exists(path._dir("cache/%s/cache_version.txt" % db_name)):
                delete_cache = True
            else:
                cache_ver = ""
                file_ver = open(path._dir("cache/%s/cache_version.txt" % db_name), "r")
                cache_ver = file_ver.read()
                file_ver.close()
                if cache_ver != PARSER_QSA_VERSION:
                    delete_cache = True

            if delete_cache:
                if cache_ver != PARSER_QSA_VERSION:
                    LOGGER.warning(
                        "QSA parser version has changed from %s to %s!. Deleting cache.",
                        cache_ver,
                        PARSER_QSA_VERSION,
                    )
                else:
                    LOGGER.warning("Deleting cache.")

        if delete_cache and os.path.exists(path._dir("cache/%s" % db_name)):

            self.message_manager().send("splash", "showMessage", ["Borrando caché ..."])
            LOGGER.info(
                "DEVELOP: delete_cache Activado\nBorrando %s", path._dir("cache/%s" % db_name)
            )

            for root, dirs, files in os.walk(path._dir("cache/%s" % db_name), topdown=False):
                for name in files:
                    if os.path.exists(os.path.join(root, name)):
                        os.remove(os.path.join(root, name))
                for name in dirs:
                    if name != "sqlite_database":
                        if os.path.exists(os.path.join(root, name)):
                            os.rmdir(os.path.join(root, name))

        else:
            keep_images = settings.CONFIG.value("ebcomportamiento/keep_general_cache", False)
            if keep_images is False:
                for file_name in os.listdir(self.tmpdir):
                    if file_name.find(".") > -1 and not file_name.endswith("sqlite3"):
                        file_path = os.path.join(self.tmpdir, file_name)
                        try:
                            os.remove(file_path)
                        except Exception:
                            LOGGER.warning(
                                "No se ha podido borrar %s al limpiar la cache", file_path
                            )
                            pass

        if not os.path.exists(path._dir("cache")):
            LOGGER.warning("RUN: Creating %s folder.", path._dir("cache"))
            os.makedirs(path._dir("cache"))

        if not os.path.exists(path._dir("cache/%s" % db_name)):
            LOGGER.warning("RUN: Creating %s folder.", path._dir("cache/%s" % db_name))
            os.makedirs(path._dir("cache/%s" % db_name))

        ret_ = False
        if self.load_system_module() and self.load_database_modules():
            ret_ = True

        # FIXME: ACLs needed at this level?
        # self.acl_ = FLAccessControlLists()
        # self.acl_.init()

        file_ver = open(path._dir("cache/%s/cache_version.txt" % db_name), "w")
        file_ver.write(PARSER_QSA_VERSION)
        file_ver.close()

        return ret_

    def call(
        self,
        function: str,
        args: List[Any],
        object_context: Any = None,
        show_exceptions: bool = True,
        default_value: Any = True,
    ) -> Optional[Any]:
        """
        Call to a QS project function.

        @param function. Nombre de la función a llamar.
        @param args. Array con los argumentos.
        @param object_context. Contexto en el que se ejecuta la función.
        @param show_exceptions. Boolean que especifica si se muestra los errores.
        @return Boolean con el resultado.
        """
        # FIXME: No deberíamos usar este método. En Python hay formas mejores
        # de hacer esto.
        LOGGER.trace(
            "JS.CALL: fn:%s args:%s ctx:%s", function, args, object_context, stack_info=True
        )

        # Tipicamente flfactalma.iface.beforeCommit_articulos()
        if function[-2:] == "()":
            function = function[:-2]

        array_fun = function.split(".")

        if object_context is None:
            if not array_fun[0] in self.actions:
                if len(array_fun) > 1:
                    msg = "%s en el módulo %s" % (array_fun[1], array_fun[0])
                else:
                    msg = array_fun[0]
                if show_exceptions:
                    LOGGER.warning("No existe la acción %s", msg)
                return None
            else:

                fun_action = self.actions[array_fun[0]]
                main_window = fun_action.load_master_widget()

                if len(array_fun) == 2:

                    if hasattr(main_window.iface, array_fun[1]):
                        object_context = main_window.iface
                    elif hasattr(main_window, array_fun[1]):
                        object_context = main_window

                    if object_context is None:
                        object_context = main_window

                elif array_fun[1] == "iface":
                    object_context = main_window.iface

                elif array_fun[1] == "widget":
                    if hasattr(main_window.iface, array_fun[2]):
                        object_context = main_window.iface
                    elif hasattr(main_window, array_fun[2]):
                        object_context = main_window
                else:
                    return False

            if not object_context:
                if show_exceptions:
                    LOGGER.error(
                        "No existe el script para la acción %s en el módulo %s",
                        array_fun[0],
                        array_fun[0],
                    )
                return None

        function_name_object = None
        function_name = ""

        if len(array_fun) == 0:
            function_name_object = object_context
        elif len(array_fun) == 1:  # Si no hay puntos en la llamada a functión
            function_name = array_fun[0]
        elif len(array_fun) == 2:  # si no exite self.iface
            function_name = array_fun[1]
        elif len(array_fun) > 2:  # si existe self.iface por ejemplo
            function_name = array_fun[2]

        if function_name_object is None:
            function_name_object = getattr(object_context, function_name, None)

            if function_name_object is None:
                if show_exceptions:
                    LOGGER.error("No existe la función %s en %s", function_name, array_fun[0])
                return default_value
                # FIXME: debería ser false, pero igual se usa por el motor para detectar propiedades

        try:
            return function_name_object(*args)
        except Exception:

            LOGGER.exception("JSCALL: Error executing function %s", function_name, stack_info=True)

        return None

    def parse_script(self, scriptname: str, txt_: str = "") -> bool:
        """
        Convert QS script into Python and stores it in the same folder.

        @param scriptname, Nombre del script a convertir
        """
        from pineboolib.application.parsers.parser_qsa import postparse

        # Intentar convertirlo a Python primero con flscriptparser2
        if not os.path.isfile(scriptname):
            raise IOError
        python_script_path = (scriptname + ".xml.py").replace(".qs.xml.py", ".qs.py")
        if not os.path.isfile(python_script_path) or self.no_python_cache:
            file_name_l = scriptname.split(os.sep)  # FIXME: is a bad idea to split by os.sep
            file_name = file_name_l[len(file_name_l) - 2]

            msg = "Convirtiendo a Python . . . %s.qs %s" % (file_name, txt_)
            LOGGER.info(msg)

            # clean_no_python = self.dgi.clean_no_python() # FIXME: No longer needed. Applied on the go.

            try:
                postparse.pythonify([scriptname], ["--strict"])
            except Exception as error:
                LOGGER.exception(
                    "El fichero %s no se ha podido convertir: %s", scriptname, str(error)
                )
                return False

        return True

    def parse_script_list(self, path_list: List[str]) -> bool:
        """Convert QS scripts list into Python and stores it in the same folders."""

        from pineboolib.application.parsers.parser_qsa import pytnyzer, pyconvert

        if not path_list:
            return True

        for file_path in path_list:
            if not os.path.isfile(file_path):
                raise IOError

        pytnyzer.STRICT_MODE = True

        itemlist = []
        for num, path_file in enumerate(path_list):
            dest_file_name = "%s.py" % path_file[:-3]
            if dest_file_name in self.pending_conversion_list:
                LOGGER.warning("The file %s is already being converted. Waiting", dest_file_name)
                while dest_file_name in self.pending_conversion_list:
                    # Esperamos a que el fichero se convierta.
                    QtWidgets.QApplication.processEvents()
            else:
                self.pending_conversion_list.append(dest_file_name)
                itemlist.append(
                    pyconvert.PythonifyItem(
                        src=path_file, dst=dest_file_name, number=num, len=len(path_list), known={}
                    )
                )

        # itemlist = [
        #    pyconvert.PythonifyItem(
        #        src=path_file, dst="%s.py" % path_file[:-3], n=n, len=len(path_list), known={}
        #    )
        #    for n, path_file in enumerate(path_list)
        # ]
        # msg = "Convirtiendo a Python . . ."
        # LOGGER.info(msg)

        threads_num = pyconvert.CPU_COUNT
        if len(itemlist) < threads_num:
            threads_num = len(itemlist)

        pycode_list: List[bool] = []

        if parser_qsa.USE_THREADS:
            with multiprocessing.Pool(threads_num) as thread:
                # TODO: Add proper signatures to Python files to avoid reparsing
                pycode_list = thread.map(pyconvert.pythonify_item, itemlist, chunksize=2)
        else:
            for item in itemlist:
                pycode_list.append(pyconvert.pythonify_item(item))

        for item in itemlist:
            self.pending_conversion_list.remove(item.dst_path)

        if not all(pycode_list):
            LOGGER.warning("Conversion failed for some files")
            return False
        # LOGGER.warning("Parseados %s", path_list)
        return True

    @decorators.deprecated
    def get_temp_dir(self) -> str:
        """
        Return temporary folder defined for pineboo.

        @return ruta a la carpeta temporal
        """
        # FIXME: anti-pattern in Python. Getters for plain variables are wrong.
        raise exceptions.CodeDoesNotBelongHereException("Use proje:q!ct.tmpdir instead, please.")
        # return self.tmpdir

    def load_version(self) -> str:
        """Initialize current version numbers."""
        from . import PINEBOO_VER

        return (
            "DBAdmin v%s" % PINEBOO_VER
            if settings.CONFIG.value("application/dbadmin_enabled", False)
            else "Quick v%s" % PINEBOO_VER
        )

    def message_manager(self):
        """Return message manager for splash and progress."""
        return self._msg_mng

    def set_session_function(self, fun_: Callable) -> None:
        """Set session funcion."""

        self._session_func_ = fun_

    def session_id(self) -> str:
        """Return id if use pineboo like framework."""

        return str(self._session_func_()) if self._session_func_ is not None else "auto"

    def load_system_module(self) -> bool:
        """Load system module."""

        conn = self.conn_manager.mainConn()
        db_name = conn.DBName()

        file_object = open(
            utils_base.filedir(utils_base.get_base_dir(), "system_module", "sys.xpm"), "r"
        )
        icono = file_object.read()
        file_object.close()

        self.modules["sys"] = module.Module("sys", "sys", "Administración", icono, "1.0")
        for root, dirs, files in os.walk(
            utils_base.filedir(utils_base.get_base_dir(), "system_module")
        ):
            for nombre in files:
                if utils_base.is_library() and nombre.endswith("ui"):
                    continue

                if root.find("modulos") == -1:
                    fileobj = file.File("sys", nombre, basedir=root, db_name=db_name)
                    self.files[nombre] = fileobj
                    self.modules["sys"].add_project_file(fileobj)

        pnormmodelsfactory.load_models()
        # Se verifica que existen estas tablas
        for table in (
            "flareas",
            "flmodules",
            "flfiles",
            "flgroups",
            "fllarge",
            "flserial",
            "flusers",
            "flvar",
            "flmetadata",
            "flsettings",
            "flupdates",
            "flmetadata",
            "flseqs",
            "flsettings",
        ):

            self.conn_manager.manager().createSystemTable(table)

        return True

    def load_database_modules(self) -> bool:
        """Load database modules."""

        conn = self.conn_manager.dbAux()
        db_name = conn.DBName()

        result: Any = []
        static_flfiles = None

        if self.USE_FLFILES_FOLDER:
            LOGGER.warning("FLFILES_FOLDER: Using %s like flfiles", self.USE_FLFILES_FOLDER)
            static_flfiles = flfiles_dir.FlFiles(self.USE_FLFILES_FOLDER)
            result = static_flfiles.areas()
        else:
            result = conn.execute_query("""SELECT idarea, descripcion FROM flareas WHERE 1 = 1""")

        for idarea, descripcion in list(result):
            if idarea == "sys":
                continue
            self.areas[idarea] = AreaStruct(idarea=idarea, descripcion=descripcion)

        self.areas["sys"] = AreaStruct(idarea="sys", descripcion="Area de Sistema")

        result = []
        # Obtener módulos activos
        if static_flfiles:
            result = static_flfiles.modules()
        else:
            result = conn.execute_query(
                """SELECT idarea, idmodulo, descripcion, icono, version FROM flmodules WHERE bloqueo = %s """
                % conn.driver().formatValue("bool", "True", False)
            )

        for idarea, idmodulo, descripcion, icono, version in list(result):
            icono = xpm.cache_xpm(icono)

            if idmodulo not in self.modules:
                self.modules[idmodulo] = module.Module(
                    idarea, idmodulo, descripcion, icono, version
                )

        result = []
        if static_flfiles:
            result = static_flfiles.files()
        else:
            result = conn.execute_query(
                """SELECT idmodulo, nombre, sha, contenido FROM flfiles WHERE NOT sha = '' ORDER BY idmodulo, nombre """
            )

        log_file = open(path._dir("project.txt"), "w")

        list_files: List[str] = []
        LOGGER.info("RUN: Populating cache.")
        for idmodulo, nombre, sha, contenido in list(result):
            # print("*", idmodulo, nombre, sha, contenido[0:10] if contenido else ".")
            if idmodulo not in self.modules:  # Si el módulo no existe.
                continue

            elif utils_base.is_library() and nombre.endswith("ui"):  # Si es un UI en modo librería.
                continue

            elif nombre in self.files:  # Si se sobreescribe un fichero ya existente.
                if self.files[nombre].module == "sys":
                    continue
                else:
                    LOGGER.warning("run: file %s already loaded, overwritting..." % nombre)

            fileobj = file.File(idmodulo, nombre, sha, db_name=db_name)
            self.files[nombre] = fileobj

            self.modules[idmodulo].add_project_file(fileobj)

            log_file.write(fileobj.filekey + "\n")

            fileobjdir = os.path.dirname(path._dir("cache", fileobj.filekey))
            file_name = path._dir("cache", fileobj.filekey)
            if not os.path.exists(
                file_name
            ):  # Borra contenido de la carpeta si no existe el fichero destino
                if os.path.exists(fileobjdir):
                    for root, dirs, files in os.walk(fileobjdir):
                        for file_item in files:
                            os.remove(os.path.join(root, file_item))
                else:
                    os.makedirs(fileobjdir)

                if contenido is not None:
                    encode_ = "UTF-8" if str(nombre).endswith((".ts", ".py")) else "ISO-8859-15"
                    self.message_manager().send(
                        "splash", "showMessage", ["Volcando a caché %s..." % nombre]
                    )

                    new_cache_file = open(file_name, "wb")
                    new_cache_file.write(contenido.encode(encode_, "replace"))
                    new_cache_file.close()
            else:
                if file_name.endswith(".py"):
                    static_flag = "%s/static.xml" % fileobjdir
                    if os.path.exists(static_flag):
                        os.remove(static_flag)

            if self.parse_project:
                if nombre.endswith(".qs"):
                    if self.no_python_cache or not os.path.exists(
                        "%spy" % file_name[:-2]
                    ):  # si es forzado o no existe el .py
                        list_files.append(file_name)

        log_file.close()
        LOGGER.info("RUN: End populating cache.")

        self.message_manager().send(
            "splash",
            "showMessage",
            ["Convirtiendo a Python %s ..." % ("(forzado)" if self.no_python_cache else "")],
        )
        if list_files:
            LOGGER.info("RUN: Parsing QSA files. (%s): %s", len(list_files), list_files)
            if not self.parse_script_list(list_files):
                LOGGER.warning("Failed QSA conversion !.See debug for mode information.")
                return False

        return True
