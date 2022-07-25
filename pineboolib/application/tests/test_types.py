"""
Tests for application.types module.
"""

import unittest
import os
from pineboolib.loader.main import init_cli
from pineboolib.core import settings
from pineboolib.application import types


init_cli()  # FIXME: This should be avoided


class TestBoolean(unittest.TestCase):
    """Test booleans."""

    def test_true(self) -> None:
        """Test for true."""
        self.assertEqual(types.boolean(1), True)
        self.assertEqual(types.boolean("True"), True)
        self.assertEqual(types.boolean("Yes"), True)
        self.assertEqual(types.boolean(0.8), True)
        self.assertEqual(types.boolean(True), True)

    def test_false(self) -> None:
        """Test for false."""
        self.assertEqual(types.boolean(0), False)
        self.assertEqual(types.boolean("False"), False)
        self.assertEqual(types.boolean("No"), False)
        self.assertEqual(types.boolean(False), False)


class TestQString(unittest.TestCase):
    """Test QString."""

    def test_basic(self) -> None:
        """Basic testing."""
        text = types.QString("hello world")
        self.assertEqual(text, "hello world")
        self.assertEqual(text.mid(5), text[5:])
        self.assertEqual(text.mid(5, 2), text[5:7])


class TestFunction(unittest.TestCase):
    """Test function. Parses QSA into Python."""

    def test_basic(self) -> None:
        """Basic testing."""
        source = "return x + 1"
        fun_ = types.function("x", source)
        self.assertEqual(fun_(1), 2)


class TestObject(unittest.TestCase):
    """Test object."""

    def test_basic1(self) -> None:
        """Basic testing."""
        object_ = types.object_()
        object_.prop1 = 1
        object_.prop2 = 2
        self.assertEqual(object_.prop1, object_["prop1"])

    def test_basic2(self) -> None:
        """Basic testing."""
        object_ = types.object_({"prop1": 1})
        self.assertEqual(object_.prop1, object_["prop1"])


