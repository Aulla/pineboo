"""Test_qradiobuttons module."""

import unittest

from pineboolib.loader.main import init_testing, finish_testing

from .. import qhbuttongroup
from .. import qvbuttongroup
from .. import qradiobutton


class TestQRadioButtons(unittest.TestCase):
    """Test TestQRadioButtons class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic_1(self) -> None:
        """Test basic 1."""

        hbg = qhbuttongroup.QHButtonGroup()
        vbg = qvbuttongroup.QVButtonGroup()

        self.assertTrue(hbg)
        self.assertTrue(vbg)

        bt1 = qradiobutton.QRadioButton(hbg)
        bt1.text = "prueba"
        bt1.setButtonGroupId(10)
        self.assertFalse(bt1.checked)
        bt1.checked = True
        bt1.send_clicked()
        self.assertTrue(bt1.checked)
        self.assertEqual(bt1.text, "prueba")
        hbg.setSelectedId(10)
        self.assertEqual(hbg.selectedId, 10)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
