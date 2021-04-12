"""Flnetwork module."""

# # -*- coding: utf-8 -*-
from PyQt6 import QtCore, QtNetwork  # type: ignore[import]

from typing import Optional, cast, Any


from pineboolib.core import decorators


class FLNetwork(QtCore.QObject):
    """FLNetwork class."""

    url: str
    request: QtNetwork.QNetworkRequest
    manager: QtNetwork.QNetworkAccessManager

    reply: Optional[QtNetwork.QNetworkReply] = None

    finished = QtCore.pyqtSignal()
    start = QtCore.pyqtSignal()
    data = QtCore.pyqtSignal(str)
    dataTransferProgress = QtCore.pyqtSignal(int, int)

    def __init__(self, url: str) -> None:
        """Inicialize."""

        super(FLNetwork, self).__init__()
        self.url = url

        self.request = QtNetwork.QNetworkRequest()

        self.manager = QtNetwork.QNetworkAccessManager()
        # self.manager.readyRead.connect(self._slotNetworkStart)
        cast(
            QtCore.pyqtSignal, self.manager.finished
        ).connect(  # type: ignore [attr-defined] # noqa: F821
            self._slotNetworkFinished
        )
        # finished_signal["QNetworkReply*"].connect(self._slotNetworkFinished) # FIXME: What does this code?
        # self.data.connect(self._slotNetWorkData)
        # self.dataTransferProgress.connect(self._slotNetworkProgress)

    @decorators.beta_implementation
    def get(self, location: str) -> None:
        """Get value from a location."""

        self.request.setUrl(QtCore.QUrl("%s%s" % (self.url, location)))
        self.reply = cast(QtNetwork.QNetworkReply, self.manager.get(self.request))
        try:
            cast(
                QtCore.pyqtSignal, self.reply.uploadProgress
            ).disconnect(  # type: ignore [attr-defined] # noqa: F821
                self._slotNetworkProgress
            )
            cast(
                QtCore.pyqtSignal, self.reply.downloadProgress
            ).disconnect(  # type: ignore [attr-defined] # noqa: F821
                self._slotNetworkProgress
            )
        except Exception:
            pass

        cast(
            QtCore.pyqtSignal, self.reply.downloadProgress
        ).connect(  # type: ignore [attr-defined] # noqa: F821
            self._slotNetworkProgress
        )

    @decorators.beta_implementation
    def put(self, data: Any, location: str) -> None:
        """Send data to a location."""

        self.request.setUrl(QtCore.QUrl("%s%s" % (self.url, location)))
        self.reply = cast(QtNetwork.QNetworkReply, self.manager.put(self.request, data))
        try:
            cast(
                QtCore.pyqtSignal, self.reply.uploadProgress
            ).disconnect(  # type: ignore [attr-defined] # noqa: F821
                self._slotNetworkProgress
            )
            cast(
                QtCore.pyqtSignal, self.reply.downloadProgress
            ).disconnect(  # type: ignore [attr-defined] # noqa: F821
                self._slotNetworkProgress
            )
        except Exception:
            pass
        cast(
            QtCore.pyqtSignal, self.reply.uploadProgress
        ).connect(  # type: ignore [attr-defined] # noqa: F821
            self._slotNetworkProgress
        )

    @decorators.beta_implementation
    def copy(self, from_location: str, to_location: str) -> None:
        """Copy data from a location to another."""

        self.request.setUrl(QtCore.QUrl("%s%s" % (self.url, from_location)))
        data = self.manager.get(self.request)
        self.put(data.readAll(), to_location)

    @decorators.pyqt_slot()
    def _slotNetworkStart(self) -> None:
        """Emit start signal."""

        self.start.emit()

    @decorators.pyqt_slot()
    def _slotNetworkFinished(self, reply: Any = None) -> None:
        """Emit finished signal."""

        self.finished.emit()

    # @decorators.pyqt_slot(QtCore.QByteArray)
    # def _slotNetWorkData(self, b):
    #    buffer = b
    #    self.data.emit(b)

    def _slotNetworkProgress(self, bytes_done: int, bytes_total: int) -> None:
        """Process data received."""

        if self.reply is None:
            raise Exception("No reply in progress")
        self.dataTransferProgress.emit(bytes_done, bytes_total)
        data_ = None
        reply_ = self.reply.readAll().data()
        try:
            data_ = str(reply_, encoding="iso-8859-15")
        except Exception:
            data_ = str(reply_, encoding="utf-8")

        self.data.emit(data_)
