"""
Data Types for QSA.
"""
import codecs

import os
import collections


from PyQt6 import QtCore  # type: ignore [import]

from pineboolib.core.utils import utils_base
from pineboolib.core import decorators, settings

from pineboolib.application.qsatypes.date import Date  # noqa: F401

from .. import logging

from typing import Any, Optional, Dict, Union, Generator, List, TYPE_CHECKING

if TYPE_CHECKING:
    from importlib.machinery import ModuleSpec

LOGGER = logging.get_logger(__name__)


def boolean(value: Union[bool, str, float] = False) -> bool:
    """
    Return boolean from string.
    """
    if isinstance(value, bool):
        return value
    elif isinstance(value, str):
        value = value.lower().strip()[0]
        if value in ["y", "t"]:
            return True
        if value in ["n", "f"]:
            return False
        raise ValueError("Cannot convert %r to Boolean" % value)
    elif isinstance(value, int):
        return value != 0
    elif isinstance(value, float):
        if abs(value) < 0.01:
            return False
        else:
            return True
    else:
        raise ValueError("Cannot convert %r to Boolean" % value)


class QString(str):
    """
    Emulate original QString as was removed from PyQt6.
    """

    def mid(self, start: int, length: int = 0) -> str:
        """
        Cut sub-string.

        @param start. Posición inicial
        @param length. Longitud de la cadena. Si no se especifica , es hasta el final
        @return sub cadena de texto.
        """

        return self[start:] if not length else self[start : start + length]

    @staticmethod
    def fromCharCode(*args: int) -> str:
        """Return a char list values."""

        return "".join([chr(val) for val in args])


def function(*args: str) -> Any:
    """
    Load QS string code and create a function from it.

    Parses it to Python and return the pointer to the function.
    """

    import sys as python_sys

    # Leer código QS embebido en Source
    # asumir que es una funcion anónima, tal que:
    #  -> function($args) { source }
    # compilar la funcion y devolver el puntero
    arguments = args[: len(args) - 1]
    source = args[len(args) - 1]
    qs_source = """

function anon(%s) {
    %s
} """ % (
        ", ".join(arguments),
        source,
    )

    # print("Compilando QS en línea: ", qs_source)
    from .parsers.parser_qsa import flscriptparse, postparse, pytnyzer
    from importlib import util

    module_name = "anon_%s" % QtCore.QDateTime.currentDateTime().toString("ddMMyyyyhhmmsszzz")

    prog = flscriptparse.parse(qs_source)
    if prog is None:
        raise ValueError("Failed to convert to Python")
    tree_data = flscriptparse.calctree(prog, alias_mode=0)
    ast = postparse.post_parse(tree_data)
    dest_filename = "%s/%s.py" % (
        settings.CONFIG.value("ebcomportamiento/temp_dir"),
        module_name,
    )
    # f1 = io.StringIO()
    if os.path.exists(dest_filename):
        os.remove(dest_filename)

    file_ = open(dest_filename, "w", encoding="UTF-8")

    pytnyzer.write_python_file(file_, ast)
    file_.close()
    module = None
    module_path = "tempdata.%s" % (module_name)

    spec: Optional["ModuleSpec"] = util.spec_from_file_location(module_path, dest_filename)
    if spec and spec.loader is not None:
        module = util.module_from_spec(spec)
        python_sys.modules[spec.name] = module
        spec.loader.exec_module(module)  # type: ignore [attr-defined]
    else:
        raise Exception("Module named %s can't be loaded from %s" % (module_path, dest_filename))

    forminternalobj = getattr(module, "FormInternalObj", None)
    # os.remove(dest_filename)
    return getattr(forminternalobj(), "anon", None)


def object_(value: Optional[Dict[str, Any]] = None) -> "utils_base.StructMyDict":
    """
    Object type "object".
    """
    return utils_base.StructMyDict(value or {})


String = QString


