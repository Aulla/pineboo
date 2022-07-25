"""QHttp module."""

from PyQt6 import QtCore, QtNetwork  # type: ignore[import]
from typing import Union, Optional, cast, Dict, List, Any
from pineboolib.core import decorators


class QHttpRequest(object):
    """QHttpRequest class."""

    _valid: bool
    _major_ver: int
    _minor_ver: int
    _values: Dict[str, Any]
    _id: int
    ID: int = 0

    def __init__(self):
        """Initialize."""

        self._id = self.ID
        print("* ID", self._id)
        self.ID += 1  # pylint: disable=invalid-name
        self._values = {}
        self._major_ver = 1
        self._minor_ver = 1
        # self.setValue("Connection", "keep-alive")

    def majorVersion(self) -> int:
        """Return major version."""

        return self._major_ver

    def minorVersion(self) -> int:
        """Return minor version."""

        return self._minor_ver

    def parse(self, text_: str) -> bool:
        """Parse text."""

        list_: List[str] = []
        pos = text_.find("\n")
        if pos > 0 and text_[pos - 1] == "\r":
            list_ = text_.strip().split("\r\n")
        else:
            list_ = text_.strip().split("\n")

        if not list_:
            return True

        lines_: List[str] = []
        for item in list_:
            if item[0].isspace():
                if lines_:
                    lines_[len(lines_) - 1] += " "
                    lines_[len(lines_) - 1] += item.strip()
            else:
                lines_.append(item)

        for i in range(len(lines_)):
            if not self.parseLine(lines_[i], i):
                self._valid = False
                return False

        return True

    def keys(self) -> str:
        """Return keys stringlist."""

        return ",".join(list(self._values.keys()))

    def setValue(self, key_: str, value_: Any):
        """Set key to dict."""

        self._values[key_.lower()] = value_

    def value(self, key_: str):
        """Return value."""

        if key_.lower() in self._values.keys():
            return self._values[key_.lower()]

        raise ValueError("%s not found in values!" % key_)

    def removeValue(self, key_: str):
        """Remove key from dict."""

        key_ = key_.lower()
        if key_ in self._values.keys():
            self._values[key_] = None
            del self._values[key_]

    def setValid(self, valid_: bool) -> None:
        """Set if is valid."""

        self._valid = valid_

    def parseLine(self, line_: str, num_: int = 0) -> bool:
        """Parse line."""

        if line_.find(":") == -1:
            return False
        else:
            list_ = line_.split(":")
            self._values[list_[0].lower()] = list_[1]

            return True

    def __str__(self):
        """Return string value."""

        if not self._valid:
            return ""
        ret_ = ""
        for key, value in self._values.items():
            ret_ += "%s:%s\r\n" % (key, value)

        return ret_

    def hasContentLength(self):
        """Return if content length is avaliable."""

        return "content-length" in self._values.keys()

    def contentLenth(self) -> int:
        """Return content length."""

        if "content-length" in self._values.keys():
            return self._values["content-length"]
        else:
            return 0

    def setContentLength(self, length_: int) -> None:
        """Set content length."""

        self._values["content-length"] = length_

    def hasContentType(self):
        """Return if has content type."""

        return "content-type" in self._values.keys()

    def contentType(self) -> str:
        """Return content type."""

        if "content-type" in self._values.keys():
            return self._values["content-type"]
        else:
            return ""

    def setContentType(self, type_: str) -> None:
        """Set content type."""

        self._values["content-type"] = type_


