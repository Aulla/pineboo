"""
Tests for application.types module.
"""

import unittest
import os
from pineboolib.loader.main import init_cli
from pineboolib.application.types import (
    Boolean,
    QString,
    Function,
    Object,
    Array,
    Date,
    File,
    FileStatic,
    Dir,
    DirStatic,
)

init_cli()  # FIXME: This should be avoided


class TestBoolean(unittest.TestCase):
    """Test booleans."""

    def test_true(self) -> None:
        """Test for true."""
        self.assertEqual(Boolean(1), True)
        self.assertEqual(Boolean("True"), True)
        self.assertEqual(Boolean("Yes"), True)
        self.assertEqual(Boolean(0.8), True)

    def test_false(self) -> None:
        """Test for false."""
        self.assertEqual(Boolean(0), False)
        self.assertEqual(Boolean("False"), False)
        self.assertEqual(Boolean("No"), False)


class TestQString(unittest.TestCase):
    """Test QString."""

    def test_basic(self) -> None:
        """Basic testing."""
        s = QString("hello world")
        self.assertEqual(s, "hello world")
        self.assertEqual(s.mid(5), s[5:])
        self.assertEqual(s.mid(5, 2), s[5:7])


class TestFunction(unittest.TestCase):
    """Test function. Parses QSA into Python."""

    def test_basic(self) -> None:
        """Basic testing."""
        source = "return x + 1"
        fn = Function("x", source)
        self.assertEqual(fn(1), 2)


class TestObject(unittest.TestCase):
    """Test object."""

    def test_basic1(self) -> None:
        """Basic testing."""
        o = Object()
        o.prop1 = 1
        o.prop2 = 2
        self.assertEqual(o.prop1, o["prop1"])

    def test_basic2(self) -> None:
        """Basic testing."""
        o = Object({"prop1": 1})
        self.assertEqual(o.prop1, o["prop1"])


class TestArray(unittest.TestCase):
    """Test Array class."""

    def test_basic1(self) -> None:
        """Basic testing."""
        a = Array()
        a.value = 1
        self.assertEqual(a.value, a["value"])

    def test_basic2(self) -> None:
        """Basic testing."""
        test_arr = [0, 1, 2, 3, 4]
        a = Array(test_arr)
        self.assertEqual(a[3], 3)
        self.assertEqual(list(a._dict.values()), test_arr)
        self.assertEqual(len(a), len(test_arr))
        self.assertEqual(a, test_arr)

        test_arr = [3, 4, 2, 1, 0]
        a = Array(test_arr)
        self.assertEqual(list(a._dict.values()), test_arr)
        a.append(10)
        self.assertEqual(a[5], 10)

    def test_basic3(self) -> None:
        """Basic Testing."""
        test_arr = {"key_0": "item_0", "key_1": "item_1", "key_2": "item_2"}
        a = Array(test_arr)
        self.assertEqual(a["key_0"], "item_0")
        self.assertEqual(a.key_1, a["key_1"])
        self.assertEqual(a.length(), 3)
        self.assertEqual(a[2], "item_2")
        self.assertEqual(list(a._dict.values()), ["item_0", "item_1", "item_2"])

    def test_repr(self) -> None:
        """Test repr method."""
        test_arr = [3, 4, 5, 6, 7]
        a1 = Array(test_arr)
        self.assertEqual(repr(a1), "<Array %r>" % test_arr)

    def test_iter(self) -> None:
        """Test iterating arrays."""

        test_arr = [3, 4, 5, 6, 7]
        a1 = Array(test_arr)
        a2 = [x for x in a1]
        self.assertEqual(test_arr, a2)

        test_arr = [8, 7, 6, 4, 2]
        a1 = Array(test_arr)
        a2 = [x for x in a1]
        self.assertEqual(test_arr, a2)


class TestDate(unittest.TestCase):
    """Test Date class."""

    # FIXME: Complete unit tests
    def test_basic1(self) -> None:
        """Basic testing."""
        d = Date("2001-02-25")
        self.assertEqual(d.getDay(), 25)
        self.assertEqual(d.getMonth(), 2)
        self.assertEqual(d.getYear(), 2001)


class TestFile(unittest.TestCase):
    """Test File class."""

    def test_write_read_values_1(self) -> None:
        """Check that you read the same as you write."""
        from pineboolib.fllegacy.systype import SysType

        temporal = "%s%s" % (SysType().installPrefix(), u"/tempdata/test_types_file.txt")
        contenido = 'QT_TRANSLATE_NOOP("MetaData","Código")'
        File(temporal).write(contenido)
        contenido_2 = File(temporal).read()
        self.assertEqual(contenido, contenido_2)
        os.remove(temporal)

    def test_write_read_values_2(self) -> None:
        """Check that you read the same as you write."""
        from pineboolib.fllegacy.systype import SysType

        temporal = "%s%s" % (SysType().installPrefix(), u"/tempdata/test_types_file_static.txt")
        contenido = 'QT_TRANSLATE_NOOP("MetaData","Código")'
        FileStatic.write(temporal, contenido)
        contenido_2 = FileStatic.read(temporal)
        self.assertEqual(contenido, contenido_2)
        os.remove(temporal)

    def test_full_name_and_readable(self) -> None:
        """Check fullName"""
        from pineboolib.fllegacy.systype import SysType

        temporal = "%s%s" % (SysType().installPrefix(), u"/tempdata/test_types_file_full_name.txt")
        contenido = 'QT_TRANSLATE_NOOP("MetaData","Código")'
        file_ = File(temporal)
        file_.write(contenido)
        self.assertEqual(file_.fullName(), temporal)
        self.assertTrue(file_.readable())


class TestDir(unittest.TestCase):
    """TestDir class."""

    def test_current(self) -> None:
        """Check Dir."""

        self.assertEqual(os.curdir, Dir().current)
        self.assertEqual(os.curdir, DirStatic.current)


if __name__ == "__main__":
    unittest.main()
