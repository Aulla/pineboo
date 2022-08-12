"""
Simple parser for FacturaLUX Scripting Language (QSA).
"""
import optparse
import pprint
import sys
import math
import hashlib
import tempfile
import re
from typing import Any, Dict, List, Tuple, Optional, TextIO

from pineboolib.core.utils import utils_base
from pineboolib.application.parsers import parser_qsa


import ply.yacc as yacc  # type: ignore
import ply.lex as lex  # type: ignore

from . import token_rules, flex

TEMP_DIR = tempfile.gettempdir()

# Get the token map
tokens = token_rules.tokens
start = "source"  # pylint: disable=invalid-name

reserv = ["nonassoc"]
reserv += list(token_rules.reserved)

endoffile = None  # pylint: disable=invalid-name

hashes: List[Tuple[str, str]] = []
ranges: List[List[Any]] = []

SEEN_TOKENS = []
TOKE_LINES: Dict[int, int] = {}
LAST_LEXSPAN = None
INPUT_DATA: str = ""

precedence = (
    ("nonassoc", "EQUALS", "TIMESEQUAL", "DIVEQUAL", "MODEQUAL", "PLUSEQUAL", "MINUSEQUAL"),
    ("nonassoc", "MATHEXPRESSION"),
    ("nonassoc", "TERNARY"),
    ("left", "LOR", "LAND"),
    ("right", "LT", "LE", "GT", "GE", "EQ", "NE", "EQQ", "NEQ"),
    ("right", "LNOT"),
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE", "MOD"),
    ("left", "OR", "AND", "XOR", "LSHIFT", "RSHIFT"),
)

LAST_OK_TOKEN: Any = None
ERROR_COUNT = 0
LAST_ERROR_TOKEN: Any = None
LAST_ERROR_LINE = -1
OK_COUNT = 0


def clean_no_python(data: str) -> str:
    """Remove NOPYTHON blocks."""
    return re.sub(r"\/\/___NOPYTHON\[\[.*?\/\/\]\]___NOPYTHON\s*", "", data, flags=re.DOTALL)


def clean_no_python_never(data: str) -> str:
    """Remove NOPYTHON_NEVER blocks."""
    return re.sub(
        r"\/\/___NOPYTHON_NEVER\[\[.*?\/\/\]\]___NOPYTHON_NEVER\s*", "", data, flags=re.DOTALL
    )


def cnvrt(val: str) -> str:
    """Convert special XML characters into XML entities."""
    val = str(val)
    val = val.replace("&", "&amp;")
    val = val.replace('"', "&quot;")
    val = val.replace("'", "&apos;")
    val = val.replace("<", "&lt;")
    val = val.replace(">", "&gt;")
    return val


def p_parse(token: Any) -> None:
    """Parse a single token."""
    global INPUT_DATA

    lexspan: List[int] = list(token.lexspan(0))
    # data = str(token.lexer.lexdata[lexspan[0]:lexspan[1]])
    # context = [
    #     str(token.lexer.lexdata[lexspan[0] - 32:lexspan[0]]),
    #     str(token.lexer.lexdata[lexspan[0]:lexspan[1]]),
    #     str(token.lexer.lexdata[lexspan[1]:lexspan[1] + 32]),
    # ]
    if len(lexspan) == 2:
        fromline = token.lineno(0)
        global endoffile  # pylint: disable=invalid-name
        endoffile = fromline, lexspan, token.slice[0]
    # print(repr(token.slice), context, lexspan)

    tok0: Dict[str, Any] = {
        "00-toktype": str(token.slice[0]),
        "02-size": lexspan,
        "50-contents": [{"01-type": s.type, "99-value": s.value} for s in token.slice[1:]],
    }
    token[0] = tok0

    for num in reversed(range(len(tok0["50-contents"]))):
        contents = tok0["50-contents"][num]
        if contents["01-type"] == tok0["00-toktype"]:
            # If the first element is same type, unpack left. This is for recursing lists
            # Makes tree calculation faster and less recursive.
            tok0["50-contents"][num : num + 1] = contents["99-value"]["50-contents"]

    numelems: int = len([s for s in token.slice[1:] if s.type != "empty" and s.value is not None])

    rspan = lexspan[0]
    if str(token.slice[0]) == "empty" or numelems == 0:
        token[0] = None
    else:
        rvalues = []
        for num, item in enumerate(token.slice[1:]):
            if item.type != "empty" and item.value is not None:
                val = None
                if isinstance(item.value, str):
                    val = token.lexspan(num + 1)[0] + len(item.value) - 1
                else:
                    val = token.lexspan(num + 1)[1]
                rvalues.append(val)
        rspan = max(rvalues)
    lexspan[1] = rspan

    # if str(token.slice[0]) == 'regexbody':
    #    token[0] = { "00-toktype": str(token.slice[0]) , "02-size" : lexspan,  "50-contents" :  INPUT_DATA[lexspan[0]:lexspan[1]+1] }

    # if str(token.slice[0]) == 'regex':
    #    print "\r\n",str(token.slice[0]) ,":" , INPUT_DATA[lexspan[0]:lexspan[1]+1]
    #    print "      " + "\n      ".join([ "%s(%r): %r" % (s.type, token.lexspan(n+1), s.value) for n,s in enumerate(token.slice[1:]) ])
    global SEEN_TOKENS, LAST_OK_TOKEN
    LAST_OK_TOKEN = token
    SEEN_TOKENS.append(
        (str(token.slice[0]), token.lineno(0), INPUT_DATA[lexspan[0] : lexspan[1] + 1])
    )
    global OK_COUNT
    OK_COUNT += 1
    if lexspan[0] not in TOKE_LINES:
        TOKE_LINES[lexspan[0]] = token.lexer.lineno
    global LAST_LEXSPAN
    LAST_LEXSPAN = lexspan


