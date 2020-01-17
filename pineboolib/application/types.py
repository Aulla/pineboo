"""
Data Types for QSA.
"""
import codecs
import os
import os.path
import collections
from typing import Any, Optional, Dict, Union, Generator, List

from os.path import expanduser
from PyQt5 import QtCore  # type: ignore
from PyQt5.Qt import QIODevice  # type: ignore

from pineboolib.core import decorators

from pineboolib.core.utils import logging
from pineboolib.core.settings import config
from pineboolib.core.utils.utils_base import StructMyDict, filedir

from pineboolib.application.qsatypes.date import Date  # noqa: F401

logger = logging.getLogger(__name__)


def Boolean(x: Union[bool, str, float] = False) -> bool:
    """
    Return boolean from string.
    """
    if isinstance(x, bool):
        return x
    if isinstance(x, str):
        x = x.lower().strip()[0]
        if x in ["y", "t"]:
            return True
        if x in ["n", "f"]:
            return False
        raise ValueError("Cannot convert %r to Boolean" % x)
    if isinstance(x, int):
        return x != 0
    if isinstance(x, float):
        if abs(x) < 0.01:
            return False
        else:
            return True
    raise ValueError("Cannot convert %r to Boolean" % x)


class QString(str):
    """
    Emulate original QString as was removed from PyQt5.
    """

    def mid(self, start: int, length: Optional[int] = None) -> str:
        """
        Cut sub-string.

        @param start. Posición inicial
        @param length. Longitud de la cadena. Si no se especifica , es hasta el final
        @return sub cadena de texto.
        """
        if length is None:
            return self[start:]
        else:
            return self[start : start + length]

    @staticmethod
    def fromCharCode(*args: int) -> str:
        """Return a char list values."""
        ret: str = ""
        for i in args:
            ret += chr(i)

        return ret


def Function(*args: str) -> Any:
    """
    Load QS string code and create a function from it.

    Parses it to Python and return the pointer to the function.
    """

    import sys as python_sys
    import importlib

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
    from .parsers.qsaparser import flscriptparse
    from .parsers.qsaparser import postparse
    from .parsers.qsaparser.pytnyzer import write_python_file

    prog = flscriptparse.parse(qs_source)
    if prog is None:
        raise ValueError("Failed to convert to Python")
    tree_data = flscriptparse.calctree(prog, alias_mode=0)
    ast = postparse.post_parse(tree_data)
    dest_filename = "%s/anon.py" % config.value("ebcomportamiento/temp_dir")
    # f1 = io.StringIO()
    if os.path.exists(dest_filename):
        os.remove(dest_filename)

    f1 = open(dest_filename, "w", encoding="UTF-8")

    write_python_file(f1, ast)
    f1.close()
    module = None
    module_path = "tempdata.anon"

    # if module_path in python_sys.modules:
    #    print("**", module_path)
    #    module = importlib.reload(python_sys.modules[module_path])
    # else:
    spec = importlib.util.spec_from_file_location(module_path, dest_filename)  # type: ignore
    module = importlib.util.module_from_spec(spec)  # type: ignore

    python_sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    forminternalobj = getattr(module, "FormInternalObj", None)
    # os.remove(dest_filename)
    return getattr(forminternalobj(), "anon", None)


