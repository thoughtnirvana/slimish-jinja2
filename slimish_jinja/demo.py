#!/usr/bin/env python
import sys
from lexer import Lexer
from parser import Parser

template = '''
html
  head
    title Slimish-Jinja Example
    meta name="keywords" content="template language"

  body#home.liquid
    h1.punch Text can be provided inline.

    #contents.main
      .lorem-ipsum
        |Text can be nested.
        And can span multiple lines.
        Left indent isn't preserved.
      p It can have dynamic =content .
    ul
        li Found a =user
         li =user.name
        li =user.age
        li No users.
'''

lexer = Lexer(template.splitlines())
Parser(lexer, debug=True).parse()
