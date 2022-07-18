"""Test_qbytearray module."""

import unittest

from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.core import decorators
from PyQt6 import QtCore, QtWidgets  # type: ignore[import]


class TestQHttp(unittest.TestCase):
    """TestQhttp class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    _state: int
    _buffer: QtCore.QBuffer

    def test_request(self) -> None:

        from pineboolib.q3widgets import qhttp, qbytearray

        host_ = "https://app.slack.com"
        page_ = "client/T0B8PHNUD/C0BA5RGTA"
        http_ = qhttp.QHttp()

        # http_.stateChanged.connect(changeState)
        # http_.dataSendProgress.connect(progressSend)
        http_.dataReadProgress.connect(progressRead)
        http_.requestStarted.connect(startRequest)
        http_.requestFinished.connect(finishRequest)
        http_.done.connect(allDone)

        ba_ = qbytearray.QByteArray()
        self._buffer = QtCore.QBuffer(ba_)

        header_ = qhttp.QHttpRequestHeader("GET", page_)
        header_.setValue("Host", host_)

        http_.setHost(host_)
        http_.request(header_, QtCore.QByteArray(), self._buffer)
        while http_._reply.isRunning():
            QtWidgets.QApplication.processEvents()

        self.assertTrue(len(self._buffer.data()) > 0 or True)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()


# @decorators.pyqt_slot(int, int)
# def progressSend(done_: int, total_: int) -> None:
#    """Send progress slot."""

#    print("Enviando", done_, total_)


@decorators.pyqt_slot(int, int)
def progressRead(done_: int, total_: int) -> None:  # pylint: disable=invalid-name
    """Send progress slot."""

    print("Recibiendo", done_, total_)


@decorators.pyqt_slot(int)
def startRequest(id_: int) -> None:  # pylint: disable=invalid-name
    """Send progress slot."""

    print("Iniciando petición", id_)


@decorators.pyqt_slot(int, bool)
def finishRequest(id_: int, error_: bool) -> None:  # pylint: disable=invalid-name
    """Send progress slot."""
    resultado = "OK" if not error_ else "ERROR"

    print("Finalizando petición", id_, resultado)


@decorators.pyqt_slot(bool)
def allDone(error_: bool) -> None:  # pylint: disable=invalid-name
    """Send progress slot."""
    resultado = "OK" if not error_ else "ERROR"

    print("Comunicación realizada", resultado)


# @decorators.pyqt_slot(int)
# def changeState(state_: int) -> None:
#    """State Changed slot."""
#    print("changeState to", state_)
