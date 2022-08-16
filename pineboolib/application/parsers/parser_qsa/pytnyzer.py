#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Pythonyzer.

Reads XML AST created by postparse.py and creates an equivalent Python file.
"""
import copy
import optparse
import os
import pathlib
import re
from xml.etree import ElementTree as ET
from typing import Any, Generator, Tuple, Type, List, Dict, Set, cast, Optional, TextIO, Callable

from pineboolib.core.utils import logging

LOGGER = logging.get_logger(__name__)
ASTGenerator = Generator[Tuple[str, str], None, None]

try:
    import black  # type: ignore

    BLACK_FILEMODE = black.FileMode(line_length=120)
except ImportError:
    black = None  # type: ignore [assignment]
    BLACK_FILEMODE = None  # type: ignore [assignment]


STRICT_MODE = False

# To get the following list updated, do:
# In [1]: from pineboolib.qsa import qsa
# In [2]: dir(qsa)

QSA_KNOWN_ATTRS = {
    "Application",
    "AQBoolFlagState",
    "AQBoolFlagStateList",
    "AQSButtonGroup",
    "AQFormDB",
    "AQObjectQueryList",
    "AQOdsColor",
    "AQOdsGenerator",
    "AQOdsImage",
    "AQOdsRow",
    "AQOdsSheet",
    "AQOdsSpreadSheet",
    "AQOdsStyle",
    "AQS",
    "AQSettings",
    "AQSignalMapper",
    "AQSSProject",
    "AQSmtpClient",
    "AQSql",
    "AQSqlCursor",
    "AQSqlQuery",
    "AQUnpacker",
    "AQPackager",
    "AQUtil",
    "Any",
    "AnyStr",
    "Array",
    "Boolean",
    "Callable",
    "CheckBox",
    "Color",
    "ComboBox",
    "Date",
    "DateEdit",
    "Dialog",
    "Dict",
    "Dir",
    "FLApplication",
    "FLCheckBox",
    "FLCodBar",
    "FLDataTable",
    "FLDateEdit",
    "FLDomDocument",
    "FLDomElement",
    "FLDomNode",
    "FLDomNodeList",
    "FLDoubleValidator",
    "FLFieldDB",
    "FLFormDB",
    "FLFormRecordDB",
    "FLFormSearchDB",
    "FLIntValidator",
    "FLLineEdit",
    "FLListViewItem",
    "FLNetwork",
    "FLPixmapView",
    "FLPosPrinter",
    "FLReportEngine",
    "FLJasperEngine",
    "FLJasperViewer",
    "FLReportViewer",
    "FLSerialPort",
    "FLSpinBox",
    "FLSqlCursor",
    "FLSqlQuery",
    "FLTable",
    "FLTableDB",
    "FLTextEditOutput",
    "FLTimeEdit",
    "FLUIntValidator",
    "FLUtil",
    "FLVar",
    "FLWidget",
    "FLWorkSpace",
    "Font",
    "File",
    "FileDialog",
    "FormDBWidget",
    "Function",
    "GroupBox",
    "Input",
    "Label",
    "Line",
    "LineEdit",
    "List",
    "LogText",
    "Math",
    "MessageBox",
    "NumberEdit",
    "Number",
    "Object",
    "ObjectNotFoundDGINotLoaded",
    "ObjectNotFoundInCurrentDGI",
    "Optional",
    "Process",
    "Picture",
    "Pixmap",
    "ProxySlot",
    "QAction",
    "QActionGroup",
    "QApplication",
    "QBuffer",
    "QBrush",
    "QButtonGroup",
    "QByteArray",
    "QCheckBox",
    "QColor",
    "QComboBox",
    "QDataView",
    "QDateEdit",
    "QDialog",
    "QDir",
    "QDockWidget",
    "QDomDocument",
    "QEventLoop",
    "QFile",
    "QFileDialog",
    "QFontDialog",
    "QFrame",
    "QGroupBox",
    "QHBoxLayout",
    "QHButtonGroup",
    "QVButtonGroup",
    "QHttp",
    "QHttpResponseHeader",
    "QHttpRequestHeader",
    "QIcon",
    "QIconSet",
    "QImage",
    "QInputDialog",
    "QKeySequence",
    "QLabel",
    "QLayoutWidget",
    "QLineEdit",
    "QListView",
    "QListViewWidget",
    "QListWidgetItem",
    "QMainWindow",
    "QMdiArea",
    "QMdiSubWindow",
    "QMenu",
    "QMessageBox",
    "QObject",
    "QPainter",
    "QPixmap",
    "QPopupMenu",
    "QProcess",
    "QProgressDialog",
    "QPushButton",
    "QRadioButton",
    "QSignalMapper",
    "QSize",
    "QSizePolicy",
    "QSpinBox",
    "QString",
    "QStyleFactory",
    "QSProject",
    "QTabWidget",
    "QTable",
    "QTextEdit",
    "QTextStream",
    "QTimeEdit",
    "QToolBar",
    "QToolBox",
    "QToolButton",
    "QTreeWidget",
    "QTreeWidgetItem",
    "QTreeWidgetItemIterator",
    "QVBoxLayout",
    "QWidget",
    "QtCore",
    "QtWidgets",
    "RadioButton",
    "RegExp",
    "Rect",
    "RichText",
    "SpinBox",
    "String",
    "SysType",
    "System",
    "System_class",
    "Size",
    "TextEdit",
    "TimeEdit",
    "Tuple",
    "TypeVar",
    "aqApp",
    "auth",
    "available_thread_sessions",
    "connect",  # <---
    "disconnect",  # <---
    "debug",
    "decorators",
    "filedir",
    "form",
    "input",
    "inspect",
    "isNaN",
    "killTimer",
    "killTimers",
    "logger",
    "parseFloat",
    "parseInt",
    "parseString",
    "print_",
    "print_stack",
    "project",
    "proxy_fn",
    "qApp",
    "qsa",
    "qsaRegExp",
    "resolveObject",
    "session",
    "slot_done",
    # "solve_connection",
    "startTimer",
    "sys",
    "types",
    "thread_session_free",
    "thread_session_current",
    "thread_session_new",
    "undefined",
    "user_id",
    "ustr",
    "ustr1",
    "util",
    "weakref",
}

DISALLOW_CONVERSION_FOR_NONSTRICT = {"connect", "disconnect", "form"}
classesDefined: List[str] = []


def id_translate(name: str, qsa_exclude: Set[str] = None, transform: Dict[str, str] = None) -> str:
    """Translate identifiers to avoid "import *" issues."""
    orig_name = name
    python_keywords = [
        "and",
        "del",
        "for",
        "is",
        "raise",
        "assert",
        "elif",
        "from",
        "lambda",
        "return",
        "break",
        "else",
        "global",
        "not",
        "try",
        "class",
        "except",
        "if",
        "or",
        "while",
        "continue",
        "from",
        "exec",
        "import",
        "pass",
        "yield",
        "def",
        "finally",
        "in",
        "print",
        "str",
        "qsa",
        "self",
    ]
    if "(" in name:
        raise ValueError("Parenthesis not allowed in ID for translation")
    if "." in name:
        raise ValueError("Dot not allowed in ID for translation")
    if name == "false":
        return "False"
    elif name == "true":
        return "True"
    elif name == "null":
        return "None"
    elif name == "unknown":
        return "None"
    elif name == "undefined":
        return "None"
    elif name == "this":
        return "self"
    elif name == "NaN":
        return 'float("nan")'

    elif name == "startsWith":
        name = "startswith"
    elif name == "endsWith":
        name = "endswith"
    elif name == "lastIndexOf":
        name = "rfind"
    # if name == "File":
    #    name = "qsatype.File"
    # if name == "Dir":
    #    name = "qsatype.Dir"
    elif name == "findRev":
        name = "find"
    elif name == "toLowerCase":
        name = "lower"
    elif name == "toUpperCase":
        name = "upper"
    elif name == "indexOf":
        name = "index"
    elif name in ("argStr", "argInt"):
        name = "arg"
    # if name == "Process":
    #    name = "qsatype.Process"
    if name in python_keywords:
        name = name + "_"

    if qsa_exclude is not None:
        qsa_lower = {
            x.lower(): x
            for x in qsa_exclude | QSA_KNOWN_ATTRS
            if x.lower() != x and x.lower() not in qsa_exclude
        }
        if orig_name.lower() in qsa_lower:
            new_name = qsa_lower[orig_name.lower()]
            count_diff_chars = len([1 for a, b in zip(new_name, orig_name) if a != b])
            if count_diff_chars <= 2:
                orig_name = name = new_name
                if name in python_keywords:
                    name = name + "_"

        if orig_name in qsa_exclude:
            return name

        if name in QSA_KNOWN_ATTRS:
            if name in DISALLOW_CONVERSION_FOR_NONSTRICT:
                if name in ["connect", "disconnect"]:  # self.module_connect
                    return "self.module_%s" % name
                else:
                    return name
            return "qsa.%s" % name

        if transform is not None and name in transform:
            return transform[name]

        if name.startswith("form") and len(name) > 4:
            return 'qsa.from_project("%s")' % name

        if STRICT_MODE:
            return "__undef__" + name
        else:

            return name
    else:
        if transform is not None and name in transform:
            return transform[name]

        return name


CONT_SWITCH = 0
CONT_DO_WHILE = 0


class ASTPythonBase(object):
    """Generate python lines. Base class."""

    elem: ET.Element

    def __init__(self, elem: ET.Element) -> None:
        """Create ASTPythonBase."""
        self.elem: ET.Element = elem
        self.parent: Optional["ASTPythonBase"] = None
        self.source: Optional["Source"] = None

    @classmethod
    def can_process_tag(cls, tagname: str) -> bool:
        """Return if this instance can process given tagname."""
        return False

    def generate(
        self, *, break_mode: bool = False, include_pass: bool = True, **kwargs: Any
    ) -> ASTGenerator:
        """Generate Python code."""
        yield "type", "value"

    def local_var(self, name: str, is_member: bool = False) -> str:
        """Transform Identifiers that are local variables."""
        locals: Optional[Set[str]] = None
        transform: Optional[Dict[str, str]] = None
        if not is_member and self.source is not None:
            locals = self.source.locals if self.source else set()
            transform = self.source.locals_transform
        return id_translate(name, qsa_exclude=locals, transform=transform) if name else ""

    def other_var(self, name: str) -> str:
        """Transform identifiers that cannot fit in any other category."""
        return id_translate(name, qsa_exclude=None)


class ASTPythonFactory(type):
    """Metaclass that registers class as a processor for its type based on its classname."""

    ast_class_types: List[Type[ASTPythonBase]] = []

    def __init__(self, name: str, bases: tuple, dct: dict) -> None:
        """Register class using class name."""
        if issubclass(self, ASTPythonBase):
            ASTPythonFactory.register_type(cast(Type[ASTPythonBase], self))

    @staticmethod
    def register_type(cls: Type[ASTPythonBase]) -> None:
        """Register class using class name."""
        ASTPythonFactory.ast_class_types.append(cls)


class ASTPython(ASTPythonBase, metaclass=ASTPythonFactory):
    """Generate Python code from AST. Class with common functionality."""

    tags: List[str] = []
    debug_file: Optional[TextIO] = None
    generate_depth = 0
    numline = 0
    DEBUGFILE_LEVEL = 6
    _last_retlen = 0
    source: "Source"
    parent: "ASTPythonBase"

    @classmethod
    def can_process_tag(self, tagname: str) -> bool:
        """Return if the class can process specified tag name."""
        return self.__name__ == tagname or tagname in self.tags

    def __init__(self, elem: ET.Element) -> None:
        """Create new ASTPython class."""
        super().__init__(elem)
        self.internal_generate = self.generate
        ASTPython._last_retlen = 0
        if self.debug_file:
            self.generate = self._generate  # type: ignore

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """Generate Python code. Abstract method. Generates debug for unknown AST."""
        yield "debug", "* not-known-seq * %s" % ET.tostring(self.elem, encoding="UTF-8")

    def debug(self, text: str) -> None:
        """Print debug on the generated file."""
        if self.debug_file is None:
            return
        splen = ASTPython.generate_depth
        retlen = 0
        if splen > self.generate_depth:
            retlen, splen = splen - self.generate_depth, self.generate_depth
        if retlen:
            # Reduce callstack to just one
            if ASTPython._last_retlen == retlen + 1 and self.DEBUGFILE_LEVEL < 10:
                ASTPython._last_retlen = retlen
                return
            spaces = " " * (splen - 1) + "<" + "-" * retlen
        else:
            spaces = " " * splen
        ASTPython._last_retlen = retlen
        cname = self.__class__.__name__
        self.debug_file.write("%04d%s%s: %s\n" % (ASTPython.numline, spaces, cname, text))

    def _generate(self, **kwargs: Any) -> ASTGenerator:
        """Debugging version of generate method."""
        if self.DEBUGFILE_LEVEL > 5:
            self.debug("begin-gen")
        ASTPython.generate_depth += 1
        self.generate_depth = ASTPython.generate_depth
        for dtype, data in self.internal_generate(**kwargs):
            yield dtype, data
            if self.DEBUGFILE_LEVEL > 2:
                self.debug("%s: %s" % (dtype, data))
        ASTPython.generate_depth -= 1
        if self.DEBUGFILE_LEVEL > 5:
            self.debug("end-gen")


class Source(ASTPython):
    """Process Source XML tags."""

    locals: Set[str]
    locals_transform: Dict[str, str]

    def __init__(self, elem: ET.Element) -> None:
        """Create Source parser. Tracks local variables."""
        super().__init__(elem)
        self.locals = set()
        self.locals_transform = {}

    def generate(
        self,
        *,
        break_mode: bool = False,
        include_pass: bool = True,
        declare_identifiers: Set[str] = None,
        **kwargs: Any
    ) -> ASTGenerator:
        """Generate python code."""
        elems = 0
        after_lines = []
        prev_ast_type = None
        if declare_identifiers:
            self.locals |= declare_identifiers
        for child in self.elem:
            # yield "debug", "<%s %s>" % (child.tag, repr(child.attrib))
            child.set("parent_", self.elem)  # type: ignore
            ast_python = parse_ast(child, parent=self)
            ast_type = ast_python.__class__.__name__
            # print(ast_type)
            if ast_type == "Function" and prev_ast_type != ast_type:
                yield "line", ""
            prev_ast_type = ast_type

            for dtype, data in ast_python.generate(
                break_mode=break_mode, plusplus_as_instruction=True
            ):
                if dtype == "line+1":
                    after_lines.append(data)
                    continue
                elif dtype == "line":
                    elems += 1
                yield dtype, data
                if dtype == "line":
                    for line in after_lines:
                        elems += 1
                        yield dtype, line
                    after_lines = []
                elif dtype == "break":
                    for line in after_lines:
                        elems += 1
                        yield "line", line

        for line in after_lines:
            elems += 1
            yield "line", line
        if not elems and include_pass:
            yield "line", "pass"


class Class(ASTPython):
    """Process Class XML tags."""

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""
        name = self.elem.get("name", "unnamed")
        extends = self.elem.get("extends", "qsa.ObjectClass")
        self.source.locals.add(name)

        yield "line", "# /** @class_declaration %s */" % name
        yield "line", "class %s(%s):" % (name, extends)
        yield "begin", "block-class-%s" % (name)
        for source in self.elem.findall("Source"):
            # FIXME: Element.set expects string.
            source.set("parent_", self.elem)  # type: ignore
            classesDefined.clear()
            ast_python = parse_ast(source, parent=self)
            for obj in ast_python.generate():
                yield obj
        yield "end", "block-class-%s" % (name)


class Function(ASTPython):
    """Process Function XML tags."""

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""
        _name = self.elem.get("name")
        anonymous = False
        if _name:
            name = self.other_var(_name)
        else:
            # Anonima:
            name = "_anonymous_fn_"
            anonymous = True
        withoutself = self.elem.get("withoutself")
        parent = cast(ET.Element, self.elem.get("parent_"))  # FIXME
        grandparent = None
        if parent is not None:
            grandparent = cast(Optional[ET.Element], parent.get("parent_"))  # FIXME

        if grandparent is not None and grandparent.get("name") == "FormInternalObj":
            class_name = name.split("_")[0]
            if class_name not in classesDefined:
                if class_name == "":
                    class_name = "FormInternalObj"
                yield "line", "# /** @class_definition %s */" % class_name
                classesDefined.append(class_name)
        # returns = self.elem.get("returns", None)

        arguments = []
        if not withoutself:
            if grandparent is not None:
                if grandparent.tag == "Class":
                    arguments.append("self")
                    if name == grandparent.get("name"):
                        name = "__init__"
            else:
                if not anonymous:
                    arguments.append("self")
        id_list: Set[str] = set()
        rtype: Optional[str] = self.elem.get("returns")
        if rtype is None:
            pass
        elif rtype == "String":
            rtype = "str"
        elif rtype == "Number":
            rtype = None
        elif rtype == "Boolean":
            rtype = "bool"
        elif rtype in QSA_KNOWN_ATTRS:
            rtype = "qsa.%s" % rtype

        for number, arg in enumerate(self.elem.findall("Arguments/*")):
            expr = []
            # FIXME: ET.Element.set expects a string not Element.
            arg.set("parent_", self.elem)  # type: ignore
            for dtype, data in parse_ast(arg, parent=self).generate():
                if dtype == "expr":
                    id_list.add(data)
                    expr.append(self.local_var(data, is_member=True))
                else:
                    yield dtype, data
            if not expr:
                arguments.append("unknownarg")
                yield "debug", "Argument %d not understood" % number
                yield "debug", ET.tostring(arg)  # type: ignore
            else:
                if len(expr) == 1:

                    dtype_: Optional[str] = arg.get("type")
                    dtyping_ = ""
                    if dtype_ is not None:
                        if dtype_ == "String":
                            dtyping_ = "str"
                        elif dtype_ == "Number":
                            pass
                            # dtype_ = "Union[int, float]"
                        elif dtype_ == "Boolean":
                            dtyping_ = "bool"
                        elif dtype_.lower() == "optional":
                            dtyping_ = "Any"
                        elif dtype_ in QSA_KNOWN_ATTRS:
                            dtyping_ = "qsa.%s" % dtype_

                    if dtyping_:
                        expr += [":", '"%s"' % dtyping_]
                    if dtyping_ == "Any":
                        expr += ["=", "None"]
                    # else:
                    #    pass
                    # def_value = "None"
                    # if dtype_ == "Number":
                    #    def_value = "0"
                    # expr += ["=", def_value]
                arguments.append("".join(expr))

        yield "line", "def %s(%s)%s:" % (
            name,
            ", ".join(arguments),
            "%s" % ' -> "%s"' % rtype if rtype is not None else "",
        )
        yield "begin", "block-def-%s" % (name)
        # if returns:  yield "debug", "Returns: %s" % returns
        for source in self.elem.findall("Source"):
            # FIXME: ET.Element.set expects a string not Element.
            source.set("parent_", self.elem)  # type: ignore
            for obj in parse_ast(source, parent=self).generate(declare_identifiers=id_list):
                yield obj
        yield "end", "block-def-%s" % (name)
        if anonymous:
            yield "expr", name


class FunctionAnon(Function):
    """Process FunctionAnon XML tags."""

    pass


class FunctionCall(ASTPython):
    """Process FunctionCall XML tags."""

    def generate(self, is_member: bool = False, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""
        name: str = self.local_var(self.elem.get("name", "noname"), is_member=is_member)
        # FIXME:
        parent = cast(ET.Element, self.elem.get("parent_"))
        # data_ = None
        if name == "":
            arg = self.elem[0]
            # FIXME:
            arg.set("parent_", self.elem)  # type: ignore
            expr = []
            for dtype, data in parse_ast(arg, parent=self).generate(isolate=False):
                # data_ = data
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data

            if len(expr) == 0:
                name = "unknownFn"
                yield "debug", "Function name not understood"
                yield "debug", ET.tostring(arg)  # type: ignore
            elif len(expr) > 1:
                name = "unknownFn"
                yield "debug", "Multiple function names"
                yield "debug", repr(expr)
            else:
                name = expr[0]

        if parent is not None:
            if parent.tag == "InstructionCall":
                class_ = None
                class_parent: Optional[ET.Element] = parent
                while class_parent is not None:
                    if class_parent.tag == "Class":
                        class_ = class_parent
                        break
                    class_parent = cast(ET.Element, class_parent.get("parent_"))

                if class_ is not None:
                    extends = class_.get("extends")
                    if extends == name:
                        name = "super().__init__"

                if not name.find("["):  # if don't search a array
                    functions = parent.findall('Function[@name="%s"]' % name)
                    for func_element in functions:
                        # yield "debug", "Function to:" + ET.tostring(f)
                        name = "self.%s" % name
                        break

        arguments = []

        for number, arg in enumerate(self.elem.findall("CallArguments/*")):
            # FIXME:
            arg.set("parent_", self.elem)  # type: ignore
            expr = []
            for dtype, data in parse_ast(arg, parent=self).generate(isolate=False):
                # data_ = data
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
            if len(expr) == 0:
                arguments.append("unknownarg")
                yield "debug", "Argument %d not understood" % number
                yield "debug", ET.tostring(arg)  # type: ignore
            else:
                arg1 = " ".join(expr)
                arg1 = arg1.replace("( ", "(")
                arg1 = arg1.replace(" )", ")")
                arguments.append(arg1)

        comment = ""
        if STRICT_MODE and name.startswith("__undef__"):
            name = name[9:]
            name = "self.%s" % name
            comment = ""

        yield "expr", "%s(%s)%s" % (name, ", ".join(arguments), comment)


class FunctionAnonExec(FunctionCall):
    """Process FunctionAnonExec XML tags."""

    pass


class If(ASTPython):
    """Process If XML tags."""

    def generate(self, break_mode: bool = False, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        main_expr = []
        for number, arg in enumerate(self.elem.findall("Condition/*")):
            arg.set("parent_", self.elem)  # type: ignore
            expr = []
            condition_yield = []
            condition = parse_ast(arg, parent=self)
            # yield "debug", repr(condition)
            for dtype, data in condition.generate(isolate=False):
                if dtype == "line+1":
                    yield "debug", "Inline update inside IF condition not allowed. Unexpected behavior."
                    dtype = "line"
                elif dtype == "expr":
                    expr.append(data)
                else:
                    condition_yield.append((dtype, data))
            if condition_yield:
                yield "debug", "Unexpected IF condition: %r" % condition_yield

            for type_, data_ in condition_yield:
                yield type_, data_

            if not expr:
                main_expr.append("False")
                yield "debug", "Expression %d not understood" % number
                yield "debug", ET.tostring(arg)  # type: ignore
            else:

                if len(expr) == 3:
                    # FIXME: This works if the pattern is alone in the IF. But if it has AND/Or does not work
                    if expr[1] == "==":
                        if expr[2] == "True":
                            expr = [expr[0]]
                        elif expr[2] == "False":
                            expr = ["not", expr[0]]
                        elif expr[2] == "None":
                            expr = [expr[0], "is", "None"]
                        elif expr[2] == 'float("nan")':
                            expr = ["qsa.isnan(%s)" % expr[0]]
                    elif expr[1] == "!=":
                        if expr[2] == "None":
                            expr = [expr[0], "is not", "None"]
                        elif expr[2] == 'float("nan")':
                            expr = ["not", "qsa.isnan(%s)" % expr[0]]
                        elif expr[2] == "True":
                            expr = ["not", expr[0]]
                        elif expr[2] == "False":
                            expr = [expr[0]]

                main_expr.append(" ".join(expr))

        yield "line", "if %s:" % (" ".join(main_expr))
        for source in self.elem.findall("Source"):
            source.set("parent_", self.elem)  # type: ignore
            yield "begin", "block-if"
            for obj in parse_ast(source, parent=self).generate(break_mode=break_mode):
                yield obj
            yield "end", "block-if"

        for source in self.elem.findall("Else/Source"):
            source.set("parent_", self.elem)  # type: ignore
            yield "line", "else:"
            yield "begin", "block-else"
            for obj in parse_ast(source, parent=self).generate(break_mode=break_mode):
                yield obj
            yield "end", "block-else"


class TryCatch(ASTPython):
    """Process TryCatch XML tags."""

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        tryblock, catchblock = self.elem.findall("Source")
        tryblock.set("parent_", self.elem)  # type: ignore
        catchblock.set("parent_", self.elem)  # type: ignore
        yield "line", "try:"
        yield "begin", "block-try"
        for obj in parse_ast(tryblock, parent=self).generate():
            yield obj
        yield "end", "block-try"

        identifier = None
        for ident in self.elem.findall("Identifier"):
            ident.set("parent_", self.elem)  # type: ignore
            expr = []
            for dtype, data in parse_ast(ident, parent=self).generate(
                isolate=False, is_member=True
            ):
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
            identifier = " ".join(expr)
        yield "line", "except Exception:"
        yield "begin", "block-except"
        if identifier:
            self.source.locals.add(identifier)
            # yield "line", "%s = str(%s)" % (identifier, identifier)
            yield "line", "%s = qsa.format_exc()" % (identifier)
        for obj in parse_ast(catchblock, parent=self).generate(include_pass=identifier is None):
            yield obj
        yield "end", "block-except"


class While(ASTPython):
    """Process While XML tags."""

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        main_expr = []
        for number, arg in enumerate(self.elem.findall("Condition/*")):
            arg.set("parent_", self.elem)  # type: ignore
            expr = []
            for dtype, data in parse_ast(arg, parent=self).generate(isolate=False):
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
            if len(expr) == 0:
                main_expr.append("False")
                yield "debug", "Expression %d not understood" % number
                yield "debug", ET.tostring(arg)  # type: ignore
            else:
                main_expr.append(" ".join(expr))

        yield "line", "while %s:" % (" ".join(main_expr))
        for source in self.elem.findall("Source"):
            source.set("parent_", self.elem)  # type: ignore
            yield "begin", "block-while"
            for obj in parse_ast(source, parent=self).generate():
                yield obj
            yield "end", "block-while"


class DoWhile(ASTPython):
    """Process DoWhile XML tags."""

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        main_expr = []
        for number, arg in enumerate(self.elem.findall("Condition/*")):
            arg.set("parent_", self.elem)  # type: ignore
            expr = []
            for dtype, data in parse_ast(arg, parent=self).generate(isolate=False):
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
            if len(expr) == 0:
                main_expr.append("False")
                yield "debug", "Expression %d not understood" % number
                yield "debug", ET.tostring(arg)  # type: ignore
            else:
                main_expr.append(" ".join(expr))
        # TODO .....
        global CONT_DO_WHILE
        CONT_DO_WHILE += 1
        key = "%02x" % CONT_DO_WHILE
        name1st = "s%s_dowhile_1stloop" % key
        yield "line", "%s = True" % (name1st)

        yield "line", "while %s or %s:" % (name1st, " ".join(main_expr))
        for source in self.elem.findall("Source"):
            source.set("parent_", self.elem)  # type: ignore
            yield "begin", "block-while"
            yield "line", "%s = False" % (name1st)
            for obj in parse_ast(source, parent=self).generate():
                yield obj
            yield "end", "block-while"


class For(ASTPython):
    """Process For XML tags."""

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        init_expr = []
        for arg in self.elem.findall("ForInitialize/*"):
            arg.set("parent_", self.elem)  # type: ignore
            expr = []
            for dtype, data in parse_ast(arg, parent=self).generate(isolate=False):
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
            if len(expr) > 1:
                init_expr.append(" ".join(expr))
        if init_expr:
            yield "line", " ".join(init_expr)
            yield "line", "while_pass = True"
        else:
            yield "line", "while_pass = True"

        incr_expr = []
        incr_lines = []
        for arg in self.elem.findall("ForIncrement/*"):
            arg.set("parent_", self.elem)  # type: ignore
            expr = []
            for dtype, data in parse_ast(arg, parent=self).generate(isolate=False):
                if dtype == "expr":
                    expr.append(data)
                elif dtype in ["line", "line+1"]:
                    incr_lines.append(data)
                else:
                    yield dtype, data
            if len(expr) > 0:
                incr_expr.append(" ".join(expr))

        main_expr = []
        for arg in self.elem.findall("ForCompare/*"):
            arg.set("parent_", self.elem)  # type: ignore
            expr = []
            for dtype, data in parse_ast(arg, parent=self).generate(isolate=False):
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
            if len(expr) == 0:
                main_expr.append("True")
            else:
                main_expr.append(" ".join(expr))
        # yield "debug", "WHILE-FROM-QS-FOR: (%r;%r;%r)" % (init_expr,main_expr,incr_lines)
        yield "line", "while %s:" % (" ".join(main_expr))
        yield "begin", "block-for"
        yield "line", "if not while_pass:"
        yield "begin", "block-while_pass"
        if incr_lines:
            for line in incr_lines:
                yield "line", line
        yield "line", "while_pass = True"
        yield "line", "continue"
        yield "end", "block-while_pass"
        yield "line", "while_pass = False"

        for source in self.elem.findall("Source"):
            source.set("parent_", self.elem)  # type: ignore
            for obj in parse_ast(source, parent=self).generate(include_pass=False):
                yield obj
            if incr_lines:
                for line in incr_lines:
                    yield "line", line

            yield "line", "while_pass = True"
            yield "line", "try:"
            # Si es por ejemplo un charAt y hace out of index nos saca del while
            yield "begin", "block-error-catch"
            yield "line", "%s" % (" ".join(main_expr))
            yield "end", "block-error-catch"
            yield "line", "except Exception:"
            yield "begin", "block-except"
            yield "line", "break"
            yield "end", "block-except"
            yield "end", "block-for"


class ForIn(ASTPython):
    """Process ForIn XML tags."""

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        list_elem, main_list = "None", "None"
        myelems = []
        for elem in self.elem:
            if elem.tag == "Source":
                break
            if elem.tag == "ForInitialize":
                elem = list(elem)[0]
            expr = []
            for dtype, data in parse_ast(elem, parent=self).generate(isolate=False, is_member=True):
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
            myelems.append(" ".join(expr))
        list_elem, main_list = myelems
        yield "debug", "FOR-IN: " + repr(myelems)
        yield "line", "for %s in %s:" % (list_elem, main_list)
        for source_elem in self.elem.findall("Source"):
            source = cast(Source, parse_ast(source_elem, parent=self))
            source.locals.add(list_elem)
            yield "begin", "block-for-in"
            for obj in source.generate(include_pass=False):
                yield obj
            yield "end", "block-for-in"


class OldSwitch(ASTPython):
    """Process OldSwitch XML tags."""

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        global CONT_SWITCH
        CONT_SWITCH += 1
        key = "%02x" % CONT_SWITCH
        name = "s%s_when" % key
        name_pr = "s%s_do_work" % key
        name_pr2 = "s%s_work_done" % key
        main_expr = []
        for number, arg in enumerate(self.elem.findall("Condition/*")):
            arg.set("parent_", self.elem)  # type: ignore
            expr = []
            for dtype, data in parse_ast(arg, parent=self).generate(isolate=False):
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
            if len(expr) == 0:
                main_expr.append("False")
                yield "debug", "Expression %d not understood" % number
                yield "debug", ET.tostring(arg)  # type: ignore
            else:
                main_expr.append(" ".join(expr))
        yield "line", "%s = %s" % (name, " ".join(main_expr))
        yield "line", "%s, %s = %s, %s" % (name_pr, name_pr2, "False", "False")
        for scase in self.elem.findall("Case"):
            scase.set("parent_", self.elem)  # type: ignore
            value_expr = []
            for number, arg in enumerate(scase.findall("Value")):
                arg.set("parent_", self.elem)  # type: ignore
                expr = []
                for dtype, data in parse_ast(arg, parent=self).generate(isolate=False):
                    if dtype == "expr":
                        expr.append(data)
                    else:
                        yield dtype, data
                if len(expr) == 0:
                    value_expr.append("False")
                    yield "debug", "Expression %d not understood" % number
                    yield "debug", ET.tostring(arg)  # type: ignore
                else:
                    value_expr.append(" ".join(expr))

            yield "line", "if %s == %s:" % (name, " ".join(value_expr))
            yield "begin", "block-if"
            yield "line", "%s, %s = %s, %s" % (name_pr, name_pr2, "True", "True")
            yield "end", "block-if"
            yield "line", "if %s:" % (name_pr)
            yield "begin", "block-if"
            count = 0
            for source in scase.findall("Source"):
                source.set("parent_", self.elem)  # type: ignore
                for obj in parse_ast(source, parent=self).generate(break_mode=True):
                    if obj[0] == "break":
                        yield "line", "%s = %s  # BREAK" % (name_pr, "False")
                        count += 1
                    else:
                        yield obj
                        count += 1
            if count < 1:
                yield "line", "pass"
            yield "end", "block-if"

        for scasedefault in self.elem.findall("CaseDefault"):
            scasedefault.set("parent_", self.elem)  # type: ignore
            yield "line", "if not %s:" % (name_pr2)
            yield "begin", "block-if"
            yield "line", "%s, %s = %s, %s" % (name_pr, name_pr2, "True", "True")
            yield "end", "block-if"
            yield "line", "if %s:" % (name_pr)
            yield "begin", "block-if"
            for source in scasedefault.findall("Source"):
                source.set("parent_", self.elem)  # type: ignore
                for obj in parse_ast(source, parent=self).generate(break_mode=True):
                    if obj[0] == "break":
                        yield "line", "%s = %s  # BREAK" % (name_pr, "False")
                    else:
                        yield obj
            yield "end", "block-if"
        # yield "line", "assert( not %s )" % name_pr
        # yield "line", "assert( %s )" % name_pr2


class Switch(ASTPython):
    """Process Switch XML tags."""

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """
        Generate python code.

        Should generate a switch using qsa.switch() like this:

        v = 'ten'
        for case in qsa.switch(v):
            if case('one'):
                print 1
                break
            if case('two'):
                print 2
                break
            if case('ten'):
                print 10
                break
            if case('eleven'):
                print 11
                break
            if case(): # default, could also just omit condition or 'if True'
                print "something else!"
                # No need to break here, it'll stop anyway
        """

        main_expr = []
        for number, arg in enumerate(self.elem.findall("Condition/*")):
            arg.set("parent_", self.elem)  # type: ignore
            expr = []
            for dtype, data in parse_ast(arg, parent=self).generate(isolate=False):
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
            if len(expr) == 0:
                main_expr.append("False")
                yield "debug", "Expression %d not understood" % number
                yield "debug", ET.tostring(arg)  # type: ignore
            else:
                main_expr.append(" ".join(expr))
        yield "line", "for case in qsa.switch(%s):" % (" ".join(main_expr))
        yield "begin", "block-for"
        for scase in self.elem.findall("Case"):
            scase.set("parent_", self.elem)  # type: ignore
            value_expr = []
            for number, arg in enumerate(scase.findall("Value")):
                arg.set("parent_", self.elem)  # type: ignore
                expr = []
                for dtype, data in parse_ast(arg, parent=self).generate(isolate=False):
                    if dtype == "expr":
                        expr.append(data)
                    else:
                        yield dtype, data
                if not expr:
                    value_expr.append("False")
                    yield "debug", "Expression %d not understood" % number
                    yield "debug", ET.tostring(arg)  # type: ignore
                else:
                    value_expr.append(" ".join(expr))

            yield "line", "if case(%s):" % (" ".join(value_expr))
            yield "begin", "block-if"
            for source in scase.findall("Source"):
                source.set("parent_", self.elem)  # type: ignore
                for obj in parse_ast(source, parent=self).generate():
                    yield obj
            yield "end", "block-if"

        for scasedefault in self.elem.findall("CaseDefault"):
            scasedefault.set("parent_", self.elem)  # type: ignore
            yield "line", "if case():"
            yield "begin", "block-if"
            for source in scasedefault.findall("Source"):
                source.set("parent_", self.elem)  # type: ignore
                for obj in parse_ast(source, parent=self).generate():
                    yield obj
            yield "end", "block-if"
        yield "end", "block-for"


class With(ASTPython):
    """Process With XML tags."""

    python_keywords = [
        "Insert",
        "Edit",
        "Del",
        "Browse",
        "select",
        "first",
        "next",
        "prev",
        "last",
        "setValueBuffer",
        "valueBuffer",
        "setTablesList",
        "setSelect",
        "setFrom",
        "setWhere",
        "setForwardOnly",
        "setOrderBy",
        "setModeAccess",
        "commitBuffer",
        "commit",
        "refreshBuffer",
        "setNull",
        "setUnLock",
        "child",
    ]

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        # key = "%02x" % random.randint(0, 255)
        # name = "w%s_obj" % key
        # yield "debug", "WITH: %s" % key
        variable, source_elem = [obj for obj in self.elem]
        var_expr = []
        for dtype, data in parse_ast(variable, parent=self).generate(isolate=False):
            if dtype == "expr":
                var_expr.append(data)
            else:
                yield dtype, data
        if not var_expr:
            var_expr.append("None")
            yield "debug", "Expression not understood"

        # yield "line", "%s = %s #WITH" % (name, " ".join(var_expr))
        yield "line", " #WITH_START"
        source = cast(Source, parse_ast(source_elem, parent=self))
        source.locals.add(" ".join(var_expr))
        source.locals_transform = {
            x: "%s.%s" % (" ".join(var_expr), x) for x in With.python_keywords
        }

        for obj in source.generate(break_mode=True):
            obj_ = None

            # para sustituir los this sueltos por var_expr
            if obj[1].find("self)") > -1:
                obj_1 = obj[1].replace("self)", "%s)" % " ".join(var_expr))
            elif obj[1].find("self ") > -1:
                obj_1 = obj[1].replace("self ", " ".join(var_expr))
            else:
                obj_1 = obj[1]

            for text in self.python_keywords:
                if obj_1.startswith(text):
                    obj_1 = "%s.%s" % (" ".join(var_expr), obj_1)
                elif obj_1.startswith("connect(%s" % text):
                    obj_1 = obj_1.replace(
                        "connect(%s" % text, "connect(%s.%s" % (" ".join(var_expr), text)
                    )
                elif obj_1.find(".") == -1 and obj_1.find(text) > -1:
                    obj_1 = obj_1.replace(text, "%s.%s" % (" ".join(var_expr), text))

            if not obj_:
                obj_ = (obj[0], obj_1)

            yield obj_
        # yield "line", "del %s" % name
        yield "line", " #WITH_END"


class Variable(ASTPython):
    """Process Variable XML tags."""

    DEBUGFILE_LEVEL = 4

    def generate(self, force_value: bool = False, **kwargs) -> ASTGenerator:
        """Generate python code."""

        name = self.elem.get("name", "unnamed")
        # if name.startswith("colorFun"): print(name)
        yield "expr", self.local_var(name, is_member=True)
        values = 0
        # for value in self.elem.findall("Value|Expression"):
        dtype: Optional[str] = self.elem.get("type", None)

        for value in self.elem:
            if value.tag not in ("Value", "Expression"):
                continue

            value.set("parent_", self.elem)  # type: ignore
            values += 1
            if not dtype:
                if name not in ("iface", "form"):
                    yield "expr", ": Any"

            elif dtype == "String":
                yield "expr", ": str"
            elif dtype == "Number":
                # yield "expr", ": Union[int, float]"
                pass
            elif dtype == "Boolean":
                yield "expr", ": bool"
            elif dtype in QSA_KNOWN_ATTRS:
                yield "expr", ': "qsa.%s"' % dtype

            yield "expr", "="
            expr = 0
            for dtype1, data in parse_ast(value, parent=self).generate(isolate=False):
                # if self.elem.get("type",None) == "Array" and data == "[]":
                if data == "qsa.Array(0)":
                    yield "expr", "[]"
                    expr += 1
                    continue

                elif data == "[]":
                    yield "expr", "qsa.Array()"
                    expr += 1
                    continue

                if dtype1 == "expr":
                    expr += 1
                yield dtype1, data
            if expr == 0:
                yield "expr", "None"

        if force_value:
            if values == 0:

                if dtype is None:
                    yield "expr", ": Any = None"
                else:
                    if dtype == "String":
                        yield "expr", ': str = ""'
                    elif dtype == "Number":
                        yield "expr", " = 0"
                    elif dtype == "Boolean":
                        yield "expr", ": bool"
                    elif dtype in ("FLUtil", "Array"):
                        yield "expr", ': "qsa.%s" = qsa.%s() # Please initialize!' % (dtype, dtype)
                    elif dtype in QSA_KNOWN_ATTRS:
                        yield "expr", ': "qsa.%s"' % dtype
                    else:
                        yield "expr", "= %s()" % self.local_var(dtype)

        self.source.locals.add(name)
        # if dtype and force_value == False: yield "debug", "Variable %s:%s" % (name,dtype)


class InstructionUpdate(ASTPython):
    """Process InstructionUpdate XML tags."""

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        arguments = []
        identifier = None
        for number, arg in enumerate(self.elem):
            arg.set("parent_", self.elem)  # type: ignore
            expr = []
            for dtype, data in parse_ast(arg, parent=self).generate(
                isolate=False, is_member=(number == 0)
            ):

                if dtype == "expr":
                    if not data:
                        raise ValueError(ET.tostring(arg))
                    elif data == "[]":
                        data = "qsa.Array()"
                    expr.append(data)
                else:
                    yield dtype, data

            if not expr:
                arguments.append("unknownarg")
                yield "debug", "Argument %d not understood" % number
                yield "debug", ET.tostring(arg)  # type: ignore
            else:
                if number == 0 and len(expr) == 1:
                    identifier = expr[0]
                arguments.append(" ".join(expr))

        yield "line", " ".join(arguments)
        if identifier:
            self.source.locals.add(identifier)


class InlineUpdate(ASTPython):
    """Process InlineUpdate XML tags."""

    def generate(self, plusplus_as_instruction: bool = False, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        arguments = []
        for number, arg in enumerate(self.elem):
            arg.set("parent_", self.elem)  # type: ignore
            expr = []
            for dtype, data in parse_ast(arg, parent=self).generate(isolate=False):
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
            if len(expr) == 0:
                arguments.append("unknownarg")
                yield "debug", "Argument %d not understood" % number
                yield "debug", ET.tostring(arg)  # type: ignore
            else:
                arguments.append(" ".join(expr))
        ctype = self.elem.get("type")
        mode = self.elem.get("mode")
        linetype = "line"
        if not plusplus_as_instruction:
            if mode == "read-update":
                linetype = "line+1"

            yield "expr", arguments[0]
        if ctype == "PLUSPLUS":
            yield linetype, arguments[0] + " += 1"
        elif ctype == "MINUSMINUS":
            yield linetype, arguments[0] + " -= 1"
        else:
            yield linetype, arguments[0] + " ?= 1"


class TypeOf(ASTPython):
    """Process TypeOf XML tags."""

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        arguments = ["qsa.typeof_"]
        for number, arg in enumerate(self.elem):
            arg.set("parent_", self.elem)  # type: ignore
            expr = []
            for dtype, data in parse_ast(arg, parent=self).generate():
                if dtype == "expr":
                    expr.append(data)
            if expr[0] != "(":
                expr = ["("] + expr
                expr.append(")")

            arguments += expr
            yield dtype, " ".join(arguments)


class InstructionCall(ASTPython):
    """Process InstructionCall XML tags."""

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        arguments = []
        for number, arg in enumerate(self.elem):
            arg.set("parent_", self.elem)  # type: ignore
            expr = []
            for dtype, data in parse_ast(arg, parent=self).generate():
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
            if len(expr) == 0:
                arguments.append("unknownarg")
                yield "debug", "Argument %d not understood" % number
                yield "debug", ET.tostring(arg)  # type: ignore
            else:
                arguments.append(" ".join(expr))
        yield "line", " ".join(arguments)


class Instruction(ASTPython):
    """Process Instruction XML tags."""

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        arguments = []
        for number, arg in enumerate(self.elem):
            arg.set("parent_", self.elem)  # type: ignore
            expr = []
            for dtype, data in parse_ast(arg, parent=self).generate():
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
            if len(expr) == 0:
                arguments.append("unknownarg")
                yield "debug", "Argument %d not understood" % number
                yield "debug", ET.tostring(arg)  # type: ignore
            else:
                arguments.append(" ".join(expr))
        if arguments:
            yield "debug", "Instruction: Maybe parse-error. This class is only for non-understood instructions or empty ones"
            yield "line", " ".join(arguments)


class InstructionFlow(ASTPython):
    """Process InstructionFlow XML tags."""

    def generate(self, break_mode: bool = False, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        arguments = []
        for number, arg in enumerate(self.elem):
            arg.set("parent_", self.elem)  # type: ignore
            expr = []
            for dtype, data in parse_ast(arg, parent=self).generate(isolate=False):
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
            if len(expr) == 0:
                arguments.append("unknownarg")
                yield "debug", "Argument %d not understood" % number
                yield "debug", ET.tostring(arg)  # type: ignore
            else:
                arguments.append(" ".join(expr))

        ctype = self.elem.get("type")
        kw_ = ctype
        if ctype == "RETURN":
            kw_ = "return"
        elif ctype == "BREAK":
            kw_ = "break"
            yield "break", kw_ + " " + ", ".join(arguments)

            # if break_mode:
            #     yield "break", kw_ + " " + ", ".join(arguments)
            #     return
        elif ctype == "CONTINUE":
            kw_ = "continue"

        elif ctype == "THROW":
            yield "line", "raise Exception(" + ", ".join(arguments) + ")"
            return
        if kw_ is None:
            LOGGER.error("Failed parsing AST. Ctype is None.")
            return
        yield "line", kw_ + " " + ", ".join(arguments)


class Member(ASTPython):
    """Process Member XML tags."""

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        arguments = []
        arg_expr = []
        # funs = None
        for number, arg in enumerate(self.elem):
            expr = []
            arg.set("parent_", self.elem)  # type: ignore
            for dtype, data in parse_ast(arg, parent=self).generate(is_member=number > 0):
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
            if len(expr) == 0:
                txtarg = "unknownarg"
                yield "debug", "Argument %d not understood" % number
                yield "debug", ET.tostring(arg)  # type: ignore
            else:
                txtarg = " ".join(expr)
            arguments.append(txtarg)
            arg_expr.append(expr)

        # Deteccion de llamada a modulo externo
        if (
            len(arguments) >= 2
            and arguments[1] == "iface"
            and arguments[0] != "self"
            and not arguments[0].startswith("qsa.from_project")
        ):
            arguments[0] = 'qsa.from_project("%s")' % arguments[0].replace("__undef__", "")
        # Lectura del self.iface.__init
        if (
            len(arguments) >= 3
            and arguments[0:2] == ["self", "iface"]
            and arguments[2].startswith("__")
            and "__undef__" not in arguments[0]
        ):
            # From: self.iface.__function()
            # to: super(class_name, self.iface).function()
            parent = cast(ET.Element, self.elem.get("parent_"))
            # funs = None
            # p_ = parent
            while parent is not None:
                if parent.tag == "Function":
                    # funs = p_
                    break
                parent = cast(ET.Element, parent.get("parent_"))

            if parent is not None:
                # fun = funs[-1]
                fun = parent
                full_fun_name = fun.get("name", "unnamed_function")
                fun_name = arguments[2][2:]
                if fun_name.find("(") > -1:
                    fun_name = fun_name[: fun_name.find("(")]

                if full_fun_name.endswith("_%s" % fun_name):
                    class_name = full_fun_name.replace("_%s" % fun_name, "")
                else:
                    class_name = full_fun_name.split("_")[0]  # happy parse...

                arguments[2] = arguments[2][2:]
                arguments[0:2] = ["qsa._super('%s', %s)" % (class_name, ".".join(arguments[0:2]))]

        # Lectura del self.iface.__init() al nuevo estilo yeboyebo
        if len(arguments) >= 2 and arguments[0:1] == ["_i"] and arguments[1].startswith("__"):
            # From: self.iface.__function()
            # to: super(class_name, self.iface).function()
            parent = cast(ET.Element, self.elem.get("parent_"))
            # funs = None
            # p_ = parent
            while parent is not None:
                if parent.tag == "Function":
                    # funs = parent
                    break
                parent = cast(ET.Element, parent.get("parent_"))

            if parent is not None:
                # fun = funs[-1]
                fun = parent
                # name_parts = fun.get("name").split("_")
                full_fun_name = fun.get("name", "unnamed_function")
                fun_name = arguments[1][2:]
                if fun_name.find("(") > -1:
                    fun_name = fun_name[: fun_name.find("(")]

                if full_fun_name.endswith("_%s" % fun_name):
                    class_name = full_fun_name.replace("_%s" % fun_name, "")
                else:
                    class_name = full_fun_name.split("_")[0]
                arguments[1] = arguments[1][2:]
                arguments[0:1] = ["qsa._super('%s', %s)" % (class_name, ".".join(arguments[0:1]))]
        if arguments[0] == "qsa.File":
            arguments[0] = "qsa.FileStatic"
        elif arguments[0] == "qsa.Dir":
            arguments[0] = "qsa.DirStatic"
        elif arguments[0] == "qsa.Process":
            arguments[0] = "qsa.ProcessStatic"
        replace_members = [
            "toString()",
            "length",
            "text",
            "join",
            "push",
            "date",
            "isEmpty()",
            "left",
            "right",
            "mid",
            "charAt",
            "charCodeAt",
            "arg",
            "substring",
            "attributeValue",
            "match",
            "replace",
            "search",
            "shift()",
            "sort",
            "splice",
        ]

        for member in replace_members:
            for idx, arg1 in enumerate(arguments):
                if member == arg1 or arg1.startswith(member + "("):
                    expr = arg_expr[idx]
                    part1 = arguments[:idx]
                    try:
                        part2 = arguments[idx + 1 :]
                    except IndexError:
                        part2 = []  # Para los que son últimos y no tienen parte adicional
                    if member == "toString()":
                        arguments = ["qsa.parseString(%s)" % ".".join(part1)] + part2
                    elif member == "shift()":
                        arguments = ["%s.pop(0)" % ".".join(part1)] + part2
                    #    arguments = ["str(%s)" % (".".join(part1))] + part2
                    elif member == "isEmpty()":
                        arguments = ["%s == ''" % (".".join(part1))] + part2
                    elif member == "left":
                        value = arg1[5:]
                        value = value[: len(value) - 1]
                        arguments = ["%s[0:%s]" % (".".join(part1), value)] + part2
                    elif member == "right":
                        value = arg1[6:]
                        value = value[: len(value) - 1]
                        arguments = [
                            "%s[(len(%s) - (%s)):]" % (".".join(part1), ".".join(part1), value)
                        ] + part2
                    elif member == "substring":
                        value = arg1[10:]
                        value = value[: len(value) - 1]
                        value = value.replace(",", ":")
                        arguments = ["%s[ %s]" % (".".join(part1), value)] + part2
                    elif member == "mid":
                        value = arg1[4:]
                        value = value[: len(value) - 1]
                        if value.find(",") > -1:
                            if (value.find("(") < value.find(",")) and value.find(")") < value.find(
                                ","
                            ):
                                si_, sk_ = value.split(",")
                                arguments = [
                                    "%s[%s:%s + %s]" % (".".join(part1), si_, si_, sk_)
                                ] + part2
                                continue
                            # if (len(value.split(",")) == 2 and value.find("(") == -1) or value.find("(") < value.find(","):
                            #    i, l = value.split(",")
                            #    if i.find("(") > -1 and i.find(")") == -1:
                            #        i = "%s)" % i
                            #        l = l.repalce(")", "")
                            else:
                                si_ = "0"
                                sk_ = value

                        else:
                            si_ = "0"
                            sk_ = value

                        value = "%s + %s:" % (si_, sk_)
                        arguments = ["%s[%s]" % (".".join(part1), value)] + part2

                    elif member == "length":
                        value = arg1[7:]
                        value = value[: len(value) - 1]
                        arguments = ["qsa.length(%s)" % (".".join(part1))] + part2
                    elif member == "charAt":
                        value = arg1[7:]
                        value = value[: len(value) - 1]
                        arguments = ["%s[%s]" % (".".join(part1), value)] + part2
                    elif member == "search":
                        if not part1:
                            # Algunas veces ve una variable "search" y cree que es una llamada
                            continue
                        value = arg1[7:]
                        value = value[: len(value) - 1]
                        arguments = ["%s.find('%s')" % (".".join(part1), value)] + part2
                    elif member == "charCodeAt":
                        value = arg1[11:]
                        value = value[: len(value) - 1]
                        arguments = ["ord(%s[%s])" % (".".join(part1), value)] + part2
                    elif member == "arg":
                        value = arg1[4:]
                        value = value[: len(value) - 1]
                        new_part_1 = ".".join(part1)
                        str_value = "str(" + value + ")"
                        if new_part_1.find(str_value) > -1:
                            arguments = [new_part_1]
                        else:
                            new_part_2 = ""
                            if len(part2) > 0:
                                for i in range(len(part2)):

                                    part2[i] = str(part2[i]).replace("arg(", "str(")
                                new_part_2 = ", " + ", ".join(part2)
                            new_part_1 = re.sub(r"%\d", "%s", new_part_1)
                            arguments = [
                                "%s %% (str(%s" % (new_part_1, value + ")" + new_part_2 + ")")
                            ]
                    elif member == "join":
                        value = arg1[5:]
                        value = value[: len(value) - 1] or '""'
                        arguments = ["%s.join(%s)" % (value, ".".join(part1))] + part2
                    elif member == "match":
                        value = arg1[6:]
                        value = value[: len(value) - 1]
                        arguments = ["qsa.re.match(%s, %s)" % (value, ".".join(part1))] + part2
                    elif member == "sort":
                        value = arg1[5:]
                        value = value[: len(value) - 1] or ""
                        arguments = ["qsa.Sort(%s).sort_(%s)" % (value, ".".join(part1))] + part2
                    elif member == "splice":
                        value = arg1[7:]
                        value = value[: len(value) - 1] or ""
                        arguments = ["qsa.splice(%s, %s)" % (".".join(part1), value)] + part2
                    elif member == "push":
                        value = arg1[5:]
                        value = value[: len(value) - 1]
                        arguments = ["%s.append(%s)" % (".".join(part1), value)] + part2
                    elif member == "attributeValue":
                        value = arg1[15:]
                        value = value[: len(value) - 1]
                        arguments = [
                            "%s.attributes().namedItem(%s).nodeValue()" % (".".join(part1), value)
                        ] + part2
                    elif member == "replace":
                        value = arg1[8:-1]
                        part_list = []
                        if value.startswith('","'):
                            part_list.append('","')
                            part_list.append(value[4:])
                        else:
                            part_list = value.split(",")
                            if part_list[1] == ' "':
                                part_list[1] = '","'
                        if part_list[0].find("re.compile") > -1:
                            arguments = [
                                "%s.sub(%s,%s)"
                                % (part_list[0], ",".join(part_list[1:]), ".".join(part1))
                            ] + part2
                        else:
                            # if not part2:
                            # if ".".join(part1) and "replace(" in " ".join(arguments[0:1]):
                            # arguments = ['numeroCSV', 'replace(".", ",")']
                            #    rep_str = arguments[0]
                            #    rep_from_to = arguments[1].replace("replace", "").strip()
                            #    if rep_from_to[0] == "(" and rep_from_to[-1] == ")":
                            #        rep_from_to = rep_from_to[1:-1]

                            #    rep_extra = arguments[2:]
                            # print(arguments)
                            #    arguments = [
                            #        "qsa.replace(%s, %s)" % (rep_str, rep_from_to)
                            #    ] + rep_extra
                            # print(arguments)
                            # print("*")
                            rep_str = arguments[0]
                            rep_from_to = arguments[1].replace("replace", "").strip()
                            if rep_from_to[0] == "(" and rep_from_to[-1] == ")":
                                rep_from_to = rep_from_to[1:-1]

                            rep_extra = arguments[2:]
                            # for r in rep_extra:
                            #    print(r)

                            if (
                                rep_extra
                                and rep_extra[0].startswith("replace")
                                or len(rep_from_to.split(",")) > 2
                            ):
                                continue
                            else:
                                arguments = [
                                    "qsa.replace(%s, %s)" % (rep_str, rep_from_to)
                                ] + rep_extra

                            # Es un regexpr
                        # else:
                        #    if ".".join(part1):
                        #        arguments = ["%s.%s" % (".".join(part1), arg1)] + part2

                    else:
                        if ".".join(part1):
                            arguments = ["%s.%s" % (".".join(part1), arg1)] + part2
                        else:
                            arguments = ["%s" % arg1] + part2
        yield "expr", ".".join(arguments)


class ArrayMember(ASTPython):
    """Process ArrayMember XML tags."""

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        arguments = []
        for number, arg in enumerate(self.elem):
            arg.set("parent_", self.elem)  # type: ignore
            expr = []
            for dtype, data in parse_ast(arg, parent=self).generate(
                isolate=False, is_member=(number == 0)
            ):
                # if data.find(".") > -1:
                #    l = data.split(".")
                #    data = "%s['%s']" % (l[0], l[1])

                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data

            if len(expr) == 0:
                arguments.append("unknownarg")
                yield "debug", "Argument %d not understood" % number
                yield "debug", ET.tostring(arg)  # type: ignore
            else:
                arguments.append(" ".join(expr))

        yield "expr", "%s[%s]" % (arguments[0], arguments[1])


class Value(ASTPython):
    """Process Value XML tags."""

    def generate(self, isolate: bool = True, **kwargs) -> ASTGenerator:
        """Generate python code."""

        if isolate:
            yield "expr", "("
        for child in self.elem:
            child.set("parent_", self.elem)  # type: ignore
            child_ast = parse_ast(child, parent=self)
            for dtype, data in child_ast.generate():
                if data is None:
                    raise ValueError(ET.tostring(child))
                yield dtype, data
        if isolate:
            yield "expr", ")"


class Expression(ASTPython):
    """Process Expression XML tags."""

    DEBUGFILE_LEVEL = 10
    tags = ["base_expression", "math_expression"]

    def generate(self, isolate: bool = True, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        if isolate:
            yield "expr", "("
        coerce_string_mode = False
        if self.elem.findall('OpMath[@type="PLUS"]'):
            if self.elem.findall('Constant[@type="String"]'):
                coerce_string_mode = True
        if coerce_string_mode:
            yield "expr", "qsa.ustr("

        found_in = False
        expr = []
        for child in self.elem:
            child.set("parent_", self.elem)  # type: ignore
            if coerce_string_mode and child.tag == "OpMath":
                if child.get("type") == "PLUS":
                    expr.append(["expr", ","])
                    continue

            for dtype, data in parse_ast(child, parent=self).generate():
                expr.append([dtype, data])

                if found_in:
                    idx = len(expr) - 2  # penúltimo
                    cadena = "( hasattr(%s, %s) or %s in %s )" % (
                        expr[idx + 1][1],
                        expr[idx - 1][1],
                        expr[idx - 1][1],
                        expr[idx + 1][1],
                    )
                    new_expr = expr[0 : idx - 1]  # hasta anterior a in.
                    new_expr += [["expr", valor] for valor in cadena.split(" ")]
                    expr = new_expr

                    found_in = False

                if data == "in":
                    found_in = True
                else:
                    found_in = False

        for dtype, data in expr:
            yield dtype, data

        if coerce_string_mode:
            yield "expr", ")"
        if isolate:
            yield "expr", ")"


class Parentheses(ASTPython):
    """Process Parentheses XML tags."""

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        yield "expr", "("
        for child in self.elem:
            child.set("parent_", self.elem)  # type: ignore
            for dtype, data in parse_ast(child, parent=self).generate(isolate=False):
                yield dtype, data
        yield "expr", ")"


class Delete(ASTPython):
    """Process Delete XML tags."""

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        expr = []
        for child in self.elem:
            child.set("parent_", self.elem)  # type: ignore
            for dtype, data in parse_ast(child, parent=self).generate(isolate=False):
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
        yield "line", "del %s" % (" ".join(expr))


class OpTernary(ASTPython):
    """Process OpTernary XML tags."""

    DEBUGFILE_LEVEL = 3

    def generate(self, isolate: bool = False, **kwargs: Any) -> ASTGenerator:
        """
        Generate python code.

        Example XML:
            <OpTernary>
                <Parentheses>
                    <OpUnary type="LNOT"><Identifier name="codIso"/></OpUnary>
                    <Compare type="LOR"/><Identifier name="codIso"/><Compare type="EQ"/>
                    <Constant delim="&quot;" type="String" value=""/>
                </Parentheses>
                <Constant delim="&quot;" type="String" value="ES"/>
                <Identifier name="codIso"/>
            </OpTernary>
        """
        if_cond = self.elem[0]
        then_val = self.elem[1]
        else_val = self.elem[2]
        yield "expr", "("  # Por seguridad, unos paréntesis
        for dtype, data in parse_ast(then_val, parent=self).generate():
            yield dtype, data
        yield "expr", "if"
        for dtype, data in parse_ast(if_cond, parent=self).generate():
            yield dtype, data
        yield "expr", "else"
        for dtype, data in parse_ast(else_val, parent=self).generate():
            yield dtype, data
        yield "expr", ")"  # Por seguridad, unos paréntesis


class DictObject(ASTPython):
    """Process DictObject XML tags."""

    def generate(self, isolate: bool = False, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        yield "expr", "qsa.AttributeDict({"
        key = True
        for child in self.elem:
            child.set("parent_", self.elem)  # type: ignore
            empty = True
            for dtype, data in parse_ast(child, parent=self).generate():
                empty = False
                if key:
                    if isinstance(data, bool):  # type: ignore [unreachable] # noqa: F821
                        yield dtype, data  # type: ignore [unreachable] # noqa: F821
                    else:
                        yield dtype, "'%s'" % data if not data.startswith(
                            ("'", '"')
                        ) else "%s" % data
                    key = False
                else:
                    yield dtype, data
            # Como en Python la coma final la ignora, pues la ponemos.

            if not empty:
                yield "expr", ","
            key = True

        yield "expr", "})"


class DictElem(ASTPython):
    """Process DictElem XML tags."""

    def generate(self, isolate: bool = False, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        # Clave:
        for dtype, data in parse_ast(self.elem[0], parent=self).generate():
            yield dtype, data
        yield "expr", ":"
        # Valor:
        for dtype, data in parse_ast(self.elem[1], parent=self).generate():
            yield dtype, data


class OpUnary(ASTPython):
    """Process OpUnary XML tags."""

    DEBUGFILE_LEVEL = 3

    def generate(self, isolate: bool = False, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        ctype = self.elem.get("type", "NONE")
        if ctype == "LNOT":
            yield "expr", "not"
        elif ctype == "MINUS":
            yield "expr", "-"
        elif ctype == "PLUS":
            yield "expr", "+"
        else:
            yield "expr", ctype
        if isolate:
            yield "expr", "("
        for child in self.elem:
            child.set("parent_", self.elem)  # type: ignore
            for dtype, data in parse_ast(child, parent=self).generate():
                yield dtype, data
        if isolate:
            yield "expr", ")"


class New(ASTPython):
    """Process New XML tags."""

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        for child in self.elem:
            child.set("parent_", self.elem)  # type: ignore
            for dtype, data in parse_ast(child, parent=self).generate():
                if dtype != "expr":
                    yield dtype, data
                    continue
                if child.tag == "Identifier":
                    data = data + "()"
                ident = data[: data.find("(")]
                if ident.find(".") == -1:
                    parent_class = cast(ET.Element, self.elem.get("parent_"))
                    # classIdent_ = False
                    while parent_class is not None:
                        if parent_class.tag == "Source":
                            for item in parent_class.findall("Class"):
                                if item.get("name") == ident:
                                    # classIdent_ = True
                                    break
                        parent_class = cast(ET.Element, parent_class.get("parent_"))

                yield dtype, data


class Constant(ASTPython):
    """Process Constant XML tags."""

    DEBUGFILE_LEVEL = 10

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        ctype = self.elem.get("type")
        value = self.elem.get("value")
        self.debug("ctype: %r -> %r" % (ctype, value))
        if ctype is None or value is None:
            for child in self.elem:
                if child.tag == "list_constant":
                    # TODO/FIXME:: list_constant debe ser ELIMINADO o CONVERTIDO por postparse.py
                    # .... este generador convertirá todos los arrays en vacíos, sin importar
                    # .... si realmente tienen algo.
                    yield "expr", "[]"

                elif child.tag == "regex":
                    val = ""
                    for dtype, data in parse_ast(child, parent=self).generate(isolate=False):
                        if data:
                            val += data
                    yield "expr", 'qsa.re.compile(r"/%s/i")' % val

                elif child.tag == "regexbody":
                    val = ""
                    for dtype, data in parse_ast(child, parent=self).generate(isolate=False):
                        if data:
                            val += data
                    yield "expr", 'r"%s"' % val

                elif child.tag == "CallArguments":
                    arguments = []
                    for number, arg in enumerate(child):
                        expr = []
                        for dtype, data in parse_ast(arg, parent=self).generate(isolate=False):
                            if dtype == "expr":
                                expr.append(data)
                            else:
                                yield dtype, data
                        if len(expr) == 0:
                            arguments.append("unknownarg")
                            yield "debug", "Argument %d not understood" % number
                            yield "debug", ET.tostring(arg)  # type: ignore
                        else:
                            arguments.append(" ".join(expr))

                    yield "expr", "qsa.Array([%s])" % (", ".join(arguments))
                else:
                    for dtype, data in parse_ast(child, parent=self).generate(isolate=False):
                        yield dtype, data
            return
        if ctype == "String":
            delim = self.elem.get("delim")
            if delim == "'":
                yield "expr", "'%s'" % value
            else:
                yield "expr", '"%s"' % value
        elif ctype == "Number":
            value = value.lstrip("0")
            if value == "":
                value = "0"
            yield "expr", value
        else:
            yield "expr", value


class Identifier(ASTPython):
    """Process Identifier XML tags."""

    DEBUGFILE_LEVEL = 0

    def generate(self, is_member: bool = False, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        varname = self.elem.get("name", "unnamed_var")
        name = self.local_var(varname, is_member=is_member)
        yield "expr", name


class regex(ASTPython):  # pylint: disable=invalid-name
    """Process regex XML tags."""

    DEBUGFILE_LEVEL = 10

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        child = self.elem.find("regexbody")
        # args_ = self.elem.items()
        if not child:
            return

        for arg in child:
            for dtype, data in parse_ast(arg, parent=self).generate(isolate=False):
                yield "expr", data


class regexbody(ASTPython):  # pylint: disable=invalid-name
    """Process regexbody XML tags."""

    DEBUGFILE_LEVEL = 10

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        for arg in self.elem:
            for dtype, data in parse_ast(arg, parent=self).generate(isolate=False):
                yield "expr", data


class regexchar(ASTPython):  # pylint: disable=invalid-name
    """Process regexchar XML tags."""

    DEBUGFILE_LEVEL = 10

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        val = self.elem.get("arg00", "")
        ret = None
        if val == "XOR":
            ret = "^"
        elif val == "LBRACKET":
            ret = "["
        elif val == "RBRACKET":
            ret = "]"
        elif val == "MINUS":
            ret = "-"
        elif val == "PLUS":
            ret = "+"
        elif val == "BACKSLASH":
            ret = "\\"
        elif val == "COMMA":
            ret = ","
        elif val == "PERIOD":
            ret = "."
        elif val == "MOD":
            ret = "%"
        elif val == "RBRACE":
            ret = "}"
        elif val == "LBRACE":
            ret = "{"
        elif val == "DOLLAR":
            ret = "$"
        elif val == "COLON":
            ret = ":"
        elif val == "CONDITIONAL1":
            ret = "?"
        elif val == "AT":
            ret = "@"
        elif val == "OR":
            ret = "|"
        elif val == "RPAREN":
            ret = ")"
        elif val == "LPAREN":
            ret = "("
        else:
            if val.find(":") > -1:
                val_l: str = val.split(":")[1]
                ret = val_l.replace("'", "")
            else:
                LOGGER.warning("regexchar:: item desconocido %s", val)
        if ret:
            yield "exp", ret


class OpUpdate(ASTPython):
    """Process OpUpdate XML tags."""

    DEBUGFILE_LEVEL = 3

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        ctype = self.elem.get("type", "NONE")
        if ctype == "EQUALS":
            yield "expr", "="
        elif ctype == "PLUSEQUAL":
            yield "expr", "+="
        elif ctype == "MINUSEQUAL":
            yield "expr", "-="
        elif ctype == "TIMESEQUAL":
            yield "expr", "*="
        elif ctype == "DIVEQUAL":
            yield "expr", "/="
        elif ctype == "MODEQUAL":
            yield "expr", "%="
        else:
            yield "expr", "OpUpdate." + ctype


class Compare(ASTPython):
    """Process Compare XML tags."""

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        ctype = self.elem.get("type", "NONE")
        if ctype == "GT":
            yield "expr", ">"
        elif ctype == "LT":
            yield "expr", "<"
        elif ctype == "LE":
            yield "expr", "<="
        elif ctype == "GE":
            yield "expr", ">="
        elif ctype == "EQ":
            yield "expr", "=="
        elif ctype == "NE":
            yield "expr", "!="
        elif ctype == "EQQ":
            yield "expr", "is"
        elif ctype == "NEQ":
            yield "expr", "is not"
        elif ctype == "IN":
            yield "expr", "in"
        elif ctype == "LOR":
            yield "expr", "or"
        elif ctype == "LAND":
            yield "expr", "and"
        else:
            yield "expr", "Compare." + ctype


class OpMath(ASTPython):
    """Process OpMath XML tags."""

    DEBUGFILE_LEVEL = 3

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        ctype = self.elem.get("type", "NONE")
        if ctype == "PLUS":
            yield "expr", "+"
        elif ctype == "MINUS":
            yield "expr", "-"
        elif ctype == "TIMES":
            yield "expr", "*"
        elif ctype == "DIVIDE":
            yield "expr", "/"
        elif ctype == "MOD":
            yield "expr", "%"
        elif ctype == "XOR":
            yield "expr", "^"
        elif ctype == "OR":
            yield "expr", "or"
        elif ctype == "LSHIFT":
            yield "expr", "<<"
        elif ctype == "RSHIFT":
            yield "expr", ">>"
        elif ctype == "AND":
            yield "expr", "&"
        else:
            yield "expr", "Math." + ctype


class DeclarationBlock(ASTPython):
    """Process DeclarationBlock XML tags."""

    def generate(self, **kwargs: Any) -> ASTGenerator:
        """Generate python code."""

        # mode = self.elem.get("mode")
        is_constructor = self.elem.get("constructor")
        is_definition = True if self.elem.get("definition") else False
        # if mode == "CONST": yield "debug", "Const Declaration:"
        for var in self.elem:
            var.set("parent_", self.elem)  # type: ignore
            expr = []
            for dtype, data in parse_ast(var, parent=self).generate(force_value=True):
                if dtype == "expr":
                    if data is None:
                        raise ValueError(ET.tostring(var))
                    expr.append(data)
                else:
                    yield dtype, data
            if is_constructor:

                if expr[0] in list(self.source.locals):
                    if expr[0] not in ["form", "iface"]:
                        # LOGGER.warning("Pasando de %s", expr[0])
                        continue

                expr[0] = "self." + expr[0]
                # print(1, expr[0], self.elem.get("parent_").tag, self.source.locals)
                # print(2, data)
            if is_definition:
                if expr[0] == "form" and expr[2] == "self":
                    expr[1] = ":"
                    expr[2] = '"qsa.FormDBWidget"'

                # Transform: ['iface', '=', 'ifaceCtx(self)']
                # To: ['iface', ':', 'ifaceCtx']
                else:
                    if len(expr) > 2:
                        if expr[2] == "=":
                            expr[1] = " : Any"
                            expr[2] = " %s" % expr[2].replace("(self)", "")
                        else:
                            expr[1] = " :"
                            expr[2] = ' "%s"' % expr[2].replace("(self)", "")
            else:
                if expr[0] == "ctx" and expr[1].find("qsa.Object") > -1:
                    expr[1] = ': "FormInternalObj"'
            yield "line", " ".join(expr)


# ----- keep this one at the end.
class Unknown(ASTPython):
    """Process Unknown XML tags."""

    @classmethod
    def can_process_tag(cls, tagname: str) -> bool:
        """Catch all and process it for reporting errors."""
        return True


# -----------------


def astparser_for(elem: ET.Element) -> ASTPythonBase:
    """Construct proper AST parser for given XML element."""
    for cls in ASTPythonFactory.ast_class_types:
        if cls.can_process_tag(elem.tag):
            return cls(elem)
    raise ValueError("No suitable class for %r" % elem.tag)


def parse_ast(elem: ET.Element, parent: Optional[ASTPython] = None) -> ASTPythonBase:
    """Parse XML Element."""
    elemparser = astparser_for(elem)
    elemparser.parent = parent

    if isinstance(parent, Source):
        elemparser.source = parent
    elif parent:
        elemparser.source = parent.source
    else:
        elemparser.source = None

    if isinstance(elemparser, Source):
        if elemparser.source is not None:
            if isinstance(parent, (Switch, If, While, With)):
                # For certain elements, use the same locals, don't copy.
                # this will share locals.
                elemparser.locals = elemparser.source.locals
                elemparser.locals_transform = elemparser.source.locals_transform
            else:
                elemparser.locals = elemparser.source.locals.copy()
                elemparser.locals_transform = elemparser.source.locals_transform.copy()
        elemparser.source = elemparser

    return elemparser


def file_template(ast: ET.Element, import_refs: Dict[str, Tuple[str, str]] = {}) -> ASTGenerator:
    """Create a new file template."""

    from pineboolib.application import PINEBOO_VER

    yield "line", "# -*- coding: utf-8 -*-"
    yield "line", "# Translated with pineboolib %s" % PINEBOO_VER
    yield "line", "from typing import TYPE_CHECKING, Any, Union"

    if not STRICT_MODE:
        yield "line", "from pineboolib.qsa.qsa import *  # noqa: F403"
    yield "line", "from pineboolib.qsa import qsa"
    # yield "line", "from pineboolib.qsaglobals import *"
    for alias, (path, name) in import_refs.items():
        yield "line", "from %s import %s as %s" % (path, name, alias)
    yield "line", ""
    yield "line", "# /** @file */"
    yield "line", ""
    yield "line", ""

    sourceclasses = ET.Element("Source")
    for cls_ in ast.findall("Class"):
        # LOGGER.warning("Element %s type(%s)", cls, type(cls_))
        # cls_.set("parent_", cast(str, ast))  # FIXME: AST is an XML Element, not a string.
        sourceclasses.append(cast(ET.Element, cls_))

    mainclass = ET.SubElement(
        sourceclasses, "Class", name="FormInternalObj", extends="qsa.FormDBWidget"
    )
    mainsource = ET.SubElement(mainclass, "Source")

    constructor = ET.SubElement(mainsource, "Function", name="_class_init")
    # args = etree.SubElement(constructor, "Arguments")
    csource = ET.SubElement(constructor, "Source")

    for child in ast:
        if child.tag != "Function":
            if child.tag != "Class":  # Limpiamos las class, se cuelan desde el cambio de xml
                def_iface = copy.deepcopy(child)
                def_iface.set("definition", "1")
                child.set("constructor", "1")
                csource.append(child)
                mainsource.insert(0, def_iface)
        else:
            mainsource.append(child)

    for dtype, data in parse_ast(sourceclasses).generate():
        yield dtype, data

    # yield "line", ""
    # yield "line", "if TYPE_CHECKING:"
    # yield "line", '    form: "FormInternalObj" = FormInternalObj()'
    # yield "line", "    iface = form.iface"
    # yield "line", "else:"
    # yield "line", "    form = None"


def expression_template(
    ast: ET.Element, import_refs: Dict[str, Tuple[str, str]] = {}  # pylint: disable=unused-argument
) -> ASTGenerator:
    """Create a new file template."""

    for dtype, data in parse_ast(ast).generate():
        yield dtype, data


def write_python_file(
    fobj: TextIO, ast: ET.Element, import_refs: Dict[str, Tuple[str, str]] = {}
) -> None:
    """Write python file."""
    template_list: Dict[str, Callable[[ET.Element, Dict[str, Tuple[str, str]]], ASTGenerator]] = {
        "file_template": file_template,
        "expression_template": expression_template,
    }
    indent: List[str] = []
    indent_text = "    "
    last_line_for_indent: Dict[int, int] = {}
    numline = 0
    ASTPython.numline = 1
    last_dtype = None

    parser_template = template_list[ast.get("parser-template", default="file_template")]

    for dtype, data in parser_template(ast, import_refs):
        # if isinstance(data, bytes):
        #    data = data.decode("UTF-8", "replace")
        line = None
        if dtype == "line":
            line = data
            numline += 1
            try:
                lines_since_last_indent = numline - last_line_for_indent[len(indent)]
            except KeyError:
                lines_since_last_indent = 0
            if lines_since_last_indent > 4:
                ASTPython.numline += 1
                fobj.write("\n")
            last_line_for_indent[len(indent)] = numline
        elif dtype == "debug":
            line = "# DEBUG:: %s" % data
            # print(numline, line)
        elif dtype == "expr":
            line = "# EXPR??:: " + data
        elif dtype == "line+1":
            line = "# LINE+1??:: " + data
        elif dtype == "begin":
            # line = "# BEGIN:: " + data
            indent.append(data)
            last_line_for_indent[len(indent)] = numline
        elif dtype == "end":
            if last_dtype == "begin":
                ASTPython.numline += 1
                fobj.write((len(indent) * indent_text) + "pass\n")
                last_line_for_indent[len(indent)] = numline

            if data not in ["block-if"]:
                # line = "# END:: " + data
                pass
            endblock = indent.pop()
            if endblock != data:
                line = "# END-ERROR!! was %s but %s found. (%s)" % (endblock, data, repr(indent))

        if line is not None:
            ASTPython.numline += 1
            txtline = (len(indent) * indent_text) + line
            fobj.write(txtline.rstrip() + "\n")

        if dtype == "end":
            if data.split("-")[1] in ["class", "def", "else", "except"]:
                ASTPython.numline += 1
                fobj.write("\n")
                last_line_for_indent[len(indent)] = numline
        last_dtype = dtype


def pythonize(filename: str, destfilename: str, debugname: Optional[str] = None) -> None:
    """Convert given QS filename into Python saved as destfilename."""
    # bname = os.path.basename(filename)
    ASTPython.debug_file = open(debugname, "w", encoding="UTF-8") if debugname else None
    parser = ET.XMLParser(encoding="UTF-8")
    try:
        ast_tree = ET.parse(open(filename, "r", encoding="UTF-8", errors="replace"), parser)
    except Exception:
        print("filename:", filename)
        raise
    ast = ast_tree.getroot()

    file_ = open(destfilename, "w", encoding="UTF-8")
    write_python_file(file_, ast)
    file_.close()
    if black:
        try:
            new_code = black.format_file_contents(
                pathlib.Path(destfilename).read_text(encoding="UTF-8"),
                fast=True,
                mode=BLACK_FILEMODE,
            )
        except black.NothingChanged:
            # The file we saved earlier is already good.
            return

        file_ = open(destfilename, "w", encoding="UTF-8")
        file_.write(new_code)
        file_.close()


def pythonize2(root_ast: ET.Element, known_refs: Dict[str, Tuple[str, str]] = {}) -> str:
    """Convert AST into Python. Faster version of pythonize as does not read/save XML."""
    from io import StringIO

    ASTPython.debug_file = None
    ident: ET.Element
    ident_set = set()
    if known_refs:
        for ident in root_ast.findall(".//Identifier[@name]"):
            name = ident.get("name")
            if name is not None:
                if name in known_refs:
                    ident_set.add(name)

    known_refs_found: Dict[str, Tuple[str, str]] = {k: known_refs[k] for k in ident_set}
    file_ = StringIO()
    write_python_file(file_, root_ast, import_refs=known_refs_found)
    unformatted_code = file_.getvalue()
    if unformatted_code and black:
        try:
            new_code = black.format_file_contents(unformatted_code, fast=True, mode=BLACK_FILEMODE)
        except black.NothingChanged:
            new_code = unformatted_code
    else:
        new_code = unformatted_code
    return new_code


def main() -> None:
    """Run main program."""
    parser = optparse.OptionParser()
    parser.add_option(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        default=True,
        help="don't print status messages to stdout",
    )

    parser.add_option(
        "--optdebug",
        action="store_true",
        dest="optdebug",
        default=False,
        help="debug optparse module",
    )

    parser.add_option(
        "--debug",
        action="store_true",
        dest="debug",
        default=False,
        help="prints lots of useless messages",
    )

    parser.add_option("--path", dest="storepath", default=None, help="store PY results in PATH")

    (options, args) = parser.parse_args()
    if options.optdebug:
        print(options, args)

    for filename in args:
        bname = os.path.basename(filename)
        if options.storepath:
            destname = os.path.join(options.storepath, bname + ".py")
        else:
            destname = filename + ".py"
        pythonize(filename, destname)


if __name__ == "__main__":
    main()
