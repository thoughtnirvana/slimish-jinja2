#!/usr/bin/env python
import sys
from slim_to_jinja import Lexer, Translator

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
      p
        |It can have dynamic =content .
    ul
      -for user in users
        li Found a =user
        li =user.name
        li =user.age
      -else
        li No users.
'''

lexer = Lexer(template.splitlines())
translator = Translator(lexer, debug=True)
for t in translator():
    sys.stdout.write(t)
