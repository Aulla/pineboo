#!/usr/bin/python
# -*- coding: utf-8 -*-
# ------ Pythonyzer ... reads XML AST created by postparse.py and creates an equivalent Python file.
from optparse import OptionParser
import os
import os.path
import re
from xml.etree import ElementTree
from typing import Any, Generator, Optional, Tuple, Type, List


def id_translate(name) -> Any:
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
    ]
    if name in python_keywords:
        return name + "_"
    if name == "false":
        name = "False"
    if name == "true":
        name = "True"
    if name == "null":
        name = "None"
    if name == "unknown":
        name = "None"
    if name == "undefined":
        name = "None"
    if name == "this":
        name = "self"

    if name == "startsWith":
        name = "startswith"
    if name == "endsWith":
        name = "endswith"
    if name == "lastIndexOf":
        name = "rfind"
    # if name == "File":
    #    name = "qsatype.File"
    # if name == "Dir":
    #    name = "qsatype.Dir"
    if name == "findRev":
        name = "find"
    if name == "toLowerCase":
        name = "lower"
    if name == "toUpperCase":
        name = "upper"
    # if name == "Process":
    #    name = "qsatype.Process"
    return name


cont_switch = 0
cont_do_while = 0


class ASTPythonBase(object):
    @classmethod
    def can_process_tag(self, tagname) -> Any:
        return False


class ASTPythonFactory(type):
    ast_class_types: List[Type[ASTPythonBase]] = []

    def __init__(cls, name, bases, dct) -> None:
        if isinstance(cls, ASTPythonBase):
            ASTPythonFactory.ast_class_types.append(cls)
        super().__init__(name, bases, dct)


class ASTPython(ASTPythonBase, metaclass=ASTPythonFactory):
    tags = []
    debug_file = None
    generate_depth = 0
    numline = 0

    @classmethod
    def can_process_tag(self, tagname) -> Any:
        return self.__name__ == tagname or tagname in self.tags

    def __init__(self, elem) -> None:
        self.elem = elem
        self.internal_generate = self.generate
        if self.debug_file:
            self.generate = self._generate

    def debug(self, text) -> None:
        if self.debug_file is None:
            return
        splen = ASTPython.generate_depth
        retlen = 0
        if splen > self.generate_depth:
            retlen, splen = splen - self.generate_depth, self.generate_depth
        if retlen > 0:
            sp = " " * (splen - 1) + "<" + "-" * retlen
        else:
            sp = " " * splen
        cname = self.__class__.__name__
        self.debug_file.write("%04d%s%s: %s\n" % (ASTPython.numline, sp, cname, text.encode("UTF-8")))

    def polish(self) -> "ASTPython":
        return self

    def generate(self, **kwargs):
        yield "debug", "* not-known-seq * %s" % ElementTree.tostring(self.elem, encoding="UTF-8")

    def _generate(self, **kwargs) -> Generator[Tuple[str, str], Any, None]:
        self.debug("begin-gen")
        ASTPython.generate_depth += 1
        self.generate_depth = ASTPython.generate_depth
        for dtype, data in self.internal_generate(**kwargs):
            self.debug("%s: %r" % (dtype, data))
            yield dtype, data
        ASTPython.generate_depth -= 1
        self.debug("end-gen")


class Source(ASTPython):
    def generate(self, break_mode=False, include_pass=True, **kwargs):
        elems = 0
        after_lines = []
        for child in self.elem:
            # yield "debug", "<%s %s>" % (child.tag, repr(child.attrib))
            child.set("parent_", self.elem)
            for dtype, data in parse_ast(child).generate(break_mode=break_mode, plusplus_as_instruction=True):
                if dtype == "line+1":
                    after_lines.append(data)
                    continue
                if dtype == "line":
                    elems += 1
                yield dtype, data
                if dtype == "line" and after_lines:
                    for line in after_lines:
                        elems += 1
                        yield dtype, line
                    after_lines = []
                if dtype == "break":
                    for line in after_lines:
                        elems += 1
                        yield "line", line

        for line in after_lines:
            elems += 1
            yield "line", line
        if elems == 0 and include_pass:
            yield "line", "pass"


classesDefined = []


class Class(ASTPython):
    def generate(self, **kwargs):
        name = self.elem.get("name")
        extends = self.elem.get("extends", "object")

        yield "line", "#/** @class_declaration %s */" % name
        yield "line", "class %s(%s):" % (name, extends)
        yield "begin", "block-class-%s" % (name)
        for source in self.elem.findall("Source"):
            source.set("parent_", self.elem)
            classesDefined.clear()
            for obj in parse_ast(source).generate():
                yield obj
        yield "end", "block-class-%s" % (name)


