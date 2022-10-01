"""Main module for starting up Pineboo."""


from pineboolib import application, logging

from pineboolib.core import settings

from . import dgi as dgi_module
from . import connection
from pineboolib.core.utils import utils_base

import gc
import sys
import shutil
import os


from typing import List, Type, Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from . import projectconfig  # noqa: F401 # pragma: no cover
    import optparse  # noqa: F401 # pragma: no cover
    from PyQt6 import QtWidgets  # type: ignore[import] # pragma: no cover
    from types import TracebackType  # pragma: no cover

LOGGER = logging.get_logger(__name__)


def startup_no_x() -> None:
    """Start Pineboo with no GUI."""
    startup(enable_gui=False)


def startup_framework(conn: Optional["projectconfig.ProjectConfig"] = None) -> None:
    """Start Pineboo project like framework."""
    if conn is None:
        raise Exception("conn is empty!")

    import pyfiglet  # type: ignore

    qapp = call_qapplication(sys.argv + ["-platform", "offscreen"])
    init_logging(True)
    init_cli(catch_ctrl_c=False)

    LOGGER.info(pyfiglet.figlet_format("\nPINEBOO %s " % application.PINEBOO_VER, font="starwars"))

    debug_level = 200
    if application.DEVELOPER_MODE:
        LOGGER.warning("Developer mode activated")
        debug_level = 1000

    application.PROJECT.setDebugLevel(debug_level)

    application.PROJECT.set_app(qapp)
    dgi = dgi_module.load_dgi("qt", None)
    application.PROJECT.init_dgi(dgi)
    application.PROJECT.aq_app._inicializing = False

    LOGGER.info("STARTUP_FRAMEWORK:(1/7) Setting profile data.")
    conn_ = connection.connect_to_db(conn)
    LOGGER.info("STARTUP_FRAMEWORK:(2/7) Establishing connection.")

    if not application.PROJECT.init_conn(connection=conn_):
        raise Exception("No main connection was established. Aborting Pineboo load.")

    _initialize_data(True)


def startup(enable_gui: bool = None) -> None:
    """Start up pineboo."""
    # FIXME: No hemos cargado pineboo aún. No se pueden usar métodos internos.
    from pineboolib.core.utils import check_dependencies
    from . import options as options_module

    if not check_dependencies.check_dependencies_cli(
        {"ply": "python3-ply", "PyQt6.QtCore": "python3-PyQt6", "Python": "Python"}
    ):
        sys.exit(32)

    min_python = (3, 6)
    if sys.version_info < min_python:
        sys.exit("Python %s.%s or later is required.\n" % min_python)

    options = options_module.parse_options()

    if options.pineboo_version:
        print("Pineboo %s." % application.PINEBOO_VER)
        sys.exit(0)

    print(chr(27) + "[2J")

    if enable_gui is not None:
        options.enable_gui = enable_gui
    trace_loggers: List[str] = []
    if options.trace_loggers:
        trace_loggers = options.trace_loggers.split(",")

    init_logging(logtime=options.log_time, loglevel=options.loglevel, trace_loggers=trace_loggers)
    if application.DEVELOPER_MODE:
        LOGGER.info("Developer mode activated")

    ret = exec_main_with_profiler(options) if options.enable_profiler else exec_main(options)

    gc.collect()
    LOGGER.info("Closing Pineboo...")
    sys.exit(ret if ret else 0)


def init_logging(
    logtime: bool = False, loglevel: int = logging.INFO, trace_loggers: List[str] = []
) -> None:
    """Initialize pineboo logging."""

    # ---- LOGGING -----
    log_format = "%(levelname)-8s: %(thread)s: %(name)s:%(lineno)d: %(message)s"

    if logtime:
        log_format = "%(asctime)s - %(levelname)-8s: %(thread)s: %(name)s:%(lineno)d: %(message)s"

    app_loglevel = logging.TRACE if trace_loggers else loglevel

    import coloredlogs  # type: ignore [import]

    coloredlogs.DEFAULT_LOG_LEVEL = app_loglevel
    coloredlogs.DEFAULT_LOG_FORMAT = log_format
    # 'black', 'blue', 'cyan', 'green', 'magenta', 'red', 'white' and 'yellow'
    coloredlogs.DEFAULT_FIELD_STYLES = {
        "asctime": {"color": "green"},
        "hostname": {"color": "magenta"},
        "levelname": {"bold": True, "color": "cyan"},
        "name": {"color": "white"},
        "programname": {"color": "cyan"},
        "username": {"color": "yellow"},
        "thread": {"color": "green"},
    }
    coloredlogs.DEFAULT_LEVEL_STYLES = {
        "critical": {"bold": True, "color": "red"},
        "debug": {"color": "green"},
        "error": {"color": "red"},
        "info": {},
        "notice": {"color": "magenta"},
        "spam": {"color": "green", "faint": True},
        "success": {"bold": True, "color": "green"},
        "verbose": {"color": "blue"},
        "warning": {"color": "yellow"},
    }
    coloredlogs.install()
    if trace_loggers:
        logging.Logger.set_pineboo_default_level(loglevel)

    logging.basicConfig(format=log_format, level=app_loglevel)
    # LOGGER.info("LOG LEVEL: %s", loglevel)
    disable_loggers = ["PyQt6.uic.uiparser", "PyQt6.uic.properties", "blib2to3.pgen2.driver"]
    for loggername in disable_loggers:
        modlogger = logging.get_logger(loggername)
        modlogger.setLevel(logging.WARN)

    for loggername in trace_loggers:
        modlogger = logging.get_logger(loggername)
        modlogger.setLevel(logging.TRACE)


