from __future__ import unicode_literals

from textwrap import dedent  # noqa

from rply import Token
from pytest import raises

from blackbeard.lexer import Lexer, LexerError


class TestLexer(object):
    def has_tokens(self, result, token_list):
        for i, j in zip(result, token_list):
            if i.gettokentype() != j:
                break
        else:
            return True
        return False

    def do(self, source):
        lexer = Lexer(source, 1, {})
        return list(lexer.tokenize())

    def test_comment(self):
        source = "# This is a comment."
        assert self.has_tokens(self.do(source), ["COMMENT"])

    def test_symbol(self):
        assert self.do("foo") == [Token("SYMBOL", "foo")]
        assert self.do("foo bar") == [
            Token("SYMBOL", "foo"),
            Token("SYMBOL", "bar")
        ]

    def test_star(self):
        assert self.has_tokens(
            self.do("a*b"),
            ["SYMBOL", "MUL", "SYMBOL"])
        assert self.has_tokens(
            self.do("a**b"),
            ["SYMBOL", "POW", "SYMBOL"])

    def test_exclamation(self):
        assert self.has_tokens(
            self.do("!a"),
            ["NOT", "SYMBOL"])
        assert self.has_tokens(
            self.do("a != b"),
            ["SYMBOL", "NE", "SYMBOL"])

    def test_equal(self):
        assert self.has_tokens(
            self.do("a = b"),
            ["SYMBOL", "EQ_ASSIGN", "SYMBOL"])
        assert self.has_tokens(
            self.do("a == b"),
            ["SYMBOL", "EQ", "SYMBOL"])

    def test_less_than(self):
        assert self.has_tokens(
            self.do("a < b"),
            ["SYMBOL", "LT", "SYMBOL"])
        assert self.has_tokens(
            self.do("a <= b"),
            ["SYMBOL", "LE", "SYMBOL"])
        assert self.has_tokens(
            self.do("a <- b"),
            ["SYMBOL", "LEFT_ASSIGN", "SYMBOL"])

    def test_greater_than(self):
        assert self.has_tokens(
            self.do("a > b"),
            ["SYMBOL", "GT", "SYMBOL"])
        assert self.has_tokens(
            self.do("a >= b"),
            ["SYMBOL", "GE", "SYMBOL"])

    def test_string_quote(self):
        assert self.has_tokens(
            self.do("'The rain in Spain'"),
            ["STR_CONST"])
        assert self.has_tokens(
            self.do('"I\'m crazy! For Johnny Pumpkins!"'),
            ["STR_CONST"])
        assert self.has_tokens(
            self.do('"I\\"m crazy! For Johnny Pumpkins!"'),
            ["STR_CONST"])
        with raises(LexerError):
            self.do("'EOF in string")

    def test_plus(self):
        assert self.has_tokens(
            self.do("a + b"),
            ["SYMBOL", "PLUS", "SYMBOL"])

    def test_minus(self):
        assert self.has_tokens(
            self.do("a - b"),
            ["SYMBOL", "MINUS", "SYMBOL"])
        assert self.has_tokens(
            self.do("a -> b"),
            ["SYMBOL", "RIGHT_ASSIGN", "SYMBOL"])
        assert self.has_tokens(
            self.do("-b"),
            ["MINUS", "SYMBOL"])
