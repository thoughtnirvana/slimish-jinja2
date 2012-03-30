import os.path
from cStringIO import StringIO
# Jinja imports.
from jinja2.ext import Extension
# Project imports.
from .lexer import Lexer
from .parse import Parser

class SlimishExtension(Extension):
    """
    Converts slim templates to jinja format.
    """
    def __init__(self, environment):
        """
        Sets defaults for the extension.
        """
        super(SlimishExtension, self).__init__(environment)
        environment.extend(
            slim_debug=True,
            file_extensions=('.slim',),
        )

    def preprocess(self, source, name, filename=None):
        """
        Converts given slim template to jinja template.
        If `source` isn't slim, it's returned as is.
        """
        if not os.path.splitext(name)[1] in self.environment.file_extensions:
            return source
        output = StringIO()
        lexer = Lexer(iter(source.splitlines()))
        Parser(lexer, callback=output.write, debug=self.environment.slim_debug).parse()
        return output.getvalue()
