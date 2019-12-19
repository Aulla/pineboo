"""Test_dateedit module."""

import unittest


class TestDateEdit(unittest.TestCase):
    """TestDateEdit Class."""

    def test_all(self) -> None:
        """Test DateEdit."""

        from pineboolib.qsa import qsa

        date_edit = qsa.DateEdit()
        date_edit.label = "Prueba label"
        date_edit.date = qsa.Date("2019-01-10")
        self.assertEqual(str(date_edit.date), "2019-01-10T00:00:00")
        self.assertEqual(date_edit.label, "Prueba label")