def p_error(text: Any) -> Any:
    """Process and report errors in parsing."""
    global ERROR_COUNT
    global OK_COUNT
    global LAST_ERROR_TOKEN
    global LAST_ERROR_LINE, SEEN_TOKENS, LAST_OK_TOKEN
    debug = False  # Poner a True para toneladas de debug.
    # if ERROR_COUNT == 0: print
    if text is not None:
        if LAST_ERROR_TOKEN is None or text.lexpos != getattr(LAST_ERROR_TOKEN, "lexpos", None):
            if abs(LAST_ERROR_LINE - text.lineno) > 4 and OK_COUNT > 1 and ERROR_COUNT < 4:
                ERROR_COUNT += 1
                try:
                    print_context(text)
                except Exception:
                    pass
                if debug:
                    ERROR_COUNT += 20  # no imprimir mas de un error en debug.
                    print()
                    for tokname, tokln, tokdata in SEEN_TOKENS[-32:]:
                        if tokln == text.lineno:
                            print(tokname, tokdata)
                    if LAST_OK_TOKEN:
                        print(repr(LAST_OK_TOKEN[0]))
                        for sli_ in LAST_OK_TOKEN.slice[:]:
                            print(
                                ">>>", sli_.lineno, repr(sli_), pprint.pformat(sli_.value, depth=3)
                            )
                LAST_ERROR_LINE = text.lineno
            elif abs(LAST_ERROR_LINE - text.lineno) > 1 and OK_COUNT > 1:
                LAST_ERROR_LINE = text.lineno
            parser.errok()
            OK_COUNT = 0
            return

    OK_COUNT = 0
    if text is None:
        if LAST_ERROR_TOKEN != "EOF":
            print("ERROR: End of the file reached.")
            global endoffile  # pylint: disable=invalid-name
            print("Last data:", endoffile)

            if LAST_LEXSPAN:
                try:
                    print("HINT: Last lexspan:", LAST_LEXSPAN)
                    print("HINT: Last line:", TOKE_LINES[LAST_LEXSPAN[0]])
                except Exception as error:
                    print("ERROR:", error)
        LAST_ERROR_TOKEN = "EOF"
        return text
    text = parser.token()
    parser.restart()
    LAST_ERROR_TOKEN = text
    return text


