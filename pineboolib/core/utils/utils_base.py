# -*- coding: utf-8 -*-
"""
Collection of utility functions.

Just an assortment of functions that don't depend on externals and don't fit other modules.
"""


from PyQt6 import QtCore, QtXml, QtWidgets  # type: ignore[import]

from . import logging
from .. import settings

import os
import re
import sys
import io
import os.path
import hashlib
import traceback
import types
import threading
import time

from typing import Optional, Union, Any, List, cast, Callable, TypeVar, TYPE_CHECKING

from xml.etree import ElementTree

if TYPE_CHECKING:
    from pineboolib.application.qsatypes.date import Date  # noqa: F401 # pragma: no cover

LOGGER = logging.get_logger(__name__)
T1 = TypeVar("T1")

# FIXME: Move commaSeparator to Pineboo internals, not aqApp
DECIMAL_SEPARATOR = (
    "," if QtCore.QLocale.system().toString(float(0.01), "f", 2).find(",") > -1 else "."
)

BASE_DIR = None
FORCE_DESKTOP = False

SHOWED_FORCE_DESKTOP_WARNING = False


def auto_qt_translate_text(text: Optional[str]) -> str:
    """Remove QT_TRANSLATE from Eneboo XML files. This function does not translate."""
    if not isinstance(text, str):
        text = str(text)

    if isinstance(text, str):
        if text.find("QT_TRANSLATE") != -1:
            match = re.search(r"""QT_TRANSLATE\w*\(.+,["'](.+)["']\)""", text)
            text = match.group(1) if match else ""

    return text


def qt_translate_noop(string: str, path: str, mod: str) -> str:
    """Translate string."""

    if string.find("QT_TRANSLATE_NOOP") == -1:
        return string
    string_list = string[18:-1].split(",")
    string = string_list[1][1:-1]

    nombre_fichero = os.path.join(
        path, "translations", "%s.%s.ts" % (mod, QtCore.QLocale().name()[:2])
    )
    if not os.path.exists(nombre_fichero):
        LOGGER.debug("flreloadlast.traducirCadena: No se encuentra el fichero %s" % nombre_fichero)
        return string

    fichero = open(nombre_fichero, "r", encoding="ISO-8859-15")
    file_data = fichero.read()
    xml_translations = QtXml.QDomDocument()
    if xml_translations.setContent(file_data):
        node_mess = xml_translations.elementsByTagName("message")
        for node_number in range(len(node_mess)):
            node = node_mess.item(node_number)
            if node.namedItem("source").toElement().text() == string:
                traduccion = node.namedItem("translation").toElement().text()
                if traduccion:
                    return traduccion

    return string


AQTT = auto_qt_translate_text


def one(list_: List[T1], default: Any = None) -> Optional[T1]:
    """
    Retrieve first element of the list or None/default.

    Useful to avoid try/except cluttering and clean code.
    """
    try:
        return list_[0]
    except IndexError:
        return default


def traceit(
    frame: types.FrameType, event: str, arg: Any  # pylint: disable=unused-argument
) -> Callable[[types.FrameType, str, Any], Any]:
    """
    Print a trace line for each Python line executed or call.

    This function is intended to be the callback of sys.settrace.
    """

    # if event != "line":
    #    return traceit
    try:
        import linecache

        lineno = frame.f_lineno
        filename = frame.f_globals["__file__"]
        # if "pineboo" not in filename:
        #     return traceit
        if filename.endswith(".pyc") or filename.endswith(".pyo"):
            filename = filename[:-1]
        name = frame.f_globals["__name__"]
        line = linecache.getline(filename, lineno)
        print("%s:%s:%s %s" % (name, lineno, event, line.rstrip()))
    except Exception:
        pass
    return traceit


class TraceBlock:
    """
    With Decorator to add traces on a particular block.

    Use it like:

    with TraceBlock():
        code
    """

    def __enter__(self) -> Callable[[types.FrameType, str, Any], Any]:
        """Create tracing context on enter."""
        # NOTE: "sys.systrace" function could lead to arbitrary code execution
        sys.settrace(traceit)  # noqa: DUO111
        return traceit

    def __exit__(self, type: Any, value: Any, traceback: Any) -> None:
        """Remove tracing context on exit."""
        # NOTE: "sys.systrace" function could lead to arbitrary code execution
        sys.settrace(None)  # noqa: DUO111


def trace_function(func_: Callable) -> Callable:
    """Add tracing to decorated function."""

    def wrapper(*args: Any) -> Any:
        with TraceBlock():
            return func_(*args)

    return wrapper