class Function(ASTPython):
    def generate(self, **kwargs):
        _name = self.elem.get("name")
        if _name:
            name = id_translate(_name)
        else:
            # Anonima:
            name = "_"
        withoutself = self.elem.get("withoutself")
        parent = self.elem.get("parent_")
        grandparent = None
        if parent is not None:
            grandparent = parent.get("parent_")

        if grandparent and grandparent.get("name") == "FormInternalObj":
            className = name.split("_")[0]
            if className not in classesDefined:
                if className == "":
                    yield "line", ""
                    className = "FormInternalObj"
                yield "line", "#/** @class_definition %s */" % className
                classesDefined.append(className)

        # returns = self.elem.get("returns", None)

        arguments = []
        if not withoutself:
            if grandparent is not None:
                if grandparent.tag == "Class":
                    arguments.append("self")
                    if name == grandparent.get("name"):
                        name = "__init__"
            else:
                arguments.append("self")
        for n, arg in enumerate(self.elem.findall("Arguments/*")):
            expr = []
            arg.set("parent_", self.elem)
            for dtype, data in parse_ast(arg).generate():
                if dtype == "expr":
                    expr.append(id_translate(data))
                else:
                    yield dtype, data
            if len(expr) == 0:
                arguments.append("unknownarg")
                yield "debug", "Argument %d not understood" % n
                yield "debug", ElementTree.tostring(arg)
            else:
                if len(expr) == 1:
                    expr += ["=", "None"]
                arguments.append("".join(expr))

        yield "line", "def %s(%s):" % (name, ", ".join(arguments))
        yield "begin", "block-def-%s" % (name)
        # if returns:  yield "debug", "Returns: %s" % returns
        for source in self.elem.findall("Source"):
            source.set("parent_", self.elem)
            for obj in parse_ast(source).generate():
                yield obj
        yield "end", "block-def-%s" % (name)


class FunctionAnon(Function):
    pass


class FunctionCall(ASTPython):
    def generate(self, **kwargs):
        name = id_translate(self.elem.get("name"))
        parent = self.elem.get("parent_")
        # data_ = None
        if name == "":
            arg = self.elem[0]
            arg.set("parent_", self.elem)
            expr = []
            for dtype, data in parse_ast(arg).generate(isolate=False):
                # data_ = data
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
            if len(expr) == 0:
                name = "unknownFn"
                yield "debug", "Function name not understood"
                yield "debug", ElementTree.tostring(arg)
            elif len(expr) > 1:
                name = "unknownFn"
                yield "debug", "Multiple function names"
                yield "debug", repr(expr)
            else:
                name = expr[0]

        if parent and parent.tag == "InstructionCall":
            class_ = None
            p_ = parent
            while p_:
                if p_.tag == "Class":
                    class_ = p_
                    break
                p_ = p_.get("parent_")

            if class_:
                extends = class_.get("extends")
                if extends == name:
                    name = "super(%s, self).__init__" % class_.get("name")
            functions = parent.findall('Function[@name="%s"]' % name)
            for f in functions:
                # yield "debug", "Function to:" + ElementTree.tostring(f)
                name = "self.%s" % name
                break

        arguments = []
        for n, arg in enumerate(self.elem.findall("CallArguments/*")):
            arg.set("parent_", self.elem)
            expr = []
            for dtype, data in parse_ast(arg).generate(isolate=False):
                # data_ = data
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
            if len(expr) == 0:
                arguments.append("unknownarg")
                yield "debug", "Argument %d not understood" % n
                yield "debug", ElementTree.tostring(arg)
            else:
                arguments.append(" ".join(expr))

        yield "expr", "%s(%s)" % (name, ", ".join(arguments))


class FunctionAnonExec(FunctionCall):
    pass


class If(ASTPython):
    def generate(self, break_mode=False, **kwargs):
        main_expr = []
        for n, arg in enumerate(self.elem.findall("Condition/*")):
            arg.set("parent_", self.elem)
            expr = []
            for dtype, data in parse_ast(arg).generate(isolate=False):
                if dtype == "line+1":
                    yield "debug", "Inline update inside IF condition not allowed. Unexpected behavior."
                    dtype = "line"
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
            if len(expr) == 0:
                main_expr.append("False")
                yield "debug", "Expression %d not understood" % n
                yield "debug", ElementTree.tostring(arg)
            else:
                main_expr.append(" ".join(expr))

        yield "line", "if %s:" % (" ".join(main_expr))
        for source in self.elem.findall("Source"):
            source.set("parent_", self.elem)
            yield "begin", "block-if"
            for obj in parse_ast(source).generate(break_mode=break_mode):
                yield obj
            yield "end", "block-if"

        for source in self.elem.findall("Else/Source"):
            source.set("parent_", self.elem)
            yield "line", "else:"
            yield "begin", "block-else"
            for obj in parse_ast(source).generate(break_mode=break_mode):
                yield obj
            yield "end", "block-else"


class TryCatch(ASTPython):
    def generate(self, **kwargs):

        tryblock, catchblock = self.elem.findall("Source")
        tryblock.set("parent_", self.elem)
        catchblock.set("parent_", self.elem)
        yield "line", "try:"
        yield "begin", "block-try"
        for obj in parse_ast(tryblock).generate():
            yield obj
        yield "end", "block-try"

        identifier = None
        for ident in self.elem.findall("Identifier"):
            ident.set("parent_", self.elem)
            expr = []
            for dtype, data in parse_ast(ident).generate(isolate=False):
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
            identifier = " ".join(expr)
        if identifier:
            yield "line", "except Exception as %s:" % (identifier)
        else:
            yield "line", "except Exception:"
        yield "begin", "block-except"
        if identifier:
            # yield "line", "%s = str(%s)" % (identifier, identifier)
            yield "line", "%s = traceback.format_exc()" % (identifier)
        for obj in parse_ast(catchblock).generate(include_pass=identifier is None):
            yield obj
        yield "end", "block-except"


