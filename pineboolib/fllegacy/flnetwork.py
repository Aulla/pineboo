"""Flnetwork module."""

# # -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtNetwork

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
        cast(QtCore.pyqtSignal, self.manager.finished).connect(self._slotNetworkFinished)
        # finished_signal["QNetworkReply*"].connect(self._slotNetworkFinished) # FIXME: What does this code?
        # self.data.connect(self._slotNetWorkData)
        # self.dataTransferProgress.connect(self._slotNetworkProgress)

    @decorators.BetaImplementation
    def get(self, location: str) -> None:
        """Get value from a location."""

        self.request.setUrl(QtCore.QUrl("%s%s" % (self.url, location)))
        self.reply = self.manager.get(self.request)
        try:
            cast(QtCore.pyqtSignal, self.reply.uploadProgress).disconnect(self._slotNetworkProgress)
            cast(QtCore.pyqtSignal, self.reply.downloadProgress).disconnect(
                self._slotNetworkProgress
            )
        except Exception:
            pass

        cast(QtCore.pyqtSignal, self.reply.downloadProgress).connect(self._slotNetworkProgress)

    @decorators.BetaImplementation
    def put(self, data: Any, location: str) -> None:
        """Send data to a location."""

        self.request.setUrl(QtCore.QUrl("%s%s" % (self.url, location)))
        self.reply = self.manager.put(data, self.request)
        try:
            cast(QtCore.pyqtSignal, self.reply.uploadProgress).disconnect(self._slotNetworkProgress)
            cast(QtCore.pyqtSignal, self.reply.downloadProgress).disconnect(
                self._slotNetworkProgress
            )
        except Exception:
            pass
        cast(QtCore.pyqtSignal, self.uploadProgress).connect(self.slotNetworkProgress)

    @decorators.BetaImplementation
    def copy(self, fromLocation: str, toLocation: str) -> None:
        """Copy data from a location to another."""

        self.request.setUrl(QtCore.QUrl("%s%s" % (self.url, fromLocation)))
        data = self.manager.get(self.request)
        self.put(data.readAll(), toLocation)

    @decorators.pyqtSlot()
    def _slotNetworkStart(self) -> None:
        """Emit start signal."""

        self.start.emit()

    @decorators.pyqtSlot()
    def _slotNetworkFinished(self, reply: Any = None) -> None:
        """Emit finished signal."""

        self.finished.emit()

    # @decorators.pyqtSlot(QtCore.QByteArray)
    # def _slotNetWorkData(self, b):
    #    buffer = b
    #    self.data.emit(b)

    def _slotNetworkProgress(self, bDone: int, bTotal: int) -> None:
        """Process data received."""

        if self.reply is None:
            raise Exception("No reply in progress")
        self.dataTransferProgress.emit(bDone, bTotal)
        data_ = None
        reply_ = self.reply.readAll().data()
        try:
            data_ = str(reply_, encoding="iso-8859-15")
        except Exception:
            data_ = str(reply_, encoding="utf-8")

        self.data.emit(data_)