class QHttpResponseHeader(QHttpRequest):
    """QHttpRespnse class."""

    _status_code: int
    _reason_phr: Optional[str]

    def __init__(self, *args):
        """Initialize."""

        super().__init__()
        self.setValid(False)
        self._status_code = 0
        self._reason_phr = ""

        if len(args) > 1:
            self._status_code = args[0]
            self._reason_phr = args[1] or ""
            if len(args) > 2:
                self._major_ver = args[2]
            if len(args) > 3:
                self._minor_ver = args[3]
        else:
            self.parse(args[0])

    def setStatusLine(self, code_: int, text_: Optional[str] = None, major_ver_=1, minor_ver_=1):
        """Set status line."""

        self.setValid(True)
        self._status_code = code_
        self._reason_phr = text_
        self._major_ver = major_ver_
        self._minor_ver = minor_ver_

    def statusCode(self) -> int:
        """Return status code."""

        return self._status_code

    def reasonPhrase(self) -> str:
        """Return reason."""

        return self._reason_phr or ""

    def parseLine(self, line_: str, number_: int = 0) -> bool:
        """Parse Line."""
        if number_ != 0:
            return super().parseLine(line_)

        line_striped = line_.strip()
        if len(line_striped) < 10:
            return False

        if (
            line_striped[0:5] == "HTTP/"
            and line_striped[5].isdigit()
            and line_striped[6] == "."
            and line_striped[7].isdigit()
            and line_striped[8] == "."
            and line_striped[9].isdigit()
        ):
            self._major_ver = int(line_striped[5]) - 0
            self._minor_ver = int(line_striped[7]) - 0

            pos = line_striped[9:].find(" ")
            if pos > -1:
                self._reason_phr = line_striped[9 + pos :]
                self._status_code = int(line_striped[9 : 9 + pos])
            else:
                self._status_code = int(line_striped[9:])
                self._reason_phr = ""
        else:
            return False

        return True

    def __str__(self):
        """Return str value."""

        return "HTTP/%s.%s %s %s\r\n%s\r\n" % (
            self._major_ver,
            self._minor_ver,
            self._status_code,
            self._reason_phr,
            str(super()),
        )


class QHttpRequestHeader(QHttpRequest):
    """QHttpRequestHeader class."""

    _method: str
    _path: str

    def __init__(self, *args):
        """Initialize."""

        super().__init__()

        self.setValid(False)
        self._method = "POS"

        if len(args) > 1:
            self._method = args[0]
            self._path = args[1]
            if len(args) > 2:
                self._major_ver: int = args[2]
            if len(args) > 3:
                self._minor_ver: int = args[3]

        elif isinstance(args[0], str):
            self.parse(args[0])
        else:
            self = args[0]

    def setRequest(self, method_: str, path_: str, major_ver: int = 1, minor_ver=1):
        """Set request."""

        self.setValid(True)
        self._method = method_
        self._path = path_
        self._major_ver = major_ver
        self._minor_ver = minor_ver

    def method(self) -> str:
        """Return method."""

        return self._method

    def path(self) -> str:
        """Return path."""

        return self._path

    def __str__(self):
        """Return string value."""

        return "%s %s HTTP/%s.%s\r\n%s\r\n" % (
            self._method,
            self._path,
            self._major_ver,
            self._minor_ver,
            str(super()),
        )


class HttpState(QtCore.QObject):
    """HttpState class."""

    Unconnected = 0
    HostLookup = 1
    Connecting = 2
    Sending = 3
    Reading = 4
    Connected = 5
    Closing = 6


class HttpError(QtCore.QObject):
    """HttpError class."""

    NoError = 0
    UnknownError = 1
    HostNotFound = 2
    ConnectionRefused = 3
    UnexpectedClose = 4
    InvalidResponseHeader = 5
    WrongContentLength = 6
    Aborted = 7