p_parse.__doc__ = """

    inlinestoreinstruction  : PLUSPLUS variable
                            | MINUSMINUS variable
                            | variable PLUSPLUS
                            | variable MINUSMINUS

    exprval : constant
            | variable
            | funccall
            | error

    identifier : ID

    dictobject_value : LBRACE RBRACE
                     | LBRACE dictobject_value_elemlist RBRACE

    dictobject_value_elemlist : dictobject_value_elem
                              | dictobject_value_elemlist COMMA dictobject_value_elem

    dictobject_value_elem : exprval COLON expression

    base_expression     : ternary_operator
                        | inlinestoreinstruction
                        | parentheses
                        | unary_operator
                        | new_operator
                        | typeof_operator
                        | dictobject_value
                        | exprval
                        | base_expression mathoperator base_expression      %prec MATHEXPRESSION
                        | base_expression cmp_symbol base_expression        %prec MATHEXPRESSION
                        | base_expression boolcmp_symbol base_expression    %prec MATHEXPRESSION





    parentheses         : LPAREN base_expression RPAREN
                        | LPAREN variable_1 RPAREN

    unary_operator      : LNOT base_expression
                        | MINUS base_expression
                        | PLUS base_expression

    new_operator        : NEW funccall_1
                        | NEW identifier

    typeof_operator     : TYPEOF parentheses

    expression  : base_expression
                | funcdeclaration_anon
                | funcdeclaration_anon_exec
                | LPAREN expression RPAREN
                | error

    case_cblock_list  :  case_block
    case_cblock_list  :  case_cblock_list case_block

    case_block  :  CASE expression COLON statement_list

    case_default    :  DEFAULT COLON statement_list

    case_block_list  :  empty
    case_block_list  :  case_default
    case_block_list  :  case_cblock_list
    case_block_list  :  case_cblock_list case_default

    source_element  : docstring
                    | vardeclaration
                    | classdeclaration
                    | funcdeclaration
                    | funcdeclaration_anon
                    | funcdeclaration_anon_exec

    source  : source_element
    source  : source source_element
            | statement_list


    basicsource     : statement_list
                    | empty

    statement   : instruction
                | vardeclaration
                | ifstatement
                | whilestatement
                | dowhilestatement
                | withstatement
                | forstatement
                | forinstatement
                | switch
                | trycatch

    statement_list      : statement_list statement

    statement_list      : statement

    statement_list      : LBRACE statement_list RBRACE

    statement_list      : LBRACE RBRACE
    statement_list      : empty

    optvartype  : COLON ID
                | empty

    vardeclaration  :  VAR vardecl_list SEMI
                    |  CONST vardecl_list SEMI
    vardeclaration  :  VAR vardecl_list
                    |  CONST vardecl_list
                    |  STATIC VAR vardecl_list

    vardecl  :  ID optvartype EQUALS expression
             |  vardecl EQUALS expression
    vardecl  :  ID optvartype

    vardecl_list    : vardecl
                    | vardecl_list COMMA vardecl

    arglist : vardecl_list
            |

    funcdeclaration : FUNCTION ID LPAREN arglist RPAREN optvartype LBRACE basicsource RBRACE
    funcdeclaration : STATIC FUNCTION ID LPAREN arglist RPAREN optvartype LBRACE basicsource RBRACE
    funcdeclaration_anon : FUNCTION LPAREN arglist RPAREN LBRACE basicsource RBRACE
                         | FUNCTION LPAREN RPAREN LBRACE basicsource RBRACE
    funcdeclaration_anon_exec : funcdeclaration_anon LPAREN RPAREN
                              | funcdeclaration_anon LPAREN arglist RPAREN

    callarg     : expression

    callargs    : callarg
                | callargs COMMA callarg

    varmemcall  : variable_1
                | funccall_1
                | member_call
                | member_var
                | base_expression

    member_var  : varmemcall PERIOD variable_1

    member_call : LPAREN member_var RPAREN PERIOD funccall_1

    member_call : varmemcall PERIOD funccall_1
    member_call : LPAREN member_call RPAREN PERIOD funccall_1

    funccall    : funccall_1
                | member_call
                | LPAREN member_call RPAREN
                | LPAREN funccall_1 RPAREN
                | LPAREN error RPAREN

    funccall_1  : ID LPAREN callargs RPAREN
                | ID LPAREN RPAREN
                | TYPEOF LPAREN callargs RPAREN
                | array_member LPAREN callargs RPAREN
                | array_member LPAREN RPAREN

    mathoperator    : PLUS
                    | MINUS
                    | TIMES
                    | DIVIDE
                    | MOD
                    | XOR
                    | OR
                    | LSHIFT
                    | RSHIFT
                    | AND

    variable    : variable_1
                | member_var
                | LPAREN variable_1 RPAREN
                | LPAREN member_var RPAREN

    variable_1  : identifier
                | array_member

    array_member : variable_1 LBRACKET expression RBRACKET
                 | funccall_1 LBRACKET expression RBRACKET

        updateoperator : EQUALS
                       | PLUSEQUAL
                       | MINUSEQUAL
                       | MODEQUAL
                       | DIVEQUAL
                       | TIMESEQUAL

        updateinstruction : variable updateoperator expression
                          | variable updateoperator updateinstruction

        deleteinstruction   : DELETE variable

        storeinstruction    : inlinestoreinstruction
                            | updateinstruction
                            | deleteinstruction


    flowinstruction : RETURN expression
                    | RETURN expression COMMA
                    | THROW expression
                    | RETURN
                    | BREAK
                    | CONTINUE

    instruction : base_instruction SEMI
                | SEMI
                | base_instruction
                | funcdeclaration
                | error SEMI

    callinstruction : funccall
                    | variable

    base_instruction : storeinstruction
                | callinstruction
                | flowinstruction

    varorcall : variable
              | funccall
              | base_expression

    optextends  : EXTENDS ID
                | empty

    classdeclaration   : CLASS ID optextends LBRACE classdeclarationsource RBRACE

    classdeclarationsource  : vardeclaration
                            | funcdeclaration
                            | classdeclarationsource vardeclaration
                            | classdeclarationsource funcdeclaration
                            | SEMI
                            | classdeclarationsource SEMI

    docstring   : DOCSTRINGOPEN AT ID COMMENTCLOSE
                | DOCSTRINGOPEN AT ID ID COMMENTCLOSE

    list_constant   : LBRACKET RBRACKET
    list_constant   : LBRACKET callargs RBRACKET
    list_constant   : LBRACKET callargs COMMA RBRACKET

    constant : ICONST
                | FCONST
                | CCONST
                | SCONST
                | regex
                | list_constant

    regex : DIVIDE regexbody DIVIDE regexflags
          | DIVIDE regexbody COMMENTCLOSE regexflags

    regexbody   : regexchar
                | regexbody regexchar

    regexchar :  LPAREN
              | RPAREN
              | ID
              | COMMA
              | XOR
              | LBRACKET
              | RBRACKET
              | ICONST
              | PLUS
              | MINUS
              | LBRACE
              | RBRACE
              | DOLLAR
              | SQOUTE
              | DQOUTE
              | PERIOD
              | BACKSLASH
              | CONDITIONAL1
              | EQUALS
              | OR
              | SCONST
              | SEMI
              | MOD
              | AT
              | COLON
              | error

    regexflags : ID
               | empty


    statement_block : statement
                    | LBRACE statement_list RBRACE
                    | LBRACE RBRACE

    optelse : ELSE statement_block
            | empty

    cmp_symbol  : LT
                | LE
                | GT
                | GE
                | EQ
                | NE
                | EQQ
                | NEQ
                | IN

    boolcmp_symbol  : LOR
                    | LAND

    condition   : expression
                | error

    ifstatement : IF LPAREN condition RPAREN statement_block optelse

    whilestatement  : WHILE LPAREN condition RPAREN statement_block
    dowhilestatement  : DO statement_block WHILE LPAREN condition RPAREN SEMI
                      | DO statement_block WHILE LPAREN condition RPAREN

    withstatement   : WITH LPAREN variable RPAREN statement_block
                    | error

    storeormember   : storeinstruction
                    | member_var

    for_initialize  : storeinstruction
                    | VAR vardecl
                    | vardecl
                    | for_initialize COMMA for_initialize
                    | empty

    for_compare     : expression
                    | empty

    for_increment   : storeormember
                    | for_increment COMMA for_increment
                    | empty


    forstatement    : FOR LPAREN for_initialize SEMI for_compare SEMI for_increment RPAREN statement_block
                    | error

    forinstatement  : FOR LPAREN for_initialize IN varorcall RPAREN statement_block
                    | FOR LPAREN variable IN varorcall RPAREN statement_block
                    | error

    switch  : SWITCH LPAREN condition RPAREN LBRACE case_block_list RBRACE

    optid   : ID
            | empty

    trycatch    : TRY statement_block CATCH LPAREN optid RPAREN statement_block

    ternary_operator    : base_expression CONDITIONAL1 base_expression COLON base_expression %prec TERNARY

    empty :
    """


