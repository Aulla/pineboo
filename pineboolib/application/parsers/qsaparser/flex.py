"""Flex module."""

import ply.lex as lex  # type: ignore
from . import token_rules

from pineboolib import logging


# TODO: Cada vez que se cambia este fichero, se tiene que lanzar sin el "-OO" de python para acelerar. Construye entonces
# ..... el fichero de cache que subimos a git, y se relee desde ahí las siguientes veces con el -OO.
# ..... Si da problemas, hay que volver a optimize=0 y/o eliminar lextab.py
lexer = lex.lex(debug=False, optimize=1, module=token_rules, debuglog=logging)
if __name__ == "__main__":
    lex.runmain(lexer)
