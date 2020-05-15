"""Basemodel module."""

import sqlalchemy
from sqlalchemy import orm


from pineboolib.core.utils import logging
from pineboolib import application
from pineboolib.qsa import qsa
from typing import Optional, Dict, Any, TYPE_CHECKING

import datetime

if TYPE_CHECKING:
    from pineboolib.application.metadata import pntablemetadata  # noqa: F401
    from sqlalchemy.orm import query as orm_query  # noqa: F401


LOGGER = logging.get_logger(__name__)


class Copy:
    """Copy class."""

    pass


class BaseModel(object):
    """Base Model class."""

    __tablename__: str = ""

    _session: Optional["orm.session.Session"]
    _session_name: str
    _buffer_copy: "Copy"

    @orm.reconstructor  # type: ignore [misc] # noqa: F821
    def constructor_init(self) -> None:
        """Initialize from constructor."""

        self._session = sqlalchemy.inspect(self).session
        for name, conn in application.PROJECT.conn_manager.dictDatabases().items():
            if conn.session() is self._session:
                self._session_name = name
                break

        self._common_init()

    def qsa_init(target, args=[], kwargs={}) -> None:
        """Initialize from qsa."""

        # target._session = None
        session_name = "default"
        if "session" in kwargs:
            session_name = kwargs["session"] or "default"
        target._session = application.PROJECT.conn_manager.useConn(session_name).session()
        target._session_name = session_name

        target._common_init()

    def _common_init(self) -> None:
        """Initialize."""

        if not self._session:
            raise Exception("session is empty!")

        if not self._session_name:
            raise Exception("Session_name not found!")

        if self in self._session.new:
            raise Exception("Common init with session.new instance!")

        self.update_copy()

        pk_name = self.pk_name
        if getattr(self, pk_name, None) is None:
            self._populate_default()

            if self.type(pk_name) == "serial":
                setattr(
                    self,
                    pk_name,
                    application.PROJECT.conn_manager.useConn(self._session_name)
                    .driver()
                    .nextSerialVal(self.table_metadata().name(), pk_name),
                )

        self.init()

    def init(self):
        """Initialize."""
        # print("--->", self, self._session)
        pass

    def copy(self) -> "Copy":
        """Return buffer_copy."""

        return self._buffer_copy

    def update_copy(self) -> None:
        """Update buffer copy."""
        if hasattr(self, "_buffer_copy"):
            del self._buffer_copy
        self._buffer_copy = Copy()

        table_mtd = self.table_metadata()
        if table_mtd is None:
            raise Exception("table_metadata is empty!")

        for field_name in table_mtd.fieldNames():
            setattr(self._buffer_copy, field_name, getattr(self, field_name, None))

    def changes(self) -> Dict[str, Any]:
        """Return field names changed and values."""

        changes = {}

        table_mtd = self.table_metadata()
        if table_mtd is None:
            raise Exception("table_metadata is empty!")

        for field_name in table_mtd.fieldNames():
            original_value = getattr(self._buffer_copy, field_name, None)
            current_value = getattr(self, field_name)

            if type(original_value) != type(current_value):
                changes[field_name] = current_value
            elif original_value != current_value:
                changes[field_name] = current_value

        return changes

    def after_new(self) -> bool:
        """After flush new instance."""

        return True

    def after_change(self) -> bool:
        """After update a instance."""

        return True

    def after_delete(self) -> bool:
        """After delete a instance."""

        return True

    def before_new(self) -> bool:
        """Before flush new instance."""

        return True

    def before_change(self) -> bool:
        """Before update a instance."""

        return True

    def before_delete(self) -> bool:
        """Before delete a instance."""

        return True

    def delete(self) -> bool:
        """Delete instance."""

        if self._session is None:
            raise ValueError("session is empty!!")

        self._session.delete(self)
        result = self.before_delete()
        if result:
            result = self._flush()
            if result:
                result = self.after_delete()

            # if result:
            #    self._session.commit()
            # else:
            #    self._session.rollback()

        return result

    def _flush(self) -> bool:
        """Flush data."""

        if self._session is None:
            raise ValueError("session is empty!!")

        try:
            self._session.flush()
        except Exception as error:
            LOGGER.error("%s flush: %s", self, str(error))
            return False

        return True

    @classmethod
    def table_metadata(cls) -> "pntablemetadata.PNTableMetaData":
        """Return table metadata."""

        ret_ = application.PROJECT.conn_manager.manager().metadata(cls.__tablename__)

        if ret_ is None:
            raise Exception("table_metadata is empty!")

        return ret_

    @classmethod
    def type(cls, field_name: str = ""):
        """Return field type."""

        field_mtd = cls.table_metadata().field(field_name)
        if field_mtd is not None:
            return field_mtd.type()

        return None

    @classmethod
    def get(cls, pk_value: str, session_name: str = "default") -> Any:
        """Return instance selected by pk."""

        if session_name in application.PROJECT.conn_manager.dictDatabases().keys():

            return (
                application.PROJECT.conn_manager.useConn(session_name)
                .session()
                .query(cls)
                .get(pk_value)
            )

        LOGGER.warning("get: session_name %s not found", session_name)
        return None

    @classmethod
    def query(cls, session: str = "default") -> Optional["orm_query.Query"]:
        """Return Session query."""

        if session:
            session_ = None
            if isinstance(session, str):
                if session in application.PROJECT.conn_manager.dictDatabases().keys():
                    session_ = application.PROJECT.conn_manager.useConn(session).session()
            else:
                session_ = session

            if isinstance(session_, orm.Session):
                return session_.query(cls)

        LOGGER.warning("query: Invalid session %s ", session)
        return None

    def _populate_default(self) -> None:
        """Populate with default values."""

        metadata = self.table_metadata()
        if metadata is None:
            raise Exception("table_metadata is empty!")

        for name in metadata.fieldNames():
            field_mtd = metadata.field(name)

            if field_mtd is None:
                LOGGER.warning("%s metadata not found!", name)
                continue

            default_value = field_mtd.defaultValue()
            if default_value is None:
                continue

            if isinstance(default_value, str):
                type_ = field_mtd.type()

                if type_ == "date":
                    default_value = datetime.date.fromisoformat(str(default_value)[:10])
                elif type_ == "timestamp":
                    default_value = datetime.datetime.strptime(
                        str(default_value), "%Y-%m-%d %H:%M:%S"
                    )
                elif type_ == "time":
                    default_value = str(default_value)
                    if default_value.find("T") > -1:
                        default_value = default_value[default_value.find("T") + 1 :]

                    default_value = datetime.datetime.strptime(
                        str(default_value)[:8], "%H:%M:%S"
                    ).time()

            setattr(self, name, default_value)

    def save(self, check_integrity=True) -> bool:
        """Save object."""

        if self._session is None:
            raise ValueError("session is empty!!")

        result = True

        # beforeCommit
        mode = 0
        if self in self._session.new:
            mode = 1
        elif self in self._session.dirty:
            mode = 2
        elif self in self._session.deleted:
            raise Exception("Trying to save a deleted instance!")
            # result = self.before_delete()
        else:
            table_meta = self.table_metadata()

            if self.pk is None:
                raise ValueError("pk is empty!")
            else:
                current_data = self._session.query(self.__class__).get(self.pk)
                if current_data:
                    LOGGER.warning("Current pk %s already exists!", self.pk)
                    # result = False
                    # self._session.update(self)
                    # raise Exception("pk already exists!!: %s" % pk_value)
                else:
                    mode = 1
                    self._session.add(self)

        if mode:
            if not self._check_integrity(mode):
                result = False
            elif mode == 1:
                result = self.before_new()
            elif mode == 2:
                result = self.before_change()
        else:
            result = False

        # añade la instancio a la transaccion
        if result:
            result = self._flush()
            if result:
                # afterCommit
                if mode == 1:
                    result = self.after_new()
                elif mode == 2:
                    result = self.after_change()

                # elif self in self._session.delete:
                #    result = self.after_delete()

            # if result:
            #    self._session.commit()
            # else:
            #    self._session.rollback()

        return result

    def _check_integrity(self, mode: int) -> bool:
        """Check data integrity."""

        table_meta = self.table_metadata()

        if not table_meta.isQuery():

            for field in table_meta.fieldList():
                if mode in [1, 2]:
                    # not Null fields.
                    if not field.allowNull():
                        if getattr(self, field.name(), None) is None:
                            LOGGER.warning(
                                "INTEGRITY::Field %s.%s need a value"
                                % (table_meta.name(), field.name())
                            )
                            return False

            for field in table_meta.fieldList():
                # para poder comprobar relaciones , tengo que mirar primero que los campos not null esten ok, si no , da error.
                field_name = field.name()
                relation_m1 = field.relationM1()
                if relation_m1 is not None:
                    foreign_class_ = qsa.orm_(relation_m1.foreignTable())

                    if foreign_class_ is not None:
                        foreign_field_obj = getattr(
                            foreign_class_, relation_m1.foreignField(), None
                        )

                        qry_data = (
                            foreign_class_.query(self._session)
                            .filter(foreign_field_obj == getattr(self, field_name))
                            .first()
                        )

                        if qry_data is None:
                            LOGGER.warning(
                                "INTEGRITY::Relation %s.%s M1 %s.%s with value %s is invalid"
                                % (
                                    table_meta.name(),
                                    field_name,
                                    relation_m1.foreignTable(),
                                    relation_m1.foreignField(),
                                    getattr(self, field_name),
                                )
                            )
                            return False
                    else:
                        LOGGER.warning(
                            "INTEGRITY::Relationed table %s.%s M1 %s.%s is invalid"
                            % (
                                table_meta.name(),
                                field_name,
                                relation_m1.foreignTable(),
                                relation_m1.foreignField(),
                            )
                        )
                        return False

        return True

    def get_transaction_level(self) -> int:
        """Return current transaction level."""

        ret_ = -1
        parent_transaction = self._session.transaction if self._session else None
        while parent_transaction:
            ret_ += 1
            parent_transaction = parent_transaction.parent

        return ret_

    def set_session(self, session: "orm.session.Session") -> None:
        """Set instance session."""
        # LOGGER.warning("Set session %s to instance %s", session, self)
        if self._session is None:
            # session.add(self)
            self._session = session
        else:
            LOGGER.warning("This instance already belongs to a session")

    def get_session(self) -> Optional["orm.session.Session"]:
        """Get instance session."""

        return self._session

    def get_pk_name(self) -> str:
        """Return primary key."""

        return self.table_metadata().primaryKey()

    def get_pk_value(self) -> Any:
        """Return pk value."""

        return getattr(self, self.get_pk_name())

    def set_pk_value(self, pk_value: Any) -> None:
        """Set pk value."""

        setattr(self, self.get_pk_name(), pk_value)

    session = property(get_session, set_session)
    transaction_level = property(get_transaction_level)
    pk_name = property(get_pk_name)
    pk = property(get_pk_value, set_pk_value)