class While(ASTPython):
    def generate(self, **kwargs):
        main_expr = []
        for n, arg in enumerate(self.elem.findall("Condition/*")):
            arg.set("parent_", self.elem)
            expr = []
            for dtype, data in parse_ast(arg).generate(isolate=False):
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
            if len(expr) == 0:
                main_expr.append("False")
                yield "debug", "Expression %d not understood" % n
                yield "debug", ElementTree.tostring(arg)
            else:
                main_expr.append(" ".join(expr))

        yield "line", "while %s:" % (" ".join(main_expr))
        for source in self.elem.findall("Source"):
            source.set("parent_", self.elem)
            yield "begin", "block-while"
            for obj in parse_ast(source).generate():
                yield obj
            yield "end", "block-while"


class DoWhile(ASTPython):
    def generate(self, **kwargs):
        main_expr = []
        for n, arg in enumerate(self.elem.findall("Condition/*")):
            arg.set("parent_", self.elem)
            expr = []
            for dtype, data in parse_ast(arg).generate(isolate=False):
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
            if len(expr) == 0:
                main_expr.append("False")
                yield "debug", "Expression %d not understood" % n
                yield "debug", ElementTree.tostring(arg)
            else:
                main_expr.append(" ".join(expr))
        # TODO .....
        global cont_do_while
        cont_do_while += 1
        key = "%02x" % cont_do_while
        name1st = "s%s_dowhile_1stloop" % key
        yield "line", "%s = True" % (name1st)

        yield "line", "while %s or %s:" % (name1st, " ".join(main_expr))
        for source in self.elem.findall("Source"):
            source.set("parent_", self.elem)
            yield "begin", "block-while"
            yield "line", "%s = False" % (name1st)
            for obj in parse_ast(source).generate():
                yield obj
            yield "end", "block-while"


class For(ASTPython):
    def generate(self, **kwargs):
        init_expr = []
        for n, arg in enumerate(self.elem.findall("ForInitialize/*")):
            arg.set("parent_", self.elem)
            expr = []
            for dtype, data in parse_ast(arg).generate(isolate=False):
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
        for n, arg in enumerate(self.elem.findall("ForIncrement/*")):
            arg.set("parent_", self.elem)
            expr = []
            for dtype, data in parse_ast(arg).generate(isolate=False):
                if dtype == "expr":
                    expr.append(data)
                elif dtype in ["line", "line+1"]:
                    incr_lines.append(data)
                else:
                    yield dtype, data
            if len(expr) > 0:
                incr_expr.append(" ".join(expr))

        main_expr = []
        for n, arg in enumerate(self.elem.findall("ForCompare/*")):
            arg.set("parent_", self.elem)
            expr = []
            for dtype, data in parse_ast(arg).generate(isolate=False):
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
            source.set("parent_", self.elem)
            for obj in parse_ast(source).generate(include_pass=False):
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
    def generate(self, **kwargs):
        list_elem, main_list = "None", "None"
        myelems = []
        for e in self.elem:
            if e.tag == "Source":
                break
            if e.tag == "ForInitialize":
                e = list(e)[0]
            expr = []
            for dtype, data in parse_ast(e).generate(isolate=False):
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
            myelems.append(" ".join(expr))
        list_elem, main_list = myelems
        yield "debug", "FOR-IN: " + repr(myelems)
        yield "line", "for %s in %s:" % (list_elem, main_list)
        for source in self.elem.findall("Source"):
            yield "begin", "block-for-in"
            for obj in parse_ast(source).generate(include_pass=False):
                yield obj
            yield "end", "block-for-in"


class Switch(ASTPython):
    def generate(self, **kwargs):
        global cont_switch
        cont_switch += 1
        key = "%02x" % cont_switch
        name = "s%s_when" % key
        name_pr = "s%s_do_work" % key
        name_pr2 = "s%s_work_done" % key
        main_expr = []
        for n, arg in enumerate(self.elem.findall("Condition/*")):
            arg.set("parent_", self.elem)
            expr = []
            for dtype, data in parse_ast(arg).generate(isolate=False):
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
            if len(expr) == 0:
                main_expr.append("False")
                yield "debug", "Expression %d not understood" % n
                yield "debug", ElementTree.tostring(arg)
            else:
                main_expr.append(" ".join(expr))
        yield "line", "%s = %s" % (name, " ".join(main_expr))
        yield "line", "%s, %s = %s, %s" % (name_pr, name_pr2, "False", "False")
        for scase in self.elem.findall("Case"):
            scase.set("parent_", self.elem)
            value_expr = []
            for n, arg in enumerate(scase.findall("Value")):
                arg.set("parent_", self.elem)
                expr = []
                for dtype, data in parse_ast(arg).generate(isolate=False):
                    if dtype == "expr":
                        expr.append(data)
                    else:
                        yield dtype, data
                if len(expr) == 0:
                    value_expr.append("False")
                    yield "debug", "Expression %d not understood" % n
                    yield "debug", ElementTree.tostring(arg)
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
                source.set("parent_", self.elem)
                for obj in parse_ast(source).generate(break_mode=True):
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
            scasedefault.set("parent_", self.elem)
            yield "line", "if not %s:" % (name_pr2)
            yield "begin", "block-if"
            yield "line", "%s, %s = %s, %s" % (name_pr, name_pr2, "True", "True")
            yield "end", "block-if"
            yield "line", "if %s:" % (name_pr)
            yield "begin", "block-if"
            for source in scasedefault.findall("Source"):
                source.set("parent_", self.elem)
                for obj in parse_ast(source).generate(break_mode=True):
                    if obj[0] == "break":
                        yield "line", "%s = %s  # BREAK" % (name_pr, "False")
                    else:
                        yield obj
            yield "end", "block-if"
        # yield "line", "assert( not %s )" % name_pr
        # yield "line", "assert( %s )" % name_pr2


