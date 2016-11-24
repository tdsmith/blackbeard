# coding=utf-8
import pytest  # noqa:F401
from textwrap import dedent

from blackbeard import ast
from blackbeard.parser import parse


class TestParser(object):
    def test_constant(self):
        assert parse("3") == ast.Block([
            ast.Vector([ast.FloatValue(3.)])
        ])
        assert parse("3e3") == ast.Block([
            ast.Vector([ast.FloatValue(3000.)])
        ])
        assert parse("5e-1") == ast.Block([
            ast.Vector([ast.FloatValue(0.5)])
        ])
        assert parse("NA") == ast.Block([
            ast.Vector([ast.BoolValue(False, na=True)])
        ])

    def test_simple_exprs(self):
        assert parse("(3)") == ast.Block([
            ast.Vector([ast.FloatValue(3.)])
        ])
        assert parse("3;;\n3") == ast.Block([
            ast.Vector([ast.FloatValue(3.)]),
            ast.Vector([ast.FloatValue(3.)])
        ])

    def test_assignment(self):
        assert parse("a = 123") == ast.Block([
            ast.Assign(ast.Symbol("a"), ast.Vector([ast.FloatValue(123.)]))
        ])
        assert parse("a <- 123") == ast.Block([
            ast.Assign(ast.Symbol("a"), ast.Vector([ast.FloatValue(123.)]))
        ])
        assert parse("123 -> a") == ast.Block([
            ast.Assign(ast.Symbol("a"), ast.Vector([ast.FloatValue(123.)]))
        ])

    def test_binary_operation(self):
        assert parse("a + b") == ast.Block([
            ast.BinaryOperation("+", ast.Symbol("a"), ast.Symbol("b"))
        ])

    def test_funcdef(self):
        assert parse("function() x") == ast.Block([
            ast.Function(formals=ast.FormalList(), body=ast.Symbol("x"))
        ])
        assert parse("function(x) x") == ast.Block([
            ast.Function(
                formals=ast.FormalList([
                    (ast.Symbol("x"), None)
                ]),
                body=ast.Symbol("x"))
        ])
        assert parse("function(x) { x + 3 }") == ast.Block([
            ast.Function(
                formals=ast.FormalList([
                    (ast.Symbol("x"), None)
                ]),
                body=ast.Block([
                    ast.BinaryOperation("+", ast.Symbol("x"), ast.Vector([ast.FloatValue(3.)]))
                ]))
        ])
        assert parse("function(x, y=0) { x + y }") == ast.Block([
            ast.Function(
                formals=ast.FormalList([
                    (ast.Symbol("x"), None),
                    (ast.Symbol("y"), ast.Vector([ast.FloatValue(0.)]))
                ]),
                body=ast.Block([
                    ast.BinaryOperation("+", ast.Symbol("x"), ast.Symbol("y"))
                ]))
        ])

    def test_parses_block(self):
        source = dedent(
            """\
            {
                "String literal"
            }
            """)
        assert parse(source) == ast.Block([
            ast.Block([
                ast.Vector([ast.CharValue(u"String literal")])
            ])
        ])

    def test_unicode_string(self):
        source = u'"👺"'
        assert parse(source.encode("utf-8")) == ast.Block([
            # strip quotes in a narrow-python friendly way
            ast.Vector([ast.CharValue(source[1:-1])])
        ])

    def test_unicode_symbol(self):
        assert parse(u"👺 = 5".encode("utf-8")) == ast.Block([
            ast.Assign(ast.Symbol(u"👺"), ast.Vector([ast.FloatValue(5.)]))
        ])
