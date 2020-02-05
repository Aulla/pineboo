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
        # from pineboolib.core.settings import config
        from pineboolib.qsa import qsa

        # tmp_dir = config.value("ebcomportamiento/temp_dir")
        dir_ = qsa.QDir(".", "*.py *.pyo")
        # current_path = dir_.path()
        # dir_.setPath(tmp_dir)
        path_ = os.path.abspath(dir_.path())
        self.assertTrue(dir_.exists())
        self.assertTrue(dir_.isReadable())
        self.assertEqual(dir_.absPath(), qsa.QDir(path_).absPath())
        # dir_.setPath(current_path)

    def test_qtextstream(self) -> None:
        """Test qtextstream class."""

        from pineboolib import application
        from pineboolib.qsa import qsa

        txt_ = "Hola!"
        txt_2 = "Hola de nuevo!"
        file_1 = qsa.QFile("%s/test_qtextstream.txt" % application.PROJECT.tmpdir)
        if not file_1.open(qsa.File.WriteOnly | qsa.File.Append):
            raise Exception("ay!")

        text_stream = qsa.QTextStream()
        text_stream.setDevice(file_1.ioDevice())
        text_stream.opIn(txt_ + "\n")
        file_1.close()

        with open("%s/test_qtextstream.txt" % application.PROJECT.tmpdir) as file_3:
            read_data = file_3.read()
            self.assertEqual(read_data, "Hola!\n")

        file_2 = qsa.QFile("%s/test_qtextstream.txt" % application.PROJECT.tmpdir)
        if not file_2.open(qsa.File.WriteOnly | qsa.File.Append):
            raise Exception("ay!")

        text_stream = qsa.QTextStream()
        text_stream.setDevice(file_2.ioDevice())
        text_stream.opIn(txt_2 + "\n")
        file_2.close()

        with open("%s/test_qtextstream.txt" % application.PROJECT.tmpdir) as file_4:
            read_data = file_4.read()
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

    def saludo(self) -> None:
        """AQGlobalFunction test."""
        self._prueba = True

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
