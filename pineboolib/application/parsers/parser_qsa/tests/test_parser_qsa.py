"""
Test QS Snippets.
"""
import unittest
from ..postparse import pythonify_string as qs2py
from .. import pytnyzer
from . import fixture_read, fixture_path
from pineboolib.loader.main import init_testing, finish_testing

NUMERO_MULTI = 0


class TestParser(unittest.TestCase):
    """Test Parsing QS to PY."""

    @classmethod
    def setUpClass(cls) -> None:
        """Enable strict parsing."""
        pytnyzer.STRICT_MODE = True
        init_testing()

    def test_basic(self) -> None:
        """Test basic stuff."""

        self.assertEqual(qs2py("x = 0"), "x = 0\n")

    def test_aqssproject(self) -> None:
        """Test aqssproject parse."""

        self.assertEqual(qs2py("QSProject.entryFunction"), "qsa.QSProject.entryFunction\n")

    def test_file_class(self) -> None:
        """Test parsing the file class."""
        self.assertEqual(qs2py('x = File.read("test")'), 'x = qsa.FileStatic.read("test")\n')
        self.assertEqual(
            qs2py('x = File.write("test", "contents")'),
            'x = qsa.FileStatic.write("test", "contents")\n',
        )
        self.assertEqual(qs2py('x = File.remove("test")'), 'x = qsa.FileStatic.remove("test")\n')

        self.assertEqual(qs2py('x = File("test").read()'), 'x = qsa.File("test").read()\n')
        self.assertEqual(
            qs2py('x = File("test").write("contents")'), 'x = qsa.File("test").write("contents")\n'
        )
        self.assertEqual(qs2py('x = File("test").remove()'), 'x = qsa.File("test").remove()\n')

    def test_list_arrays(self) -> None:
        """Test parsing iterable classes."""
        self.assertEqual(qs2py("var value = Array().shift()"), "value: Any = qsa.Array().pop(0)\n")
        self.assertEqual(qs2py("var value = [].shift()"), "value: Any = [].pop(0)\n")

    def test_array(self) -> None:
        """Test array."""

        self.assertEqual(qs2py("var a = new Array();"), "a: Any = qsa.Array()\n")
        self.assertEqual(qs2py("var b = new Array(0);"), "b: Any = []\n")

    def test_typeof(self) -> None:
        """Test typeof."""

        self.assertEqual(qs2py("var a = typeof('juan')"), 'a: Any = qsa.typeof_("juan")\n')
        self.assertEqual(
            qs2py('debug("hola " + " " + typeof("juan"));'),
            'qsa.debug(qsa.ustr("hola ", " ", qsa.typeof_("juan")))\n',
        )

    def test_process_class(self) -> None:
        """Test parsing the process class."""
        self.assertEqual(
            qs2py('x = Process.execute(["ls", "*"])'),
            'x = qsa.ProcessStatic.execute(qsa.Array(["ls", "*"]))\n',
        )

    def test_while(self) -> None:
        """Test while class."""
        value = "with (this.iface.curFactura)"
        value += (
            'setValueBuffer("neto", formfacturascli.iface.pub_commonCalculateField("neto", this));'
        )
        result_value = "# WITH_START\n"
        result_value += "self.iface.curFactura.setValueBuffer(\n"
        result_value += '    "neto", qsa.from_project("formfacturascli").iface.pub_commonCalculateField("neto", self.iface.curFactura)\n'
        result_value += ")\n"
        result_value += "# WITH_END\n"

        self.assertEqual(qs2py(value), result_value)

    def test_flfacturac(self) -> None:
        """Test conveting fixture flfacturac."""

        flfacturac_qs = fixture_read("flfacturac.qs")
        flfacturac_py = fixture_read("flfacturac.python")
        flfacturac_qs_py = qs2py(flfacturac_qs, parser_template="file_template")

        # Delete version translator tag.
        pos_ini = flfacturac_qs_py.find("# Translated with pineboolib ")
        pos_fin = flfacturac_qs_py[pos_ini:].find("\n")
        flfacturac_qs_py = flfacturac_qs_py.replace(
            flfacturac_qs_py[pos_ini : pos_ini + pos_fin + 1], ""
        )

        # Write onto git so we have an example.
        with open(fixture_path("flfacturac.qs.python"), "w") as file_:
            file_.write(flfacturac_qs_py)

        self.assertEqual(flfacturac_qs_py, flfacturac_py)

    def test_lib_str(self) -> None:
        """Test conveting fixture lib_str."""
        self.maxDiff = None  # pylint: disable=invalid-name
        flfacturac_qs = fixture_read("lib_str.qs")
        flfacturac_py = fixture_read("lib_str.python")
        flfacturac_qs_py = qs2py(flfacturac_qs, parser_template="file_template")

        # Delete version translator tag.
        pos_ini = flfacturac_qs_py.find("# Translated with pineboolib ")
        pos_fin = flfacturac_qs_py[pos_ini:].find("\n")
        flfacturac_qs_py = flfacturac_qs_py.replace(
            flfacturac_qs_py[pos_ini : pos_ini + pos_fin + 1], ""
        )

        # Write onto git so we have an example.
        with open(fixture_path("lib_str.qs.python"), "w") as file_:
            file_.write(flfacturac_qs_py)

        self.assertEqual(flfacturac_qs_py, flfacturac_py)

    def test_form(self) -> None:
        """Test converting form"""
        self.assertEqual(qs2py("form = this;"), "form = self\n")

    def test_parse_int(self) -> None:
        """Test parseInt function."""
        self.assertEqual(qs2py('var value = parseInt("21");'), 'value: Any = qsa.parseInt("21")\n')
        self.assertEqual(
            qs2py("var value = parseInt(2000.21 , 10);"), "value: Any = qsa.parseInt(2000.21, 10)\n"
        )
        self.assertEqual(
            qs2py('var value = parseInt("0xA0", 16);'), 'value: Any = qsa.parseInt("0xA0", 16)\n'
        )

    def test_qdir(self) -> None:
        """Test QDir translation."""
        self.assertEqual(
            qs2py(
                'var rutaImp:String = "."; var impDir = new QDir(rutaImp, "c*.csv C*.csv c*.CSV C*.CSV");'
            ),
            'rutaImp: str = "."\nimpDir: Any = qsa.QDir(rutaImp, "c*.csv C*.csv c*.CSV C*.CSV")\n',
        )

    def test_qobject(self) -> None:
        """Test QObject translation."""

        self.assertEqual(qs2py("var prueba = new QObject;"), "prueba: Any = qsa.QObject()\n")

    def test_inicialize_float(self) -> None:
        """Test float inicialization."""

        self.assertEqual(qs2py("var num:Number = 0.0;"), "num = 0.0\n")

    def test_aqsignalmapper(self) -> None:
        """Test AQSignalmapper."""

        self.assertEqual(
            qs2py("var sigMap = new AQSignalMapper(this);"),
            "sigMap: Any = qsa.AQSignalMapper(self)\n",
        )

    def test_replace(self) -> None:
        """Test replace."""

        self.assertEqual(
            qs2py(
                'var listaOutlet:Array = new Array();flfactppal.iface.replace(listaOutlet, ", ", " "," ");'
            ),
            """listaOutlet: \"qsa.Array\" = qsa.Array()
qsa.from_project("flfactppal").iface.replace(listaOutlet, ", ", " ", " ")\n""",
        )

        self.assertEqual(
            qs2py(
                "function pub_replace(cadena:String, searchValue:Number, newValue:Array)"
                + " {\nreturn this.replace(cadena, searchValue, newValue);\n}"
            ),
            """def pub_replace(self, cadena: "str", searchValue, newValue: "qsa.Array"):
    return self.replace(cadena, searchValue, newValue)\n""",
        )

    def test_optional(self) -> None:
        """Test optional."""

        self.assertEqual(
            qs2py(
                "function pub_replace(cadena:String, searchValue:Number, newValue:optional)"
                + " {\nreturn this.replace(cadena, searchValue, newValue);\n}"
            ),
            """def pub_replace(self, cadena: "str", searchValue, newValue: "Any" = None):
    return self.replace(cadena, searchValue, newValue)\n""",
        )

    def test_sort_1(self) -> None:
        """Test replace."""

        self.assertEqual(
            qs2py("var listaOutlet:Array = new Array();listaOutlet.sort();"),
            'listaOutlet: "qsa.Array" = qsa.Array()\nqsa.Sort().sort_(listaOutlet)\n',
        )

    def test_sort_2(self) -> None:
        """Test replace."""

        self.assertEqual(
            qs2py(
                """
                var aLista:Array = new Array()
                aLista.sort(parseString);
                """
            ),
            'aLista: "qsa.Array" = qsa.Array()\nqsa.Sort(qsa.parseString).sort_(aLista)\n',
        )

    def test_form2(self) -> None:
        """Test replace."""

        """Test conveting fixture flfacturac_2."""
        self.maxDiff = None
        flfacturac_qs = fixture_read("flfacturac_2.qs")
        flfacturac_py = fixture_read("flfacturac_2.python")
        flfacturac_qs_py = qs2py(flfacturac_qs, parser_template="file_template")

        # Delete version translator tag.
        pos_ini = flfacturac_qs_py.find("# Translated with pineboolib ")
        pos_fin = flfacturac_qs_py[pos_ini:].find("\n")
        flfacturac_qs_py = flfacturac_qs_py.replace(
            flfacturac_qs_py[pos_ini : pos_ini + pos_fin + 1], ""
        )

        # Write onto git so we have an example.
        with open(fixture_path("flfacturac_2.qs.python"), "w") as file_:
            file_.write(flfacturac_qs_py)

        self.assertEqual(flfacturac_qs_py, flfacturac_py)

    def test_splice(self) -> None:
        """Test splice."""

        self.assertEqual(
            qs2py(
                """
                var aLista = new Array();
                aLista.splice(10,1);
                """
            ),
            "aLista: Any = qsa.Array()\nqsa.splice(aLista, 10, 1)\n",
        )

    def test_all_any(self) -> None:
        """Test variable parse."""

        self.assertEqual(qs2py('var prueba = "hola";'), 'prueba: Any = "hola"\n')

    def test_pyconvert(self) -> None:
        """Test pyconvert."""
        from pineboolib import application
        import os
        import shutil

        path = fixture_path("flfacturac.qs")
        tmp_path = "%s/%s" % (application.PROJECT.tmpdir, "temp_qs.qs")
        path_py = "%s.py" % tmp_path[:-3]

        shutil.copy(path, tmp_path)
        application.PROJECT.parse_script_list([tmp_path])

        self.assertTrue(os.path.exists(path_py))

        if os.path.exists(tmp_path):
            os.remove(tmp_path)

        if os.path.exists(path_py):
            os.remove(path_py)

    def test_pyconvert_multi(self) -> None:
        """Test pyconvert simultaneously."""

        from PyQt6 import QtCore, QtWidgets  # type: ignore[import]

        global NUMERO_MULTI

        timer = QtCore.QTimer
        timer.singleShot(0, self.convert)
        timer.singleShot(0, self.convert)
        timer.singleShot(0, self.convert)
        QtWidgets.QApplication.processEvents()

    def convert(self) -> None:
        """Convert a file."""
        global NUMERO_MULTI
        from pineboolib import application
        import os
        import shutil

        NUMERO_MULTI += 1

        path = fixture_path("flfacturac.qs")
        tmp_path = "%s/%s" % (application.PROJECT.tmpdir, "multi.qs")
        if not os.path.exists(tmp_path):
            shutil.copy(path, tmp_path)

        application.PROJECT.parse_script_list([tmp_path])

    def test_pyconvert_2(self) -> None:
        """Test conveting fixture lib_str."""

        from pineboolib import application
        import os
        import shutil

        self.maxDiff = None
        simple_qs_path = fixture_path("simple.qs")
        tmp_path = "%s/%s" % (application.PROJECT.tmpdir, "simple.qs")
        if not os.path.exists(tmp_path):
            shutil.copy(simple_qs_path, tmp_path)

        print("Convirtiendo", tmp_path, "existe", os.path.exists(tmp_path))
        self.assertTrue(application.PROJECT.parse_script_list([tmp_path]))
        simple_py = fixture_read("simple.python")
        simple_qs_py_path = "%spy" % tmp_path[:-2]
        self.assertTrue(os.path.exists(simple_qs_py_path))
        file_ = open(simple_qs_py_path, "r", encoding="utf-8")
        simple_qs_py = file_.read()

        # Delete version translator tag.
        pos_ini = simple_qs_py.find("# Translated with pineboolib ")
        pos_fin = simple_qs_py[pos_ini:].find("\n")
        simple_qs_py = simple_qs_py.replace(simple_qs_py[pos_ini : pos_ini + pos_fin + 1], "")

        # Write onto git so we have an example.
        with open(fixture_path("simple.qs.python"), "w") as file_:
            file_.write(simple_qs_py)

        self.assertEqual(simple_qs_py, simple_py)

    def test_ignore_no_python_flag_disabled(self) -> None:
        """Test no python flag."""
        from pineboolib import application
        from pineboolib.core.utils import utils_base
        from pineboolib.application.parsers import parser_qsa
        import os
        import shutil

        utils_base.FORCE_DESKTOP = False

        print(
            "Is library",
            utils_base.is_library(),
            "ignore no_python tags",
            parser_qsa.IGNORE_NO_PYTHON_TAGS,
        )
        qs_path = fixture_path("no_python.qs")
        tmp_path = "%s/%s" % (application.PROJECT.tmpdir, "no_python.qs")
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        shutil.copy(qs_path, tmp_path)

        self.assertTrue(application.PROJECT.parse_script_list([tmp_path]))
        qs_py_path = "%spy" % tmp_path[:-2]

        utils_base.FORCE_DESKTOP = True

        file_ = open(qs_py_path, "r", encoding="utf-8")
        qs_py = file_.read()
        self.assertTrue(qs_py.find("TYPE_INT_") > -1)
        self.assertTrue(qs_py.find("TYPE_UINT_") == -1)

    def test_ignore_no_python_flag_enabled(self) -> None:
        """Test no python flag."""
        from pineboolib import application
        from pineboolib.core.utils import utils_base
        from pineboolib.application.parsers import parser_qsa
        import os
        import shutil

        utils_base.FORCE_DESKTOP = False
        parser_qsa.IGNORE_NO_PYTHON_TAGS = True

        qs_path = fixture_path("no_python.qs")
        tmp_path = "%s/%s" % (application.PROJECT.tmpdir, "no_python2.qs")
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        shutil.copy(qs_path, tmp_path)

        self.assertTrue(application.PROJECT.parse_script_list([tmp_path]))
        qs_py_path = "%spy" % tmp_path[:-2]

        parser_qsa.IGNORE_NO_PYTHON_TAGS = False
        utils_base.FORCE_DESKTOP = True

        file_ = open(qs_py_path, "r", encoding="utf-8")
        qs_py = file_.read()
        self.assertTrue(qs_py.find("TYPE_INT_") > -1)
        self.assertTrue(qs_py.find("TYPE_UINT_") > -1)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()