def copy_dir_recursive(from_dir: str, to_dir: str, replace_on_conflict: bool = False) -> bool:
    """
    Copy a folder recursively.

    *** DEPRECATED ***
    Use python shutil.copytree for this.
    """
    dir = QtCore.QDir()
    dir.setPath(from_dir)

    from_dir += QtCore.QDir.separator()
    to_dir += QtCore.QDir.separator()

    if not os.path.exists(to_dir):
        os.makedirs(to_dir)

    for file_ in dir.entryList(QtCore.QDir.Filter.Files):
        from_ = from_dir + file_
        to_ = to_dir + file_
        if str(to_).endswith(".src"):
            to_ = str(to_).replace(".src", "")
            # print("Destino", to_)

        if os.path.exists(to_):
            if replace_on_conflict:
                os.remove(to_)
            else:
                continue

        if not QtCore.QFile.copy(from_, to_):
            return False

    for dir_ in dir.entryList(
        cast(QtCore.QDir.Filter, QtCore.QDir.Filter.Dirs | QtCore.QDir.Filter.NoDotAndDotDot)
    ):
        from_ = from_dir + dir_
        to_ = to_dir + dir_

        if not os.path.exists(to_):
            os.makedirs(to_)

        if not copy_dir_recursive(from_, to_, replace_on_conflict):
            return False

    return True


def text2bool(text: str) -> bool:
    """Convert input text into boolean, if possible."""

    if str(text).lower().startswith(("t", "y", "1", "on", "s")):
        return True
    elif str(text).lower().startswith(("f", "n", "0", "off")):
        return False

    raise ValueError("Valor booleano no comprendido '%s'" % text)


def ustr(*full_text: Union[bytes, str, int, "Date", None, float]) -> str:
    """Convert and concatenate types to text."""

    def ustr1(text_: Union[bytes, str, int, "Date", None, float]) -> str:

        if isinstance(text_, str):
            return text_

        elif isinstance(text_, float):
            t_float = text_
            try:
                text_ = int(text_)

                if not t_float == text_:
                    text_ = str(t_float)

            except Exception:
                pass

            return str(text_)

        elif isinstance(text_, bytes):
            return str(text_, "UTF-8")

        else:
            return repr("" if text_ is None else text_)

    return "".join([ustr1(text) for text in full_text])


class StructMyDict(dict):
    """Dictionary that can be read/written using properties."""

    def __getattr__(self, name: str) -> Any:
        """Get property."""
        try:
            return self[name]
        except KeyError as error:
            raise AttributeError(error)

    def __setattr__(self, name: str, value: Any) -> None:
        """Set property."""
        self[name] = value


def load2xml(form_path_or_str: str) -> ElementTree.ElementTree:
    """Parse a Eneboo style XML."""

    """
    class xml_parser(ET.TreeBuilder):


        def start(self, tag, attrs):
            return super(xml_parser, self).start(tag, attrs)

        def end(self, tag):
            return super(xml_parser, self).end(tag)

        def data(self, data):
            super(xml_parser, self).data(data)

        def close(self):
            return super(xml_parser, self).close()
    """

    file_ptr: Optional[io.StringIO] = None
    if form_path_or_str.find("KugarTemplate") > -1 or form_path_or_str.find("DOCTYPE") > -1:
        form_path_or_str = _parse_for_duplicates(form_path_or_str)
        file_ptr = io.StringIO(form_path_or_str)
    elif not os.path.exists(form_path_or_str):
        raise Exception("File %s not found" % form_path_or_str[:200])

    try:
        parser = ElementTree.XMLParser()
        return ElementTree.parse(file_ptr or form_path_or_str, parser)
    except Exception:
        try:
            parser = ElementTree.XMLParser(encoding="ISO-8859-15")
            return ElementTree.parse(file_ptr or form_path_or_str, parser)
        except Exception:
            LOGGER.exception(
                "Error cargando UI después de intentar con UTF8 e ISO \n%s", form_path_or_str
            )
            raise


def _parse_for_duplicates(text: str) -> str:
    """load2xml helper for Kugar XML."""
    ret_ = ""
    text = text.replace("+", "__PLUS__")
    text = text.replace("(", "__LPAREN__")
    text = text.replace(")", "__RPAREN__")
    text = text.replace("*", "__ASTERISK__")

    for section_orig in text.split(">"):
        # print("section", section)
        duplicate_ = False
        attr_list: List[str] = []

        # print("--->", section_orig)
        ret2_ = ""
        section = ""
        for action in section_orig.split(" "):

            count_ = action.count("=")
            if count_ > 1:
                # part_ = ""
                text_to_process = action
                for item in range(count_):
                    pos_ini = text_to_process.find('"')
                    pos_fin = text_to_process[pos_ini + 1 :].find('"')
                    # print("Duplicado", item, pos_ini, pos_fin, text_to_process, "***" , text_to_process[0:pos_ini + 2 + pos_fin])
                    ret2_ += " %s " % text_to_process[0 : pos_ini + 2 + pos_fin]
                    text_to_process = text_to_process[pos_ini + 2 + pos_fin :]

            else:
                ret2_ += "%s " % action

        section += ret2_
        if section.endswith(" "):
            section = section[0 : len(section) - 1]

        if section_orig.endswith("/") and not section.endswith("/"):
            section += "/"

        # print("***", section)
        section = section.replace(" =", "=")
        section = section.replace('= "', '="')

        for attribute_ in section.split(" "):

            # print("attribute", attribute_)
            if attribute_.find("=") > -1:
                attr_name = attribute_[0 : attribute_.find("=")]
                if attr_name not in attr_list:
                    attr_list.append(attr_name)
                else:
                    if attr_name != "":
                        # print("Eliminado attributo duplicado", attr_name)
                        duplicate_ = True

            if not duplicate_:
                if not section.endswith(attribute_):
                    ret_ += "%s " % attribute_
                else:
                    ret_ += "%s" % attribute_
            else:
                if attribute_.endswith("/"):
                    ret_ += "/"

            duplicate_ = False

        if (section.find(">") == -1 and section.find("<") > -1) or section.endswith("--"):
            ret_ += ">"

    # print(ret_)
    return ret_


