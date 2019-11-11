"""Test classes module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
import os


class TestClasses(unittest.TestCase):
    """Test classes."""

    _prueba = False

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_qdir(self) -> None:
        """Test qdir class."""

        from pineboolib.qsa import qsa

        dir_ = qsa.QDir(".", "*.py *.pyo")
        path_ = os.path.abspath(dir_.path())
        self.assertTrue(dir_.exists())
        self.assertTrue(dir_.isReadable())
        self.assertEqual(dir_.absPath(), qsa.QDir(path_).absPath())

    def test_qtextstream(self) -> None:
        """Test qtextstream class."""

        from pineboolib import application
        from pineboolib.qsa import qsa

        txt_ = "Hola!"
        txt_2 = "Hola de nuevo!"
        file = qsa.QFile("%s/test_qtextstream.txt" % application.project.tmpdir)
        if not file.open(qsa.File.WriteOnly | qsa.File.Append):
            raise Exception("ay!")

        ts = qsa.QTextStream()
        ts.setDevice(file.ioDevice())
        ts.opIn(txt_ + "\n")
        file.close()

        with open("%s/test_qtextstream.txt" % application.project.tmpdir) as f:
            read_data = f.read()
            self.assertEqual(read_data, "Hola!\n")

        file_2 = qsa.QFile("%s/test_qtextstream.txt" % application.project.tmpdir)
        if not file_2.open(qsa.File.WriteOnly | qsa.File.Append):
            raise Exception("ay!")

        ts = qsa.QTextStream()
        ts.setDevice(file_2.ioDevice())
        ts.opIn(txt_2 + "\n")
        file_2.close()

        with open("%s/test_qtextstream.txt" % application.project.tmpdir) as f:
            read_data = f.read()
            self.assertEqual(read_data, "Hola!\nHola de nuevo!\n")

    def test_qsproject(self) -> None:
        """Test qsproject."""

        from pineboolib.qsa import qsa

        value_1 = "flfactppal.iface.prueba"
        qsa.aqApp.setScriptEntryFunction("flfactppal.iface.prueba")

        value_2 = qsa.QSProject.entryFunction

        self.assertEqual(value_1, value_2)

    def test_aq_global_functions(self) -> None:
        """Test AQGlobal function."""
        from pineboolib.qsa import qsa
        from PyQt5 import QtWidgets

        qsa.sys.AQGlobalFunctions.set("saludo", self.saludo)
        btn = QtWidgets.QPushButton()
        qsa.sys.AQGlobalFunctions.mapConnect(btn, "clicked()", "saludo")
        self.assertFalse(self._prueba)
        btn.clicked.emit()
        self.assertTrue(self._prueba)

    def saludo(self):
        """AQGlobalFunction test."""
        self._prueba = True

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
