"""
Lexer for Pineboo QS files.
"""
from ply.lex import TOKEN  # type: ignore


# Reserved words
reserved = [
    "BREAK",
    "CASE",
    "CONST",
    "STATIC",
    "CONTINUE",
    "DEFAULT",
    "DO",
    "ELSE",
    "FOR",
    "IF",
    "IN",
    "RETURN",
    "SWITCH",
    "WHILE",
    "CLASS",
    "VAR",
    "FUNCTION",
    "EXTENDS",
    "NEW",
    "WITH",
    "TRY",
    "CATCH",
    "THROW",
    "DELETE",
    "TYPEOF",
]
token_literals = [
    # Literals (identifier, integer constant, float constant, string constant, char const)
    "ID",
    "ICONST",
    "FCONST",
    "SCONST",
    "CCONST",  # , 'RXCONST'
]
tokens = (
    reserved
    + token_literals
    + [
        # Operators (+,-,*,/,%,|,&,~,^,<<,>>, ||, &&, !, <, <=, >, >=, ==, !=)
        "PLUS",
        "MINUS",
        "TIMES",
        "DIVIDE",
        "MOD",
        "OR",
        "AND",
        "AT",
        "XOR",
        "LSHIFT",
        "RSHIFT",
        "LOR",
        "LAND",
        "LNOT",
        "LT",
        "LE",
        "GT",
        "GE",
        "EQ",
        "NE",
        "EQQ",
        "NEQ",
        # Assignment (=, *=, /=, %=, +=, -=, <<=, >>=, &=, ^=, |=)
        "EQUALS",
        "TIMESEQUAL",
        "DIVEQUAL",
        "MODEQUAL",
        "PLUSEQUAL",
        "MINUSEQUAL",
        #    'LSHIFTEQUAL','RSHIFTEQUAL', 'ANDEQUAL', 'XOREQUAL', 'OREQUAL',
        # Increment/decrement (++,--)
        "PLUSPLUS",
        "MINUSMINUS",
        # Structure dereference (->)
        #    'ARROW',
        # Conditional operator (?)
        "CONDITIONAL1",
        #    'CONDOP',
        # Delimeters ( ) [ ] { } , . ; :
        "LPAREN",
        "RPAREN",
        "LBRACKET",
        "RBRACKET",
        "LBRACE",
        "RBRACE",
        "COMMA",
        "PERIOD",
        "SEMI",
        "COLON",
        # Ellipsis (...)
        #    'ELLIPSIS',
        "DOCSTRINGOPEN",
        #   'COMMENTOPEN',
        "COMMENTCLOSE",
        "DOLLAR",
        "SQOUTE",
        "DQOUTE",
        "BACKSLASH",
    ]
)

# Completely ignored characters
t_ignore = " \r\t\x0c"  # pylint: disable=invalid-name

# Newlines


@TOKEN(r"\n+")
def t_NEWLINE(t):  # pylint: disable=invalid-name
    """Keep track of line numbers."""
    t.lexer.lineno += t.value.count("\n")


# Operators
t_BACKSLASH = "\\\\"  # pylint: disable=invalid-name
t_DOLLAR = r"\$"  # pylint: disable=invalid-name
t_SQOUTE = "'"  # pylint: disable=invalid-name
t_DQOUTE = '"'  # pylint: disable=invalid-name
t_PLUS = r"\+"  # pylint: disable=invalid-name
t_MINUS = r"-"  # pylint: disable=invalid-name
t_TIMES = r"\*"  # pylint: disable=invalid-name
t_DIVIDE = r"/"  # pylint: disable=invalid-name
t_MOD = r"%"  # pylint: disable=invalid-name
t_OR = r"\|"  # pylint: disable=invalid-name
t_AND = r"&"  # pylint: disable=invalid-name
# t_NOT              = r'~'
t_XOR = r"\^"  # pylint: disable=invalid-name
t_LSHIFT = r"<<"  # pylint: disable=invalid-name
t_RSHIFT = r">>"  # pylint: disable=invalid-name
t_LOR = r"\|\|"  # pylint: disable=invalid-name
t_LAND = r"&&"  # pylint: disable=invalid-name
t_LNOT = r"!"  # pylint: disable=invalid-name
t_LT = r"<"  # pylint: disable=invalid-name
t_GT = r">"  # pylint: disable=invalid-name
t_LE = r"<="  # pylint: disable=invalid-name
t_GE = r">="  # pylint: disable=invalid-name
t_EQ = r"=="  # pylint: disable=invalid-name
t_NE = r"!="  # pylint: disable=invalid-name
t_EQQ = r"==="  # pylint: disable=invalid-name
t_NEQ = r"!=="  # pylint: disable=invalid-name
t_CONDITIONAL1 = r"\?"  # pylint: disable=invalid-name

