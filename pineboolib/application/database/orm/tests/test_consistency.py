"""Test consistency module."""

import unittest
import threading

from pineboolib.loader.main import init_testing, finish_testing
from pineboolib import application
from pineboolib.core.utils import utils_base
from pineboolib.qsa import qsa


class TestConsistency(unittest.TestCase):
    """TestConsistency Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_isolation(self) -> None:
        """Create multiples diferents sessions."""

        conn_name = "default"

        single_session = qsa.session(conn_name)
        legacy_session = qsa.session(conn_name, True)
        thread_session = qsa.thread_session_new(conn_name)

        self.assertTrue(single_session is not legacy_session)
        self.assertTrue(thread_session is not single_session)
        self.assertEqual(
            legacy_session, application.PROJECT.conn_manager.useConn("default").session()
        )

    @qsa.serialize()  # type: ignore [misc] # noqa: F821
    def test_serialize(self) -> None:
        """Test serialize decorator."""
        conn_ident = utils_base.session_id()
        id_thread = threading.current_thread().ident
        self.assertTrue(
            conn_ident in application.SERIALIZE_LIST[id_thread]  # type: ignore [index] # noqa: F821
        )

    @qsa.atomic()  # type: ignore [misc] # noqa: F821
    def test_transaction(self) -> None:
        """Create a new record and query it from a query in the same transaction."""
        self.assertTrue(atomica())
        session = qsa.session_atomic()
        self.assertTrue(session)

        class_ = qsa.orm.fltest
        obj_1 = class_()
        self.assertFalse(obj_1.string_field)
        self.assertFalse(obj_1.empty_relation)
        obj_1.empty_relation = None
        self.assertFalse(obj_1.empty_relation)
        self.assertTrue(obj_1.save())
        self.assertTrue(obj_1.id)

        cursor_fltest = qsa.FLSqlCursor("fltest")
        cursor_fltest.select("id = %s" % obj_1.id)
        self.assertTrue(cursor_fltest.first())

        self.assertTrue(session is obj_1.session)
        self.assertTrue(session is cursor_fltest.db().session())

        # Check string_field
        result = qsa.FLUtil.sqlSelect("fltest", "string_field", "id = %s" % obj_1.id)
        self.assertFalse(result)
        self.assertTrue(result == "", 'El valor devuelto (%s) no es ""' % result)

        self.assertTrue(
            cursor_fltest.valueBuffer("string_field") == "",
            'El valor devuelto (%s) no es ""' % result,
        )
        # Check empty_relation
        self.assertTrue(obj_1.empty_relation is None)
        result_er = qsa.FLUtil.sqlSelect("fltest", "empty_relation", "id = %s" % obj_1.id)
        self.assertFalse(result_er)
        self.assertTrue(result_er == "", 'El valor devuelto (%s) no es ""' % result_er)

        self.assertTrue(
            cursor_fltest.valueBuffer("empty_relation") == "",
            'El valor devuelto (%s) no es ""' % result,
        )

    def test_save_point_launch(self) -> None:
        """Test save points."""

        conn_ = qsa.aqApp.db().useConn("default")
        session = conn_.session()
        self.assertTrue(session.transaction is None)
        conn_.transaction()
        self.assertTrue(session.transaction is not None)
        id_ = session.transaction
        conn_.transaction()
        self.assertNotEqual(id_, session.transaction)
        self.assertTrue(id_ is not None)
        conn_.rollback()
        self.assertEqual(id_, session.transaction)
        conn_.rollback()
        self.assertTrue(session.transaction is None)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()


def atomica():
    """Atomica function test."""
    obj_area = qsa.orm.flareas()
    obj_area.idarea = "A"
    obj_area.descripcion = "Area A"
    obj_area.save()
    qry = qsa.FLUtil.sqlSelect("flareas", "descripcion", "idarea = 'A'")
    return qry == "Area A" and qsa.session_atomic() is not None
