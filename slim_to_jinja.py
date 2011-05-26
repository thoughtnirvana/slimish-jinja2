import re, sys

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

# Token types.
DE_INDENT = intern('de_indent')
INDENT = intern('indent')
JINJA_TAG = intern('jinja_tag')
JINJA_OUTPUT_TAG = intern('jinja_output_tag')
HTML_TAG = intern('html_tag')
HTML_NC_TAG = intern('html_nc_tag')
HTML_TAG_OPEN = intern('html_tag_open')
HTML_TAG_CLOSE = intern('html_tag_close')
TEXT = intern('text')
no_content_html_tags = set(map(intern,
                               ['br', 'img', 'link', 'hr', 'meta', 'input']))
no_content_jinja_tags = set(map(intern,
                                ['include', 'extends', 'import', 'set',
                                 'from', 'do', 'break', 'continue',
                                ]))


class Lexer(object):
    """
    Tokenizes html in slim templates format.
    """

    key_val_pat = re.compile(r'\s+ (.+?) \s*=\s* (["\']) ([^\2]+?) \2', re.X)
    whitespace = re.compile(r'\s+')

    def __init__(self, src):
        self.src = src
        self.indents = []
        self.in_text_block = False
        self.buf = []
        self.handlers = {'-': self.handle_jinja,
                         '=': self.handle_output,
                         '|': self.handle_text}

    def __call__(self):
        """
        Tokenizes `self.src` and yields the `(token_type, token_vals)` pairs.
        """
        for line in self.src:
            # Ignore blank lines and check for indent.
            stripped_line = line.strip()
            if not stripped_line and not self.in_text_block: continue
            indent_change = self.check_indent(line)
            if indent_change:
                if self.in_text_block:
                    if indent_change[0] == DE_INDENT:
                        text = (t.lstrip() for t in self.buf)
                        yield (TEXT, " ".join(text))
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
        If indent increases, record it and the parent token.
        If indent decreases, yield parent token.
        """
        indent = self.whitespace.match(line)
        if indent:
            indent = indent.group()
            indent_len = len(indent)
            indents = self.indents
            if not indents or indent_len > indents[-1]:
                indents.append(indent_len)
                return (INDENT, indent)
            elif indent_len < self.indents[-1]:
                self.indents.pop()
                return (DE_INDENT, indent)
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
            return (HTML_TAG_OPEN, (tag_name, {}))
        # Get the attributes for the tag.
        attrs, contents = self.extract_values(tag_name, line)
        if contents:
            return (HTML_TAG, (tag_name, attrs, contents))
        elif tag_name in no_content_html_tags:
            return (HTML_NC_TAG, (tag_name, attrs))
        else:
            return (HTML_TAG_OPEN, (tag_name, attrs))

    def handle_jinja(self, line):
        """
        Handles jinja tags.
        """
        tag_name = intern(self.whitespace.split(line)[0][1:])
        return (JINJA_TAG, (tag_name, line[1:]))

    def handle_text(self, line):
        """
        Handles text nested with pipes.
        """
        self.in_text_block = True
        self.buf.append(line[1:])


    def handle_output(self, line):
        """
        Handles output statements
        """
        return (JINJA_OUTPUT_TAG, line[1:])


class Translator(object):
    def __init__(self, lexer, debug=False, jinja_env=None):
        self.__dict__.update(lexer=lexer, debug=debug,
                             indent='', indents=[],
                             tokens=[], block_start_string='{%',
                             block_end_string='%}', variable_start_string='{{',
                             variable_end_string='}}')

        if jinja_env: self.__dict__.update(**jinja_env)

    def __call__(self):
        """
        Returns translated lexon.
        """
        format_output = self.format_output
        handle_html_tag = self.handle_html_tag
        for lexon in self.lexer():
            # `lexon` is a `(token_type, val)` format tuple.
            # `val` depends on the type.
            token_type = lexon[0]
            ret = None
            if token_type in  (HTML_NC_TAG, HTML_TAG, HTML_TAG_OPEN):
                ret = handle_html_tag(token_type, lexon)
            elif token_type == JINJA_OUTPUT_TAG:
                ret = format_output('%s %s %s' % (self.variable_start_string,
                                                  lexon[1], self.variable_end_string))
            elif token_type == JINJA_TAG:
                ret = format_output('%s %s %s' % (self.block_start_string,
                                                  lexon[1][1], self.block_end_string))
            elif token_type == INDENT:
                self.indent = lexon[1]
            elif token_type == DE_INDENT:
                self.indent = lexon[1]
            elif token_type == TEXT:
                ret = format_output(lexon[1])
            if ret:
                yield ret

    def format_output(self, input):
        if self.debug:
            return ('%s%s\n' % (self.indent, input))
        else:
            return ('%s' % input).strip()

    def handle_html_tag(self, token_type, lexon):
        """
        Writes html from `lexon` to `self.out`.
        """
        short_tag_name, full_tag_name = parse_tag_name(lexon[1][0])
        if token_type == HTML_TAG_CLOSE:
            return '</%s>' % short_tag_name
        else:
            attribs = lexon[1][1]
            attribs = reduce(lambda prev, k: '%s %s="%s"' % (prev, k, self.parse_text_contents(attribs[k])),
                             attribs, '')
            if token_type == HTML_NC_TAG:
                return self.format_output('<%s %s/>' % (full_tag_name, attribs))
            elif token_type == HTML_TAG:
                contents = self.parse_text_contents(lexon[1][2])
                return self.format_output('<%s %s>%s</%s>' % (full_tag_name, attribs, contents, short_tag_name))
            elif token_type == HTML_TAG_OPEN:
                return self.format_output('<%s %s>' % (full_tag_name, attribs))

    def parse_text_contents(self, contents):
        """
        Substitutes `=val` with `{{ val }}`.
        """
        dynamic_val = re.compile(r'= \s* ([^\s]+)', re.X)
        escaped_val = re.compile(r'\ \s* (=)', re.X)
        contents = dynamic_val.sub(r'%s \1 %s' % (self.variable_start_string,
                                                self.variable_end_string), contents)
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