# Build the grammar


parser = yacc.yacc(
    method="LALR",
    debug=0,
    optimize=1,
    write_tables=1,
    debugfile="%s/yaccdebug.txt" % TEMP_DIR,
    outputdir="%s/" % TEMP_DIR,
)

# parser = yacc.yacc(method='LALR', debug=1,
#                   optimize=0, write_tables=0, debugfile='%s/yaccdebug.txt' % TEMP_DIR, outputdir='%s/' % TEMP_DIR)

# profile.run("yacc.yacc(method='LALR')")


def print_context(token: Any) -> None:
    """Report errors in console when parsing fails."""
    global INPUT_DATA
    if token is None:
        return
    last_cr = INPUT_DATA.rfind("\n", 0, token.lexpos)
    next_cr = INPUT_DATA.find("\n", token.lexpos)
    column = token.lexpos - last_cr
    column1 = token.lexpos - last_cr
    while column1 < 16:
        column1 = token.lexpos - last_cr
        last_cr = INPUT_DATA.rfind("\n", 0, last_cr - 1)

    print(INPUT_DATA[last_cr:next_cr].replace("\t", " "))
    print((" " * (column - 1)) + "^", column, "#ERROR#", token)


def my_tokenfunc(*args, **kwargs) -> Any:
    """Tokenizer function."""
    # print("Call token:" ,args, kwargs)
    ret = lex.lexer.token(*args, **kwargs)
    # print "Return (",args, kwargs,") = " , ret
    return ret