def exec_main_with_profiler(options: "optparse.Values") -> int:
    """Enable profiler."""
    import cProfile
    import pstats
    import io
    from pstats import SortKey  # type: ignore

    profile = cProfile.Profile()
    profile.enable()
    ret = exec_main(options)
    profile.disable()
    string_io = io.StringIO()
    sortby = SortKey.TIME
    print_stats = pstats.Stats(profile, stream=string_io).sort_stats(sortby)
    print_stats.print_stats(40)
    print(string_io.getvalue())
    return ret


def init_cli(catch_ctrl_c: bool = True) -> None:
    """Initialize singletons, signal handling and exception handling."""

    def _excepthook(
        type_: Type["BaseException"], value: "BaseException", traceback: "TracebackType"
    ) -> None:
        import traceback as pytback

        pytback.print_exception(type_, value, traceback)

    # PyQt 5.5 o superior aborta la ejecución si una excepción en un slot()
    # no es capturada dentro de la misma; el programa falla con SegFault.
    # Aunque esto no debería ocurrir, y se debería prevenir lo máximo posible
    # es bastante incómodo y genera problemas graves para detectar el problema.
    # Agregamos sys.excepthook para controlar esto y hacer que PyQt6 no nos
    # dé un segfault, aunque el resultado no sea siempre correcto:
    sys.excepthook = _excepthook
    # -------------------
    if catch_ctrl_c:
        # Fix Control-C / KeyboardInterrupt for PyQt:
        import signal

        signal.signal(signal.SIGINT, signal.SIG_DFL)


# def init_gui() -> None:
#    """Create GUI singletons."""
#    from pineboolib.plugins.mainform.eneboo import eneboo
#    from pineboolib.plugins.mainform.eneboo_mdi import eneboo_mdi

#    eneboo.mainWindow = eneboo.MainForm()
#    eneboo_mdi.mainWindow = eneboo_mdi.MainForm()


def setup_gui(app: "QtWidgets.QApplication") -> None:
    """Configure GUI app."""

    from PyQt6 import QtGui

    noto_fonts = [
        "NotoSans-BoldItalic.ttf",
        "NotoSans-Bold.ttf",
        "NotoSans-Italic.ttf",
        "NotoSans-Regular.ttf",
    ]
    for fontfile in noto_fonts:
        QtGui.QFontDatabase.addApplicationFont(
            utils_base.filedir("./core/fonts/noto_sans", fontfile)
        )

    style_app: str = settings.CONFIG.value("application/style", "Fusion")
    app.setStyle(style_app)  # type: ignore

    default_font = settings.CONFIG.value("application/font", None)
    if default_font is None:
        font = QtGui.QFont("Noto Sans", 9)
        font.setBold(False)
        font.setItalic(False)
    else:
        # FIXME: FLSettings.readEntry does not return an array
        font = QtGui.QFont(
            default_font[0], int(default_font[1]), int(default_font[2]), default_font[3] == "true"
        )

    app.setFont(font)


def init_testing(level: int = 1000) -> None:
    """Initialize Pineboo for testing purposes."""
    settings.CONFIG.set_value("application/dbadmin_enabled", True)

    if application.PROJECT.dgi is not None:
        from pineboolib.application.database import pnconnectionmanager

        del application.PROJECT._conn_manager
        application.PROJECT._conn_manager = pnconnectionmanager.PNConnectionManager()

    else:
        qapp = call_qapplication(sys.argv + ["-platform", "offscreen"])

        init_logging(True)  # NOTE: Use pytest --log-level=0 for debug
        init_cli(catch_ctrl_c=False)

        LOGGER.info("PINEBOO TESTING %s.", application.PINEBOO_VER)
        # application.PROJECT.load_version()
        application.PROJECT.setDebugLevel(level)
        application.PROJECT.set_app(qapp)

        dgi = dgi_module.load_dgi("qt", None)

        application.PROJECT.init_dgi(dgi)

    setattr(application, "TESTING_MODE", True)
    application.PROJECT.aq_app._inicializing = False
    conn = connection.connect_to_db(connection.IN_MEMORY_SQLITE_CONN)

    if not application.PROJECT.init_conn(connection=conn):
        raise Exception("No main connection was established. Aborting Pineboo load.")

    # application.PROJECT.no_python_cache = False
    _initialize_data()


