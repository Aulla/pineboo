"""
Finalize pineboo setup and load.
"""


from pineboolib import logging
from typing import Optional, TYPE_CHECKING


from pineboolib.core import settings
from .preload import preload_actions

if TYPE_CHECKING:
    from PyQt6 import QtWidgets  # pragma: no cover
    from pineboolib.application import projectmodule  # pragma: no cover
    from pineboolib.interfaces import imainwindow, dgi_schema  # pragma: no cover
    from optparse import Values  # pragma: no cover


LOGGER = logging.get_logger(__name__)


def init_project(
    dgi: "dgi_schema.dgi_schema",
    options: "Values",
    project: "projectmodule.Project",
    main_window: Optional["imainwindow.IMainWindow"],
    app: "QtWidgets.QApplication",
) -> int:
    """Initialize the project and start it."""
    # from PyQt6 import QtCore  # type: ignore

    # if dgi.useDesktop() and dgi.localDesktop() and splash:
    #     splash.showMessage("Iniciando proyecto ...", QtCore.Qt.AlignLeft, QtCore.Qt.white)
    #     dgi.processEvents()

    project.message_manager().send("splash", "showMessage", ["Iniciando proyecto ..."])

    if options.preload:
        preload_actions(project, options.forceload)

        LOGGER.info("Finished preloading")
        return 0

    call_function = settings.SETTINGS.value("application/callFunction", None)
    if options.call_function:
        call_function = options.call_function

    if call_function:
        LOGGER.debug("callFunction (%s)", call_function)
        args = call_function.split(":")
        try:
            project.call(args[0], args[1:] if len(args) > 1 else [])
        except Exception as error:
            from pineboolib import application

            LOGGER.warning("could not be executed %s : %s", call_function, str(error))
            if not application.DEVELOPER_MODE:
                raise error

        if options.quit_after_call:
            return 0

    if "plus_sys" in project.actions.keys():
        project.call("formplus_sys.main", [], None, False)
        if options.quit_after_call:
            return 0

    if main_window is not None:
        project.message_manager().send("splash", "showMessage", ["Creando interface ..."])
        # main_window = main_form.mainWindow
        main_window.initScript()
        ret = 0

        project.message_manager().send("splash", "showMessage", ["Abriendo interfaz ..."])
        main_window.show()
        project.message_manager().send("splash", "showMessage", ["Listo ..."])
        project.message_manager().send("splash", "hide")
    # FIXME: Is always None because the earlier code is commented out
    # if objaction:
    #     project.openDefaultForm(objaction.form())

    ret = app.exec() if dgi.localDesktop() else dgi.exec()

    # if main_form is not None:
    #    main_form.mainWindow = None
    #    del main_window
    del project
    return ret