class Array(object):
    """
    Array type object.
    """

    # NOTE: To avoid infinite recursion on getattr/setattr, all attributes MUST be defined at class-level.
    _dict: Dict[Any, Any] = {}
    _pos_iter = 0

    def __init__(self, *args: Any) -> None:
        """Create new array."""
        self._pos_iter = 0
        self._dict = collections.OrderedDict()

        if not len(args):
            return
        elif len(args) == 1:
            if isinstance(args[0], list):
                for key, value in enumerate(args[0]):
                    self._dict[key] = value

            elif isinstance(args[0], dict):
                for key, value in args[0].items():
                    self._dict[key] = value

            elif isinstance(args[0], int):
                return

        elif isinstance(args[0], str):
            for item in args:
                self.__setitem__(item, item)

    def __iter__(self) -> Generator[Any, None, None]:
        """
        Iterate through values.
        """
        for value in self._dict.values():
            yield value

    def __setitem__(self, key: Union[str, int], value: Any) -> None:
        """
        Set item.

        @param key. Nombre del registro
        @param value. Valor del registro
        """
        # field_key = key
        # while field_key in self.dict_.keys():
        #    field_key = "%s_bis" % field_key
        self._dict[key] = value

    def __getitem__(self, key: Union[str, int, slice]) -> Any:
        """
        Get item.

        @param key. Valor que idenfica el registro a recoger
        @return Valor del registro especificado
        """
        result = None
        if isinstance(key, int):
            try:
                result = list(self._dict.values())[key]
            except Exception:
                pass

        elif isinstance(key, slice):
            LOGGER.warning("FIXME: Array __getitem__%s con slice" % key)
        else:
            try:
                result = self._dict[key]
            except Exception:
                pass

        return result

    def length(self) -> int:
        """Return array size."""
        return len(self._dict)

    def __getattr__(self, value: str) -> Any:
        """Support for attribute style access."""
        return self._dict[value] if value in self._dict.keys() else None

    def __setattr__(self, name: str, value: Any) -> None:
        """Support for attribute style writes."""
        if name[0] == "_":
            return super().__setattr__(name, value)
        self._dict[name] = value

    def __eq__(self, other: Any) -> bool:
        """Support for equality comparisons."""
        if isinstance(other, Array):
            return other._dict == self._dict
        elif isinstance(other, list):
            return other == list(self._dict.values())
        elif isinstance(other, dict):
            return other == self._dict
        return False

    def __repr__(self) -> str:
        """Support for repr."""
        return "<%s %r>" % (self.__class__.__name__, list(self._dict.values()))

    def splice(self, *args: Any) -> None:
        """Cut or replace array."""
        new_dict = {}

        if len(args) == 2:  # Delete

            for key in list(self._dict.keys())[args[0] : args[0] + args[1]]:
                new_dict[key] = self._dict[key]

        elif len(args) > 2 and args[1] == 0:  # Insertion

            fix_pos = 0
            for pos in range(len(self._dict.keys())):
                new_dict[pos + fix_pos] = self._dict[pos]
                if pos == args[0]:
                    for new_value in args[2:]:
                        fix_pos += 1
                        new_dict[pos + fix_pos] = new_value

        elif len(args) > 2 and args[1] > 0:  # Replacement

            for pos, key in enumerate(self._dict.keys()):
                if pos == args[0]:
                    for new_value in args[2:]:
                        new_dict[new_value] = new_value
                else:
                    if pos < args[0] or pos >= args[0] + args[1]:
                        new_dict[key] = self._dict[key]

        self._dict = new_dict

    def __len__(self) -> int:
        """Return size of array."""
        return len(self._dict.keys())

    def __str__(self) -> str:
        """Support for str."""
        return repr(list(self._dict.values()))

    def append(self, value: Any) -> None:
        """Append new value."""
        size = len(self._dict.keys())
        while size in self._dict:
            size += 1
        self._dict[size] = value

    def shift(self) -> Any:
        """Shifts (i.e. removes) the bottom-most (left-most) item off the array and returns it."""
        return self.pop(0)

    def pop(self, position: int = 0) -> Any:
        """Return a position value and delte it from list."""

        value = self._dict[position]
        self._dict[position] = None
        del self._dict[position]

        return value

    def concat(
        self, *args: Union[List[Any], Dict[str, Any], "Array"]
    ) -> Union[List[Any], Dict[str, Any]]:
        """Return arrays concatenated."""

        if len(args) > 1 and isinstance(args[1], (list, Array)):
            result_list: List[Any] = []
            for item in args:
                result_list += item

            return result_list
        elif len(args) == 1 and isinstance(args[0], (list, Array)):
            for item in args[0]:
                self.append(item)
            return self  # type: ignore [return-value]

        else:
            result_array: Dict[str, Any] = {}
            for item in args:
                for key, value in item.items():  # type: ignore [union-attr]
                    result_array[key] = value

            return result_array


