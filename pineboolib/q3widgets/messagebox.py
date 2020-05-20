"""Messagebox module."""

# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets

from pineboolib import application
from pineboolib.core.utils import logging

import clipboard  # type: ignore [import] # noqa: F821

from typing import Optional

LOGGER = logging.get_logger(__name__)


class MessageBox:
    """MessageBox class."""

    Yes = QtWidgets.QMessageBox.Yes
    No = QtWidgets.QMessageBox.No
    NoButton = QtWidgets.QMessageBox.NoButton
    Ok = QtWidgets.QMessageBox.Ok
    Cancel = QtWidgets.QMessageBox.Cancel
    Ignore = QtWidgets.QMessageBox.Ignore

    @classmethod
    def msgbox(cls, typename, *args) -> Optional["QtWidgets.QMessageBox.StandardButton"]:
        """Return a messageBox."""

        msg_box = getattr(QtWidgets.QMessageBox, typename, None)
        if msg_box is None:
            LOGGER.warning("Unknown type name %s", typename)
            return None
        else:

            title = "Pineboo"
            parent = QtWidgets.qApp.activeWindow()
            buttons = []
            text = ""

            for number, argument in enumerate(args):
                if number == 0:
                    text = argument
                else:
                    if isinstance(argument, str):
                        title = argument
                    elif isinstance(argument, QtWidgets.QMessageBox.StandardButton):
                        buttons.append(argument)
                    elif argument:
                        parent = argument

            if application.PROJECT._splash:
                application.PROJECT._splash.hide()

            return msg_box(parent, title, text, *buttons)

    @classmethod
    def question(cls, *args) -> Optional["QtWidgets.QMessageBox.StandardButton"]:
        """Return an question messageBox."""

        return cls.msgbox("question", *args)

    @classmethod
    def information(cls, *args) -> Optional["QtWidgets.QMessageBox.StandardButton"]:
        """Return an information messageBox."""
        return cls.msgbox("information", *args)

    @classmethod
    def warning(cls, *args) -> Optional["QtWidgets.QMessageBox.StandardButton"]:
        """Return an warning messageBox."""

        text_ = args[0] if isinstance(args[0], str) else args[2]
        clipboard.copy(str(text_))

        return cls.msgbox("warning", *args)

    @classmethod
    def critical(cls, *args) -> Optional["QtWidgets.QMessageBox.StandardButton"]:
        """Return an critical messageBox."""

        text_ = args[0] if isinstance(args[0], str) else args[2]
        clipboard.copy(str(text_))

        return cls.msgbox("critical", *args)