class QHttp(HttpState, HttpError):
    """QHttp class."""

    stateChanged = QtCore.pyqtSignal(int)
    dataSendProgress = QtCore.pyqtSignal(int, int)
    dataReadProgress = QtCore.pyqtSignal(int, int)
    requestStarted = QtCore.pyqtSignal(int)
    requestFinished = QtCore.pyqtSignal(int, bool)
    responseHeaderReceived = QtCore.pyqtSignal(QHttpResponseHeader)
    done = QtCore.pyqtSignal(bool)
    readyRead = QtCore.pyqtSignal(QHttpResponseHeader)

    _manager: QtNetwork.QNetworkAccessManager
    _reply: QtNetwork.QNetworkReply
    _state: int
    _error: int
    _host: str
    _port: int
    _name: str
    _error_str: str
    _parent: Optional[QtCore.QObject]
    _operation: int
    _data: Optional[QtCore.QBuffer]
    _current_id: int

    def __init__(self, *args):
        """Initialize."""

        super().__init__()
        self._state = self.Unconnected
        self._error = self.NoError

        self._data = None

        if len(args) == 2:
            self.initialize2(args[0], args[1])
        elif len(args) == 4:
            self.initialize1(args[0], args[1], args[2], args[3])

        self._manager = QtNetwork.QNetworkAccessManager()
        # self._request = QtNetwork.QNetworkRequest()
        cast(
            QtCore.pyqtSignal, self._manager.finished
        ).connect(  # type: ignore [attr-defined] # noqa: F821
            self._slotNetworkFinished
        )

        self._error_str = self.tr("Unknown error")

    def initialize1(
        self,
        host_name: str,
        port_: int = 80,
        parent_: Optional[QtCore.QObject] = None,
        name_: Optional[str] = None,
    ):
        """Initialize with kwars."""
        self._host = "%s:%s" % (host_name, port_)
        # self._port = port_
        self._parent = parent_
        self._name = name_ or ""

    def initialize2(self, parent_: QtCore.QObject, name_: str = ""):
        """Initialize with args."""

        self._parent = parent_
        self._name = name_

    def setHost(self, name_: str, port_: int = 80) -> None:
        """Set host."""

        self._name = "%s:%s" % (name_, port_)
        # self._port = port_

    def get(self, full_path: str) -> None:
        """Get data from url."""

        _request = QHttpRequestHeader("GET", full_path)
        _request.setValue("Connection", "Keep-Alive")
        self.request(_request)

        # self._data = QtCore.QBuffer()
        # _request = QtNetwork.QNetworkRequest()
        # _request.setUrl(QtCore.QUrl(path_))

        # self._state = self.Connecting
        # self._reply = self._manager.get(_request)
        # self._state = self.Connected
        # cast(QtCore.pyqtSignal, self._reply.downloadProgress).connect(self._slotNetworkProgressRead)

    def post(self, full_path: str, data_: Union[QtCore.QIODevice, QtCore.QByteArray]) -> None:
        """Send data to url."""

        _request = QHttpRequestHeader("POST", full_path)
        _request.setValue("Connection", "Keep-Alive")
        self.request(_request, data_)

        # self._data = QtCore.QBuffer()
        # _request = QtNetwork.QNetworkRequest()
        # _request.setUrl(QtCore.QUrl(path_))
        # self._state = self.Connecting
        # self._reply = self._manager.post(_request, data_)
        # self._state = self.Connected
        # cast(QtCore.pyqtSignal, self._reply.downloadProgress).connect(self._slotNetworkProgressRead)

    @decorators.not_implemented_warn
    def head(self, path_: str) -> None:
        """Set head."""
        return None
        # header = QHttpRequestHeader("HEAD", path_)
        # header.setValue("Connection", "Keep-Alive")
        # return self.request()

    def request(
        self,
        request_header: QHttpRequestHeader,
        data_: Optional[Union[QtCore.QIODevice, QtCore.QByteArray]] = None,
        buffer_: Optional[QtCore.QBuffer] = None,
    ) -> None:
        """Send request."""

        self._data = None
        del self._data

        if buffer_ is None:
            buffer_ = QtCore.QBuffer()

        _request = QtNetwork.QNetworkRequest()
        _tipo = request_header.method().lower()

        # if request_header.hasContentType():
        #    _request.setHeader(
        #        QtNetwork.QNetworkRequest.ContentTypeHeader, request_header.contentType()
        #    )
        url_ = QtCore.QUrl(request_header.path())

        for k in request_header._values.keys():
            if k != "host":
                _request.setRawHeader(
                    str.encode(k),  # type: ignore [arg-type] # noqa: F821
                    str.encode(  # type: ignore [arg-type] # noqa: F821
                        str(request_header._values[k]).lower()
                    ),
                )

            else:
                url_ = QtCore.QUrl("%s/%s" % (request_header.value("host"), request_header.path()))

        if not url_.isValid():
            raise Exception("url_ is not a valid URL!")
        _request.setUrl(url_)

        method_ = getattr(self._manager, _tipo, None)
        self._data = buffer_
        if self._data is not None:
            self._data.open(QtCore.QIODevice.OpenModeFlag.ReadWrite)

        self._state = self.Connecting

        if _tipo == "get":
            self._reply = method_(_request)
        else:
            self._reply = method_(_request, data_)

        cast(
            QtCore.pyqtSignal, self._reply.downloadProgress
        ).connect(  # type: ignore [attr-defined] # noqa: F821
            self._slotNetworkProgressRead
        )
        cast(
            QtCore.pyqtSignal, self._reply.uploadProgress
        ).connect(  # type: ignore [attr-defined] # noqa: F821
            self._slotNetworkProgressSend
        )
        self._state = self.Connected
        self._current_id = request_header._id
        self.requestStarted.emit(request_header._id)

    @decorators.not_implemented_warn
    def closeConnection(self) -> None:
        """Close Connection."""
        self._state = self.Closing
        self._reply.close()

    def bytesAvalible(self) -> int:
        """Return bytes avalible."""

        if self._data is not None:
            return self._data.size()
        else:
            return self._reply.size()

    @decorators.not_implemented_warn
    def readBlock(self, data_: str, max_length_: int) -> None:
        """Read block."""

        pass

    def readAll(self) -> QtCore.QByteArray:
        """Read all data."""
        if self._data is not None:
            return self._data.readAll()
        else:
            return self._reply.readAll()

    def currentId(self) -> int:
        """Return id."""

        return self._current_id

    @decorators.not_implemented_warn
    def currentSourceDevice(self) -> QtCore.QIODevice:
        """Return current source device."""

        pass

    @decorators.not_implemented_warn
    def currentDestinationDevice(self) -> QtCore.QIODevice:
        """Return current destination device."""

        pass

    @decorators.not_implemented_warn
    def currentRequest(self) -> None:
        """Return current request."""

        return None

    @decorators.not_implemented_warn
    def hasPendingRequests(self) -> bool:
        """Return if pendidng reuqest exists."""

        return True

    @decorators.not_implemented_warn
    def clearPendingRequests(self) -> None:
        """Clear pending requests."""

        pass
        # for request_ in list(self._pending_request):
        #    self._pending_request.remove(request_)

    def setState(self, state_: int) -> None:
        """Set state."""

        self._state = state_

    def state(self) -> int:
        """Return state."""

        return self._state

    def error(self) -> int:
        """Return error."""

        return cast(int, self._reply.error())

    def errorString(self) -> str:
        """Return error string."""

        return self._reply.errorString()

    def _slotNetworkFinished(self) -> None:
        """Send done signal."""
        self._state = self.Closing
        # sender = self.sender()

        error_ = True
        if self._error == self.NoError:
            error_ = False

        self.done.emit(error_)
        self.requestFinished.emit(0, error_)
        self._state = self.Unconnected

    def _slotNetworkProgressRead(self, b_done: int, b_total: int) -> None:
        """Send done signal."""

        if self._reply is None:
            raise Exception("No reply in progress")

        self._state = self.Reading
        self.dataReadProgress.emit(b_done, b_total)
        # self.dataSendProgress.emit(b_done, b_total)

        if self._data is not None:
            data_ = self._reply.readAll()
            self._data.write(data_)  # type: ignore [arg-type] # noqa: F821
        else:
            self.readyRead.emit()

    def _slotNetworkProgressSend(self, b_done: int, b_total: int) -> None:
        """Send done signal."""

        if self._reply is None:
            raise Exception("No reply in progress")

        self._state = self.Sending
        # self.dataReadProgress.emit(b_done, b_total)
        self.dataSendProgress.emit(b_done, b_total)

        if self._data is not None:
            data_ = self._reply.readAll()
            self._data.write(data_)  # type: ignore [arg-type] # noqa: F821
        else:
            self.readyRead.emit()