def finish_testing(delete_tmpdir: bool = True) -> None:
    """Clear data from pineboo project."""

    from pineboolib.application import qsadictmodules
    from pineboolib.application.parsers.parser_mtd import pnormmodelsfactory

    application.PROJECT.conn_manager.manager().cleanupMetaData()
    application.PROJECT.actions = {}
    application.PROJECT.areas = {}
    application.PROJECT.modules = {}
    if application.PROJECT.main_window:
        application.PROJECT.main_window.initialized_mods_ = []

    qsadictmodules.QSADictModules.clean_all()
    application.PROJECT.conn_manager.finish()
    for item_name in list(pnormmodelsfactory.PROCESSED):  # Si es de sistema, no se elimina.
        if item_name.startswith("fl"):
            continue

        pnormmodelsfactory.PROCESSED.remove(item_name)

    if delete_tmpdir:
        LOGGER.warning("Deleting temp folder %s", application.PROJECT.tmpdir)
        try:

            shutil.rmtree(application.PROJECT.tmpdir)
        except Exception as error:
            LOGGER.warning(
                "No se ha podido borrar %s al limpiar cambios del test. %s",
                application.PROJECT.tmpdir,
                error,
            )

    if not os.path.exists(application.PROJECT.tmpdir):
        os.mkdir(application.PROJECT.tmpdir)


def exec_main(options: "optparse.Values") -> int:
    """
    Exec main program.

    Handles optionlist and help.
    Also initializes all the objects
    """

    init_cli()

    # TODO: Refactorizar función en otras más pequeñas

    application.PROJECT.setDebugLevel(options.debug_level)

    # application.PROJECT.options = options

    app_args: List[str] = sys.argv
    if not options.enable_gui:
        app_args += ["-platform", "offscreen"]

    application.ENABLE_ACLS = options.enable_acls
    application.USE_INTERACTIVE_GUI = options.enable_interactive_gui
    application.ENABLE_CALL_EXCEPTIONS = options.enable_call_exceptions
    application.PARSE_PROJECT_ON_INIT = options.parse_project_on_init

    application.PROJECT.set_app(call_qapplication(app_args))

    if options.enable_gui:
        setup_gui(application.PROJECT.app)

    if options.log_sql:
        application.LOG_SQL = True

    if options.flfiles_folder:
        application.PROJECT.USE_FLFILES_FOLDER = options.flfiles_folder

    if options.trace_debug:
        # "sys.settrace" function could lead to arbitrary code execution
        sys.settrace(utils_base.traceit)  # noqa: DUO111

    if options.trace_signals:
        from .utils import monkey_patch_connect

        monkey_patch_connect()

    if options.enable_dbadmin:
        application.PROJECT._db_admin_mode = True
        settings.CONFIG.set_value("application/dbadmin_enabled", True)
    if options.enable_quick:
        application.PROJECT._db_admin_mode = False
        settings.CONFIG.set_value("application/dbadmin_enabled", False)

    if options.enable_preping:
        settings.CONFIG.set_value("application/preping", True)

    if options.main_form:
        settings.CONFIG.set_value("ebcomportamiento/main_form_name", options.main_form)

    application.PROJECT.load_version()

    if utils_base.is_deployed():
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)

        utils_base.download_files()

    dgi = dgi_module.load_dgi(options.dgi, options.dgi_parameter)
    # if options.enable_gui:
    #    init_gui()

    if dgi.useDesktop() and not options.enable_gui and options.dgi != "qt":
        LOGGER.info(
            "Selected DGI <%s> is not compatible with <pineboo-core>. Use <pineboo> instead"
            % options.dgi
        )

    if not dgi.useDesktop() and options.enable_gui:
        LOGGER.info(
            "Selected DGI <%s> does not need graphical interface. Use <pineboo-core> for better results"
            % options.dgi
        )

    if not dgi.useMLDefault():
        # When a particular DGI doesn't want the standard init, we stop loading here
        # and let it take control of the remaining pieces.
        return dgi.alternativeMain(options)

    configdb = connection.config_dbconn(options)
    LOGGER.debug(configdb)
    application.PROJECT.init_dgi(dgi)

    lang = application.PROJECT.aq_app._multi_lang_id.lower()
    if lang == "c":
        lang = "es"
    application.PROJECT.aq_app.loadTranslationFromModule("sys", lang)

    if not configdb and dgi.useDesktop() and dgi.localDesktop():
        if not dgi.mobilePlatform():
            from pineboolib.loader.dlgconnect.conn_dialog import show_connection_dialog

            configdb = show_connection_dialog(application.PROJECT.app)
            if configdb is None:
                return 2
        else:
            application.PROJECT._db_admin_mode = True
            settings.CONFIG.set_value("application/dbadmin_enabled", True)
            configdb = connection.DEFAULT_SQLITE_CONN

    if not configdb:
        raise ValueError("No connection given. Nowhere to connect. Cannot start.")

    conn = connection.connect_to_db(configdb)

    if not application.PROJECT.init_conn(connection=conn):
        LOGGER.warning("No main connection was provided. Aborting Pineboo load.")
        return -99

    settings.SETTINGS.set_value("DBA/lastDB", conn.DBName())

    if options.no_python_cache:
        application.PROJECT.no_python_cache = options.no_python_cache

    if options.enable_gui:
        from pineboolib.plugins import mainform

        main_form_name = settings.CONFIG.value("ebcomportamiento/main_form_name", "eneboo")

        main_form = getattr(mainform, main_form_name, None)
        if main_form is None:
            settings.CONFIG.set_value("ebcomportamiento/main_form_name", "eneboo")
            raise Exception(
                "mainForm %s does not exits!!.Use 'pineboo --main_form eneboo' to restore default mainForm"
                % main_form_name
            )
        # else:
        #    main_form = getattr(main_form, main_form_name)

        application.PROJECT.main_window = main_form.MainForm()
    # main_form_ = getattr(application.PROJECT.main_form, "MainForm", None)
    application.PROJECT.message_manager().send("splash", "show")
    _initialize_data()

    # FIXME: move this code to pineboo.application
    application.PROJECT.message_manager().send(
        "splash", "showMessage", ["Cargando traducciones ..."]
    )
    application.PROJECT.aq_app.loadTranslations()

    from . import init_project

    ret = init_project.init_project(
        dgi,
        options,
        application.PROJECT,
        application.PROJECT.main_window if dgi.useDesktop() else None,
        application.PROJECT.app,
    )
    return ret


