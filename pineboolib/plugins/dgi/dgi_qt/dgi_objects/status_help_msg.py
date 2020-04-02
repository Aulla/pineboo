"""StatusHelpMsg module."""

from pineboolib.core import settings


class StatusHelpMsg(object):
    """StatusHelpMsg class."""

    def send(self, text_: str) -> None:
        """Send a text."""
        from pineboolib.fllegacy.flapplication import aqApp

        aqApp.statusHelpMsg(text_)

        if settings.CONFIG.value("ebcomportamiento/parser_qsa_gui", False):
            aqApp.popupWarn(text_)
