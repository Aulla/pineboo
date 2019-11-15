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
    okButtonText: str
    cancelButtonText: str
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
        self.okButtonText = "Aceptar"
        self.cancelButtonText = "Cancelar"
        self.okButton = qpushbutton.QPushButton("&Aceptar")
        self.cancelButton = qpushbutton.QPushButton("&Cancelar")
        self._button_box.addButton(self.okButton, QtWidgets.QDialogButtonBox.AcceptRole)
        self._button_box.addButton(self.cancelButton, QtWidgets.QDialogButtonBox.RejectRole)
        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self._tab = qtabwidget.QTabWidget()
        self._tab.hide()
        self._layout.addWidget(self._tab)

    def add(self, _object: QtWidgets.QWidget) -> None:
        """Add widget to Dialog."""

        self._layout.addWidget(_object)

    def exec_(self) -> int:
        """Show dialog and return a value."""

        if self.okButtonText:
            self.okButton.setText(str(self.okButtonText))
        if self.cancelButtonText:
            self.cancelButton.setText(str(self.cancelButtonText))
        self._layout.addWidget(self._button_box)

        return super().exec_()

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

    def setHeight(self, height: Union[int, float]) -> None:
        """Set height."""

        width = self.width()
        # self.setMinimunSize(width, height)
        self.resize(width, int(height))