class With(ASTPython):
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
        "setModeAccess",
        "commitBuffer",
        "commit",
        "refreshBuffer",
        "setNull",
        "setUnLock",
    ]

    def generate(self, **kwargs):
        # key = "%02x" % random.randint(0, 255)
        # name = "w%s_obj" % key
        # yield "debug", "WITH: %s" % key
        variable, source = [obj for obj in self.elem]
        var_expr = []
        for dtype, data in parse_ast(variable).generate(isolate=False):
            if dtype == "expr":
                var_expr.append(data)
            else:
                yield dtype, data
        if len(var_expr) == 0:
            var_expr.append("None")
            yield "debug", "Expression not understood"

        # yield "line", "%s = %s #WITH" % (name, " ".join(var_expr))
        yield "line", " #WITH_START"
        for obj in parse_ast(source).generate(break_mode=True):
            obj_ = None

            # para sustituir los this sueltos por var_expr
            if obj[1].find("self") > -1 and obj[1].find("self.") == -1:
                obj_1 = obj[1].replace("self", " ".join(var_expr))
            else:
                obj_1 = obj[1]

            for t in self.python_keywords:
                if obj_1.startswith(t):
                    obj_1 = "%s.%s" % (" ".join(var_expr), obj_1)
                elif obj_1.find(".") == -1 and obj_1.find(t) > -1:
                    obj_1 = obj_1.replace(t, "%s.%s" % (" ".join(var_expr), t))

            if not obj_:
                obj_ = (obj[0], obj_1)

            yield obj_
        # yield "line", "del %s" % name
        yield "line", " #WITH_END"


class Variable(ASTPython):
    def generate(self, force_value=False, **kwargs):
        name = self.elem.get("name")
        # if name.startswith("colorFun"): print(name)
        yield "expr", id_translate(name)
        values = 0
        # for value in self.elem.findall("Value|Expression"):
        for value in self.elem:
            if value.tag not in ("Value", "Expression"):
                continue
            value.set("parent_", self.elem)
            values += 1
            yield "expr", "="
            expr = 0
            for dtype, data in parse_ast(value).generate(isolate=False):

                # if self.elem.get("type",None) == "Array" and data == "[]":
                if data == "[]":
                    yield "expr", "Array()"
                    expr += 1
                    continue

                if dtype == "expr":
                    expr += 1
                yield dtype, data
            if expr == 0:
                yield "expr", "None"

        dtype = self.elem.get("type", None)
        if (values == 0) and force_value:
            yield "expr", "="
            if dtype is None:
                yield "expr", "None"
            elif dtype == "String":
                yield "expr", '""'
            elif dtype == "Number":
                yield "expr", "0"
            else:
                # parent1 = self.elem.get("parent_")
                # parent2 = parent1.get("parent_")
                # parent3 = parent2.get("parent_")
                # print("**", parent2.tag, parent3.tag)
                # if parent2.tag == "Source" and parent3.tag == "Class":
                #    yield "expr", "None"
                # else:
                if dtype in ("FLSqlCursor", "FLTableDB"):
                    yield "expr", "None"
                else:
                    yield "expr", "%s()" % dtype

        # if dtype and force_value == False: yield "debug", "Variable %s:%s" % (name,dtype)


class InstructionUpdate(ASTPython):
    def generate(self, **kwargs):
        arguments = []
        for n, arg in enumerate(self.elem):
            arg.set("parent_", self.elem)
            expr = []
            for dtype, data in parse_ast(arg).generate(isolate=False):
                if dtype == "expr":
                    if data is None:
                        raise ValueError(ElementTree.tostring(arg))
                    if data == "[]":
                        data = "Array()"
                    expr.append(data)
                else:
                    yield dtype, data
            if len(expr) == 0:
                arguments.append("unknownarg")
                yield "debug", "Argument %d not understood" % n
                yield "debug", ElementTree.tostring(arg)
            else:
                arguments.append(" ".join(expr))

        yield "line", " ".join(arguments)


class InlineUpdate(ASTPython):
    def generate(self, plusplus_as_instruction=False, **kwargs):
        arguments = []
        for n, arg in enumerate(self.elem):
            arg.set("parent_", self.elem)
            expr = []
            for dtype, data in parse_ast(arg).generate(isolate=False):
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
            if len(expr) == 0:
                arguments.append("unknownarg")
                yield "debug", "Argument %d not understood" % n
                yield "debug", ElementTree.tostring(arg)
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


