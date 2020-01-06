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

        val_1 = utils.nextCounter("counter", cur_1)

        utils.sqlInsert("fltest3", "counter,string_field", "%s,%s" % (val_1, "Campo de prueba 1"))

        self.assertEqual(val_1, "000001")

        val_2 = utils.nextCounter("b", "counter", cur_1)
        self.assertEqual(val_2, "00001")

        val_3 = utils.nextCounter("counter", cur_1)
        self.assertEqual(val_3, "000002")

        val_4 = utils.nextCounter("ABCD", "counter", cur_1)
        self.assertEqual(val_4, "01")

        utils.sqlInsert("fltest3", "counter,string_field", "%s,%s" % (val_3, "Campo de prueba 2"))
        utils.sqlInsert(
            "fltest3", "counter,string_field", "ABCD%s,%s" % (val_4, "Campo de prueba 4")
        )

        val_5 = utils.nextCounter("ABCD", "counter", cur_1)
        self.assertEqual(val_5, "02")

        self.assertEqual(
            utils.sqlSelect("fltest3", "string_field", "counter = '%s'" % val_1),
            "Campo de prueba 1",
        )
        self.assertEqual(
            utils.sqlSelect(
                "fltest3", "string_field", "counter = '%s'" % val_3, "fltest3", 0, "default"
            ),
            "Campo de prueba 2",
        )

        self.assertNotEqual(
            utils.sqlSelect(
                "fltest3", "timezone_field", "counter = '%s'" % val_3, "fltest3", 0, "default"
            ),
            "",
        )

        self.assertEqual(
            utils.sqlSelect(
                "fltest3", "string_field", "counter = '%s'" % val_3, ["fltest3"], 0, "default"
            ),
            "Campo de prueba 2",
        )

        self.assertEqual(
            utils.quickSqlSelect("fltest3", "string_field", "counter = '%s'" % val_3, "default"),
            "Campo de prueba 2",
        )

        self.assertTrue(
            utils.sqlUpdate(
                "fltest3",
                ["string_field"],
                ["Campo de prueba 2 Modificado"],
                "counter = '%s'" % val_3,
                "default",
            )
        )

        self.assertEqual(
            utils.quickSqlSelect("fltest3", "string_field", "counter = '%s'" % val_3, "default"),
            "Campo de prueba 2 Modificado",
        )
        utils.quickSqlDelete("fltest3", "counter ='%s'" % val_1, "default")
        self.assertTrue(utils.sqlDelete("fltest3", "1=1", "dbAux"))
