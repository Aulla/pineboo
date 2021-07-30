"""isession module."""

from sqlalchemy import orm


class PinebooSession(orm.Session):
    """PinebooSession class."""

    _conn_name: str
