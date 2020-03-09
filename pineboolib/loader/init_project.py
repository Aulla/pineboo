"""
Finalize pineboo setup and load.
"""
from pineboolib import logging
from typing import Any

from pineboolib.core import settings

LOGGER = logging.getLogger("loader.init_project")


def init_project(dgi: Any, options: Any, project: Any, main_form: Any, app: Any) -> Any:
    """Initialize the project and start it."""
    # from PyQt5 import QtCore  # type: ignore

    # if dgi.useDesktop() and dgi.localDesktop() and splash:
    #     splash.showMessage("Iniciando proyecto ...", QtCore.Qt.AlignLeft, QtCore.Qt.white)
    #     dgi.processEvents()

    LOGGER.info("Iniciando proyecto ...")

    if options.preload:
        from .preload import preload_actions

        preload_actions(project, options.forceload)

        LOGGER.info("Finished preloading")
        return

    if options.action:
        list = options.action.split(":")
        action_name = list[0].split(".")[0]
        # FIXME: Why is commented out?
        # objaction = project.conn_manager.manager(options.action)
        if action_name in project.actions.keys():

            ret = project.call(list[0], list[1:] if len(list) > 1 else [])
            return ret
        else:
            raise ValueError("Action name %s not found" % options.action)

    call_function = settings.SETTINGS.value("application/callFunction", None)
    if call_function:
        project.call(call_function, [])

    project.message_manager().send("splash", "showMessage", ["Creando interface ..."])

    if main_form is not None:
        LOGGER.info("Creando interfaz ...")
        main_window = main_form.mainWindow
        main_window.initScript()
        ret = 0

        project.message_manager().send("splash", "showMessage", ["Abriendo interfaz ..."])
        LOGGER.info("Abriendo interfaz ...")
        main_window.show()
        project.message_manager().send("splash", "showMessage", ["Listo ..."])
        project.message_manager().send("splash", "hide")
    # FIXME: Is always None because the earlier code is commented out
    # if objaction:
    #     project.openDefaultForm(objaction.form())

    if dgi.localDesktop():
        ret = app.exec_()
    else:
        ret = dgi.exec_()

    if main_form is not None:
        main_form.mainWindow = None
        del main_window
    del project
    return ret