def print_tokentree(token: Any, depth: int = 0) -> None:
    """Debug output. Unused."""
    print("  " * depth, token.__class__, "=", token)

    if str(token.__class__) == "ply.yacc.YaccProduction":
        print(token.lexer)
        for token in token.slice:
            if token.value == token:
                continue
            print("  " * (depth + 1), token.type, end=" ")
            try:
                print(token.lexpos, end=" ")
                print(token.endlexpos, end=" ")
            except Exception:
                pass
            print()

            print_tokentree(token.value, depth + 1)


def calctree(
    obj: Dict[str, Any],
    depth: int = 0,
    num: List[str] = [],
    otype: str = "source",
    alias_mode: int = 1,
) -> Dict[str, Any]:
    """Extract parsed AST and generate a custom structure for later XML generation."""
    # if depth > 5: return
    # source_data = [
    #     'source',
    #     'source_element',
    #     'statement_list',
    #     'statement',
    #     'classdeclarationsource',
    #     'vardecl_list',
    # ]
    final_obj = {}
    final_obj["range"] = obj["02-size"]
    has_data = 0
    has_objects = 0
    contentlist = []
    ctype_alias: Dict[str, str]
    if alias_mode == 0:
        ctype_alias = {}
    elif alias_mode == 1:
        ctype_alias = {
            "member_var": "member",
            "member_call": "member",
            "variable_1": "variable",
            "funccall_1": "funccall",
            "flowinstruction": "instruction",
            "storeequalinstruction": "instruction",
            "vardecl": "vardeclaration",
            # "vardecl_list" : "vardeclaration",
        }
    else:
        raise ValueError("alias_mode unknown")

    if otype in ctype_alias:
        otype = ctype_alias[otype]
    # print " " * depth , obj['02-size']
    for num_, content in enumerate(obj["50-contents"]):
        if not isinstance(content, dict):
            print("ERROR: content is not a dict!:", repr(content))
            print(".. obj:", repr(obj))
            raise TypeError("content is not a dict")

        ctype = content["01-type"]
        value = content["99-value"]
        if ctype in ctype_alias:
            ctype = ctype_alias[ctype]
        # if ctype in source_data:
        #    if depth == 0: print "--"
        #    print_tree(value,depth,num)
        #    continue
        # print " " * depth , "%s:" % ".".join(num+[str(num_)]), ctype,

        if isinstance(value, dict):
            # print "*"
            # FIXME: Esto o no parsea todos los elementos o hace stackoverflow. problematico para programas largos
            if depth < 300:
                try:
                    tree_obj = calctree(
                        value, depth + 1, num + [str(num_)], ctype, alias_mode=alias_mode
                    )
                except Exception as error:
                    print("ERROR: trying to calculate member:", error)
                    continue
            else:
                print("PANIC: *** Stack overflow trying to calculate member %d on:" % num_, ctype)
                continue

            if type(tree_obj) is dict:
                if (tree_obj["has_data"] or alias_mode == 0) and ctype != otype:
                    contentlist.append([ctype, tree_obj])
                    has_objects += 1
                else:
                    contentlist += tree_obj["content"]
                    has_data += tree_obj["has_data"]
                    has_objects += tree_obj["has_objects"]
        else:
            # print "=", repr(value)
            contentlist.append([ctype, value])
            has_data += 1

    final_obj["content"] = contentlist
    final_obj["has_data"] = has_data
    final_obj["has_objects"] = has_objects

    return final_obj


