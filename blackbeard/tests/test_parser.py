# coding=utf-8
import pytest  # noqa:F401
from textwrap import dedent

from blackbeard import ast
from blackbeard.parser import parse


class TestParser(object):
    def test_constant(self):
        assert parse("3") == ast.Block([
            ast.Vector([3.], ast.Vector.FLOAT)
        ])

        assert parse("3e3") == ast.Block([
            ast.Vector([3000.], ast.Vector.FLOAT)
        ])

        assert parse("5e-1") == ast.Block([
            ast.Vector([0.5], ast.Vector.FLOAT)
        ])

    def test_assignment(self):
        assert parse("a = 123") == ast.Block([
            ast.Assign(ast.Symbol("a"), ast.Vector([123.], ast.Vector.FLOAT))
        ])
        assert parse("a <- 123") == ast.Block([
            ast.Assign(ast.Symbol("a"), ast.Vector([123.], ast.Vector.FLOAT))
        ])
        assert parse("123 -> a") == ast.Block([
            ast.Assign(ast.Symbol("a"), ast.Vector([123.], ast.Vector.FLOAT))
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
                ast.Vector([u"String literal"], ast.Vector.CHAR)
            ])
        ])
