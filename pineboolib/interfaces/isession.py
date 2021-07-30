from sqlalchemy import orm as orm_session


class PinebooSession(orm_session.Session):

    _conn_name: str

