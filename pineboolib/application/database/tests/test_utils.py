"""Test_utils module."""

import unittest
from pineboolib.loader.main import init_testing
from pineboolib.application.database import utils
from pineboolib.application.database import pnsqlcursor


class TestUtils(unittest.TestCase):
    """TestUtils Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_full(self) -> None:
        """Test all options."""

        cur_1 = pnsqlcursor.PNSqlCursor("fltest3")

        val_1 = utils.next_counter("counter_field", cur_1)

        utils.sql_insert(
            "fltest3", "counter_field,string_field", "%s,%s" % (val_1, "Campo de prueba 1")
        )

        self.assertEqual(val_1, "000001")

        val_2 = utils.next_counter("b", "counter_field", cur_1)
        self.assertEqual(val_2, "00001")

        val_3 = utils.next_counter("counter_field", cur_1)
        self.assertEqual(val_3, "000002")

        val_4 = utils.next_counter("ABCD", "counter_field", cur_1)
        self.assertEqual(val_4, "01")

        utils.sql_insert(
            "fltest3", "counter_field,string_field", "%s,%s" % (val_3, "Campo de prueba 2")
        )
        utils.sql_insert(
            "fltest3", "counter_field,string_field", "ABCD%s,%s" % (val_4, "Campo de prueba 4")
        )

        val_5 = utils.next_counter("ABCD", "counter_field", cur_1)
        self.assertEqual(val_5, "02")

        self.assertEqual(
            utils.sql_select("fltest3", "string_field", "counter_field = '%s'" % val_1),
            "Campo de prueba 1",
        )
        self.assertEqual(
            utils.sql_select(
                "fltest3", "string_field", "counter_field = '%s'" % val_3, "fltest3", 0, "default"
            ),
            "Campo de prueba 2",
        )

        self.assertNotEqual(
            utils.sql_select(
                "fltest3", "timezone_field", "counter_field = '%s'" % val_3, "fltest3", 0, "default"
            ),
            "",
        )

        self.assertEqual(
            utils.sql_select(
                "fltest3", "string_field", "counter_field = '%s'" % val_3, ["fltest3"], 0, "default"
            ),
            "Campo de prueba 2",
        )

        self.assertEqual(
            utils.quick_sql_select(
                "fltest3", "string_field", "counter_field = '%s'" % val_3, "default"
            ),
            "Campo de prueba 2",
        )

        self.assertTrue(
            utils.sql_update(
                "fltest3",
                ["string_field"],
                ["Campo de prueba 2 Modificado"],
                "counter_field = '%s'" % val_3,
                "default",
            )
        )

        self.assertEqual(
            utils.quick_sql_select(
                "fltest3", "string_field", "counter_field = '%s'" % val_3, "default"
            ),
            "Campo de prueba 2 Modificado",
        )
        self.assertTrue(utils.quick_sql_delete("fltest3", "counter_field ='%s'" % val_1, "default"))
        self.assertTrue(utils.sql_delete("fltest3", "1=1", "dbAux"))
