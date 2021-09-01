"""QBytearray module."""
# -*- coding: utf-8 -*-

from PyQt6 import QtCore  # type: ignore[import]
from typing import Union


class QByteArray(QtCore.QByteArray):
    """QByteArray class."""

    def __init__(self, *args) -> None:
        """Inicialize."""

        if len(args) == 1 and isinstance(args[0], int):  # QByteArray(int)
            super().__init__()
        else:
            super().__init__(*args)

    def set(self, pos: int, _ch: Union[str, int]) -> None:
        """Set a char into a position."""
        _ch = _ch if isinstance(_ch, str) else chr(_ch)
        super().insert(pos, _ch.encode())

    def get(self, pos: int):
        """Get a char number from a position."""
        return self.data()[pos]

    def fromBase64(self, *args) -> bytes:  # type: ignore[override] # noqa : F821
        """Return a decoded base64 value."""
        if args:
            return super().fromBase64(*args).data()
        else:
            import base64

            return base64.b64decode(self.data())

    def sha1(self) -> str:
        """Return sha1."""
        hash = QtCore.QCryptographicHash(QtCore.QCryptographicHash.Algorithm.Sha1)
        hash.addData(self.data())
        return hash.result().toHex().data().decode("utf-8").upper()

    def setString(self, val: str) -> None:
        """Set string to QByteArray."""
        self.append(val.encode())

    def getString(self) -> str:
        """Return string value format."""
        return self.data().decode("utf-8").upper()

    string = property(getString, setString)
