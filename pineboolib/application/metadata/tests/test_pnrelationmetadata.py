"""
test_pnrelationmetadata Module.
"""

import unittest
from pineboolib.loader.main import init_testing
from pineboolib import application


class TestPNRelationMetaData(unittest.TestCase):
    """TestPNRelationMetaData Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic(self) -> None:
        """PNRelationMetaData."""

        mtd = application.PROJECT.conn_manager.manager().metadata("flgroups")
        if mtd is None:
            raise Exception
        rel_1 = mtd.relation("idgroup", "idgroup", "flusers")
        rel_2 = mtd.relation("idgroup", "idgroup", "flacs")
        if rel_1 is None:
            raise Exception
        if rel_2 is None:
            raise Exception

        self.assertEqual(rel_1.field(), "idgroup")
        self.assertEqual(rel_2.foreignField(), "idgroup")
        self.assertEqual(rel_2.foreignTable(), "flacs")
        self.assertEqual(rel_2.deleteCascade(), False)
        self.assertEqual(rel_1.cardinality(), "1M")

    def test_assigment(self) -> None:
        """Test multiples relaitos asigment to a field."""

        from pineboolib.application.metadata import pnrelationmetadata

        mtd = application.PROJECT.conn_manager.manager().metadata("flmodules")
        self.assertTrue(mtd)
        if mtd is not None:
            field = mtd.field("version")
            self.assertTrue(field)
            if field is not None:
                relation0 = pnrelationmetadata.PNRelationMetaData("tabla0", "campo0", "M1")
                relation1 = pnrelationmetadata.PNRelationMetaData("tabla1", "campo1", "1M")
                relation2 = pnrelationmetadata.PNRelationMetaData("tabla2", "campo2", "1M")
                relation3 = pnrelationmetadata.PNRelationMetaData("tabla3", "campo3", "M1")
                relation4 = pnrelationmetadata.PNRelationMetaData("tabla4", "campo4", "M1")
                self.assertFalse(field.relationM1())
                self.assertFalse(field.relationList())
                field.addRelationMD(relation0)
                self.assertFalse(relation0 in field.relationList())
                self.assertEqual(relation0, field.relationM1())
                field.addRelationMD(relation1)
                self.assertTrue(relation1 in field.relationList())
                self.assertNotEqual(relation1, field.relationM1())
                field.addRelationMD(relation2)
                self.assertTrue(relation2 in field.relationList())
                field.addRelationMD(relation3)
                self.assertNotEqual(relation3, field.relationM1())
                self.assertFalse(relation3 in field.relationList())
                field.addRelationMD(relation4)
                self.assertNotEqual(relation4, field.relationM1())
                self.assertFalse(relation4 in field.relationList())
                self.assertEqual([relation1, relation2], field.relationList())


class TestCreatePNRelationMetaData(unittest.TestCase):
    """TestCreatePNRelationMetaData Class."""

    def test_basic(self) -> None:
        """PNRelationMetaData."""

        from pineboolib.application.metadata import pnrelationmetadata

        mtd = application.PROJECT.conn_manager.manager().metadata("flgroups")
        if mtd is None:
            raise Exception
        rel_1 = mtd.relation("idgroup", "idgroup", "flusers")
        if rel_1 is None:
            raise Exception("Relation is empty!.")
        rel_2 = pnrelationmetadata.PNRelationMetaData(rel_1)
        rel_3 = pnrelationmetadata.PNRelationMetaData(
            "flgroups", "idgroup", "M1", True, True, False
        )

        self.assertEqual(rel_2.foreignField(), "idgroup")
        self.assertEqual(rel_2.foreignTable(), "flusers")

        rel_3.setField("new_field")

        self.assertEqual(rel_3.field(), "new_field")
        self.assertEqual(rel_3.foreignField(), "idgroup")
        self.assertEqual(rel_3.cardinality(), "M1")
        self.assertEqual(rel_3.deleteCascade(), True)
        self.assertEqual(rel_3.updateCascade(), True)
        self.assertEqual(rel_3.checkIn(), False)


if __name__ == "__main__":
    unittest.main()
