"""Flsqlconnections module."""
from pineboolib.core import decorators


class FLSqlConnections(object):
    """FLSqlConnections class."""

    @classmethod
    @decorators.NotImplementedWarn
    def database(cls):
        """Not implemented."""
        return True
