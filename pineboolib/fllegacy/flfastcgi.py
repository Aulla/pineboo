"""Flfastcgi module."""

from pineboolib.core import decorators


class FLFastCgi(object):
    """FLFastCgi class."""

    @decorators.not_implemented_warn
    def getFullEnv(self) -> str:
        """Return full enviroment."""

        return ""

    @decorators.not_implemented_warn
    def getEnv(self, data: str) -> str:
        """Return enviroment."""

        return ""

    @decorators.not_implemented_warn
    def urlencode(self, data: str) -> str:
        """Return url encode."""

        return ""

    @decorators.not_implemented_warn
    def urldecode(self, data: str) -> str:
        """Return url decode."""

        return ""

    @decorators.not_implemented_warn
    def xmlentityencode(self, data: str) -> str:
        """Return xml entity encode."""

        return ""

    @decorators.not_implemented_warn
    def read(self, block_size: int = 65535) -> str:
        """Return xml entity decode."""

        return ""

    @decorators.not_implemented_warn
    def write(self, data: str) -> int:
        """Return xml entity decode."""

        return 0

    @decorators.not_implemented_warn
    def writeError(self, data: str) -> int:
        """Return error."""

        return 0
