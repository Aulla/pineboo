"""Progressdialogmanager module."""
from typing import Any, List
from PyQt6 import QtCore, QtWidgets  # type: ignore


class ProgressDialogManager(object):
    """ProgressDailogManager class."""

    progress_dialog_stack: List[Any]

    def __init__(self):
        """Inicialize."""
        self.progress_dialog_stack = []

    def create(self, title: str, steps: int, id_: str = "default") -> Any:
        """Create new ProgressDialog."""

        pd_widget = QtWidgets.QProgressDialog(
            str(title), str(QtWidgets.QApplication.translate("scripts", "Cancelar")), 0, steps
        )
        if pd_widget is not None:
            self.progress_dialog_stack.append(pd_widget)
            pd_widget.setObjectName(id_)
            pd_widget.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
            pd_widget.setWindowTitle(str(title))

            pd_widget.show()
            # pd_widget.setMinimumDuration(100)
            QtWidgets.QApplication.processEvents()

        return pd_widget

    def destroy(self, id_: str = "default") -> None:
        """Destroy a specific progress dialog."""

        for dialog in self.progress_dialog_stack:

            if dialog.objectName() == id_:
                self.progress_dialog_stack.remove(dialog)
                del dialog
                return

    def setProgress(self, step_number: int, id_: str = "default") -> None:
        """Set progress into a specific prores dialog."""

        for dialog in self.progress_dialog_stack:
            if dialog.objectName() == id_:
                dialog.setValue(step_number)
                return

    def setLabelText(self, label: str, id_: str) -> None:
        """Set label text to a specific progres dialog."""

        for dialog in self.progress_dialog_stack:
            if dialog.objectName() == id_:
                dialog.setLabelText(str(label))
                return

    def setTotalSteps(self, total_steps: int, id_: str) -> None:
        """Set total steps to a specific proress dialog."""

        for dialog in self.progress_dialog_stack:
            if dialog.objectName() == id_:
                dialog.setRange(0, total_steps)
                return
