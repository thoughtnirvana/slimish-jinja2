import re

# Default Jinja environment.
env = {'block_start_string': '{%', 'block_end_string': '%}',
       'variable_start_string': '{{', 'variable_end_string': '}}'}


class Token(object):
    # Parent class for all types of tokens.
    # Not really needed here since it doesn't
    # abstract anything and the parser code
    # doesn't opearte on the parent class.
    pass


DOCTYPE = intern('doctype')
class DoctypeToken(Token):
    doctypes = {'html': '<!doctype html>',
                '5': '<!doctype html>',
                '1.1': '<!doctype html public "-//w3c//dtd xhtml 1.1//en" "http://www.w3.org/tr/xhtml11/dtd/xhtml11.dtd">',
                'x_strict': '<!doctype html public "-//w3c//dtd xhtml 1.0 strict//en" "http://www.w3.org/tr/xhtml1/dtd/xhtml1-strict.dtd">',
                'x_frameset': '<!doctype html public "-//w3c//dtd xhtml 1.0 frameset//en" "http://www.w3.org/tr/xhtml1/dtd/xhtml1-frameset.dtd">',
                'x_mobile': '<!doctype html public "-//wapforum//dtd xhtml mobile 1.2//en" "http://www.openmobilealliance.org/tech/dtd/xhtml-mobile12.dtd">',
                'x_basic': '<!doctype html public "-//w3c//dtd xhtml basic 1.1//en" "http://www.w3.org/tr/xhtml-basic/xhtml-basic11.dtd">',
                'x_transitional': '<!doctype html public "-//w3c//dtd xhtml 1.0 transitional//en" "http://www.w3.org/tr/xhtml1/dtd/xhtml1-transitional.dtd">',
                'strict': '<!doctype html public "-//w3c//dtd html 4.01//en" "http://www.w3.org/tr/html4/strict.dtd">',
                'frameset': '<!doctype html public "-//w3c//dtd html 4.01 frameset//en" "http://www.w3.org/tr/html4/frameset.dtd">',
                'transitional': '<!doctype html public "-//w3c//dtd html 4.01 transitional//en" "http://www.w3.org/tr/html4/loose.dtd">',
               }

    def __init__(self, token_type, lineno, dtd):
        self.original_dtd = dtd
        self.__dict__.update(token_type=token_type, lineno=lineno)
        bang_idx = dtd.index('!')
        self.dtd = dtd[bang_idx+1:].strip()

    def __str__(self):
        try:
            return self.doctypes[self.dtd]
        except KeyError, ex:
            raise SyntaxError("Invalid doctype at line %d: %s" % (self.lineno, self.original_dtd))


# HTML token types.
HTML_TAG = intern('html_tag')
HTML_NC_TAG = intern('html_nc_tag')
HTML_TAG_OPEN = intern('html_tag_open')
HTML_TAG_CLOSE = intern('html_tag_close')

class HtmlToken(Token):
    """
    HTML token.
    """
    no_content_html_tags = set(map(intern,
                                   ['br', 'img', 'link', 'hr', 'meta', 'input']))

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
            self.contents = parse_text_contents(contents[1:])

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
UNINDENT = intern('unindent')
INDENT = intern('indent')

class IndentToken(Token):
    def __init__(self, token_type, lineno, spacer):
        self.__dict__.update(token_type=token_type, lineno=lineno,
                            spacer=spacer)

    def __str__(self):
        return self.spacer


TEXT = intern('text')

class TextToken(Token):
    def __init__(self, token_type, lineno, text):
        self.__dict__.update(token_type=token_type, lineno=lineno,
                             text=parse_text_contents(text))

    def __str__(self):
        return self.text


JINJA_TAG = intern('jinja_tag')
JINJA_OPEN_TAG = intern('jinja_open_tag')
JINJA_CLOSE_TAG = intern('jinja_close_tag')
JINJA_NC_TAG = intern('jinja_nc_tag')

class JinjaToken(Token):
    no_content_jinja_tags = set(map(intern,
                                    ['include', 'extends', 'import', 'set',
                                     'from', 'do', 'break', 'continue',
                                    ]))

    def __init__(self, token_type, lineno, tag_name, full_line):
        self.__dict__.update(token_type=token_type, lineno=lineno,
                             tag_name=tag_name.strip(), full_line=full_line)

    def __str__(self):
        if self.token_type == JINJA_TAG:
            open_tag = '%s %s %s' % (env['block_start_string'], self.full_line,
                                    env['block_end_string'])
            close_tag = '%s %s %s' % (env['block_start_string'], 'end%s' % self.tag_name,
                                     env['block_end_string'])
            return '%s%s' % (open_tag, close_tag)
        elif self.token_type in (JINJA_OPEN_TAG, JINJA_NC_TAG):
            return '%s %s %s' % (env['block_start_string'], self.full_line,
                                 env['block_end_string'])
        elif self.token_type == JINJA_CLOSE_TAG:
            return '%s %s %s' % (env['block_start_string'], 'end%s' % self.tag_name,
                                env['block_end_string'])


JINJA_OUTPUT_TAG = intern('jinja_output_tag')

class JinjaOutputToken(Token):
    def __init__(self, token_type, lineno, contents):
        self.__dict__.update(token_type=token_type, lineno=lineno,
                             contents=parse_text_contents(contents))

    def __str__(self):
        return '%s %s %s' % (env['variable_start_string'], self.contents,
                             env['variable_end_string'])


def parse_text_contents(contents):
    """
    Substitutes `=val` with `{{ val }}`.
    """
    dynamic_val = re.compile(r'(?<!\\)= \s* ([^\s]+)', re.X)
    escaped_val = re.compile(r'\\ \s* (=)', re.X)
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
    return (short_tag_name.strip(), tag_name)