class InstructionCall(ASTPython):
    def generate(self, **kwargs):
        arguments = []
        for n, arg in enumerate(self.elem):
            arg.set("parent_", self.elem)
            expr = []
            for dtype, data in parse_ast(arg).generate():
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
            if len(expr) == 0:
                arguments.append("unknownarg")
                yield "debug", "Argument %d not understood" % n
                yield "debug", ElementTree.tostring(arg)
            else:
                arguments.append(" ".join(expr))
        yield "line", " ".join(arguments)


class Instruction(ASTPython):
    def generate(self, **kwargs):
        arguments = []
        for n, arg in enumerate(self.elem):
            arg.set("parent_", self.elem)
            expr = []
            for dtype, data in parse_ast(arg).generate():
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
            if len(expr) == 0:
                arguments.append("unknownarg")
                yield "debug", "Argument %d not understood" % n
                yield "debug", ElementTree.tostring(arg)
            else:
                arguments.append(" ".join(expr))
        if arguments:
            yield "debug", "Instruction: Maybe parse-error. This class is only for non-understood instructions or empty ones"
            yield "line", " ".join(arguments)


class InstructionFlow(ASTPython):
    def generate(self, break_mode=False, **kwargs):
        arguments = []
        for n, arg in enumerate(self.elem):
            arg.set("parent_", self.elem)
            expr = []
            for dtype, data in parse_ast(arg).generate(isolate=False):
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
            if len(expr) == 0:
                arguments.append("unknownarg")
                yield "debug", "Argument %d not understood" % n
                yield "debug", ElementTree.tostring(arg)
            else:
                arguments.append(" ".join(expr))

        ctype = self.elem.get("type")
        kw = ctype
        if ctype == "RETURN":
            kw = "return"
        if ctype == "BREAK":
            kw = "break"
            if break_mode:
                yield "break", kw + " " + ", ".join(arguments)
                return
        if ctype == "CONTINUE":
            kw = "continue"

        if ctype == "THROW":
            yield "line", "raise Exception(" + ", ".join(arguments) + ")"
            return

        yield "line", kw + " " + ", ".join(arguments)


