#!/usr/bin/env python
import sys, os
from lexer import Lexer
from parser import Parser

demo_template = os.path.realpath(os.path.join(os.curdir, 'demo.slim'))
with open(demo_template) as template:
    lexer = Lexer(template)
    Parser(lexer, debug=True).parse()
    #for l in lexer(): print l, l.token_type, l.lineno
