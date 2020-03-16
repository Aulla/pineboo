"""
Actions Slots Manager Module.

Contains functions to manage the slots received from the actions.
"""
from PyQt5 import QtWidgets

from pineboolib.core.utils import logging
from pineboolib.application import load_script
from pineboolib import application


from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:

    from pineboolib.application import xmlaction
    from pineboolib.q3widgets import formdbwidget  # noqa: F401
    from pineboolib.interfaces import isqlcursor

LOGGER = logging.get_logger(__name__)


def form_record_widget(
    action_object: "xmlaction.XMLAction"
) -> Optional["formdbwidget.FormDBWidget"]:
    """
    Return formrecord widget.

    This is needed because sometimes there isn't a FLFormRecordDB initialized yet.
    @return wigdet del formRecord.
    """
    if not getattr(action_object._record_widget, "_loaded", False):
        action_object.load_record()

    return action_object._record_widget


def open_default_form(action_object: "xmlaction.XMLAction") -> None:
    """
    Open Main FLForm specified on defaults.
    """
    LOGGER.info("Opening default form for Action %s", action_object._name)
    widget = action_object.load()
    if widget:
        widget.show()


def open_default_form_record(
    action_object: "xmlaction.XMLAction", cursor: "isqlcursor.ISqlCursor", wait: bool = True
) -> None:
    """
    Open FLFormRecord specified on defaults.

    @param cursor. Cursor a usar por el FLFormRecordDB
    """
    obj_ = action_object._record_widget

    if obj_ is not None:
        if obj_._loaded:
            if obj_.showed:
                QtWidgets.QMessageBox.information(
                    QtWidgets.QApplication.activeWindow(),
                    "Aviso",
                    "Ya hay abierto un formulario de edición de resgistro para esta tabla.\n"
                    "No se abrirán mas para evitar ciclos repetitivos de edición de registros.",
                    QtWidgets.QMessageBox.Yes,
                )
                return

    LOGGER.info("Opening default formRecord for Action %s", action_object._name)
    widget = action_object.load_record(cursor)
    # w.init()
    if widget and widget.form:
        if wait:
            widget.form.show_and_wait()
        else:
            widget.form.show()


def exec_main_script(action_name: str) -> None:
    """
    Execute function for main action.
    """

    application.PROJECT.call("%s.main" % action_name, [], None, False)


def exec_default_script(action_object: "xmlaction.XMLAction") -> None:
    """
    Execute script specified on default.
    """

    if action_object._record_widget is None:
        LOGGER.info("Executing default script for Action %s", action_object._name)
        script = load_script.load_script(action_object._master_script, action_object)
        action_object._record_widget = script.form

    if action_object._record_widget is None:
        raise Exception("Unexpected: No form loaded")

    main = None
    iface = getattr(action_object._record_widget, "iface", None)

    if iface is not None:
        main = getattr(iface, "main", None)

    if main is None:
        main = getattr(script.form, "main", None)

    if main is None:
        raise Exception("main function not found!")
    else:
        main()


def unknown_slot(act_object: "xmlaction.XMLAction") -> None:
    """Log error for actions with unknown slots or scripts."""
    LOGGER.error("Executing unknown script for Action %s", act_object._name)