def Object(x: Optional[Dict[str, Any]] = None) -> StructMyDict:
    """
    Object type "object".
    """
    if x is None:
        x = {}

    return StructMyDict(x)


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
                for n, f in enumerate(args[0]):
                    self._dict[n] = f

            elif isinstance(args[0], dict):
                dict_ = args[0]
                for k, v in dict_.items():
                    self._dict[k] = v

            elif isinstance(args[0], int):
                return

        elif isinstance(args[0], str):
            for f in args:
                self.__setitem__(f, f)

    def __iter__(self) -> Generator[Any, None, None]:
        """
        Iterate through values.
        """
        for v in self._dict.values():
            yield v

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
        if isinstance(key, int):
            i = 0
            for k in self._dict.keys():
                if key == i:
                    return self._dict[k]
                i += 1

        elif isinstance(key, slice):
            logger.warning("FIXME: Array __getitem__%s con slice" % key)
        else:
            return self._dict[key] if key in self._dict.keys() else None

        return None

    def length(self) -> int:
        """Return array size."""
        return len(self._dict)

    def __getattr__(self, k: str) -> Any:
        """Support for attribute style access."""
        return self._dict[k]

    def __setattr__(self, k: str, val: Any) -> None:
        """Support for attribute style writes."""
        if k[0] == "_":
            return super().__setattr__(k, val)
        self._dict[k] = val

    def __eq__(self, other: Any) -> bool:
        """Support for equality comparisons."""
        if isinstance(other, Array):
            return other._dict == self._dict
        if isinstance(other, list):
            return other == list(self._dict.values())
        if isinstance(other, dict):
            return other == self._dict
        return False

    def __repr__(self) -> str:
        """Support for repr."""
        return "<%s %r>" % (self.__class__.__name__, list(self._dict.values()))

    def splice(self, *args: Any) -> None:
        """Cut or replace array."""
        if len(args) == 2:  # Delete
            pos_ini = args[0]
            length_ = args[1]
            i = 0
            x = 0
            new = {}
            for m in self._dict.keys():
                if i >= pos_ini and x < length_:
                    new[m] = self._dict[m]
                    x += 1

                i += 1

            self._dict = new

        elif len(args) > 2 and args[1] == 0:  # Insertion

            pos = 0
            new_dict = {}
            fix_pos = 0
            for pos in range(len(self._dict)):
                new_dict[fix_pos] = self._dict[pos]
                fix_pos += 1

                if pos == args[0]:
                    for i in range(2, len(args)):
                        new_dict[fix_pos] = args[i]
                        fix_pos += 1

            self._dict = new_dict

        elif len(args) > 2 and args[1] > 0:  # Replacement
            pos_ini = args[0]
            replacement_size = args[1]
            new_values = args[2:]

            i = 0
            x = 0
            new = {}
            for m in self._dict.keys():
                if i < pos_ini:
                    new[m] = self._dict[m]
                else:
                    if x < replacement_size:
                        if x == 0:
                            for n in new_values:
                                new[n] = n

                        x += 1
                    else:
                        new[m] = self._dict[m]

                i += 1

            self._dict = new

    def __len__(self) -> int:
        """Return size of array."""
        return len(self._dict)

    def __str__(self) -> str:
        """Support for str."""
        return repr(list(self._dict.values()))

    def append(self, val: Any) -> None:
        """Append new value."""
        k = len(self._dict)
        while k in self._dict:
            k += 1

        self._dict[k] = val


AttributeDict = StructMyDict


class Dir(object):
    """
    Manage folder.

    Emulates QtCore.QDir for QSA.
    """

    path: Optional[str]

    # Filters :
    Files = QtCore.QDir.Files
    Dirs = QtCore.QDir.Dirs
    NoFilter = QtCore.QDir.NoFilter

    # Sort Flags:
    Name = QtCore.QDir.Name
    NoSort = QtCore.QDir.NoSort

    # other:
    home = expanduser("~")

    def __init__(self, path: Optional[str] = None):
        """Create a new Dir."""
        self.path = path

    def entryList(self, patron: str, type_: int = NoFilter, sort: int = NoSort) -> list:
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
        except Exception as e:
            print("Dir_Class.entryList:", e)

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
    @decorators.Deprecated
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
        os.chdir(val or filedir("."))

    def getCurrent(self) -> str:
        """Return current folder."""
        return os.curdir

    def set_current(self, new_path: Optional[str] = None) -> None:
        """Set new patch."""
        os.chdir(new_path or filedir("."))

    def mkdir(self, name: Optional[str] = None) -> None:
        """
        Create a new folder.

        @param name. Nombre de la ruta a crear
        """
        if name is None:
            name = ""

            if self.path is None:
                raise ValueError("self.path is not defined!")

        if self.path:
            name_ = self.path + "/" + name
        else:
            name_ = name
        try:
            os.stat(name_)
        except Exception:
            os.mkdir(name_)

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

        name_ = self.path + "/" + name

        if os.path.exists(name_):
            import shutil

            shutil.rmtree(name_)

    current = property(getCurrent, set_current)


