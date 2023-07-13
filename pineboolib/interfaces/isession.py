"""isession module."""

from sqlalchemy import orm  # type: ignore [import]


class PinebooSession(orm.Session):
    """PinebooSession class."""

    _conn_name: str