class Member(ASTPython):
    def generate(self, **kwargs):
        arguments = []
        arg_expr = []
        funs = None
        for n, arg in enumerate(self.elem):
            expr = []
            arg.set("parent_", self.elem)
            for dtype, data in parse_ast(arg).generate():
                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data
            if len(expr) == 0:
                txtarg = "unknownarg"
                yield "debug", "Argument %d not understood" % n
                yield "debug", ElementTree.tostring(arg)
            else:
                txtarg = " ".join(expr)
            arguments.append(txtarg)
            arg_expr.append(expr)

        # Lectura del self.iface.__init
        if len(arguments) >= 3 and arguments[0:2] == ["self", "iface"] and arguments[2].startswith("__"):
            # From: self.iface.__function()
            # to: super(className, self.iface).function()
            parent = self.elem.get("parent_")
            funs = None
            p_ = parent
            while p_:
                if p_.tag == "Function":
                    funs = p_
                    break
                p_ = p_.get("parent_")

            if funs:
                # fun = funs[-1]
                fun = funs
                full_fun_name = fun.get("name")
                fun_name = arguments[2][2:]
                if fun_name.find("(") > -1:
                    fun_name = fun_name[: fun_name.find("(")]

                if full_fun_name.find("_%s" % fun_name):
                    classname = full_fun_name.replace("_%s" % fun_name, "")
                else:
                    classname = full_fun_name.split("_")[0]

                arguments[2] = arguments[2][2:]
                arguments[0:2] = ["super(%s, %s)" % (classname, ".".join(arguments[0:2]))]

        # Lectura del self.iface.__init() al nuevo estilo yeboyebo
        if len(arguments) >= 2 and arguments[0:1] == ["_i"] and arguments[1].startswith("__"):
            # From: self.iface.__function()
            # to: super(className, self.iface).function()
            parent = self.elem.get("parent_")
            funs = None
            p_ = parent
            while p_:
                if p_.tag == "Function":
                    funs = p_
                    break
                p_ = p_.get("parent_")
            if funs:
                # fun = funs[-1]
                fun = funs
                # name_parts = fun.get("name").split("_")
                full_fun_name = fun.get("name")
                fun_name = arguments[1][2:]
                if fun_name.find("(") > -1:
                    fun_name = fun_name[: fun_name.find("(")]

                if full_fun_name.find("_%s" % fun_name):
                    classname = full_fun_name.replace("_%s" % fun_name, "")
                else:
                    classname = full_fun_name.split("_")[0]
                arguments[1] = arguments[1][2:]
                arguments[0:1] = ["super(%s, %s)" % (classname, ".".join(arguments[0:1]))]

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
        ]
        for member in replace_members:
            for idx, arg in enumerate(arguments):
                if member == arg or arg.startswith(member + "("):
                    expr = arg_expr[idx]
                    part1 = arguments[:idx]
                    try:
                        part2 = arguments[idx + 1 :]
                    except IndexError:
                        part2 = []  # Para los que son últimos y no tienen parte adicional
                    if member == "toString()":
                        arguments = ["parseString(%s)" % ".".join(part1)] + part2
                    #    arguments = ["str(%s)" % (".".join(part1))] + part2
                    elif member == "isEmpty()":
                        arguments = ["%s == ''" % (".".join(part1))] + part2
                    elif member == "left":
                        value = arg[5:]
                        value = value[: len(value) - 1]
                        arguments = ["%s[0:%s]" % (".".join(part1), value)] + part2
                    elif member == "right":
                        value = arg[6:]
                        value = value[: len(value) - 1]
                        arguments = ["%s[(len(%s) - (%s)):]" % (".".join(part1), ".".join(part1), value)] + part2
                    elif member == "substring":
                        value = arg[10:]
                        value = value[: len(value) - 1]
                        value = value.replace(",", ":")
                        arguments = ["%s[ %s]" % (".".join(part1), value)] + part2
                    elif member == "mid":
                        value = arg[4:]
                        value = value[: len(value) - 1]
                        if value.find(",") > -1:
                            if (value.find("(") < value.find(",")) and value.find(")") < value.find(","):
                                i, k = value.split(",")
                            # if (len(value.split(",")) == 2 and value.find("(") == -1) or value.find("(") < value.find(","):
                            #    i, l = value.split(",")
                            #    if i.find("(") > -1 and i.find(")") == -1:
                            #        i = "%s)" % i
                            #        l = l.repalce(")", "")
                            else:
                                i = 0
                                k = value

                        else:
                            i = 0
                            k = value

                        value = "%s + %s:" % (i, k)
                        arguments = ["%s[%s]" % (".".join(part1), value)] + part2

                    elif member == "length":
                        value = arg[7:]
                        value = value[: len(value) - 1]
                        arguments = ["qsa_length(%s)" % (".".join(part1))] + part2
                    elif member == "charAt":
                        value = arg[7:]
                        value = value[: len(value) - 1]
                        arguments = ["%s[%s]" % (".".join(part1), value)] + part2
                    elif member == "search":
                        value = arg[7:]
                        value = value[: len(value) - 1]
                        arguments = ["%s.find('%s')" % (".".join(part1), value)] + part2
                    elif member == "charCodeAt":
                        value = arg[11:]
                        value = value[: len(value) - 1]
                        arguments = ["ord(%s[%s])" % (".".join(part1), value)] + part2
                    elif member == "arg":
                        value = arg[4:]
                        value = value[: len(value) - 1]
                        sPart1 = ".".join(part1)
                        strValue = "str(" + value + ")"
                        if sPart1.find(strValue) > -1:
                            arguments = [sPart1]
                        else:
                            sPart2 = ""
                            if len(part2) > 0:
                                for i in range(len(part2)):
                                    part2[i] = str(part2[i]).replace("arg", "str")
                                sPart2 = ", " + ", ".join(part2)
                            sPart1 = re.sub(r"%\d", "%s", sPart1)
                            arguments = ["%s %% (str(%s" % (sPart1, value + ")" + sPart2 + ")")]

                    elif member == "join":
                        value = arg[5:]
                        value = value[: len(value) - 1]
                        arguments = ["%s.join(%s)" % (value, ".".join(part1))] + part2
                    elif member == "match":
                        value = arg[6:]
                        value = value[: len(value) - 1]
                        arguments = ["re.match(%s, %s)" % (value, ".".join(part1))] + part2
                    elif member == "push":
                        value = arg[5:]
                        value = value[: len(value) - 1]
                        arguments = ["%s.append(%s)" % (".".join(part1), value)] + part2
                    elif member == "attributeValue":
                        value = arg[15:]
                        value = value[: len(value) - 1]
                        arguments = ["%s.attributes().namedItem(%s).nodeValue()" % (".".join(part1), value)] + part2
                    elif member == "replace":
                        value = arg[8:-1]
                        part_list = []
                        if value.startswith('","'):
                            part_list.append('","')
                            part_list.append(value[4:])
                        else:
                            part_list = value.split(",")

                        if part_list[0].find("re.compile") > -1:
                            arguments = ["%s.sub(%s,%s)" % (part_list[0], part_list[1], ".".join(part1))] + part2
                        else:
                            if not part2:
                                if ".".join(part1):
                                    arguments = [
                                        "%s.%s if isinstance(%s, str) else %s.replace(%s, %s)"
                                        % (".".join(part1), arg, part_list[0], part_list[0], ".".join(part1), part_list[1])
                                    ] + part2

                            # Es un regexpr
                        # else:
                        #    if ".".join(part1):
                        #        arguments = ["%s.%s" % (".".join(part1), arg)] + part2

                    else:
                        if ".".join(part1):
                            arguments = ["%s.%s" % (".".join(part1), arg)] + part2
                        else:
                            arguments = ["%s" % arg] + part2

        yield "expr", ".".join(arguments)


class ArrayMember(ASTPython):
    def generate(self, **kwargs):
        arguments = []
        for n, arg in enumerate(self.elem):
            arg.set("parent_", self.elem)
            expr = []
            for dtype, data in parse_ast(arg).generate(isolate=False):
                # if data.find(".") > -1:
                #    l = data.split(".")
                #    data = "%s['%s']" % (l[0], l[1])

                if dtype == "expr":
                    expr.append(data)
                else:
                    yield dtype, data

            if len(expr) == 0:
                arguments.append("unknownarg")
                yield "debug", "Argument %d not understood" % n
                yield "debug", ElementTree.tostring(arg)
            else:
                arguments.append(" ".join(expr))

        yield "expr", "%s[%s]" % (arguments[0], arguments[1])


