"""Messagebox module."""

# -*- coding: utf-8 -*-
from PyQt6 import QtWidgets  # type: ignore[import]

from pineboolib import application
from pineboolib.core.utils import logging
import clipboard  # type: ignore [import] # noqa: F821

from typing import Optional, List

LOGGER = logging.get_logger(__name__)


class MessageBox:
    """MessageBox class."""

    Yes = QtWidgets.QMessageBox.StandardButton.Yes
    No = QtWidgets.QMessageBox.StandardButton.No
    NoButton = QtWidgets.QMessageBox.StandardButton.NoButton
    Ok = QtWidgets.QMessageBox.StandardButton.Ok
    Cancel = QtWidgets.QMessageBox.StandardButton.Cancel
    Ignore = QtWidgets.QMessageBox.StandardButton.Ignore

    @classmethod
    def msgbox(cls, typename, *args) -> Optional["QtWidgets.QMessageBox.StandardButton"]:
        """Return a messageBox."""

        if not getattr(application, "TESTING_MODE", None):
            if QtWidgets.QApplication.platformName() == "offscreen":
                LOGGER.warning(
                    "q3widget.MessageBox launch when library mode ON! (%s : %s)",
                    typename,
                    args,
                    stack_info=True,
                )
                return None

        msg_box = getattr(QtWidgets.QMessageBox, typename, None)
        title = "Pineboo"
        parent = QtWidgets.QApplication.activeWindow()
        buttons: List["QtWidgets.QMessageBox.StandardButton"] = []
        default_button = None
        text = ""

        for number, argument in enumerate(args):
            if number == 0:
                text = argument
            else:
                if isinstance(argument, str):
                    title = argument
                elif isinstance(argument, QtWidgets.QMessageBox.StandardButton):
                    if len(buttons) < 2:
                        buttons.append(argument)
                    else:
                        default_button = argument
                elif argument:
                    parent = argument

        if application.PROJECT._splash:
            application.PROJECT._splash.hide()

        if not getattr(application, "TESTING_MODE", None):
            if not default_button:
                return msg_box(parent, title, text, *buttons)
            else:
                return msg_box(parent, title, text, *buttons, default_button)
        else:
            return QtWidgets.QMessageBox.StandardButton.Ok

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

        result = cls.msgbox("warning", *args)
        if not getattr(application, "TESTING_MODE", None):
            clipboard.copy(str(text_))
        return result

    @classmethod
    def critical(cls, *args) -> Optional["QtWidgets.QMessageBox.StandardButton"]:
        """Return an critical messageBox."""

        text_ = args[0] if isinstance(args[0], str) else args[2]
        result = cls.msgbox("critical", *args)
        if not getattr(application, "TESTING_MODE", None):
            clipboard.copy(str(text_))
        return result