AttributeDict = utils_base.StructMyDict


class Dir(object):
    """
    Manage folder.

    Emulates QtCore.QDir for QSA.
    """

    path: Optional[str]

    # Filters :
    Files = QtCore.QDir.Filter.Files
    Dirs = QtCore.QDir.Filter.Dirs
    NoFilter = QtCore.QDir.Filter.NoFilter

    # Sort Flags:
    Name = QtCore.QDir.SortFlag.Name
    NoSort = QtCore.QDir.SortFlag.NoSort

    # other:
    home = os.path.expanduser("~")

    def __init__(self, path: Optional[str] = None):
        """Create a new Dir."""
        self.path = path

    def entryList(
        self,
        patron: str,
        type_: "QtCore.QDir.Filter" = QtCore.QDir.Filter.NoFilter,
        sort: "QtCore.QDir.SortFlag" = QtCore.QDir.SortFlag.NoSort,
    ) -> list:
        """
        Create listing for files inside given folder.

        @param patron. Patron a usa para identificar los ficheros
        @return lista con los ficheros que coinciden con el patrón
        """
        # p = os.walk(self.path)
        retorno: List[str] = []
        try:
            import fnmatch

            if self.path is None:
                raise ValueError("self.path is not defined!")

            if os.path.exists(self.path):
                for file in os.listdir(self.path):
                    if fnmatch.fnmatch(file, patron):
                        retorno.append(file)
        except Exception as exception:
            print("Dir_Class.entryList:", exception)

        return retorno

    @staticmethod
    def fileExists(file_name: str) -> bool:
        """
        Check if a file does exist.

        @param file_name. Nombre del fichero
        @return Boolean. Si existe el ficehro o no.
        """
        return os.path.exists(file_name)

    @staticmethod
    def cleanDirPath(name: str) -> str:
        """
        Clean path from unnecesary folders.
        """
        return os.path.normpath(name)

    @staticmethod
    @decorators.deprecated
    def convertSeparators(filename: str) -> str:
        """
        Convert path from backslash to slashes or viceversa.

        ***DEPRECATED***
        """
        return filename

    @staticmethod
    def setCurrent(val: Optional[str] = None) -> None:
        """
        Change current working folder.

        @param val. Ruta especificada
        """
        os.chdir(val or utils_base.filedir("."))

    def getCurrent(self) -> str:
        """Return current folder."""
        return os.curdir

    def set_current(self, new_path: Optional[str] = None) -> None:
        """Set new patch."""
        os.chdir(new_path or utils_base.filedir("."))

    def mkdir(self, name: str = "") -> None:
        """
        Create a new folder.

        @param name. Nombre de la ruta a crear
        """
        if not name and self.path is None:
            raise ValueError("self.path is not defined!")

        if self.path:
            name = self.path + "/" + name

        try:
            os.stat(name)
        except Exception:
            os.mkdir(name)

    def cd(self, path: str) -> None:
        """Change dir."""

        os.chdir(path)

    def cdUp(self) -> None:
        """Change directory by moving one directory up from the Dir's current directory if possible."""

        os.chdir("..")

    def rmdirs(self, name: Optional[str] = None) -> None:
        """Delete a folder."""

        if name is None:
            raise ValueError("name is not defined!")

        if self.path is None:
            raise ValueError("self.path is not defined!")

        path_ = os.path.join(self.path, name)

        if os.path.exists(path_):
            import shutil

            shutil.rmtree(path_)

    current = property(getCurrent, set_current)


DirStatic = Dir()


