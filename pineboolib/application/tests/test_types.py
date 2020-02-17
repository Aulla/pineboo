"""
Tests for application.types module.
"""

import unittest
import os
from pineboolib.loader.main import init_cli
from pineboolib.core.settings import config
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
    String,
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
        self.assertEqual(Boolean(True), True)

    def test_false(self) -> None:
        """Test for false."""
        self.assertEqual(Boolean(0), False)
        self.assertEqual(Boolean("False"), False)
        self.assertEqual(Boolean("No"), False)
        self.assertEqual(Boolean(False), False)


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
        b = Array(test_arr)
        self.assertEqual(a[3], 3)
        self.assertEqual(list(a._dict.values()), test_arr)
        self.assertEqual(len(a), len(test_arr))
        self.assertEqual(a, test_arr)
        self.assertEqual(a[3], b[3])
        self.assertNotEqual(a[3], b[0])

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

    def test_splice(self) -> None:
        """Test splice."""

        test_arr = [3, 4, 5, 6, 7]
        a1 = Array(test_arr)
        a1.splice(1, 2)  # Delete
        self.assertEqual(str(a1), str(Array([4, 5])))
        a2 = Array(test_arr)
        a2.splice(2, 0, 9, 10)  # Insertion
        self.assertEqual(str(a2), str(Array([3, 4, 5, 9, 10, 6, 7])))
        a3 = Array(test_arr)
        a3.splice(2, 1, 9, 10)  # Replace
        self.assertEqual(str(a3), str(Array([3, 4, 9, 10, 6, 7])))


class TestDate(unittest.TestCase):
    """Test Date class."""

    # FIXME: Complete unit tests
    def test_basic1(self) -> None:
        """Basic testing."""
        d = Date("2001-02-25")
        self.assertEqual(d.getDay(), 25)
        self.assertEqual(d.getMonth(), 2)
        self.assertEqual(d.getYear(), 2001)


class TestString(unittest.TestCase):
    """TestString class."""

    # FIXME: Complete unit tests
    def test_fromCharCode(self) -> None:
        """Test fromCharCode."""
        temp: str = String.fromCharCode(13, 10)
        self.assertEqual(temp, "\r\n")