class TestArray(unittest.TestCase):
    """Test Array class."""

    def test_basic1(self) -> None:
        """Basic testing."""
        array_ = types.Array()
        array_.value = 1
        self.assertEqual(array_.value, array_["value"])

    def test_basic2(self) -> None:
        """Basic testing."""
        test_arr = [0, 1, 2, 3, 4]
        array_ = types.Array(test_arr)
        array_b = types.Array(test_arr)
        self.assertEqual(array_[3], 3)
        self.assertEqual(list(array_._dict.values()), test_arr)
        self.assertEqual(len(array_), len(test_arr))
        self.assertEqual(array_, test_arr)
        self.assertEqual(array_[3], array_b[3])
        self.assertNotEqual(array_[3], array_b[0])

        test_arr = [3, 4, 2, 1, 0]
        array_ = types.Array(test_arr)
        self.assertEqual(list(array_._dict.values()), test_arr)
        array_.append(10)
        self.assertEqual(array_[5], 10)

    def test_basic3(self) -> None:
        """Basic Testing."""
        test_arr = {"key_0": "item_0", "key_1": "item_1", "key_2": "item_2"}
        array_ = types.Array(test_arr)
        self.assertEqual(array_["key_0"], "item_0")
        self.assertEqual(array_.key_1, array_["key_1"])
        self.assertEqual(array_.length(), 3)
        self.assertEqual(array_[2], "item_2")
        self.assertEqual(list(array_._dict.values()), ["item_0", "item_1", "item_2"])

    def test_repr(self) -> None:
        """Test repr method."""
        test_arr = [3, 4, 5, 6, 7]
        array_ = types.Array(test_arr)
        self.assertEqual(repr(array_), "<Array %r>" % test_arr)

    def test_iter(self) -> None:
        """Test iterating arrays."""

        test_arr = [3, 4, 5, 6, 7]
        array_ = types.Array(test_arr)
        array_2 = [x for x in array_]
        self.assertEqual(test_arr, array_2)

        test_arr = [8, 7, 6, 4, 2]
        array_ = types.Array(test_arr)
        array_2 = [x for x in array_]
        self.assertEqual(test_arr, array_2)

    def test_splice(self) -> None:
        """Test splice."""

        test_arr = [3, 4, 5, 6, 7]
        array_ = types.Array(test_arr)
        array_.splice(1, 2)  # Delete
        self.assertEqual(str(array_), str(types.Array([4, 5])))
        array_2 = types.Array(test_arr)
        array_2.splice(2, 0, 9, 10)  # Insertion
        self.assertEqual(str(array_2), str(types.Array([3, 4, 5, 9, 10, 6, 7])))
        array_3 = types.Array(test_arr)
        array_3.splice(2, 1, 9, 10)  # Replace
        self.assertEqual(str(array_3), str(types.Array([3, 4, 9, 10, 6, 7])))

    def test_concat(self) -> None:
        """Test concat."""
        rules = [
            {"idregla": "pedidoscli", "grupo": "pedidoscli", "descripcion": "Pedidos de cliente"},
            {
                "idregla": "pedidoscli/get",
                "grupo": "pedidoscli",
                "descripcion": "Puede recibir pedidos de cliente",
            },
            {
                "idregla": "pedidoscli/post",
                "grupo": "pedidoscli",
                "descripcion": "Puede crear pedidos de cliente",
            },
            {
                "idregla": "pedidoscli/patch",
                "grupo": "pedidoscli",
                "descripcion": "Puede modificar pedidos de cliente",
            },
            {
                "idregla": "pedidoscli/delete",
                "grupo": "pedidoscli",
                "descripcion": "Puede eliminar pedidos de cliente",
            },
            {
                "idregla": "pedidoscli/accion1",
                "grupo": "pedidoscli",
                "descripcion": "Puede ejecutar la accion 1 de pedidos de cliente. Puede ejecutar la accion 1 de pedidos de cliente.",
            },
            {
                "idregla": "pedidoscli/accion2",
                "grupo": "pedidoscli",
                "descripcion": "Puede ejecutar la accion 2 de pedidos de cliente",
            },
        ]
        self.assertEqual(self.getRules(), rules)

    def getRules(self):
        from pineboolib.qsa import qsa

        result = qsa.Array().concat(
            self.getCrudRules("pedidoscli", "Pedidos de cliente"),
            qsa.Array(
                [
                    qsa.AttributeDict(
                        {
                            "idregla": ("pedidoscli/accion1"),
                            "grupo": ("pedidoscli"),
                            "descripcion": (
                                "Puede ejecutar la accion 1 de pedidos de cliente. Puede ejecutar la accion 1 de pedidos de cliente."
                            ),
                        }
                    ),
                    qsa.AttributeDict(
                        {
                            "idregla": ("pedidoscli/accion2"),
                            "grupo": ("pedidoscli"),
                            "descripcion": ("Puede ejecutar la accion 2 de pedidos de cliente"),
                        }
                    ),
                ]
            ),
        )
        return result

    def getCrudRules(self, grupo, descripcion):
        from pineboolib.qsa import qsa

        crudRules = qsa.Array(
            [
                qsa.AttributeDict({"id": ("get"), "desc": ("Puede recibir")}),
                qsa.AttributeDict({"id": ("post"), "desc": ("Puede crear")}),
                qsa.AttributeDict({"id": ("patch"), "desc": ("Puede modificar")}),
                qsa.AttributeDict({"id": ("delete"), "desc": ("Puede eliminar")}),
            ]
        )
        rules = qsa.Array(
            [
                qsa.AttributeDict(
                    {"idregla": (grupo), "grupo": (grupo), "descripcion": (descripcion)}
                )
            ]
        )

        i = 0
        while_pass = True
        while i < qsa.length(crudRules):
            if not while_pass:
                i += 1
                while_pass = True
                continue
            while_pass = False
            rules.append(
                qsa.AttributeDict(
                    {
                        "idregla": (qsa.ustr(grupo, "/", crudRules[i].id)),
                        "grupo": (grupo),
                        "descripcion": (qsa.ustr(crudRules[i].desc, " ", descripcion.lower())),
                    }
                )
            )
            i += 1
            while_pass = True
            try:
                i < qsa.length(crudRules)
            except Exception:
                break
        return rules


class TestDate(unittest.TestCase):
    """Test Date class."""

    # FIXME: Complete unit tests
    def test_basic1(self) -> None:
        """Basic testing."""
        date_ = types.Date("2001-02-25")
        self.assertEqual(date_.getDay(), 25)
        self.assertEqual(date_.getMonth(), 2)
        self.assertEqual(date_.getYear(), 2001)


class TestString(unittest.TestCase):
    """TestString class."""

    # FIXME: Complete unit tests
    def test_fromCharCode(self) -> None:
        """Test fromCharCode."""
        temp: str = types.String.fromCharCode(13, 10)
        self.assertEqual(temp, "\r\n")
        temp2: str = types.String.fromCharCode()
        self.assertEqual(temp2, "")


