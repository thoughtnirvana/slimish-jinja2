import re, sys

no_content_html_tags = set(map(intern,
                               ['br', 'img', 'link', 'hr', 'meta', 'input']))
no_content_jinja_tags = set(map(intern,
                                ['include', 'extends', 'import', 'set',
                                 'from', 'do', 'break', 'continue',
                                ]))

env = {'block_start_string': '{%', 'block_end_string': '%}',
       'variable_start_string': '{{', 'variable_end_string': '}}'}


class Token(object):
    pass


# HTML token types.
HTML_TAG = intern('html_tag')
HTML_NC_TAG = intern('html_nc_tag')
HTML_TAG_OPEN = intern('html_tag_open')
HTML_TAG_CLOSE = intern('html_tag_close')

class HtmlToken(Token):
    """
    HTML token.
    """
    def __init__(self, token_type, lineno, tag_name,
                 attribs=None, contents=None):
        self.__dict__.update(token_type=token_type, lineno=lineno)
        self.tag_name, self.full_tag_name = parse_tag_name(tag_name)
        # Parse the attributes and the contents if any.
        if attribs:
            self.attribs = reduce(lambda prev, k: '%s %s="%s"' %
                            (prev, k, parse_text_contents(attribs[k])), attribs, ' ')
        else:
            self.attribs = ''
        if contents:
            self.contents = parse_text_contents(contents)

    def __str__(self):
        token_type = self.token_type
        if token_type == HTML_TAG_CLOSE:
            return '</%s>' % self.tag_name
        elif token_type == HTML_NC_TAG:
            return '<%s%s/>' % (self.full_tag_name, self.attribs)
        elif token_type == HTML_TAG:
            return '<%s%s>%s</%s>' % (self.full_tag_name, self.attribs, self.contents, self.tag_name)
        elif token_type == HTML_TAG_OPEN:
            return '<%s%s>' % (self.full_tag_name, self.attribs)



# Indent token types.
DE_INDENT = intern('de_indent')
INDENT = intern('indent')

class IndentToken(Token):
    def __init__(self, token_type, lineno, indent_len):
        self.__dict__.update(token_type=token_type, lineno=lineno,
                            indent_len=indent_len)

    def __str__(self):
        return ' ' * indent_len


TEXT = intern('text')

class TextToken(Token):
    def __init__(self, token_type, lineno, text):
        self.__dict__.update(token_type=token_type, lineno=lineno,
                             text=parse_text_contents(text))

    def __str__(self):
        return self.text


JINJA_TAG = intern('jinja_tag')

class JinjaToken(Token):
    def __init__(self, token_type, lineno, tag_name, full_line):
        self.__dict__.update(token_type=token_type, lineno=lineno,
                             tag_name=tag_name, full_line=full_line)

    def __str__(self):
        return '%s %s %s' % (env['block_start_string'], self.full_line,
                             env['block_end_string'])


JINJA_OUTPUT_TAG = intern('jinja_output_tag')

class JinjaOutputToken(Token):
    def __init__(self, token_type, lineno, contents):
        self.__dict__.update(token_type=token_type, lineno=lineno,
                             contents=parse_text_contents(contents))

    def __str__(self):
        return '%s %s %s' % (env['variable_start_string'], self.contents,
                             env['variable_end_string'])


