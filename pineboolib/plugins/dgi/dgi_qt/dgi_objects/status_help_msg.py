"""StatusHelpMsg module."""


class StatusHelpMsg(object):
    """StatusHelpMsg class."""

    def send(self, text_: str) -> None:
        """Send a text."""
        from pineboolib.fllegacy.flapplication import aqApp

        aqApp.statusHelpMsg(text_)