# Assignment operators

t_EQUALS = r"="  # pylint: disable=invalid-name
t_TIMESEQUAL = r"\*="  # pylint: disable=invalid-name
t_DIVEQUAL = r"/="  # pylint: disable=invalid-name
t_MODEQUAL = r"%="  # pylint: disable=invalid-name
t_PLUSEQUAL = r"\+="  # pylint: disable=invalid-name
t_MINUSEQUAL = r"-="  # pylint: disable=invalid-name

# Increment/decrement
t_PLUSPLUS = r"\+\+"  # pylint: disable=invalid-name
t_MINUSMINUS = r"--"  # pylint: disable=invalid-name

# ->
# t_ARROW            = r'->'

# ?
# t_CONDOP           = r'\?'


# Delimeters
t_LPAREN = r"\("  # pylint: disable=invalid-name
t_RPAREN = r"\)"  # pylint: disable=invalid-name
t_LBRACKET = r"\["  # pylint: disable=invalid-name
t_RBRACKET = r"\]"  # pylint: disable=invalid-name
t_LBRACE = r"\{"  # pylint: disable=invalid-name
t_RBRACE = r"\}"  # pylint: disable=invalid-name
t_COMMA = r","  # pylint: disable=invalid-name
t_PERIOD = r"\."  # pylint: disable=invalid-name
t_SEMI = r";"  # pylint: disable=invalid-name
t_COLON = r":"  # pylint: disable=invalid-name
# t_ELLIPSIS         = r'\.\.\.'
t_AT = r"@"  # pylint: disable=invalid-name
# Identifiers and reserved words

reserved_map = {}
for r in reserved:
    reserved_map[r.lower()] = r


@TOKEN(r"[A-Za-z_]+[\w_]*")
def t_ID(t):  # pylint: disable=invalid-name
    """Get ID tokens."""
    t.type = reserved_map.get(t.value, "ID")
    return t


# Integer literal
t_ICONST = r"\d+([uU]|[lL]|[uU][lL]|[lL][uU])?"  # pylint: disable=invalid-name

# Floating literal
t_FCONST = (  # pylint: disable=invalid-name
    r"((\d+)(\.\d+)(e(\+|-)?(\d+))? | (\d+)e(\+|-)?(\d+))([lL]|[fF])?"
)

# String literal
t_SCONST = r"\"([^\"\\\n]|(\\.)|\\\n)*?\""  # pylint: disable=invalid-name

# Character constant 'c' or L'c'
t_CCONST = r"\'([^\'\\\n]|(\\.)|\\\n)*?\'"  # pylint: disable=invalid-name

# REGEX constant
# t_RXCONST = r'/[^/ ]+/g?'

# Comments


@TOKEN(r"(/\*( |\*\*)(.|\n)*?\*/)|(//.*)")
def t_comment(t):  # pylint: disable=invalid-name
    """Keep track of line count in comments."""
    t.lexer.lineno += t.value.count("\n")


@TOKEN(r"/\*\*[ ]+")
def t_DOCSTRINGOPEN(t):  # pylint: disable=invalid-name
    """Return docstring for later analysis."""
    return t


# t_COMMENTOPEN      = r'/\*'
t_COMMENTCLOSE = r"\*/"  # pylint: disable=invalid-name


# Preprocessor directive (ignored)
@TOKEN(r"\#(.)*?\n")
def t_preprocessor(t):  # pylint: disable=invalid-name
    """Ignored Preprocessor directive. Not used."""
    t.lexer.lineno += 1


def t_error(t) -> None:  # pylint: disable=invalid-name
    """Skip invalid characters and report."""
    print("Illegal character %s" % repr(t.value[0]))
    t.lexer.skip(1)
