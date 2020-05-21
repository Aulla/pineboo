"""Basemodel module."""


from pineboolib.core.utils import logging
from pineboolib.application.metadata import pnrelationmetadata
from pineboolib.application import qsadictmodules
from pineboolib import application

from typing import Optional, List, Dict, Union, Callable, Any, TYPE_CHECKING

from sqlalchemy import orm, inspect, event
import datetime

if TYPE_CHECKING:
    from pineboolib.application.metadata import pntablemetadata  # noqa: F401


LOGGER = logging.get_logger(__name__)

relation_proxy_objects: Dict[str, List] = {}


class Copy:
    """Copy class."""

    pass


class BaseModel(object):
    """Base Model class."""

    __tablename__: str = ""

    _session: Optional["orm.session.Session"]
    _session_name: str
    _buffer_copy: "Copy"
    _result_before_flush: bool
    _result_after_flush: bool
    _force_mode: int
    _current_mode: int

    @orm.reconstructor  # type: ignore [misc] # noqa: F821
    def _constructor_init(self) -> None:
        """Initialize from constructor."""

        self._session = inspect(self).session
        for name, conn in application.PROJECT.conn_manager.dictDatabases().items():
            if conn.session() is self._session:
                self._session_name = name
                break

        self._common_init()

    def _qsa_init(target, args=[], kwargs={}) -> None:
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
        self._force_mode = 0
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
        if getattr(self, "_buffer_copy", None):
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

    def after_flush(self) -> bool:
        """After flush."""

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

    def before_flush(self) -> bool:
        """Before flush."""

        return True

    def delete(self) -> bool:
        """Flush instance to current session."""

        if self._session:
            self._session.delete(self)
            return self._flush()
        else:
            raise Exception("_session is empty!")

    def _delete_cascade(self) -> bool:
        """Delete cascade instances if proceed."""

        for field in self.table_metadata().fieldList():
            relation_list = field.relationList()
            for relation in relation_list:

                foreign_table_mtd = application.PROJECT.conn_manager.manager().metadata(
                    relation.foreignTable()
                )
                if foreign_table_mtd is not None:

                    foreign_field_mtd = foreign_table_mtd.field(relation.foreignField())
                    if foreign_field_mtd is not None:

                        relation_m1 = foreign_field_mtd.relationM1()
                        if relation_m1 is not None and relation_m1.deleteCascade():
                            foreign_table_class = qsadictmodules.QSADictModules.orm_(
                                foreign_table_mtd.name()
                            )
                            foreign_field_object = getattr(
                                foreign_table_class, relation.foreignField()
                            )
                            relation_objects = (
                                foreign_table_class.query(self._session_name)
                                .filter(foreign_field_object == getattr(self, field.name()))
                                .all()
                            )

                            for obj in relation_objects:
                                if not obj.delete():
                                    LOGGER.warning(
                                        "obj: %s, pk_value: %s can't deleted", obj, obj.pk
                                    )
                                    return False

        return True

    def _flush(self) -> bool:
        """Flush data."""

        if self._session is None:
            raise ValueError("session is empty!!")

        self._current_mode = self.mode_access
        ret_ = False
        try:
            ret_ = True
            if self._current_mode == 3:
                try:
                    ret_ = self._delete_cascade()
                except Exception as error:
                    LOGGER.warning("Delete_cascade: %s ", str(error))
                    ret_ = False
            if ret_:
                ret_ = self._before_flush()
                if ret_:
                    try:
                        self._session.flush()
                    except Exception as error:
                        LOGGER.warning("flush! %s", str(error))
                        ret_ = False
                    if ret_:
                        ret_ = self._after_flush()

        except Exception as error:
            LOGGER.error("%s flush: %s", self, str(error))
            return False

        self._current_mode = 0
        return ret_

    def _before_flush(self) -> bool:
        """Before flush."""
        ret_ = self.before_flush()

        if ret_:
            try:
                mode = self._current_mode
            except Exception as error:
                LOGGER.warning("Error retriving mode! %s: %s", self, str(error))
                return False

            print("*BF", self, mode)
            if mode == 1:
                try:
                    ret_ = self.before_new()
                except Exception as error:
                    LOGGER.warning("Before_new %s: %s", self, str(error))
                    return False

            elif mode == 2:
                try:
                    ret_ = self.before_change()
                except Exception as error:
                    LOGGER.warning("Before_change %s: %s", self, str(error))
                    return False
            elif mode == 3:
                try:
                    ret_ = self.before_delete()
                except Exception as error:
                    LOGGER.warning("Before_delete %s: %s", self, str(error))
                    return False

        return ret_

    def _after_flush(self) -> bool:
        """After flush."""

        ret_ = False
        try:
            ret_ = self.after_flush()
            if ret_:
                mode = self._current_mode

                print("*AF", self, mode)

                if mode == 1:
                    try:
                        ret_ = self.after_new()
                    except Exception as error:
                        LOGGER.warning("After_new %s: %s", self, str(error))
                        return False
                elif mode == 2:
                    try:
                        ret_ = self.after_change()
                    except Exception as error:
                        LOGGER.warning("After_change %s: %s", self, str(error))
                        return False
                elif mode == 3:
                    try:
                        ret_ = self.after_delete()
                    except Exception as error:
                        LOGGER.warning("After_delete %s: %s", self, str(error))
                        return False
        except Exception as error:
            LOGGER.warning("_after_flush: %s", str(error))
            ret_ = False

        return ret_

    # ===============================================================================
    #     def _check_unlock(self) -> bool:
    #         """Return if unloks field are locked."""
    #
    #         field_list = self.table_metadata().fieldsList()
    #         copy_object = self.query("dbAux").get(self.pk)
    #         for field in field_list:
    #             field_name = field.name()
    #             if field.isLocked():
    #                 if not getattr(copy_object, field_name, True):
    #                     return False
    #
    #             relation_m1 = field.relationM1()
    #             if relation_m1 is not None:
    #                 foreign_table_class = qsadictmodules.QSADictModules.orm_(relation_m1.foreignTable())
    #                 if foreign_table_class is not None:
    #                     foreign_field_obj = foreign_table_class.get(getattr(self, field.name()))
    #                     if foreign_field_obj is not None:
    #                         if not foreign_field_obj._check_unlock():
    #                             return False
    #
    #         return True
    # ===============================================================================

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
        qry = cls.query(session_name)
        return qry.get(pk_value) if qry is not None else None

    @classmethod
    def query(cls, session: Union[str, "orm.Session"] = "default") -> Optional["orm.query.Query"]:
        """Return Session query."""

        if session:
            session_ = None
            if isinstance(session, str):
                if session in application.PROJECT.conn_manager.dictDatabases().keys():
                    session_ = application.PROJECT.conn_manager.useConn(session).session()
            else:
                session_ = session

            if isinstance(session_, orm.Session):
                ret_ = session_.query(cls)
                event.listen(ret_, "before_compile_update", cls._before_compile_update)
                event.listen(ret_, "before_compile_delete", cls._before_compile_delete)
                return ret_

        LOGGER.warning("query: Invalid session %s ", session)
        return None

    @classmethod
    def _before_compile_update(cls, query, context) -> bool:
        """Before compile Update!."""

        for obj in query.all():
            obj.mode_access = 2
            obj._before_flush()
            ret_ = obj._result_before_flush
            if ret_:
                obj._after_flush()
                ret_ = obj._result_after_flush

            if not ret_:
                return False

        return True

    @classmethod
    def _before_compile_delete(cls, query, context) -> bool:
        """Before compile Update!."""
        for obj in query.all():
            obj.mode_access = 3
            ret_ = obj._delete_cascade()
            if ret_:
                ret_ = obj._before_flush()
                if ret_:
                    ret_ = obj._after_flush()

            if not ret_:
                return False

        return True

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
        """Flush instance to current session."""

        if not hasattr(self, "_session"):
            raise Exception("This new instance was not initialized with qsa.orm_(class_name)")

        if self._session is None:
            raise Exception("_session is empty!")

        result = True
        if self.mode_access == 1:
            self._session.add(self)

        if check_integrity:
            result = self._check_integrity()

        if result:
            result = self._flush()

        return result

    def _check_integrity(self) -> bool:
        """Check data integrity."""

        mode = self.mode_access

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
                    foreign_class_ = qsadictmodules.QSADictModules.orm_(relation_m1.foreignTable())

                    if foreign_class_ is not None:
                        foreign_field_obj = getattr(
                            foreign_class_, relation_m1.foreignField(), None
                        )

                        qry_data = (
                            foreign_class_.query(self._session)
                            .filter(foreign_field_obj == getattr(self, field_name))
                            .first()
                        )

                        if qry_data is None and not field.allowNull():
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
                    elif not field.allowNull():
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

    def relationM1(self, field_name: str = "") -> Optional[Callable]:
        """Return relationM1 object if exists."""

        if field_name:
            meta = self.table_metadata().field(field_name)
            if meta is not None:
                meta_rel = meta.relationM1()
                if meta_rel is not None:
                    foreign_table_class = qsadictmodules.QSADictModules.orm_(
                        meta_rel.foreignTable()
                    )
                    if foreign_table_class is not None:
                        foreign_field_obj = getattr(foreign_table_class, meta_rel.foreignField())
                        return (
                            foreign_table_class.query(self._session_name)
                            .filter(foreign_field_obj == getattr(self, field_name))
                            .first()
                        )

        return None

    def relation1M(self, field_name: str = "") -> Dict[str, List[Callable]]:
        """Return relationed instances."""
        ret_ = {}
        field_metadata = self.table_metadata().field(field_name)
        if field_metadata is not None:
            relation_list = field_metadata.relationList()
            for relation in relation_list:
                if relation.cardinality() == pnrelationmetadata.PNRelationMetaData.RELATION_M1:
                    continue

                ft_class = qsadictmodules.QSADictModules.orm_(relation.foreignTable())
                if ft_class is not None:
                    ff_obj = getattr(ft_class, relation.foreignField(), None)
                    if ff_obj is not None:
                        list_ = (
                            ft_class.query(self._session_name)
                            .filter(ff_obj == getattr(self, field_name))
                            .all()
                        )
                        ret_["%s_%s" % (relation.foreignTable(), relation.foreignField())] = list_

        else:
            LOGGER.warning("RELATION_1M: invalid field_name %s", field_name)

        return ret_

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

    def get_mode_access(self) -> int:
        """Return mode_access."""
        if hasattr(self, "_force_mode") and self._force_mode:
            return self._force_mode

        session = self.session

        mode = 0
        if self in session.deleted:
            mode = 3
        elif self in session.dirty:
            mode = 2
        else:
            mode = 1

        return mode

    def set_mode_access(self, value: int) -> None:
        """Set forced mode access."""

        self._force_mode = value

    session = property(get_session, set_session)
    transaction_level = property(get_transaction_level)
    pk_name = property(get_pk_name)
    pk = property(get_pk_value, set_pk_value)
    mode_access = property(get_mode_access, set_mode_access)