class TestFile(unittest.TestCase):
    """Test File class."""

    def test_write_read_values_1(self) -> None:
        """Check that you read the same as you write."""

        temporal = "%s%s" % (
            settings.CONFIG.value("ebcomportamiento/temp_dir"),
            "/test_types_file.txt",
        )
        contenido = 'QT_TRANSLATE_NOOP("MetaData","Código")'
        contenido_3 = 'QT_TRANSLATE_NOOP("MetaData","Código")'
        types.File(temporal).write(contenido)
        contenido_2 = types.File(temporal).read()
        self.assertEqual(contenido, contenido_2)
        os.remove(temporal)
        types.File(temporal).write(contenido_3)
        contenido_4 = types.File(temporal).read()
        self.assertEqual(contenido_3, contenido_4)
        os.remove(temporal)

    def test_write_read_values_2(self) -> None:
        """Check that you read the same as you write."""

        temporal = "%s%s" % (
            settings.CONFIG.value("ebcomportamiento/temp_dir"),
            "/test_types_file_static.txt",
        )
        contenido = 'QT_TRANSLATE_NOOP("MetaData","Código")'
        types.FileStatic.write(temporal, contenido)
        contenido_2 = types.FileStatic.read(temporal)
        self.assertEqual(contenido, contenido_2)
        os.remove(temporal)

    def test_write_read_bytes_1(self) -> None:
        """Check that you read the same as you write."""

        temporal = "%s%s" % (
            settings.CONFIG.value("ebcomportamiento/temp_dir"),
            "/test_types_file_bytes.txt",
        )
        contenido = "Texto escrito en bytes\n".encode("utf-8")
        types.File(temporal).write(contenido)
        contenido_2 = types.File(temporal).read(True)
        self.assertEqual(contenido, contenido_2.encode("utf-8"))
        os.remove(temporal)

    def test_write_read_byte_1(self) -> None:
        """Check that you read the same as you write."""

        temporal = "%s%s" % (
            settings.CONFIG.value("ebcomportamiento/temp_dir"),
            "/test_types_file_bytes.txt",
        )
        contenido = "Texto\n".encode("utf-8")
        types.File(temporal).write(contenido)
        contenido_2 = types.File(temporal).read(True)
        self.assertEqual(contenido, contenido_2.encode("utf-8"))
        os.remove(temporal)

    def test_write_read_line_1(self) -> None:
        """Check that you read the same as you write."""

        temporal = "%s%s" % (
            settings.CONFIG.value("ebcomportamiento/temp_dir"),
            "/test_types_file_lines.txt",
        )
        contenido = "Esta es la linea"
        types.File(temporal).writeLine("%s 1" % contenido)
        types.File(temporal).writeLine("%s 2" % contenido, 4)
        file_read = types.File(temporal)
        linea_1 = file_read.readLine()
        self.assertEqual("%s 1\n" % contenido, linea_1)
        linea_2 = file_read.readLine()
        self.assertEqual("%s" % contenido[0:4], linea_2)
        os.remove(temporal)

    def test_full_name_and_readable(self) -> None:
        """Check fullName"""

        temporal = "%s%s" % (
            settings.CONFIG.value("ebcomportamiento/temp_dir"),
            "/test_types_file_full_name.txt",
        )
        contenido = 'QT_TRANSLATE_NOOP("MetaData","Código")'
        file_ = types.File(temporal)
        file_.write(contenido)
        self.assertEqual(file_.fullName, temporal)
        self.assertTrue(file_.readable())

    def test_last_modified(self) -> None:
        """Test lastModified."""

        temporal = "%s%s" % (
            settings.CONFIG.value("ebcomportamiento/temp_dir"),
            "/test_last_modified.txt",
        )
        contenido = 'QT_TRANSLATE_NOOP("MetaData","Código")'
        file_ = types.File(temporal)
        file_.write(contenido)
        file_.close()
        self.assertNotEqual(file_.lastModified(), "")

    def test_properties(self) -> None:
        temporal = "%s%s" % (
            settings.CONFIG.value("ebcomportamiento/temp_dir"),
            "/test_last_modified.txt",
        )
        file_ = types.File(temporal)
        self.assertEqual(file_.path, settings.CONFIG.value("ebcomportamiento/temp_dir"))
        self.assertEqual(file_.fullName, temporal)
        self.assertEqual(file_.extension, ".txt")
        self.assertEqual(file_.baseName, "test_last_modified")
        self.assertTrue(file_.exists)
        self.assertEqual(file_.size, 38)


class TestDir(unittest.TestCase):
    """TestDir class."""

    def test_current(self) -> None:
        """Check Dir."""

        self.assertEqual(os.curdir, types.Dir().current)
        self.assertEqual(os.curdir, types.DirStatic.current)

    def test_mkdir_rmdir(self) -> None:
        """Test mkdir and rmdir."""

        tmp_dir = settings.CONFIG.value("ebcomportamiento/temp_dir")
        my_dir = types.Dir(tmp_dir)
        my_dir.mkdir("test")
        self.assertTrue(os.path.exists("%s/test" % tmp_dir))
        my_dir.rmdirs("test")
        self.assertFalse(os.path.exists("%s/test" % tmp_dir))

    def test_change_dir(self) -> None:
        """Test change dir."""

        tmp_dir = settings.CONFIG.value("ebcomportamiento/temp_dir")
        my_dir = types.Dir(tmp_dir)
        original_dir = my_dir.current
        # my_dir.mkdir("test_change_dir")
        # my_dir.cd("%s/test_change_dir" % tmp_dir)
        my_dir.cd(original_dir)
        self.assertEqual(my_dir.current, original_dir)
        my_dir.cdUp()
        # self.assertEqual(os.path.realpath(my_dir.current), tmp_dir)
        # my_dir.rmdirs("test_change_dir")
        my_dir.cd(original_dir)
