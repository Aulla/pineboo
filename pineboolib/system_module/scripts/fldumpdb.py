"""Fldump module."""
# -*- coding: utf-8 -*-
from pineboolib.qsa import qsa


class FormInternalObj(qsa.FormDBWidget):
    """FormInternalObj class."""

    def main(self):
        """Entry function."""
        qsa.sys.dumpDatabase()
