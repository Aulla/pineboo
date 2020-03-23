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

    @classmethod
    def msgbox(
        cls, typename, text, button0, button1=None, button2=None, title=None, form=None
    ) -> Optional["QtWidgets.QMessageBox.StandardButton"]:
        """Return a messageBox."""
        if not application.PROJECT.main_form:
            return None

        if application.PROJECT._splash:
            application.PROJECT._splash.hide()

        if not isinstance(text, str):
            LOGGER.warning("MessageBox help!", stack_info=True)
            # temp = text
            text = button1
            button1 = title
            title = button0
            button0 = button2
            button2 = None

        dgi_ = application.PROJECT.dgi

        if dgi_ is not None:

            message_box = None

            if not title:
                title = "Pineboo"

            if typename == "question":
                message_box = getattr(dgi_, "msgBoxQuestion", None)
            elif typename == "information":
                message_box = getattr(dgi_, "msgBoxInfo", None)
            elif typename == "warning":
                message_box = getattr(dgi_, "msgBoxWarning", None)
            else:
                message_box = getattr(dgi_, "msgBoxError", None)

        if message_box is not None:
            return message_box(text, None, title)

        return None

    @classmethod
    def question(cls, *args) -> Optional["QtWidgets.QMessageBox.StandardButton"]:
        """Return an question messageBox."""

        return cls.msgbox("question", *args)

    @classmethod
    def information(cls, *args) -> Optional["QtWidgets.QMessageBox.StandardButton"]:
        """Return an information messageBox."""
        return cls.msgbox("question", *args)

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