def _initialize_data(is_framework: bool = False) -> None:
    """Initialize data."""

    from PyQt6 import QtCore

    application.ID_SESSION = QtCore.QDateTime.currentDateTime().toString(
        QtCore.Qt.DateFormat.ISODate
    )

    if is_framework:
        LOGGER.info("STARTUP_FRAMEWORK:(3/7) Loading database.")
    if not application.PROJECT.run():
        if not application.DEVELOPER_MODE:
            raise Exception("Project initialization failed!")

    from pineboolib.application.acls import pnaccesscontrollists

    acl = pnaccesscontrollists.PNAccessControlLists()
    acl.init()

    if acl._access_control_list:
        if is_framework:
            LOGGER.info("STARTUP_FRAMEWORK:(4/7) Loading ACLS.")
        application.PROJECT.aq_app.set_acl(acl)

    # LOGGER.info("STARTUP_FRAMEWORK:(5/9) Loading area definitions.")
    # application.PROJECT.conn_manager.managerModules().loadIdAreas()
    # LOGGER.info("STARTUP_FRAMEWORK:(6/9) Loading module definitions.")
    # application.PROJECT.conn_manager.managerModules().loadAllIdModules()
    if is_framework:
        LOGGER.info("STARTUP_FRAMEWORK:(5/7) Loading modules. Making QSA Tree.")
    application.PROJECT.load_modules()
    if is_framework:
        LOGGER.info("STARTUP_FRAMEWORK:(6/7) Loading classes. Making QSA Tree.")
    application.PROJECT.load_classes()
    if is_framework:
        LOGGER.info("STARTUP_FRAMEWORK:(7/7) Loading orm models. Making QSA Tree. ")
    application.PROJECT.load_orm()
    if is_framework:
        LOGGER.info("STARTUP_FRAMEWORK: All processes completed. Continue ...")
    application.PROJECT.conn_manager.removeConn("default")
    application.PROJECT.conn_manager.removeConn("dbAux")


def call_qapplication(args: List[str] = []) -> "QtWidgets.QApplication":
    """Call to QApplication."""
    from PyQt6 import QtWidgets

    return QtWidgets.QApplication(args)