class TestFile(unittest.TestCase):
    """Test File class."""

    def test_write_read_values_1(self) -> None:
        """Check that you read the same as you write."""

        temporal = "%s%s" % (config.value("ebcomportamiento/temp_dir"), u"/test_types_file.txt")
        contenido = 'QT_TRANSLATE_NOOP("MetaData","Código")'
        contenido_3 = 'QT_TRANSLATE_NOOP("MetaData","Código")'
        File(temporal).write(contenido)
        contenido_2 = File(temporal).read()
        self.assertEqual(contenido, contenido_2)
        os.remove(temporal)
        File(temporal).write(contenido_3)
        contenido_4 = File(temporal).read()
        self.assertEqual(contenido_3, contenido_4)
        os.remove(temporal)

    def test_write_read_values_2(self) -> None:
        """Check that you read the same as you write."""

        temporal = "%s%s" % (
            config.value("ebcomportamiento/temp_dir"),
            u"/test_types_file_static.txt",
        )
        contenido = 'QT_TRANSLATE_NOOP("MetaData","Código")'
        FileStatic.write(temporal, contenido)
        contenido_2 = FileStatic.read(temporal)
        self.assertEqual(contenido, contenido_2)
        os.remove(temporal)

    def test_write_read_bytes_1(self) -> None:
        """Check that you read the same as you write."""

        temporal = "%s%s" % (
            config.value("ebcomportamiento/temp_dir"),
            u"/test_types_file_bytes.txt",
        )
        contenido = "Texto escrito en bytes\n".encode("utf-8")
        File(temporal).write(contenido)
        contenido_2 = File(temporal).read(True)
        self.assertEqual(contenido, contenido_2.encode("utf-8"))
        os.remove(temporal)

    def test_write_read_byte_1(self) -> None:
        """Check that you read the same as you write."""

        temporal = "%s%s" % (
            config.value("ebcomportamiento/temp_dir"),
            u"/test_types_file_bytes.txt",
        )
        contenido = "Texto\n".encode("utf-8")
        File(temporal).write(contenido)
        contenido_2 = File(temporal).read(True)
        self.assertEqual(contenido, contenido_2.encode("utf-8"))
        os.remove(temporal)

    def test_write_read_line_1(self) -> None:
        """Check that you read the same as you write."""

        temporal = "%s%s" % (
            config.value("ebcomportamiento/temp_dir"),
            u"/test_types_file_lines.txt",
        )
        contenido = "Esta es la linea"
        File(temporal).writeLine("%s 1" % contenido)
        File(temporal).writeLine("%s 2" % contenido, 4)
        file_read = File(temporal)
        linea_1 = file_read.readLine()
        self.assertEqual("%s 1\n" % contenido, linea_1)
        linea_2 = file_read.readLine()
        self.assertEqual("%s" % contenido[0:4], linea_2)
        os.remove(temporal)

    def test_full_name_and_readable(self) -> None:
        """Check fullName"""

        temporal = "%s%s" % (
            config.value("ebcomportamiento/temp_dir"),
            u"/test_types_file_full_name.txt",
        )
        contenido = 'QT_TRANSLATE_NOOP("MetaData","Código")'
        file_ = File(temporal)
        file_.write(contenido)
        self.assertEqual(file_.fullName, temporal)
        self.assertTrue(file_.readable())

    def test_last_modified(self) -> None:
        """Test lastModified."""

        temporal = "%s%s" % (config.value("ebcomportamiento/temp_dir"), u"/test_last_modified.txt")
        contenido = 'QT_TRANSLATE_NOOP("MetaData","Código")'
        file_ = File(temporal)
        file_.write(contenido)
        file_.close()
        self.assertNotEqual(file_.lastModified(), "")

    def test_properties(self) -> None:
        temporal = "%s%s" % (config.value("ebcomportamiento/temp_dir"), u"/test_last_modified.txt")
        file_ = File(temporal)
        self.assertEqual(file_.path, config.value("ebcomportamiento/temp_dir"))
        self.assertEqual(file_.fullName, temporal)
        self.assertEqual(file_.extension, ".txt")
        self.assertEqual(file_.baseName, "test_last_modified")
        self.assertTrue(file_.exists)
        self.assertEqual(file_.size, 38)


class TestDir(unittest.TestCase):
    """TestDir class."""

    def test_current(self) -> None:
        """Check Dir."""

        self.assertEqual(os.curdir, Dir().current)
        self.assertEqual(os.curdir, DirStatic.current)

    def test_mkdir_rmdir(self) -> None:
        """Test mkdir and rmdir."""

        tmp_dir = config.value("ebcomportamiento/temp_dir")
        my_dir = Dir(tmp_dir)
        my_dir.mkdir("test")
        self.assertTrue(os.path.exists("%s/test" % tmp_dir))
        my_dir.rmdirs("test")
        self.assertFalse(os.path.exists("%s/test" % tmp_dir))

    def test_change_dir(self) -> None:
        """Test change dir."""

        tmp_dir = config.value("ebcomportamiento/temp_dir")
        my_dir = Dir(tmp_dir)
        original_dir = my_dir.current
        # my_dir.mkdir("test_change_dir")
        # my_dir.cd("%s/test_change_dir" % tmp_dir)
        my_dir.cd(original_dir)
        self.assertEqual(my_dir.current, original_dir)
        my_dir.cdUp()
        # self.assertEqual(os.path.realpath(my_dir.current), tmp_dir)
        # my_dir.rmdirs("test_change_dir")
        my_dir.cd(original_dir)


if __name__ == "__main__":
    unittest.main()
