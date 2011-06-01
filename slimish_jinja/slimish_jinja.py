import os.path
from cStringIO import StringIO
# Jinja imports.
from jinja2 import  Environment, TemplateSyntaxError
from jinja2.ext import Extension
# Project imports.
from lexer import Lexer
from parser import Parser

class SlimishExtension(Extension):
    """
    Converts slim templates to jinja format.
    """
    def __init__(self, env):
        """
        Sets defaults for the extension.
        """
        super(SlimishExtension, self).__init__(environment)
        env.extend(
            slim_debug=True,
            file_extensions=('.slim',),
        )

    def preprocess(self, source, name, filename=None):
        """
        Converts given slim template to jinja template.
        If `source` isn't slim, it's returned as is.
        """
        if not os.path.splitext(name)[1] in self.env.file_extensions:
            return source
        output = StringIO()
        lexer = Lexer(iter(source.splitlines()))
        Parser(lexer, callback=output.write, debug=self.env.slim_debug).parse()
        return output.getvalue()
