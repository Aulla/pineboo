"""Flscripteditor module."""

from pineboolib.q3widgets import qtextedit


class FLScriptEditor(qtextedit.QTextEdit):
    """FLScriptEditor class."""

    def __init__(self, name: str) -> None:
        """Inicialize."""

        super().__init__()

    def exec_(self):
        """Show edior."""

        self.show()

    def code(self) -> str:
        """Return text."""

        return self.PlainText
