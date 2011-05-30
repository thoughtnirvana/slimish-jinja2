import re, sys
from tokens import *

class Lexer(object):
    """
    Tokenizes slim templates.
    """

    key_val_pat = re.compile(r'\s+ (.+?) \s*=\s* (["\']) ([^\2]+?) \2', re.X)
    whitespace = re.compile(r'\s+')

    def __init__(self, src):
        self.__dict__.update(src=src, indents=[], in_text_block=False,
                             buf=[], lineno=0, text_lineno=1)
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
                    if indent_change.token_type == UNINDENT:
                        yield TextToken(TEXT, self.text_lineno, "".join(self.buf))
                        yield indent_change
                        self.in_text_block = False
                        self.buf = []
                else:
                    yield indent_change
            # Keep reading text if we are in text block.
            if self.in_text_block:
                self.buf.append(line[self.indents[-1]:].rstrip())
                continue
            first_char = stripped_line[0]
            if first_char == '/':
                # Ignore comments.
                continue
            # Pass the read line to relevant handler.
            handler = self.handlers.get(first_char, self.handle_html)
            ret = handler(stripped_line)
            if ret: yield ret
        # yield implicit closed tags.
        indents = self.indents
        lineno = self.lineno
        while indents:
            indent_len = indents.pop()
            yield IndentToken(UNINDENT, lineno, ' ' * indent_len)
            lineno += 1
        # unindent for `html` for which no indent was recorded.
        yield IndentToken(UNINDENT, lineno, '')

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
                if not self.in_text_block:
                    indents.append(indent_len)
                    return IndentToken(INDENT, self.lineno, indent)
            elif indent_len < self.indents[-1]:
                self.indents.pop()
                return IndentToken(UNINDENT, self.lineno, indent)
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
        elif tag_name in HtmlToken.no_content_html_tags:
            return HtmlToken(HTML_NC_TAG, self.lineno, tag_name, attrs)
        else:
            return HtmlToken(HTML_TAG_OPEN, self.lineno, tag_name, attrs)

    def handle_jinja(self, line):
        """
        Handles jinja tags.
        """
        tag_name = intern(self.whitespace.split(line)[0][1:])
        if tag_name in JinjaToken.no_content_jinja_tags:
            return JinjaToken(JINJA_NC_TAG, self.lineno, tag_name, line[1:])
        return JinjaToken(JINJA_OPEN_TAG, self.lineno, tag_name, line[1:])

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
