from __future__ import unicode_literals

from pprint import pprint
import pytest  # noqa:F401
from textwrap import dedent

from blackbeard.lexer import Lexer
from blackbeard.parser import Parser


class TestParser(object):
    def do(self, source):
        lexer = Lexer(source, 1, {})
        pprint(list(lexer.tokenize()))

        lexer = Lexer(source, 1, {})
        parser = Parser(lexer)
        return parser.parse()

    def test_parses_source(self):
        source = dedent(
            """\
            a = 456.7
            b <- 5
            6 -> c
            """)
        self.do(source)

    def test_parses_block(self):
        source = dedent(
            """\
            {
                "String literal"
            }
            """)
        self.do(source)