def printtree(
    tree: Dict[str, Any],
    depth: int = 0,
    otype: str = "source",
    mode: Optional[str] = None,
    output: TextIO = sys.stdout,
) -> Tuple[Any, Any, Any]:
    """Export AST into different formats, mainly used for XML export."""
    global hashes, ranges  # pylint: disable=invalid-name
    if depth == 0:
        hashes = []
        ranges = []

    sep = "    "
    marginblocks = {
        "classdeclaration": 1,
        "funcdeclaration": 1,
        "statement_block": 1,
        # "instruction" : 1,
    }
    closingtokens = ["RBRACE", "RPAREN", "RBRACKET", "SEMI"]
    nuevalinea = False
    name = ""
    lines: List[str] = []
    L = 0  # pylint: disable=invalid-name

    for ctype, value in tree["content"]:
        if nuevalinea:
            if ctype in closingtokens:
                nuevalinea = False

            else:
                for item in range(int(math.ceil(L / 2.0))):
                    lines.append(sep * depth)
                nuevalinea = False

        if isinstance(value, dict):
            if ctype == otype:
                tname, tlines, trange = printtree(value, depth, ctype)
                if name == "" and tname:
                    name = tname

                lines += tlines
            else:
                L = 0  # pylint: disable=invalid-name
                if ctype in marginblocks:
                    L = marginblocks[ctype]  # pylint: disable=invalid-name

                for i in range(int(math.floor(L / 2.0))):
                    lines.append(sep * depth)
                tname, tlines, trange = printtree(value, depth + 1, ctype)
                # lines.append(sep * depth + "<!-- %d -->" % (len("".join(tlines))))

                if value["has_data"] > 0 and value["has_objects"] == 0 and False:
                    pass
                    # Do it inline!
                    # if value["has_data"] == 1 and tname:
                    #     lines.append(sep * depth + '<%s id="%s" />' % (ctype, tname))
                    # else:
                    #     txt = "".join([x.strip() for x in tlines])
                    #     lines.append(sep * depth + "<%s>%s</%s>" % (ctype, txt, ctype))
                else:
                    attrs = []
                    if tname:
                        attrs.append(("id", tname))

                    txtinline = "".join([line.strip() for line in tlines])

                    # if len(tlines)>1:
                    txthash = hashlib.sha1(txtinline.encode("utf8")).hexdigest()[:16]
                    # hashes.append(("depth:",depth,"hash:",txthash,"element:",ctype+":"+tname))
                    hashes.append((txthash, ctype + ":" + tname + "(%d)" % len(txtinline)))
                    ranges.append([depth, txthash] + trange + [ctype + ":" + tname, len(txtinline)])
                    # ,"start:",trange[0],"end:",trange[1]))
                    # attrs.append(("start",trange[0]))
                    # attrs.append(("end",trange[1]))
                    # attrs.append(("hash",txthash))

                    txtattrs = ""
                    for name1, val1 in attrs:
                        txtattrs += ' %s="%s"' % (name1, cnvrt(val1))

                    lines.append(sep * depth + "<%s%s>" % (ctype, txtattrs))
                    if depth > 50:
                        lines.append(sep * (depth + 1) + "...")
                    else:
                        if len(txtinline) < 80:
                            lines.append(sep * (depth + 1) + txtinline)
                        else:
                            lines += tlines
                    if txtattrs:
                        txtattrs = "<!--%s -->" % txtattrs
                    lines.append(sep * depth + "</%s>" % (ctype))

                    nuevalinea = True
        else:
            if ctype == "ID" and name == "":
                name = value
            if ctype in token_rules.token_literals:
                lines.append(sep * depth + '<%s value="%s" />' % (ctype, cnvrt(value)))
            else:
                lines.append(sep * depth + "<%s />" % (ctype))

    if mode == "hash":
        # print "\n".join(lines)
        for row in sorted(ranges):
            output.write("\t".join([str(x) for x in row]))
            output.write("\n")
            output.flush()
    elif mode == "xml":
        for strrow in lines:
            output.write(strrow)
            output.write("\n")
            output.flush()

    return name, lines, tree["range"]


