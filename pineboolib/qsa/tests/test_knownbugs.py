"""
Tests for known bugs on qsa.
"""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.application.types import Function
from pineboolib.application.parsers.qsaparser.postparse import pythonify_string as qs2py


class TestKnownBugs(unittest.TestCase):
    """Test known bugs."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_isloadedmodule(self) -> None:
        """Test bug where sys.isLoadedModule seems to be None."""

        fn_test = Function("module", "return sys.isLoadedModule(module);")
        self.assertEqual(fn_test("random_module"), False)
        self.assertEqual(fn_test("sys"), True)

    def test_mid(self) -> None:
        """Test str.mid(5, 2)."""

        value_1 = 'var cadena:String = "abcdefg";\ncadena.mid(5, 2);'
        self.assertEqual(qs2py(value_1), 'cadena = "abcdefg"\ncadena[5 : 5 + 2]\n')

        value_2 = 'var cadena:String = "abcdefg";\ncadena.mid(5);'
        self.assertEqual(qs2py(value_2), 'cadena = "abcdefg"\ncadena[0 + 5 :]\n')

    def test_system_get_env(self) -> None:
        """Check that qsa.System.getenv () works correctly."""

        from pineboolib.qsa import qsa

        qsa.System.setenv("TEST_PINEBOO", "¡hola!")

        self.assertEqual(qsa.System.getenv("TEST_PINEBOO"), "¡hola!")

    def test_reg_exp(self) -> None:
        """Test regExp parser."""
        value = """var reg_exp:RegExp = new RegExp( "''" );\nreg_exp.global = true;"""
        self.assertEqual(qs2py(value), """reg_exp = qsa.RegExp("''")\nreg_exp.global_ = True\n""")

    def test_from_project(self) -> None:
        """Test from_project parser."""
        value_1 = (
            'qsa.sys.AQTimer.singleShot(0, qsa.from_project("formescarrosproveedor").reject)\n'
        )
        self.assertEqual(qs2py("sys.AQTimer.singleShot(0, formescarrosproveedor.reject);"), value_1)
        value_2 = (
            'qsa.sys.AQTimer.singleShot(0, qsa.from_project("formRecordflmodules").iface.prueba)\n'
        )
        self.assertEqual(
            qs2py("sys.AQTimer.singleShot(0, formRecordflmodules.iface.prueba);"), value_2
        )
        value_3 = 'qsa.sys.AQTimer.singleShot(0, qsa.from_project("flfactppal").iface.test)\n'
        self.assertEqual(qs2py("sys.AQTimer.singleShot(0, flfactppal.iface.test);"), value_3)

    def test_multiples_if(self) -> None:
        """Check stackoverflow when parsing."""

        cadena = """var fN : String ="uno0";
                    if (fN == "uno0") {
                        debug(fN);
                        }
                    else if (fN == "dos0") {
                        debug(fN)
                        }
                    else if (fN == "tres0") {
                        debug(fN);
                        }
                    else if (fN == "cuatro0") {
                        debug(fN);
                        }
                    else if (fN == "cinco0") {
                        debug(fN);
                        }
                    else if (fN == "seis0") {
                        debug(fN);
                        }
                    else if (fN == "siete0") {
                        debug(fN);
                        }
                    else if (fN == "ocho0") {
                            debug(fN);
                            }
                    else if (fN == "nueve0") {
                        debug(fN);
                        }
                    else if (fN == "diez0") {
                        debug(fN);
                        }
                    else if (fN == "uno0") {
                        debug(fN);
                        }
                    else if (fN == "dos0") {
                        debug(fN);
                        }
                    else if (fN == "tres0") {
                        debug(fN);
                        }
                    else if (fN == "cuatro0") {
                        debug(fN);
                        }
                    else if (fN == "cinco0") {
                        debug(fN);
                        }
                    else if (fN == "seis0") {
                        debug(fN);
                        }
                    else if (fN == "siete0") {
                        debug(fN);
                        }
                    else if (fN == "ocho0") {
                            debug(fN);
                            }
                    else if (fN == "nueve0") {
                        debug(fN);
                        }
                    else if (fN == "diez0") {
                        debug(fN);
                        }
                    else if (fN == "dos0") {
                        debug(fN);
                        }
                    else if (fN == "tres0") {
                        debug(fN);
                        }
                    else if (fN == "cuatro0") {
                        debug(fN);
                        }
                    else if (fN == "cinco0") {
                        debug(fN);
                        }
                    else if (fN == "seis0") {
                        debug(fN);
                        }
                    else if (fN == "siete0") {
                        debug(fN);
                        }
                    else if (fN == "ocho0") {
                            debug(fN);
                            }
                    else if (fN == "nueve0") {
                        debug(fN);
                        }
                    else if (fN == "diez0") {
                        debug(fN);
                        }
                    else if (fN == "uno0") {
                        debug(fN);
                        }
                    else if (fN == "dos0") {
                        debug(fN);
                        }
                    else if (fN == "tres0") {
                        debug(fN);
                        }
                    else if (fN == "cuatro0") {
                        debug(fN);
                        }
                    else if (fN == "cinco0") {
                        debug(fN);
                        }
                    else if (fN == "seis0") {
                        debug(fN);
                        }
                    else if (fN == "siete0") {
                        debug(fN);
                        }
                    else if (fN == "ocho0" || fN == "once0") {
                            debug(fN);
                            }
                    else if (fN == "nueve0") {
                        debug(fN);
                        }
                    else if (fN == "diez0") {
                        debug(fN);
                        }

                    return fN;"""

        cadena_result = qs2py(cadena)
        self.assertFalse(cadena_result.find("not-known-seq") > -1)

    def test_from_project_2(self) -> None:
        """Test from_project('sys')."""
        from pineboolib.qsa import qsa

        self.assertTrue(hasattr(qsa.from_project("sys"), "iface"))

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()


if __name__ == "__main__":
    unittest.main()
