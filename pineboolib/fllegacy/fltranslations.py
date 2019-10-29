"""Fltranslations mdoule."""

# -*- coding: utf-8 -*-
import os
from pineboolib import logging
from pineboolib.core import decorators

from PyQt5 import QtCore, Qt
from typing import Any, Union


"""
Esta clase gestiona las diferenetes trducciones de módulos y aplicación
"""


class FLTranslations(object):
    """
    FLTranslations class manages the different module and application traductions.
    """

    qmFileName: str

    def __init__(self) -> None:
        """Initialize."""

        super(FLTranslations, self).__init__()
        self.logger = logging.getLogger("FLTranslations")

    def loadTsFile(self, tor: Any, ts_file_name: Union[bytes, int, str], verbose) -> bool:
        """
        If the .qm does not exist, convert the .ts we give to .qm.

        @param tor. Object metatranslator class. type: "FLTranslator".
        @param tsFileName. Name of the .ts file to convert.
        @param verbose. Sample verbose (True, False).
        @return Boolean. Successful process.
        """

        # qm_file_name = "%s.qm" % ts_file_name[:-3]
        ok = False
        if os.path.exists(ts_file_name):
            ok = tor.load(ts_file_name)

        if not ok:
            self.logger.warning("For some reason, I cannot load '%s'", ts_file_name)
        return ok

    @decorators.Deprecated
    def releaseTsFile(self, ts_file_name: str, verbose: bool, stripped: bool) -> None:
        """
        Free the .ts file.

        @param tsFileName. .Ts file name
        @param verbose. Sample verbose (True, False)
        @param stripped. not used
        """

        pass
        # tor = None

        # if self.loadTsFile(tor, ts_file_name, verbose):
        #    pass
        # qm_file_name = "%s.qm" % ts_file_name[:-3]
        # FIXME: self.releaseMetaTranslator - does not exist in this class
        # if not os.path.exists(qm_file_name):
        #     self.releaseMetaTranslator(tor, qm_file_name, verbose, stripped)

    def lrelease(self, ts_input_file: str, qm_output_file: str, stripped: bool = True) -> None:
        """
        Convert the .ts file to .qm.

        @param tsImputFile. Source .ts file name.
        @param qmOutputFile. Destination .qm file name.
        @param stripped. Not used.
        """

        from pineboolib.application import project

        verbose = False
        metTranslations = False

        f = Qt.QFile(ts_input_file)
        if not f.open(QtCore.QIODevice.ReadOnly):
            self.logger.warning("Cannot open file '%s'", ts_input_file)
            return

        t = Qt.QTextStream(f)
        full_text = t.readAll()
        f.close()

        if full_text.find("<!DOCTYPE TS>") >= 0:
            self.releaseTsFile(ts_input_file, verbose, stripped)

        else:
            if project.conn_manager is None:
                raise Exception("Project has no connection yet")

            key = project.conn_manager.managerModules().shaOfFile(ts_input_file)
            tagMap = full_text
            # TODO: hay que cargar todo el contenido del fichero en un diccionario
            for key, value in tagMap:
                toks = value.split(" ")

                for t in toks:
                    if key == "TRANSLATIONS":
                        metTranslations = True
                        self.releaseTsFile(t, verbose, stripped)

            if not metTranslations:
                self.logger.warning(
                    "Met no 'TRANSLATIONS' entry in project file '%s'", ts_input_file
                )
