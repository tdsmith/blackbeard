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

    def do(self, source, state=None):
        lexer = Lexer(source, 1, {})
        result = list(lexer.tokenize())
        if state:
            assert lexer.state == state
        return result

    def test_comment(self):
        source = "# This is a comment."
        assert self.has_tokens(self.do(source), ["COMMENT"])
        source = "foo + bar # This is a comment."
        assert self.has_tokens(
            self.do(source),
            ["SYMBOL", "PLUS", "SYMBOL", "COMMENT"])

    def test_symbol(self):
        assert self.do("foo") == [Token("SYMBOL", "foo")]
        assert self.do("foo bar") == [
            Token("SYMBOL", "foo"),
            Token("SYMBOL", "bar")
        ]
        assert (
            self.do("this.is.a.symbol") ==
            [Token("SYMBOL", "this.is.a.symbol")]
        )

    def test_star(self):
        assert self.has_tokens(
            self.do("a*b"),
            ["SYMBOL", "MUL", "SYMBOL"])
        assert self.has_tokens(
            self.do("a**b"),
            ["SYMBOL", "POW", "SYMBOL"])
        with raises(LexerError):
            self.do("*a")
        with raises(LexerError):
            self.do("**a")

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
        with raises(LexerError):
            self.do("=b")

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

    def test_question(self):
        assert self.has_tokens(
            self.do("a ? b"),
            ["SYMBOL", "QUESTION", "SYMBOL"])
        assert self.has_tokens(
            self.do("?b"),
            ["UQUESTION", "SYMBOL"])

    def test_ampersand(self):
        assert self.has_tokens(
            self.do("a&b"),
            ["SYMBOL", "AND", "SYMBOL"])
        assert self.has_tokens(
            self.do("a&&b"),
            ["SYMBOL", "AND2", "SYMBOL"])
        with raises(LexerError):
            self.do("&a")
        with raises(LexerError):
            self.do("a & & b")

    def test_pipe(self):
        assert self.has_tokens(
            self.do("a|b"),
            ["SYMBOL", "OR", "SYMBOL"])
        assert self.has_tokens(
            self.do("a||b"),
            ["SYMBOL", "OR2", "SYMBOL"])
        with raises(LexerError):
            self.do("|a")
        with raises(LexerError):
            self.do("a | | b")

    def test_plus(self):
        assert self.has_tokens(
            self.do("a + b"),
            ["SYMBOL", "PLUS", "SYMBOL"])
        assert self.has_tokens(
            self.do("+ b"),
            ["UPLUS", "SYMBOL"])

    def test_minus(self):
        assert self.has_tokens(
            self.do("a - b"),
            ["SYMBOL", "MINUS", "SYMBOL"])
        assert self.has_tokens(
            self.do("a -> b"),
            ["SYMBOL", "RIGHT_ASSIGN", "SYMBOL"])
        assert self.has_tokens(
            self.do("-b"),
            ["UMINUS", "SYMBOL"])

    def test_number(self):
        assert self.do("3") == [Token("NUM_CONST", "3")]
        assert self.do("3L") == [Token("NUM_CONST", "3L")]
        assert self.do("3.1415") == [Token("NUM_CONST", "3.1415")]
        assert self.do("1.23e4") == [Token("NUM_CONST", "1.23e4")]
        assert self.do("1e-2") == [Token("NUM_CONST", "1e-2")]
        assert len(self.do("1e23e4")) > 1
        with raises(LexerError):
            self.do("1.23.4")

    def test_parens(self):
        assert self.has_tokens(
            self.do("3 * (-a + 2)"),
            ["NUM_CONST", "MUL", "LPAREN", "UMINUS",
             "SYMBOL", "PLUS", "NUM_CONST", "RPAREN"])

    def test_parser_state_binops(self):
        assert self.has_tokens(
            self.do("3 + b"),
            ["NUM_CONST", "PLUS", "SYMBOL"])
        assert self.has_tokens(
            self.do("b + 3"),
            ["SYMBOL", "PLUS", "NUM_CONST"])

    def test_state_reset_on_newline(self):
        lexer = Lexer("a\n", 1, {})
        list(lexer.tokenize())
        assert lexer.state == lexer.EXPR_BEG