class FileBaseClass(object):
    """
    Constants for File and FileStatic.
    """

    ReadOnly = QtCore.QIODevice.OpenModeFlag.ReadOnly
    WriteOnly = QtCore.QIODevice.OpenModeFlag.WriteOnly
    ReadWrite = QtCore.QIODevice.OpenModeFlag.ReadWrite
    Append = QtCore.QIODevice.OpenModeFlag.Append
    ioDevice = QtCore.QIODevice

    @staticmethod
    def exists(name: str) -> bool:
        """
        Check if a file does exist.

        @param name. Nombre del fichero.
        @return boolean informando si existe o no el fichero.
        """
        return os.path.exists(name)

    @staticmethod
    def isDir(dir_name: str) -> bool:
        """
        Check if given path is a folder.

        @param. Nombre del directorio
        @return. boolean informando si la ruta dada es un directorio o no.
        """
        return os.path.isdir(dir_name)

    @staticmethod
    def isFile(file_name: str) -> bool:
        """
        Check if given path is a file.

        @param. Nombre del fichero
        @return. boolean informando si la ruta dada es un fichero o no.
        """
        return os.path.isfile(file_name)


class File(FileBaseClass):  # FIXME : Rehacer!!
    """
    Manage a file.
    """

    _file_name: str
    _mode: "QtCore.QIODevice.OpenModeFlag"

    _encode: str
    _last_seek: int
    _q_file: QtCore.QFile
    eof: bool

    def __init__(self, file_path: Optional[str] = None, encode: Optional[str] = None):
        """Create a new File Object. This does not create a file on disk."""

        self._encode = "iso-8859-15"
        self._last_seek = 0
        self._file_name = ""
        self.eof = False

        if file_path is not None:
            self._q_file = QtCore.QFile(file_path)
            file_name, extension = os.path.splitext(file_path)
            self._file_name = "%s%s" % (file_name, extension)

        if encode is not None:
            self._encode = encode

        self._mode = self.ReadWrite

    def open(self, mode: "QtCore.QIODevice.OpenModeFlag") -> bool:
        """Open file."""

        self._mode = mode
        self.eof = False
        if self._q_file is not None:
            self._q_file.open(self._mode)

        return True

    def ioDevice(self) -> "QtCore.QIODevice":  # type: ignore [override] # noqa: F821
        """Return ioDevice mode."""
        return self._q_file

    def close(self) -> None:
        """Close file."""
        if self._q_file is not None:
            self._q_file.close()

    def errorString(self) -> str:
        """Return error string."""
        return self._q_file.errorString()

    def read(self, bytes: bool = False) -> str:
        """
        Read file completely.

        @param bytes. Especifica si se lee en modo texto o en bytes
        @retunr contenido del fichero
        """

        if not self._file_name:
            raise ValueError("self._file_name is not defined!")

        file_ = codecs.open(self._file_name, "r" if not bytes else "rb", encoding=self._encode)
        ret = file_.read()
        file_.close()
        self.eof = True
        return ret

    def readAll(self) -> str:
        """Read file completely."""
        return self.read()

    def write(self, data: Union[str, bytes], length: int = -1) -> None:
        """
        Write data back to the file.

        @param data. Valores a guardar en el fichero
        @param length. Tamaño de data. (No se usa)
        """
        if not self._file_name:
            raise ValueError("self._file_name is empty!")

        mode = "a" if self._mode == self.Append else "w"

        if not isinstance(data, str):
            data = data.decode(self._encode)

        file_ = codecs.open(self._file_name, mode, encoding=self._encode, errors="replace")
        file_.write(data)
        file_.close()

    def writeBlock(self, data: bytes) -> None:
        """Write a block of data to the file."""
        if not self._file_name:
            raise ValueError("self._file_name is empty!")

        data_string = data.decode(self._encode)

        file_ = codecs.open(self._file_name, "w", encoding=self._encode, errors="replace")
        file_.write(data_string)
        file_.close()

    def getName(self) -> str:
        """
        Get file name.

        @return Nombre del _file_name
        """
        if not self._file_name:
            raise ValueError("self._file_name is empty!")

        _path, file_name = os.path.split(self._file_name)
        return file_name

    def getBaseName(self) -> str:
        """Return baseName."""

        if not self._file_name:
            raise ValueError("self._file_name is empty!")

        return os.path.basename(self._file_name.split(".")[0])

    def getExtension(self) -> str:
        """Return extension."""
        if not self._file_name:
            raise ValueError("self._file_name is empty!")

        return os.path.splitext(self._file_name)[1]

    def writeLine(self, data: str, len: Optional[int] = None) -> None:
        """
        Write a new line with "data" contents into the file.

        @param data. Datos a añadir en el _file_name
        """
        import codecs

        if not self._file_name:
            raise ValueError("self._file_name is empty!")

        file_ = codecs.open(self._file_name, encoding=self._encode, mode="a")
        file_.write("%s\n" % data if len is None else data[0:len])
        file_.close()

    def readLine(self) -> str:
        """
        Read a line from file.

        @return cadena de texto con los datos de la linea actual
        """

        import codecs

        if not self._file_name:
            raise ValueError("self._file_name is empty!")

        file_ = codecs.open(self._file_name, "r", encoding=self._encode)
        file_.seek(self._last_seek)
        ret = file_.readline(self._last_seek)
        self._last_seek += len(ret)
        self.eof = True if ret else False

        file_.close()

        return ret

    def readLines(self) -> List[str]:
        """
        Read all lines from a file and return it as array.

        @return array con las lineas del _file_name.
        """

        if not self._file_name:
            raise ValueError("self._file_name is empty!")

        ret: List[str]
        import codecs

        file_ = codecs.open(self._file_name, encoding=self._encode, mode="a")
        file_.seek(self._last_seek)
        ret = file_.readlines()
        file_.close()
        return ret

    def readbytes(self) -> bytes:
        """
        Read the whole file as binary.

        @return bytess con los datos de la linea actual
        """
        ret_ = self.read(True)

        return ret_.encode(self._encode)

    def writebytes(self, data_b: bytes) -> None:
        """
        Write file as binary.

        @param data_b. Datos a añadir en el _file_name
        """
        if not self._file_name:
            raise ValueError("self._file_name is empty!")

        file_ = open(self._file_name, "wb")
        file_.write(data_b)
        file_.close()

    def readByte(self) -> bytes:
        """Read a byte from file."""
        if not self.eof:
            with open(self._file_name, "rb") as file_:
                file_.seek(self._last_seek)
                self._last_seek += 1
                ret = file_.read(1)
                self.eof = True if not ret else False
                return ret

        return b""

    def writeByte(self, data: bytes) -> None:
        """Write a byte to file."""
        with open(self._file_name, "wb") as file_:
            file_.seek(self._last_seek)
            self._last_seek += 1
            file_.write(data)

    def remove(self) -> bool:
        """
        Delete file from filesystem.

        @return Boolean . True si se ha borrado el _file_name, si no False.
        """
        return self._q_file.remove()

    def getFullName(self) -> str:
        """Return full name."""
        return self._file_name or ""

    def getSize(self) -> int:
        """Return file size."""

        return self._q_file.size()

    def getPath(self) -> str:
        """Return getPath."""

        return os.path.abspath(os.path.dirname(self._file_name))

    def readable(self) -> bool:
        """Return if file is readable."""

        return os.access(self._file_name or "", os.R_OK)

    def lastModified(self) -> str:
        """Return last modified date."""

        return QtCore.QFileInfo(self._q_file).lastModified().toString("yyyy-MM-dd-hh:mm:ss")

    def exists(self) -> bool:  # type: ignore [override] # noqa: F821
        """Return True if exists a file else False."""

        return self._q_file.exists()

    name = property(getName)
    path = property(getPath)
    fullName = property(getFullName)
    baseName = property(getBaseName)
    extension = property(getExtension)
    size = property(getSize)


class FileStatic(FileBaseClass):
    """
    Static methods for File that overlap in name.
    """

    @staticmethod
    def remove(file_name: str) -> bool:
        """
        Delete file from filesystem.

        @return Boolean . True si se ha borrado el fichero, si no False.
        """
        file = File(file_name)
        return file.remove()

    @staticmethod
    def read(file_: str, bytes: bool = False) -> str:
        """
        Read file completely.

        @param bytes. Especifica si se lee en modo texto o en bytes
        @return contenido del fichero
        """

        with codecs.open(file_, "r" if not bytes else "rb", encoding="ISO-8859-15") as file_obj:
            ret = file_obj.read()

        return ret

    @staticmethod
    def write(file_: str, data: Union[str, bytes], length: int = -1) -> None:
        """
        Write data back to the file.

        @param data. Valores a guardar en el fichero
        @param length. Tamaño de data. (No se usa)
        """

        bytes_ = data.encode("ISO-8859-15") if isinstance(data, str) else data

        with open(file_, "wb") as file:
            file.write(bytes_)

        file.close()
