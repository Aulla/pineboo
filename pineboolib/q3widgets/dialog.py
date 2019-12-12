"""Dialog module."""

from PyQt5 import QtCore, QtWidgets

from . import qdialog
from . import qpushbutton
from . import qtabwidget

from typing import Optional, Union


class Dialog(qdialog.QDialog):
    """Dialog class."""

    _layout: QtWidgets.QVBoxLayout
    _button_box: QtWidgets.QDialogButtonBox
    okButton: qpushbutton.QPushButton
    cancelButton: qpushbutton.QPushButton
    _tab: qtabwidget.QTabWidget

    def __init__(
        self,
        title: Optional[str] = None,
        f: Union[Optional[QtCore.Qt.WindowFlags], int] = None,
        desc: Optional[str] = None,
    ) -> None:
        """Inicialize."""

        # FIXME: f no lo uso , es qt.windowsflg
        super(Dialog, self).__init__(None, f if isinstance(f, str) else None)
        if title:
            self.setWindowTitle(str(title))

        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self._layout = QtWidgets.QVBoxLayout()
        self.setLayout(self._layout)
        self._button_box = QtWidgets.QDialogButtonBox()
        self.okButton = qpushbutton.QPushButton("&Aceptar")
        self.cancelButton = qpushbutton.QPushButton("&Cancelar")
        self.okButtonText = "Aceptar"
        self.cancelButtonText = "Cancelar"

        self._button_box.addButton(self.okButton, QtWidgets.QDialogButtonBox.AcceptRole)
        self._button_box.addButton(self.cancelButton, QtWidgets.QDialogButtonBox.RejectRole)
        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self._tab = qtabwidget.QTabWidget()
        self._tab.hide()

    def add(self, _object: QtWidgets.QWidget) -> None:
        """Add widget to Dialog."""

        self._layout.addWidget(_object)

    def newTab(self, name: str) -> None:
        """Add a new tab to Dialog."""

        if self._tab.isHidden():
            self._tab.show()
        self._tab.addTab(QtWidgets.QWidget(), str(name))

    def setWidth(self, width: Union[int, float]) -> None:
        """Set width."""

        height = self.height()
        # self.setMinimunSize(width, height)
        self.resize(int(width), height)

    def exec_(self) -> int:
        """Execute Dialog."""

        self._layout.addWidget(self._button_box)
        return super().exec_()

    def setHeight(self, height: Union[int, float]) -> None:
        """Set height."""

        width = self.width()
        # self.setMinimunSize(width, height)
        self.resize(width, int(height))

    def getCancelButtonText(self) -> str:
        """Return cancel button text."""

        return self.cancelButton.text

    def setCancelButtonText(self, text_: str) -> None:
        """Set cancel button text."""

        self.cancelButton.setText(text_)

    def getOkButtonText(self) -> str:
        """Return cancel button text."""

        return self.okButton.text

    def setOkButtonText(self, text_: str) -> None:
        """Set cancel button text."""

        self.okButton.setText(text_)

    def getTitle(self) -> str:
        """Return dialog title."""

        return self.windowTitle()

    def setTitle(self, title_: str) -> None:
        """Set dialog title."""

        self.setWindowTitle(title_)

    cancelButtonText: str = property(  # type: ignore [assignment] # noqa: F821
        getCancelButtonText, setCancelButtonText
    )
    okButtonText: str = property(  # type: ignore [assignment] # noqa: F821
        getOkButtonText, setOkButtonText
    )
    title: str = property(getTitle, setTitle)  # type: ignore [assignment] # noqa: F821