class Value(ASTPython):
    def generate(self, isolate=True, **kwargs):
        if isolate:
            yield "expr", "("
        for child in self.elem:
            child.set("parent_", self.elem)
            for dtype, data in parse_ast(child).generate():
                if data is None:
                    raise ValueError(ElementTree.tostring(child))
                yield dtype, data
        if isolate:
            yield "expr", ")"


class Expression(ASTPython):
    tags = ["base_expression", "math_expression"]

    def generate(self, isolate=True, **kwargs):
        if isolate:
            yield "expr", "("
        coerce_string_mode = False
        if self.elem.findall('OpMath[@type="PLUS"]'):
            if self.elem.findall('Constant[@type="String"]'):
                coerce_string_mode = True
        if coerce_string_mode:
            yield "expr", "ustr("
        for child in self.elem:
            child.set("parent_", self.elem)
            if coerce_string_mode and child.tag == "OpMath":
                if child.get("type") == "PLUS":
                    yield "expr", ","
                    continue

            for dtype, data in parse_ast(child).generate():
                yield dtype, data

        if coerce_string_mode:
            yield "expr", ")"
        if isolate:
            yield "expr", ")"


class Parentheses(ASTPython):
    def generate(self, **kwargs):
        yield "expr", "("
        for child in self.elem:
            child.set("parent_", self.elem)
            for dtype, data in parse_ast(child).generate(isolate=False):
                yield dtype, data
        yield "expr", ")"


class Delete(ASTPython):
    def generate(self, **kwargs):
        yield "expr", "del"
        for child in self.elem:
            child.set("parent_", self.elem)
            for dtype, data in parse_ast(child).generate(isolate=False):
                yield dtype, data


