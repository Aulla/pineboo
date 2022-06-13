"""PNTranslations module."""

# -*- coding: utf-8 -*-
import os
from pineboolib.core import decorators
from pineboolib import application, logging

from PyQt5 import QtCore
from typing import Any


"""
Esta clase gestiona las diferenetes trducciones de módulos y aplicación
"""
LOGGER = logging.get_logger(__name__)


class PNTranslations(object):
    """
    FLTranslations class manages the different module and application traductions.
    """

    def loadTsFile(self, tor: Any, ts_file_name: str, verbose: bool = False) -> bool:
        """
        If the .qm does not exist, convert the .ts we give to .qm.

        @param tor. Object metatranslator class. type: "FLTranslator".
        @param tsFileName. Name of the .ts file to convert.
        @param verbose. Sample verbose (True, False).
        @return Boolean. Successful process.
        """

        # qm_file_name = "%s.qm" % ts_file_name[:-3]
        ret_ = False
        if os.path.exists(ts_file_name):
            ret_ = tor.load(ts_file_name)

        if not ret_:
            LOGGER.warning("For some reason, I cannot load '%s'", ts_file_name)
        return ret_

    @decorators.deprecated
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

        verbose = False
        meta_trans = False

        file_ = QtCore.QFile(ts_input_file)
        if not file_.open(QtCore.QIODevice.ReadOnly):
            LOGGER.warning("Cannot open file '%s'", ts_input_file)
            return

        stream = QtCore.QTextStream(file_)
        full_text = stream.readAll()
        file_.close()

        if full_text.find("<!DOCTYPE TS>") >= 0:
            self.releaseTsFile(ts_input_file, verbose, stripped)

        else:
            if application.PROJECT.conn_manager is None:
                raise Exception("Project has no connection yet")

            key = application.PROJECT.conn_manager.managerModules().shaOfFile(ts_input_file)
            for key, value in full_text:  # type: ignore [misc]
                toks = value.split(" ")  # type: ignore [has-type]

                for token in toks:
                    if key == "TRANSLATIONS":
                        meta_trans = True
                        self.releaseTsFile(token, verbose, stripped)

            if not meta_trans:
                LOGGER.warning("Met no 'TRANSLATIONS' entry in project file '%s'", ts_input_file)
