# -*- coding: utf-8 -*-
"""
PNUnpacker package.

Extract the files from the .abanq and .eneboopkg packages and save them in the flfiles table
"""

from PyQt6 import QtCore  # type: ignore
from typing import Any, List
from pineboolib.core import decorators

err_msgs_: List[str] = []


class PNUnpacker(QtCore.QObject):
    """PNUnpacker Class."""

    def __init__(self, in_: str) -> None:
        """
        Initialize the class.

        @param in_. package file name.
        """

        self.file_ = QtCore.QFile(QtCore.QDir.cleanPath(in_))
        if not self.file_.open(QtCore.QIODevice.OpenModeFlag.ReadOnly):
            raise Exception("Error opening file %r" % in_)
        self.stream_ = QtCore.QDataStream(self.file_)
        self.package_version_ = self.stream_.readBytes().decode("utf-8")

    @decorators.not_implemented_warn
    def errorMessages(self) -> list:
        """
        Return a list of messages with errors that have occurred.

        @return error list.
        """

        return err_msgs_

    def getText(self) -> str:
        """
        Return a record.

        @return record string.
        """

        data_bytes: bytes = QtCore.qUncompress(self.stream_.readBytes()).data()  # type: ignore [call-overload]
        try:
            data_ = data_bytes.decode("utf-8")
        except UnicodeDecodeError:
            data_ = data_bytes.decode("iso-8859-15")

        return data_

    def getBinary(self) -> Any:
        """
        Return a record in byte format.

        @return record bytes.
        """

        return QtCore.qUncompress(self.stream_.readBytes())  # type: ignore [call-overload]

    def getVersion(self) -> str:
        """
        Return the package version.

        @return package version string.
        """

        return self.package_version_

    def jump(self) -> None:
        """
        Skip a field in the package structure.
        """
        self.stream_.readBytes()
