"""
Project Module.
"""


from pineboolib import logging

from pineboolib.core.utils import utils_base, struct
from pineboolib.core import exceptions, settings, message_manager, decorators

from .database import pnconnectionmanager
from .database import utils as db_utils
from .parsers.parser_mtd import pnmtdparser, pnormmodelsfactory
from .parsers import parser_qsa
from .utils import path, xpm, flfiles_dir
from . import qsadictmodules

from . import module, file as file_module
from . import connections

import os
from typing import List, Optional, Any, Dict, Callable, Union, TYPE_CHECKING

from pineboolib import application

if TYPE_CHECKING:
    from pineboolib.interfaces import dgi_schema, imainwindow  # noqa: F401 # pragma: no cover
    from .database import pnconnection  # pragma: no cover
    from . import xmlaction, pnapplication  # noqa: F401 # pragma: no cover
    from PyQt6 import QtWidgets  # type: ignore[import] # pragma: no cover
    from pineboolib.qsa import formdbwidget


LOGGER = logging.get_logger(__name__)


class Project(object):
    """
    Singleton for the whole application.

    Can be accessed with pineboolib.project from anywhere.
    """

    _conn_manager: Optional["pnconnectionmanager.PNConnectionManager"]

    _app: "QtWidgets.QApplication"
    _aq_app: Optional["pnapplication.PNApplication"] = None
    # _conn: Optional["PNConnection"] = None  # Almacena la conexión principal a la base de datos
    debug_level = 100
    # options: Values

    main_window: Optional["imainwindow.IMainWindow"] = None
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
    _session_func_: Optional["Callable"]

    areas: Dict[str, "struct.AreaStruct"]
    files: Dict[str, "file_module.File"]
    actions: Dict[str, "xmlaction.XMLAction"]

    modules: Dict[str, "module.Module"]
    pending_conversion_list: List[str]
    USE_FLFILES_FOLDER: str = ""
    _db_admin_mode: bool = False

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
        self.delete_cache = False
        self.parse_project = True
        self.no_python_cache = False

        self.actions = {}
        self.files = {}
        self.areas = {}
        self.modules = {}
        self._db_admin_mode = settings.CONFIG.value("application/dbadmin_enabled", False)

        import pathlib

        if not self.tmpdir:
            self.tmpdir = utils_base.filedir("%s/Pineboo/tempdata" % pathlib.Path.home())
            settings.CONFIG.set_value("ebcomportamiento/temp_dir", self.tmpdir)

        if not os.path.exists(self.tmpdir):
            try:
                pathlib.Path(self.tmpdir).mkdir(parents=True, exist_ok=True)
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
    def app(self) -> "QtWidgets.QApplication":
        """Retrieve current Qt Application or throw error."""
        if self._app is None:
            raise Exception("No application set")
        return self._app

    def set_app(self, app: "QtWidgets.QApplication"):
        """Set Qt Application."""
        self._app = app

    @property
    def aq_app(self) -> "pnapplication.PNApplication":
        """Retrieve current Qt Application or throw error."""
        if self._aq_app is None:
            from . import pnapplication

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

        result_init_conn = self.conn_manager.setMainConn(connection)

        if result_init_conn:
            self.apppath = utils_base.filedir("..")
            self.delete_cache = settings.CONFIG.value("ebcomportamiento/deleteCache", False)

            self.parse_project = (
                settings.CONFIG.value("ebcomportamiento/parseProject", True)
                if application.PARSE_PROJECT_ON_INIT
                else False
            )

            if not self.no_python_cache:
                self.no_python_cache = settings.CONFIG.value(
                    "ebcomportamiento/noPythonCache", False
                )

        return result_init_conn

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

        for file_item in [item for item in self.files.values() if item.filename.endswith(".mtd")]:
            file_name_model = "%s_model.py" % file_item.filename[:-4]
            if file_name_model not in self.files.keys():
                path_file = pnmtdparser.mtd_parse(file_item.filename, file_item.path())
                if path_file:
                    self.files[file_name_model] = file_module.File(
                        file_item.module,
                        "%s_model.py" % file_item.path(),
                        basedir=file_item.basedir,
                        sha=file_item.sha,
                        db_name=self.conn_manager.mainConn().DBName(),
                    )

                    self.files[file_name_model].filekey = "%s_model.py" % file_item.filekey

            else:
                LOGGER.debug(
                    "%s already exists (%s).", file_name_model, self.files[file_name_model].path()
                )

        self.message_manager().send("splash", "showMessage", ["Cargando objetos ..."])
        LOGGER.info("Loading ORMS ...")
        pnormmodelsfactory.load_models()

    def load_classes(self) -> None:
        """Load class files into qsa tree."""

        for key in list(self.files.keys()):
            if not key.endswith(".py") or key.startswith("test_"):
                continue

            db_utils.process_file_class(self.files[key])

    def setDebugLevel(self, level: int) -> None:
        """
        Set debug level for application.

        @param q Número con el nivel espeficicado
        ***DEPRECATED***
        """
        self.debug_level = level

    def run(self) -> bool:
        """Run project. Connects to DB and loads data."""

        LOGGER.info("RUN: Loading project data.")

        self.pending_conversion_list.clear()
        self.actions.clear()
        self.files.clear()
        self.areas.clear()
        self.modules.clear()

        if self.dgi is None:
            raise Exception("DGI not loaded")

        delete_cache = self.delete_cache
        cache_ver = parser_qsa.PARSER_QSA_VERSION

        cache_folder = path._dir("cache")
        db_cache_folder = os.path.join(cache_folder, self.conn_manager.mainConn().DBName())
        cache_version_file_path = os.path.join(db_cache_folder, "cache_version.txt")

        if not os.path.exists(cache_folder):
            path_build: List[str] = []
            try:
                LOGGER.info("RUN: Checking if cache folder exists (%s)", cache_folder)
                for folder in os.path.split(cache_folder):
                    path_build.append(folder)
                    path_med = os.path.join(*path_build)
                    if not os.path.exists(path_med):
                        os.mkdir(path_med)
            except Exception as error:
                raise Exception("Error building cache folder (%s) : %s" % (path_build, error))

        if os.path.exists(db_cache_folder):

            if not os.path.exists(cache_version_file_path):
                delete_cache = True
            else:
                cache_ver = ""
                try:
                    file_ver = open(cache_version_file_path, "r", encoding="UTF8")
                    cache_ver = file_ver.read()
                    file_ver.close()
                except Exception:
                    pass
                if cache_ver != parser_qsa.PARSER_QSA_VERSION:
                    delete_cache = True

            if delete_cache:
                if cache_ver != parser_qsa.PARSER_QSA_VERSION:
                    LOGGER.warning(
                        "QSA parser version has changed from %s to %s!. Deleting cache.",
                        cache_ver,
                        parser_qsa.PARSER_QSA_VERSION,
                    )
                else:
                    LOGGER.warning("Deleting cache.")

        if delete_cache and os.path.exists(db_cache_folder):

            self.message_manager().send("splash", "showMessage", ["Borrando caché ..."])
            LOGGER.info("DEVELOP: delete_cache Activado\nBorrando %s", db_cache_folder)

            for root, dirs, files in os.walk(db_cache_folder, topdown=False):
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

        if not os.path.exists(cache_folder):
            LOGGER.info("RUN: Creating %s folder.", cache_folder)
            os.makedirs(cache_folder)

        if not os.path.exists(db_cache_folder):
            LOGGER.info("RUN: Creating %s folder.", db_cache_folder)
            os.makedirs(db_cache_folder)

        file_ver = open(cache_version_file_path, "w", encoding="UTF8")
        file_ver.write(parser_qsa.PARSER_QSA_VERSION)
        file_ver.close()
        del file_ver

        return self.load_system_module() and self.load_database_modules()

    def call(
        self,
        function: str,
        args: List[Any],
        object_context: Union["formdbwidget.FormDBWidget", "object", None] = None,
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

        LOGGER.trace(
            "JS.CALL: fn:%s args:%s ctx:%s", function, args, object_context, stack_info=True
        )

        if not application.ENABLE_CALL_EXCEPTIONS:
            show_exceptions = False

        # Tipicamente flfactalma.iface.beforeCommit_articulos()
        if function[-2:] == "()":
            function = function[:-2]

        array_fun = function.split(".")
        module_name = array_fun[0]
        function_name = array_fun[-1]

        if object_context is None:
            object_context = qsadictmodules.QSADictModules.from_project(module_name)

            if hasattr(
                object_context, "iface"
            ) and hasattr(  # comprueba si la función es realmente de iface.
                object_context.iface, function_name  # type: ignore [union-attr]
            ):
                object_context = object_context.iface  # type: ignore [union-attr]

        function_object = getattr(object_context, function_name, None)
        if function_object is not None:
            try:

                # Controlar numero de argumentos
                args_num = connections.get_expected_args_num(function_object)
                while args_num > len(args):
                    args.append(None)

                if args and args_num:
                    args = args[0:args_num]

                return function_object(*args)
            except Exception as error:
                if show_exceptions:
                    LOGGER.exception(
                        "JSCALL: Error executing function %s ERROR: %s" % (function_name, error),
                        stack_info=True,
                    )
        else:
            if show_exceptions:
                LOGGER.error("No existe la función %s en %s", function_name, module_name)
            return default_value
            # FIXME: debería ser false, pero igual se usa por el motor para detectar propiedades

        return None

    def parse_script(self, scriptname: str, txt_: str = "") -> bool:
        """
        Convert QS script into Python and stores it in the same folder.

        @param scriptname, Nombre del script a convertir
        """
        from .parsers.parser_qsa import postparse

        # Intentar convertirlo a Python primero con flscriptparser2
        if not os.path.isfile(scriptname):
            raise IOError
        python_script_path = (scriptname + ".xml.py").replace(".qs.xml.py", ".qs.py")
        if not os.path.isfile(python_script_path) or self.no_python_cache:
            file_name_l = scriptname.split(os.sep)  # FIXME: is a bad idea to split by os.sep
            file_name = file_name_l[len(file_name_l) - 2]

            msg = "Convirtiendo a Python . . . %s.qs %s" % (file_name, txt_)
            LOGGER.info(msg)

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

        from .parsers.parser_qsa import pytnyzer, pyconvert

        if not path_list:
            return True

        for file_path in path_list:
            if not os.path.isfile(file_path):
                raise IOError

        pytnyzer.STRICT_MODE = True

        itemlist = []
        size_list = len(path_list)
        for num, orig_file_name in enumerate(path_list):
            dest_file_name = "%s.py" % orig_file_name[:-3]
            if dest_file_name in self.pending_conversion_list:
                LOGGER.warning("The file %s is already being converted. Waiting", dest_file_name)
                while dest_file_name in self.pending_conversion_list:
                    # Esperamos a que el fichero se convierta.
                    self.app.processEvents()  # type: ignore[misc] # noqa: F821
            else:
                self.pending_conversion_list.append(dest_file_name)
                itemlist.append(
                    pyconvert.PythonifyItem(
                        src=orig_file_name, dst=dest_file_name, number=num, len=size_list, known={}
                    )
                )

        threads_num = pyconvert.CPU_COUNT
        if len(itemlist) < threads_num:
            threads_num = len(itemlist)

        pycode_list: List[bool] = []

        if parser_qsa.USE_THREADS:
            import multiprocessing

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
        raise exceptions.CodeDoesNotBelongHereException("Use project.tmpdir instead, please.")
        # return self.tmpdir

    def load_version(self) -> str:
        """Initialize current version numbers."""
        from . import PINEBOO_VER

        return "DBAdmin v%s" % PINEBOO_VER if self._db_admin_mode else "Quick v%s" % PINEBOO_VER

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

        base_dir = utils_base.get_base_dir()
        is_library = utils_base.is_library()

        file_object = open(utils_base.filedir(base_dir, "system_module", "sys.xpm"), "r")
        icono = file_object.read()
        file_object.close()

        del file_object

        self.modules["sys"] = module.Module("sys", "sys", "Administración", icono, "1.0")
        for root, dirs, files in os.walk(utils_base.filedir(base_dir, "system_module")):
            for nombre in files:
                if is_library and nombre.endswith("ui"):
                    continue

                if root.find("modulos") == -1:
                    fileobj = file_module.File(
                        "sys", nombre, basedir=root, db_name=self.conn_manager.mainConn().DBName()
                    )
                    self.files[nombre] = fileobj
                    self.modules["sys"].add_project_file(fileobj)
                    del fileobj

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
        is_library = utils_base.is_library()
        result_areas: Any = []
        static_flfiles = None

        if self.USE_FLFILES_FOLDER:
            LOGGER.warning("FLFILES_FOLDER: Using %s like flfiles", self.USE_FLFILES_FOLDER)
            static_flfiles = flfiles_dir.FlFiles(self.USE_FLFILES_FOLDER)
            result_areas = static_flfiles.areas()
        else:
            result_areas = conn.execute_query(
                """SELECT idarea, descripcion FROM flareas WHERE 1 = 1"""
            )

        for idarea, descripcion in list(result_areas):
            if idarea == "sys":
                continue
            self.areas[idarea] = struct.AreaStruct(idarea=idarea, descripcion=descripcion)

        self.areas["sys"] = struct.AreaStruct(idarea="sys", descripcion="Area de Sistema")

        result_modules: Any = []
        # Obtener módulos activos
        if static_flfiles:
            result_modules = static_flfiles.modules()
        else:
            result_modules = conn.execute_query(
                """SELECT idarea, idmodulo, descripcion, icono, version FROM flmodules WHERE bloqueo = %s """
                % conn.driver().formatValue("bool", "True", False)
            )

        for idarea, idmodulo, descripcion, icono, version in list(result_modules):

            if idmodulo not in self.modules:
                icon_cached = xpm.cache_xpm(icono)
                self.modules[idmodulo] = module.Module(
                    idarea, idmodulo, descripcion, icon_cached, version
                )

        result_files: Any = []
        if static_flfiles:
            result_files = static_flfiles.files()
        else:
            result_files = conn.execute_query(
                """SELECT idmodulo, nombre, sha, bloqueo FROM flfiles WHERE NOT sha = '' ORDER BY idmodulo, nombre """
            )

        log_file = open(path._dir("project.txt"), "w")

        list_files: List[str] = []
        LOGGER.info("RUN: Populating cache.")
        for idmodulo, nombre, sha, contenido_or_bloqueo in list(result_files):

            if idmodulo not in self.modules.keys():  # Si el módulo no existe.
                continue

            elif is_library and nombre.endswith("ui"):  # Si es un UI en modo librería.
                continue

            elif nombre in self.files.keys():  # Si se sobreescribe un fichero ya existente.
                if self.files[nombre].module == "sys":
                    continue
                else:
                    LOGGER.warning("run: file %s already loaded, overwritting..." % nombre)

            fileobj = file_module.File(idmodulo, nombre, sha, db_name=db_name)
            self.files[nombre] = fileobj

            self.modules[idmodulo].add_project_file(fileobj)

            log_file.write(fileobj.filekey + "\n")

            fileobjdir = os.path.dirname(path._dir("cache", fileobj.filekey))
            file_name = path._dir("cache", fileobj.filekey)
            if not os.path.exists(file_name):  # Borra
                if os.path.exists(fileobjdir):
                    utils_base.empty_dir(fileobjdir)
                else:
                    os.makedirs(fileobjdir)

                contenido_content: Optional[str] = None

                if not static_flfiles:
                    qry = conn.execute_query(
                        """SELECT contenido FROM flfiles WHERE sha = %s AND nombre = %s """
                        % (
                            conn.driver().formatValue("string", sha, False),
                            conn.driver().formatValue("string", nombre, False),
                        )
                    )

                    result_content: Any = None
                    if qry is not None:
                        result_content = qry.first()

                    if result_content is not None:
                        contenido_content = result_content[
                            0
                        ]  # Recogemos verdadero contenido_content. cuando usamos flfiles. más rpapido conexiones lentas.
                else:
                    contenido_content = contenido_or_bloqueo

                if contenido_content is not None:
                    encode_ = "UTF-8" if str(nombre).endswith((".ts", ".py")) else "ISO-8859-15"
                    self.message_manager().send(
                        "splash", "showMessage", ["Volcando a caché %s..." % nombre]
                    )

                    new_cache_file = open(file_name, "wb")
                    new_cache_file.write(contenido_content.encode(encode_, "replace"))
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
        self.conn_manager.removeConn("dbaux")
        del log_file

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
