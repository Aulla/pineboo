"""Test query_orm module."""

import unittest

from pineboolib.loader.main import init_testing, finish_testing
from pineboolib import application
from pineboolib.qsa import qsa


class TestQueryOrm(unittest.TestCase):
    """TestQueryOrm Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()
        application.PROJECT.conn_manager.manager().createTable("fltest4")
        application.PROJECT.conn_manager.manager().createTable("fltest5")

    def test_session(self) -> None:
        """Test session query."""

        session = qsa.session()
        session.begin()
        class_area = qsa.orm_("fltest4")
        obj_area = class_area()
        session.close()
        obj_area.idarea = "E"
        obj_area.other_field = "DSGDSGSDG**"
        self.assertTrue(obj_area.save())

        class_area = qsa.orm_("fltest4")
        result = class_area.query().filter(class_area.idarea == "E").first()
        self.assertTrue(result)

    def test_delete(self) -> None:
        """Test delete with children."""

        session = qsa.thread_session_new()
        session.begin()
        class_area = qsa.orm_("fltest4")
        obj_area = class_area()

        obj_area.idarea = "E"
        obj_area.other_field = "DSGDSGSDG**"
        self.assertTrue(obj_area.save())

        class_child = qsa.orm_("fltest5")
        child_1 = class_child()
        child_2 = class_child()

        child_1.idmodulo = "A"
        child_2.idmodulo = "B"
        child_1.idarea = "E"
        child_2.idarea = "E"
        self.assertTrue(child_1.save())
        child_1.session.commit()
        session.begin()
        self.assertTrue(child_2.save())
        child_2.session.commit()

        self.assertEqual(len(class_child.query().all()), 2)

        # session.commit()
        session.begin()
        self.assertTrue(class_area.query().filter(class_area.idarea == "E").first())
        # session = qsa.session()
        # new_obj = class_area.get("E")
        self.assertEqual(len(class_child.query().all()), 2)
        lista = obj_area.query().filter(class_area.idarea == "E")
        for obj in lista:
            obj.delete()

        session.commit()
        # session.commit()
        self.assertEqual(len(class_child.query().all()), 0)

        self.assertFalse(class_area.get("E"))
        session.close()

    def test_delete2(self) -> None:
        """Test delete with children."""

        session = qsa.thread_session_new()
        session.begin()
        class_area = qsa.orm_("fltest4")
        obj_area = class_area()

        obj_area.idarea = "E"
        obj_area.other_field = "DSGDSGSDG**"
        self.assertTrue(obj_area.save())

        class_child = qsa.orm_("fltest5")
        child_1 = class_child()
        child_2 = class_child()

        child_1.idmodulo = "A"
        child_2.idmodulo = "B"
        child_1.idarea = "E"
        child_2.idarea = "E"
        self.assertTrue(child_1.save())
        child_1.session.commit()
        session.begin()
        self.assertTrue(child_2.save())
        child_2.session.commit()

        self.assertEqual(len(class_child.query().all()), 2)

        # session.commit()
        session.begin()
        self.assertTrue(class_area.query().filter(class_area.idarea == "E").first())
        # session = qsa.session()
        # new_obj = class_area.get("E")
        self.assertEqual(len(class_child.query().all()), 2)
        lista = class_child.query().filter(class_child.idarea == "E").all()
        for obj in lista:
            self.assertTrue(class_area.query().filter(class_area.idarea == obj.idarea).first())
            obj.delete()

        session.commit()
        # session.commit()
        self.assertEqual(len(class_child.query().all()), 0)

        self.assertFalse(class_area.get("E"))
        session.close()

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()
