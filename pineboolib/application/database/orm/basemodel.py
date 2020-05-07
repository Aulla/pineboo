"""Basemodel module."""

import sqlalchemy
from sqlalchemy import orm


from pineboolib.core.utils import logging
from pineboolib import application
from typing import Optional, TYPE_CHECKING

import datetime

if TYPE_CHECKING:
    from pineboolib.application.metadata import pntablemetadata  # noqa: F401


LOGGER = logging.get_logger(__name__)


class BaseModel:
    """Base Model class."""

    __tablename__: str = ""

    _session: Optional["orm.session.Session"]

    @orm.reconstructor  # type: ignore [misc] # noqa: F821
    def constructor_init(self) -> None:
        """Initialize from constructor."""

        # print("constructor", self)
        self._session = sqlalchemy.inspect(self).session

        if not self._session:
            raise Exception("session is empty!")

        if self in self._session.new:
            self.populate_default()

        self.init()

    def qsa_init(self, target, args=[], kwargs={}) -> None:
        """Initialize from qsa."""
        # print("orm", self)
        self._session = None
        self.populate_default()
        self.init()

    def init(self):
        """Initialize."""
        # print("--->", self, self._session)
        pass

    def after_new(self) -> bool:
        """After flush new instance."""

        return True

    def after_update(self) -> bool:
        """After update a instance."""

        return True

    def after_delete(self) -> bool:
        """After delete a instance."""

        return True

    def before_new(self) -> bool:
        """Before flush new instance."""

        return True

    def before_update(self) -> bool:
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

            if result:
                self._session.commit()
            else:
                self._session.rollback()

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

    def table_metadata(self) -> Optional["pntablemetadata.PNTableMetaData"]:
        """Return table metadata."""

        return application.PROJECT.conn_manager.manager().metadata(self.__tablename__)

    def populate_default(self) -> None:
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

    def save(self,) -> bool:
        """Save object."""

        if self._session is None:
            raise ValueError("session is empty!!")

        result = True

        # beforeCommit
        if self in self._session.new:
            result = self.before_new()
        elif self in self._session.dirty:
            result = self.before_update()
        elif self in self._session.deleted:
            raise Exception("Trying to save a deleted instance!")
            # result = self.before_delete()
        else:
            table_meta = self.table_metadata()
            if not table_meta:
                raise Exception("%s metadata not found" % self.__tablename__)

            pk_name = table_meta.primaryKey()
            pk_value = getattr(self, pk_name, None)

            if pk_value is None:
                raise ValueError("pk is empty!")
            else:
                current_data = self._session.query(self.__class__).get(pk_value)
                if current_data:
                    LOGGER.warning("Current pk %s already exists!", pk_value)
                    result = False
                    # self._session.update(self)
                    # raise Exception("pk already exists!!: %s" % pk_value)
                else:
                    self._session.add(self)
                    self.before_new()

        # añade la instancio a la transaccion
        if result:
            result = self._flush()
            if result:
                # afterCommit
                if self in self._session.new:
                    result = self.after_new()
                elif self in self._session.dirty:
                    result = self.after_update()
                # elif self in self._session.delete:
                #    result = self.after_delete()

            if result:
                self._session.commit()
            else:
                self._session.rollback()

        return result

    def set_session(self, session: "orm.session.Session") -> None:
        """Set instance session."""
        LOGGER.warning("Set session %s to instance %s", session, self)
        if self._session is None:
            # session.add(self)
            self._session = session
        else:
            LOGGER.warning("This instance already belongs to a session")

    def get_session(self) -> Optional["orm.session.Session"]:
        """Get instance session."""

        return self._session

    session = property(get_session, set_session)