class Lexer(object):
    """
    Tokenizes html in slim templates format.
    """

    key_val_pat = re.compile(r'\s+ (.+?) \s*=\s* (["\']) ([^\2]+?) \2', re.X)
    whitespace = re.compile(r'\s+')

    def __init__(self, src):
        self.__dict__.update(src=src, indents=[], in_text_block=False,
                             buf=[], lineno=1, text_lineno=1)
        self.handlers = {'-': self.handle_jinja,
                         '=': self.handle_jinja_output,
                         '|': self.handle_text}

    def __call__(self):
        """
        Tokenizes `self.src` and yields `Token` objects..
        """
        for line in self.src:
            self.lineno += 1
            # Ignore blank lines and check for indent.
            stripped_line = line.strip()
            if not stripped_line and not self.in_text_block: continue
            indent_change = self.check_indent(line)
            if indent_change:
                if self.in_text_block:
                    if indent_change.token_type == DE_INDENT:
                        text = (t.lstrip() for t in self.buf)
                        yield TextToken(TEXT, self.text_lineno, " ".join(text))
                        yield indent_change
                        self.in_text_block = False
                        self.buf = []
                else:
                    yield indent_change
            # Keep reading text if we are in text block.
            if self.in_text_block:
                self.buf.append(line)
                continue
            # Pass the read line to relevant handler.
            handler = self.handlers.get(stripped_line[0], self.handle_html)
            ret = handler(stripped_line)
            if ret: yield ret

    def check_indent(self, line):
        """
        Checks for increase or decrease in indent.
        Yield `IndentToken` if index changes.
        """
        indent = self.whitespace.match(line)
        if indent:
            indent = indent.group()
            indent_len = len(indent)
            indents = self.indents
            if not indents or indent_len > indents[-1]:
                indents.append(indent_len)
                return IndentToken(INDENT, self.lineno, indent)
            elif indent_len < self.indents[-1]:
                self.indents.pop()
                return IndentToken(DE_INDENT, self.lineno, indent)
        return False

    def extract_values(self, tag_name, line):
        """
        Extracts `key=val` pairs and `contents` from the given `tokens`
        and returns the resulting dictionary and contents.
        """
        attrs = {}
        contents = ''
        # Get the attributes for the tag.
        m = None
        for m in self.key_val_pat.finditer(line):
            attrs[m.group(1)] = m.group(3)
        if not m or m.end() < len(line) - 1:
            start_idx = m.end() + 1 if m else len(tag_name)
            contents = line[start_idx:]
        return attrs, contents

    def handle_html(self, line):
        """
        Returns `(token_type, token_vals)` for html tags.
        """
        tag_and_vals = self.whitespace.split(line)
        tag_name = intern(tag_and_vals[0])
        if len(tag_and_vals) == 1:
            return HtmlToken(HTML_TAG_OPEN, self.lineno, tag_name)
        # Get the attributes for the tag.
        attrs, contents = self.extract_values(tag_name, line)
        if contents:
            return HtmlToken(HTML_TAG, self.lineno, tag_name, attrs, contents)
        elif tag_name in no_content_html_tags:
            return HtmlToken(HTML_NC_TAG, self.lineno, tag_name, attrs)
        else:
            return HtmlToken(HTML_TAG_OPEN, self.lineno, tag_name, attrs)

    def handle_jinja(self, line):
        """
        Handles jinja tags.
        """
        tag_name = intern(self.whitespace.split(line)[0][1:])
        return JinjaToken(JINJA_TAG, self.lineno, tag_name, line[1:])

    def handle_text(self, line):
        """
        Handles text nested with pipes.
        """
        self.in_text_block = True
        self.text_start_line = self.lineno
        self.buf.append(line[1:])


    def handle_jinja_output(self, line):
        """
        Handles output statements
        """
        return JinjaOutputToken(JINJA_OUTPUT_TAG, self.lineno, line[1:])


class Translator(object):
    """
    Translates slim syntax to jinja2 syntax.
    """
    def __init__(self, lexer, debug=False):
        self.__dict__.update(lexer=lexer, debug=debug,
                             indent='', indents=[],
                             tokens=[])

    def __call__(self):
        """
        Returns translated lexon.
        """
        format_output = self.format_output
        for token in self.lexer():
            # `lexon` is a `(token_type, val)` format tuple.
            # `val` depends on the type.
            token_type = token.token_type
            ret = None
            if token_type in  (HTML_NC_TAG, HTML_TAG, HTML_TAG_OPEN):
                yield format_output(token)
            elif token_type == JINJA_OUTPUT_TAG:
                yield format_output(token)
            elif token_type == JINJA_TAG:
                yield format_output(token)
            elif token_type == INDENT:
                self.indent = token.indent_len
            elif token_type == DE_INDENT:
                self.indent = token.indent_len
            elif token_type == TEXT:
                yield format_output(token)

    def format_output(self, input):
        if self.debug:
            return ('%s%s\n' % (self.indent, input))
        else:
            return ('%s' % input).strip()



def parse_text_contents(contents):
    """
    Substitutes `=val` with `{{ val }}`.
    """
    dynamic_val = re.compile(r'= \s* ([^\s]+)', re.X)
    escaped_val = re.compile(r'\ \s* (=)', re.X)
    contents = dynamic_val.sub(r'%s \1 %s' % (env['variable_start_string'],
                                              env['variable_end_string']), contents)
    contents = escaped_val.sub(r'\1', contents)
    return contents


def parse_tag_name(tag_name):
    """
    Returns tag name with classname and id substituted.
    p.name => p class="name"
    p.name#test => p class="name" id="test"
    .mid => div class="mid"
    #top => div id="top"
    .mid#top => div id="top" class="mid"
    """
    id_or_class = re.compile(r'[#.]')
    id_pat = re.compile(r'#([^#.]+)')
    class_pat = re.compile(r'\.([^#.]+)')
    tag_pat = re.compile(r'([^#.]+)')
    short_tag_name = tag_name

    if id_or_class.search(tag_name):
        if id_or_class.match(tag_name):
            short_tag_name = real_tag_name = 'div'
        else:
            short_tag_name = real_tag_name = tag_pat.match(tag_name).group(1)
        id_val = id_pat.search(tag_name)
        if id_val:
            real_tag_name = '%s id="%s"' % (real_tag_name, id_val.group(1))
        classes = []
        for m in class_pat.finditer(tag_name):
            classes.append(m.group(1))
        if classes:
            real_tag_name = '%s class="%s"' % (real_tag_name, " ".join(classes))
        tag_name = real_tag_name
    return (short_tag_name, tag_name)
