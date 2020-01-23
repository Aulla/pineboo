"""
Test QS Snippets.
"""
import unittest
from pineboolib.application.parsers.qsaparser.postparse import pythonify_string as qs2py
from pineboolib.application.parsers.qsaparser import pytnyzer
from . import fixture_read, fixture_path
from pineboolib.loader.main import init_testing, finish_testing


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
        self.assertEqual(qs2py("var value = Array().shift()"), "value = qsa.Array().pop(0)\n")
        self.assertEqual(qs2py("var value = [].shift()"), "value = [].pop(0)\n")

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
        pos_ini = flfacturac_qs_py.find("# Translated with pineboolib v")
        pos_fin = flfacturac_qs_py[pos_ini:].find("\n")
        flfacturac_qs_py = flfacturac_qs_py.replace(
            flfacturac_qs_py[pos_ini : pos_ini + pos_fin + 1], ""
        )

        # Write onto git so we have an example.
        with open(fixture_path("flfacturac.qs.python"), "w") as f:
            f.write(flfacturac_qs_py)

        self.assertEqual(flfacturac_qs_py, flfacturac_py)

    def test_lib_str(self) -> None:
        """Test conveting fixture lib_str."""
        flfacturac_qs = fixture_read("lib_str.qs")
        flfacturac_py = fixture_read("lib_str.python")
        flfacturac_qs_py = qs2py(flfacturac_qs, parser_template="file_template")

        # Delete version translator tag.
        pos_ini = flfacturac_qs_py.find("# Translated with pineboolib v")
        pos_fin = flfacturac_qs_py[pos_ini:].find("\n")
        flfacturac_qs_py = flfacturac_qs_py.replace(
            flfacturac_qs_py[pos_ini : pos_ini + pos_fin + 1], ""
        )

        # Write onto git so we have an example.
        with open(fixture_path("lib_str.qs.python"), "w") as f:
            f.write(flfacturac_qs_py)

        self.assertEqual(flfacturac_qs_py, flfacturac_py)

    def test_form(self) -> None:
        """Test converting form"""
        self.assertEqual(qs2py("form = this;"), "form = self\n")

    def test_parse_int(self) -> None:
        """Test parseInt function."""
        self.assertEqual(qs2py('var value = parseInt("21");'), 'value = qsa.parseInt("21")\n')
        self.assertEqual(
            qs2py("var value = parseInt(2000.21 , 10);"), "value = qsa.parseInt(2000.21, 10)\n"
        )
        self.assertEqual(
            qs2py('var value = parseInt("0xA0", 16);'), 'value = qsa.parseInt("0xA0", 16)\n'
        )

    def test_qdir(self) -> None:
        """Test QDir translation."""
        self.assertEqual(
            qs2py(
                'var rutaImp:String = "."; var impDir = new QDir(rutaImp, "c*.csv C*.csv c*.CSV C*.CSV");'
            ),
            'rutaImp = "."\nimpDir = qsa.QDir(rutaImp, "c*.csv C*.csv c*.CSV C*.CSV")\n',
        )

    def test_qobject(self) -> None:
        """Test QObject translation."""

        self.assertEqual(qs2py("var prueba = new QObject;"), "prueba = qsa.QObject()\n")

    def test_inicialize_float(self) -> None:
        """Test float inicialization."""

        self.assertEqual(qs2py("var num:Number = 0.0;"), "num = 0.0\n")

    def test_aqsignalmapper(self) -> None:
        """Test AQSignalmapper."""

        self.assertEqual(
            qs2py("var sigMap = new AQSignalMapper(this);"), "sigMap = qsa.AQSignalMapper(self)\n"
        )

    def test_pyconvert(self) -> None:
        """Test pyconvert."""
        from pineboolib import application
        import os
        import shutil

        path = fixture_path("flfacturac.qs")
        tmp_path = "%s/%s" % (application.PROJECT.tmpdir, "temp_qs.qs")
        path_py = "%s.py" % tmp_path[:-3]
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

        if os.path.exists(path_py):
            os.remove(path_py)

        shutil.copy(path, tmp_path)
        application.PROJECT.parse_script_list([tmp_path])

        self.assertTrue(os.path.exists(path_py))

        if os.path.exists(tmp_path):
            os.remove(tmp_path)

        if os.path.exists(path_py):
            os.remove(path_py)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()


if __name__ == "__main__":
    unittest.main()
