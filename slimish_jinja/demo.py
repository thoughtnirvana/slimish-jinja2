#!/usr/bin/env python
import os
from lexer import Lexer
from parse import Parser

cur_dir = os.path.dirname(os.path.realpath(__file__))
demo_template = os.path.join(cur_dir, 'demo.slim')
with open(demo_template) as template:
    lexer = Lexer(template)
    Parser(lexer, debug=True).parse()