def pretty_print_xml(elem: ElementTree.Element, level: int = 0) -> None:
    """
    Generate pretty-printed version of given XML.

    copy and paste from http://effbot.org/zone/element-lib.htm#prettyprint
    it basically walks your tree and adds spaces and newlines so the tree is
    printed in a nice way
    """
    lev_ = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = lev_ + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = lev_
        for elem in elem:
            pretty_print_xml(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = lev_
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = lev_


def format_double(value: Union[int, str, float], part_integer: int, part_decimal: int = 0) -> str:
    """Convert number into string with fixed point style."""
    if isinstance(value, str) and value == "":
        return value

    value_array = str(round(float(str(value)), part_decimal)).split(".")

    str_integer = format_int(value_array[0], part_integer)
    str_decimal = value_array[1] if len(value_array) > 1 and part_decimal else ""

    while part_decimal > len(str_decimal):
        str_decimal += "0"

    # Fixme: Que pasa cuando la parte entera sobrepasa el limite, se coge el maximo valor o
    return "%s%s%s" % (str_integer, DECIMAL_SEPARATOR if str_decimal else "", str_decimal)


def format_int(value: Union[str, int, float, None], part_integer: int = 0) -> str:
    """Convert integer into string."""
    if value is not None:
        str_integer = "{:,d}".format(int(value))
        value = str_integer.replace(DECIMAL_SEPARATOR, "," if DECIMAL_SEPARATOR == "," else ".")
        len_value = len(value)
        return (
            value[len_value - part_integer :]
            if part_integer and part_integer < len_value
            else value
        )
    else:
        return ""


def is_deployed() -> bool:
    """Return wether we're running inside a PyInstaller bundle."""
    return getattr(sys, "frozen", False)


def is_library() -> bool:
    """Return if pineboolib is used as external library."""

    global SHOWED_FORCE_DESKTOP_WARNING

    if FORCE_DESKTOP:
        if not SHOWED_FORCE_DESKTOP_WARNING:
            LOGGER.info("is_library: Force Desktop is Activated!")
            SHOWED_FORCE_DESKTOP_WARNING = True

        return False
    return QtWidgets.QApplication.platformName() == "offscreen"


def get_base_dir() -> str:
    """Obtain pinebolib installation path."""
    global BASE_DIR
    if not BASE_DIR:
        BASE_DIR = "%s/../.." % os.path.dirname(__file__)
        BASE_DIR = (
            os.path.realpath(".%s" % BASE_DIR[1:])
            if is_deployed() and BASE_DIR.startswith(":")
            else BASE_DIR
        )
        LOGGER.info("BaseDir %s", BASE_DIR)
    return BASE_DIR


def filedir(*path: str) -> str:
    """
    Get file full path reltive to the project.

    filedir(path1[, path2, path3 , ...])
    @param array de carpetas de la ruta
    @return devuelve la ruta absoluta resultado de concatenar los paths que se le pasen y aplicarlos desde la ruta del proyecto.
    Es útil para especificar rutas a recursos del programa.
    """
    return os.path.realpath(os.path.join(get_base_dir(), *path))


def download_files() -> None:
    """Download data for PyInstaller bundles."""
    if os.path.exists(filedir("forms")):
        return

    if not os.path.exists(filedir("../pineboolib")):
        os.mkdir(filedir("../pineboolib"))

    copy_dir_recursive(":/pineboolib", filedir("../pineboolib"))

    tmp_dir = settings.CONFIG.value("ebcomportamiento/temp_dir")

    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)


def pixmap_from_mime_source(name: str) -> Any:
    """Convert mime source into a pixmap."""
    from PyQt6 import QtGui

    file_name = filedir("./core/images/icons", name)

    return QtGui.QPixmap(file_name) if os.path.exists(file_name) else None


def sha1(text_: str) -> str:
    """Get SHA1 hash from string in hex form."""
    return hashlib.sha1(str(text_).encode("UTF-8")).hexdigest()


def print_stack(maxsize: int = 1) -> None:
    """Print Python stack, like a traceback."""
    for item in traceback.format_list(traceback.extract_stack())[1:-2][-maxsize:]:
        print(item.rstrip())


def session_id(conn_name: str = "default", with_time: bool = False) -> str:
    """Return session id."""

    return "%s|%s%s" % (
        threading.current_thread().ident,
        conn_name,
        "|%s" % time.time() if with_time else "",
    )


def empty_dir(dir_name: str) -> None:
    """Empty a dir."""

    for root, dirs, files in os.walk(dir_name):
        for file_item in files:
            os.remove(os.path.join(root, file_item))