class OpTernary(ASTPython):
    def generate(self, isolate=False, **kwargs):
        """
            Ejemplo op. ternario
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
        for dtype, data in parse_ast(then_val).generate():
            yield dtype, data
        yield "expr", "if"
        for dtype, data in parse_ast(if_cond).generate():
            yield dtype, data
        yield "expr", "else"
        for dtype, data in parse_ast(else_val).generate():
            yield dtype, data
        yield "expr", ")"  # Por seguridad, unos paréntesis


class DictObject(ASTPython):
    def generate(self, isolate=False, **kwargs):
        yield "expr", "{"
        key = True
        for child in self.elem:
            child.set("parent_", self.elem)
            for dtype, data in parse_ast(child).generate():
                if key:
                    yield dtype, "'%s'" % data
                    key = False
                else:
                    yield dtype, data
            # Como en Python la coma final la ignora, pues la ponemos.
            yield "expr", ","
            key = True

        yield "expr", "}"


class DictElem(ASTPython):
    def generate(self, isolate=False, **kwargs):
        # Clave:
        for dtype, data in parse_ast(self.elem[0]).generate():
            yield dtype, data
        yield "expr", ":"
        # Valor:
        for dtype, data in parse_ast(self.elem[1]).generate():
            yield dtype, data


class OpUnary(ASTPython):
    def generate(self, isolate=False, **kwargs):
        ctype = self.elem.get("type")
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
            child.set("parent_", self.elem)
            for dtype, data in parse_ast(child).generate():
                yield dtype, data
        if isolate:
            yield "expr", ")"


class New(ASTPython):
    def generate(self, **kwargs):
        for child in self.elem:
            child.set("parent_", self.elem)
            for dtype, data in parse_ast(child).generate():
                if dtype != "expr":
                    yield dtype, data
                    continue
                if child.tag == "Identifier":
                    data = data + "()"
                ident = data[: data.find("(")]
                if ident.find(".") == -1:
                    parentClass_ = self.elem.get("parent_")
                    # classIdent_ = False
                    while parentClass_:
                        if parentClass_.tag == "Source":
                            for m in parentClass_.findall("Class"):
                                if m.get("name") == ident:
                                    # classIdent_ = True
                                    break
                        parentClass_ = parentClass_.get("parent_")

                yield dtype, data


class Constant(ASTPython):
    def generate(self, **kwargs):
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
                    for dtype, data in parse_ast(child).generate(isolate=False):
                        if data:
                            val += data
                    yield "expr", 're.compile("/%s/i")' % val

                elif child.tag == "CallArguments":
                    arguments = []
                    for n, arg in enumerate(child):
                        expr = []
                        for dtype, data in parse_ast(arg).generate(isolate=False):
                            if dtype == "expr":
                                expr.append(data)
                            else:
                                yield dtype, data
                        if len(expr) == 0:
                            arguments.append("unknownarg")
                            yield "debug", "Argument %d not understood" % n
                            yield "debug", ElementTree.tostring(arg)
                        else:
                            arguments.append(" ".join(expr))

                    yield "expr", "Array([%s])" % (", ".join(arguments))
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
    def generate(self, **kwargs):
        name = id_translate(self.elem.get("name"))
        yield "expr", name


class regex(ASTPython):
    def generate(self, **kwargs):
        child = self.elem.find("regexbody")
        # args_ = self.elem.items()
        if not child:
            return

        for arg in child:
            for dtype, data in parse_ast(arg).generate(isolate=False):
                yield "expr", data


class regexchar(ASTPython):
    def generate(self, **kwargs):
        val = self.elem.get("arg00")
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
        elif val == "RPAREN":
            ret = ")"
        elif val == "LPAREN":
            ret = "("
        else:
            if val.find(":") > -1:
                ret = val.split(":")[1]
                ret = ret.replace("'", "")
            else:
                print("regexchar:: item desconocido %s" % val)

        yield "exp", ret


class OpUpdate(ASTPython):
    def generate(self, **kwargs):
        ctype = self.elem.get("type")
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
    def generate(self, **kwargs):
        ctype = self.elem.get("type")
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
            yield "expr", "not is"
        elif ctype == "IN":
            yield "expr", "in"
        elif ctype == "LOR":
            yield "expr", "or"
        elif ctype == "LAND":
            yield "expr", "and"
        else:
            yield "expr", "Compare." + ctype


class OpMath(ASTPython):
    def generate(self, **kwargs):
        ctype = self.elem.get("type")
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
    def generate(self, **kwargs):
        # mode = self.elem.get("mode")
        is_constructor = self.elem.get("constructor")
        # if mode == "CONST": yield "debug", "Const Declaration:"
        for var in self.elem:
            var.set("parent_", self.elem)
            expr = []
            for dtype, data in parse_ast(var).generate(force_value=True):
                if dtype == "expr":
                    if data is None:
                        raise ValueError(ElementTree.tostring(var))
                    expr.append(data)
                else:
                    yield dtype, data
            if is_constructor:
                expr[0] = "self." + expr[0]
            yield "line", " ".join(expr)


# ----- keep this one at the end.
class Unknown(ASTPython):
    @classmethod
    def can_process_tag(self, tagname) -> bool:
        return True


# -----------------


def astparser_for(elem) -> Optional[ASTPython]:
    classobj = None
    for cls in ASTPythonFactory.ast_class_types:
        if cls.can_process_tag(elem.tag):
            classobj = cls
            break
    if classobj is None:
        return None
    return classobj(elem)


def parse_ast(elem) -> Any:
    elemparser = astparser_for(elem)
    return elemparser.polish()


def file_template(ast: Any) -> Generator[Tuple[Any, Any], Any, None]:
    yield "line", "# -*- coding: utf-8 -*-"
    yield "line", "from pineboolib.qsa import *"
    # yield "line", "from pineboolib.qsaglobals import *"
    yield "line", ""
    yield "line", "#/** @file */"
    yield "line", ""
    sourceclasses = ElementTree.Element("Source")
    for cls in ast.findall("Class"):
        cls.set("parent_", ast)
        sourceclasses.append(cls)

    mainclass = ElementTree.SubElement(sourceclasses, "Class", name="FormInternalObj", extends="FormDBWidget")
    mainsource = ElementTree.SubElement(mainclass, "Source")

    constructor = ElementTree.SubElement(mainsource, "Function", name="_class_init")
    # args = etree.SubElement(constructor, "Arguments")
    csource = ElementTree.SubElement(constructor, "Source")

    for child in ast:
        if child.tag != "Function":
            child.set("constructor", "1")
            if child.tag != "Class":  # Limpiamos las class, se cuelan desde el cambio de xml
                csource.append(child)
        else:
            mainsource.append(child)

    for dtype, data in parse_ast(sourceclasses).generate():
        yield dtype, data
    yield "line", ""
    yield "line", "form = None"


def write_python_file(fobj, ast) -> None:
    indent = []
    indent_text = "    "
    last_line_for_indent = {}
    numline = 0
    ASTPython.numline = 1
    last_dtype = None
    for dtype, data in file_template(ast):
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
                fobj.write((len(indent) * indent_text) + "\n")
            last_line_for_indent[len(indent)] = numline
        if dtype == "debug":
            line = "# DEBUG:: %s" % data
            # print(numline, line)
        if dtype == "expr":
            line = "# EXPR??:: " + data
        if dtype == "line+1":
            line = "# LINE+1??:: " + data
        if dtype == "begin":
            # line = "# BEGIN:: " + data
            indent.append(data)
            last_line_for_indent[len(indent)] = numline
        if dtype == "end":
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
            fobj.write((len(indent) * indent_text) + line + "\n")

        if dtype == "end":
            if data.split("-")[1] in ["class", "def", "else", "except"]:
                ASTPython.numline += 1
                fobj.write((len(indent) * indent_text) + "\n")
                last_line_for_indent[len(indent)] = numline
        last_dtype = dtype


def pythonize(filename, destfilename, debugname=None) -> None:
    # bname = os.path.basename(filename)
    ASTPython.debug_file = open(debugname, "w") if debugname else None
    parser = ElementTree.XMLParser(encoding="UTF-8")
    try:
        ast_tree = ElementTree.parse(open(filename, "r", encoding="UTF-8"), parser)
    except Exception:
        print("filename:", filename)
        raise
    ast = ast_tree.getroot()

    f1 = open(destfilename, "w", encoding="UTF-8")
    write_python_file(f1, ast)
    f1.close()


def main() -> None:
    parser = OptionParser()
    parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True, help="don't print status messages to stdout")

    parser.add_option("--optdebug", action="store_true", dest="optdebug", default=False, help="debug optparse module")

    parser.add_option("--debug", action="store_true", dest="debug", default=False, help="prints lots of useless messages")

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
