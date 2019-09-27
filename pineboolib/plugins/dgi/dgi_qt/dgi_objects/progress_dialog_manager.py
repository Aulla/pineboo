"""Progressdialogmanager module."""
from typing import Any, List
from PyQt5 import QtCore, QtWidgets  # type: ignore


class ProgressDialogManager(object):
    """ProgressDailogManager class."""

    progress_dialog_stack: List[Any]

    def __init__(self):
        """Inicialize."""
        self.progress_dialog_stack = []

    def create(self, title: str, steps: int, id_: str) -> Any:
        """Create new ProgressDialog."""

        pd_widget = QtWidgets.QProgressDialog(
            str(title), str(QtWidgets.QApplication.translate("scripts", "Cancelar")), 0, steps
        )
        if pd_widget is not None:
            pd_widget.setObjectName(id_)
            pd_widget.setWindowModality(QtCore.Qt.WindowModal)
            pd_widget.setWindowTitle(str(title))
            self.progress_dialog_stack.append(pd_widget)
            pd_widget.show()
            pd_widget.setMinimumDuration(100)

            return pd_widget

        return None

    def destroy(self, id_: str) -> None:
        """Destroy a specific progress dialog."""
        pd_widget = self.progress_dialog_stack[-1]

        if id_ != "default":
            for w in self.progress_dialog_stack:
                if w.objectName() == id_:
                    pd_widget = w
                    break

        pd_widget.close()
        self.progress_dialog_stack.remove(pd_widget)

    def setProgress(self, step_number: int, id_: str) -> None:
        """Set progress into a specific prores dialog."""
        pd_widget = self.progress_dialog_stack[-1]

        if id_ != "default":
            for w in self.progress_dialog_stack:
                if w.objectName() == id_:
                    pd_widget = w
                    break

        pd_widget.setValue(step_number)

    def setLabelText(self, l: str, id_: str) -> None:
        """Set label text to a specific progres dialog."""
        pd_widget = self.progress_dialog_stack[-1]

        if id_ != "default":
            for w in self.progress_dialog_stack:
                if w.objectName() == id_:
                    pd_widget = w
                    break

        pd_widget.setLabelText(str(l))

    def setTotalSteps(self, tS: int, id_: str) -> None:
        """Set total steps to a specific proress dialog."""
        pd_widget = self.progress_dialog_stack[-1]

        if id_ != "default":
            for w in self.progress_dialog_stack:
                if w.objectName() == id_:
                    pd_widget = w
                    break

        pd_widget.setRange(0, tS)
