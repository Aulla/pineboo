"""Flsqlconnections module."""
from pineboolib.core import decorators


class FLSqlConnections(object):
    """FLSqlConnections class."""

    @classmethod
    @decorators.not_implemented_warn
    def database(cls):
        """Not implemented."""
        return True
