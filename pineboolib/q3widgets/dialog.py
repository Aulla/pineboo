"""Dialog module."""

from PyQt5 import QtCore, QtWidgets

from .qdialog import QDialog
from .qpushbutton import QPushButton
from .qtabwidget import QTabWidget

from typing import Optional, Union


class Dialog(QDialog):
    """Dialog class."""

    _layout: QtWidgets.QVBoxLayout
    _button_box: QtWidgets.QDialogButtonBox
    okButtonText: str
    cancelButtonText: str
    okButton: QPushButton
    cancelButton: QPushButton
    _tab: QTabWidget

    def __init__(
        self,
        title: Optional[str] = None,
        f: Union[Optional[QtCore.Qt.WindowFlags], int] = None,
        desc: Optional[str] = None,
    ) -> None:
        """Inicialize."""

        # FIXME: f no lo uso , es qt.windowsflg
        super(Dialog, self).__init__(None, f if not isinstance(f, int) else None)
        if title:
            self.setWindowTitle(str(title))

        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self._layout = QtWidgets.QVBoxLayout()
        self.setLayout(self._layout)
        self._button_box = QtWidgets.QDialogButtonBox()
        self.okButtonText = "Aceptar"
        self.cancelButtonText = "Cancelar"
        self.okButton = QPushButton("&Aceptar")
        self.cancelButton = QPushButton("&Cancelar")
        self._button_box.addButton(self.okButton, QtWidgets.QDialogButtonBox.AcceptRole)
        self._button_box.addButton(self.cancelButton, QtWidgets.QDialogButtonBox.RejectRole)
        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self._tab = QTabWidget()
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
