"""
Test QS Snippets.
"""
import unittest
from pineboolib.application.parsers.qsaparser.postparse import pythonify_string as qs2py
from pineboolib.application.parsers.qsaparser import pytnyzer
from . import fixture_read, fixture_path


class TestParser(unittest.TestCase):
    """Test Parsing QS to PY."""

    @classmethod
    def setUpClass(cls) -> None:
        """Enable strict parsing."""
        pytnyzer.STRICT_MODE = True

    def test_basic(self) -> None:
        """Test basic stuff."""

        self.assertEqual(qs2py("x = 0"), "x = 0\n")

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

        # Write onto git so we have an example.
        with open(fixture_path("flfacturac.qs.python"), "w") as f:
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


if __name__ == "__main__":
    unittest.main()
