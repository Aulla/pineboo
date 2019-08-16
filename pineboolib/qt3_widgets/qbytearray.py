"""QBytearray module."""
# -*- coding: utf-8 -*-

from PyQt5 import QtCore  # type: ignore


class QByteArray(QtCore.QByteArray):
    """QByteArray class."""

    def sha1(self) -> str:
        """Return sha1."""
        hash = QtCore.QCryptographicHash(QtCore.QCryptographicHash.Sha1)
        hash.addData(self.data())
        return hash.result().toHex().data().decode("utf-8").upper()

    def setString(self, val: str) -> None:
        """Set string to QByteArray."""
        self.append(val)

    def getString(self) -> str:
        """Return string value format."""
        return self.data().decode("utf-8").upper()

    string = property(getString, setString)
