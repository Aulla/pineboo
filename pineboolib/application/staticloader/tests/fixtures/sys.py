"""Sys module."""
# -*- coding: utf-8 -*-
from pineboolib.qsa import qsa
from pineboolib import logging


LOGGER = logging.get_logger(__name__)


class FormInternalObj(qsa.FormDBWidget):
    """FormInternalObj class."""

    def _class_init(self) -> None:
        """Inicialize."""
        self.form = self
        self.iface = self

    def saluda(self) -> str:
        """Test overload function."""

        return "Hola!"


form = None