DirStatic = Dir()


class FileBaseClass(object):
    """
    Constants for File and FileStatic.
    """

    ReadOnly = QIODevice.ReadOnly
    WriteOnly = QIODevice.WriteOnly
    ReadWrite = QIODevice.ReadWrite
    Append = QIODevice.Append
    ioDevice = QIODevice

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
    _mode: QIODevice

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

    def open(self, m: QIODevice) -> bool:
        """Open file."""

        self._mode = m
        self.eof = False
        if self._q_file is not None:
            self._q_file.open(self._mode)

        return True

    def ioDevice(self) -> QIODevice:
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
        file_: str
        encode: str

        if not self._file_name:
            raise ValueError("self._file_name is not defined!")

        file_ = self._file_name
        encode = self._encode
        import codecs

        if file_ is None:
            raise ValueError("file is empty!")

        f = codecs.open(file_, "r" if not bytes else "rb", encoding=encode)
        ret = ""
        for l in f:
            ret = ret + l

        f.close()
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
        file_: str = self._file_name
        encode: str = self._encode

        if isinstance(data, str):
            bytes_ = data.encode(encode)
        else:
            bytes_ = data

        mode = "ab" if self._mode == self.Append else "wb"
        with open(file_, mode) as file:
            file.write(bytes_)

        file.close()

    def writeBlock(self, bytes_array: bytes) -> None:
        """Write a block of data to the file."""
        if not self._file_name:
            raise ValueError("self._file_name is empty!")

        with open(self._file_name, "wb") as file:
            file.write(bytes_array)

        file.close()

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

        f = codecs.open(self._file_name, encoding=self._encode, mode="a")
        f.write("%s\n" % data if len is None else data[0:len])
        f.close()

    def readLine(self) -> str:
        """
        Read a line from file.

        @return cadena de texto con los datos de la linea actual
        """

        import codecs

        if not self._file_name:
            raise ValueError("self._file_name is empty!")

        f = codecs.open(self._file_name, "r", encoding=self._encode)
        f.seek(self._last_seek)
        ret = f.readline(self._last_seek)
        self._last_seek += len(ret)
        self.eof = True if ret else False

        f.close()

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

        f = codecs.open(self._file_name, encoding=self._encode, mode="a")
        f.seek(self._last_seek)
        ret = f.readlines()
        f.close()
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

        f = open(self._file_name, "wb")
        f.write(data_b)
        f.close()

    def readByte(self) -> bytes:
        """Read a byte from file."""
        if not self.eof:
            with open(self._file_name, "rb") as f:
                f.seek(self._last_seek)
                self._last_seek += 1
                ret = f.read(1)
                self.eof = True if not ret else False
                return ret

        return b""

    def writeByte(self, b: bytes) -> None:
        """Write a byte to file."""
        with open(self._file_name, "wb") as f:
            f.seek(self._last_seek)
            self._last_seek += 1
            f.write(b)

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

        return os.path.dirname(self._file_name)

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

        with codecs.open(file_, "r" if not bytes else "rb", encoding="ISO-8859-15") as f:
            ret = f.read()

        return ret

    @staticmethod
    def write(file_: str, data: Union[str, bytes], length: int = -1) -> None:
        """
        Write data back to the file.

        @param data. Valores a guardar en el fichero
        @param length. Tamaño de data. (No se usa)
        """
        if isinstance(data, str):
            bytes_ = data.encode("ISO-8859-15")
        else:
            bytes_ = data

        with open(file_, "wb") as file:
            file.write(bytes_)

        file.close()
