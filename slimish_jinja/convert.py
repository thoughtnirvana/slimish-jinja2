#!/usr/bin/env python
import sys, os
from lexer import Lexer
from parser import Parser

with open(sys.argv[1]) as template:
    lexer = Lexer(template)
    Parser(lexer, debug=True).parse()