def parse(data: str, clean: bool = True) -> Optional[Dict[str, Any]]:
    """Parse QS String."""

    global INPUT_DATA
    global ERROR_COUNT
    global SEEN_TOKENS

    if clean:
        data = clean_no_python_never(data)
        if utils_base.is_library() and not parser_qsa.IGNORE_NO_PYTHON_TAGS:
            data = clean_no_python(data)
    SEEN_TOKENS[:] = []
    parser.error = 0
    INPUT_DATA = data
    flex.lexer.lineno = 1
    ERROR_COUNT = 0
    parser_ = parser.parse(data, debug=0, tracking=1, tokenfunc=my_tokenfunc)
    if ERROR_COUNT > 0:
        print("ERRORS (%d)" % ERROR_COUNT)
    if parser_ is not None:

        try:
            parser_["error_count"] = ERROR_COUNT
        except Exception as error:
            print(error)
            return None

        if parser.error:
            return None

    return parser_


def main() -> None:
    """Manage direct script calls for flscriptparse. Deprecated."""
    global start  # pylint: disable=invalid-name
    parser = optparse.OptionParser()
    parser.add_option(
        "-O",
        "--output",
        dest="output",
        default="none",
        help="Set output TYPE: xml|hash",
        metavar="TYPE",
    )
    parser.add_option("--start", dest="start", default=None, help="Set start block", metavar="STMT")
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

    (options, args) = parser.parse_args()
    if options.optdebug:
        print(options, args)
    if options.start:
        start = options.start
        print("Start setted to:", start)

    def do_it():
        if options.output == "none":
            return
        tree_data = calctree(prog)
        if options.output == "hash":
            printtree(tree_data, mode="hash")
        elif options.output == "xml":
            printtree(tree_data, mode="xml")
        elif options.output == "file":
            f1_hash = open(filename + ".hash", "w")
            printtree(tree_data, mode="hash", output=f1_hash)
            f1_hash.close()

            f1_xml = open(filename + ".xml", "w")
            printtree(tree_data, mode="xml", output=f1_xml)
            f1_xml.close()
        elif options.output == "yaml":
            import yaml

            print(yaml.safe_dump(tree_data["content"]))

        else:
            print("Unknown outputmode", options.output)

    prog: Dict[str, Any]
    if len(args) > 0:
        for filename in args:
            fs = filename.split("/")  # pylint: disable=invalid-name
            sys.stderr.write("Loading %s ..." % fs[-1])
            sys.stderr.flush()
            data = open(filename).read()
            sys.stderr.write(" parsing ...")
            sys.stderr.flush()
            prog_ = parse(data)
            if prog_ is not None:
                prog = prog_
                sys.stderr.write(" formatting ...")
                sys.stderr.flush()
                do_it()
                sys.stderr.write(" Done.\n")
                sys.stderr.flush()

    else:

        line = ""
        while 1:
            try:
                line1 = input("flscript> ")
                if line1.startswith("#"):
                    comm = line1[1:].split(" ")
                    if comm[0] == "setstart":
                        start = comm[1]
                        print("Start setted to:", start)
                    if comm[0] == "parse":
                        print()
                        line = ""
                        prog_ = parse(line)
                        if prog_ is None:
                            continue
                        prog = prog_

                else:
                    line += line1
            except EOFError:
                break
            line += "\n"
        print()
        prog_ = parse(line)
        if prog_ is not None:
            prog = prog_
            do_it()
    """
    import yaml

    print yaml.dump(tree_data)
    """
    # print_tokentree(prog)

    # for varName in prog.byDefName:
    #    var = prog.byDefName[varName]
    #    print "%-15s / %-15s > " % var.type  , varName

    # import tests.ifaceclass
    # tests.ifaceclass.do_test(prog)


if __name__ == "__main__":
    main()
