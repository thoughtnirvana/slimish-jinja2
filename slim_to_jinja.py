#!/usr/bin/env python
import sys
from slimish_jinja import Lexer, Parser

with open(sys.argv[1]) as template:
    lexer = Lexer(template)
    Parser(lexer, debug=True).parse()
