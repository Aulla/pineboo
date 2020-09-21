"""Test_process module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing


class TestProcess(unittest.TestCase):
    """TestProcess Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_Process(self) -> None:
        """Test Process."""

        from pineboolib.application import process

        proc = process.Process()

        proc.execute("python3 --version")

        self.assertFalse(proc.stderr)
        salida = proc.stdout

        self.assertTrue(salida.find("Python") > -1)

    def test_ProcessStatic(self) -> None:
        """Test ProcessStatic."""

        from pineboolib.qsa import qsa

        comando_py = ""
        proc = qsa.ProcessStatic

        proc.execute("python3 --version")

        self.assertFalse(proc.stderr)
        salida = proc.stdout

        comando_py = "python3"
        self.assertTrue(salida.find("Python") > -1)

        comando = qsa.Array(comando_py, "--version")

        proc_2 = qsa.ProcessStatic
        proc_2.executeNoSplit(comando)
        self.assertTrue(salida in [proc_2.stderr, proc_2.stdout])

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
