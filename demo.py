#!/usr/bin/env python
import sys
from slim_to_jinja import Lexer, Translator

template = '''
html
  head
    title Slimish-Jinja Example
    meta name="keywords" content="template language"

  body#main.main
    h1.class1.class2#punch Markup examples

    #contents.example1
      | This content would come directly under div#content.
        It can span multiple lines.
      p Text can have dynamic =content .
    ul
      -for user in users
        li Found a =user
      -else
        li No users
'''

lexer = Lexer(iter(template.splitlines()))
translator = Translator(lexer, debug=True)
for t in translator():
    sys.stdout.write(t)
