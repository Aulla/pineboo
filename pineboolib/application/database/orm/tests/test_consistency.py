"""Test query_orm module."""

import unittest

from pineboolib.loader.main import init_testing, finish_testing
from pineboolib import application
from pineboolib.qsa import qsa


class TestConsistency(unittest.TestCase):
    """TestQueryOrm Class."""

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
        self.assertTrue(
            single_session in application.PROJECT.conn_manager._thread_sessions.values()
        )
        self.assertTrue(
            legacy_session in application.PROJECT.conn_manager._thread_sessions.values()
        )
        self.assertTrue(
            thread_session in application.PROJECT.conn_manager._thread_sessions.values()
        )

    @qsa.atomic()
    def test_transaction(self) -> None:
        """Create a new record and query it from a query in the same transaction."""
        self.assertTrue(atomica())
        session = qsa.session_atomic()
        self.assertTrue(session)

        class_ = qsa.orm_("fltest")
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

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()


def atomica():
    obj_area = qsa.orm.flareas()
    obj_area.idarea = "A"
    obj_area.descripcion = "Area A"
    obj_area.save()
    qry = qsa.FLUtil.sqlSelect("flareas", "descripcion", "idarea" == "A")
    return qry == "Area A" and qsa.session_atomic() is not None

