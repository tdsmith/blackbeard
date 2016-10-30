from __future__ import unicode_literals

from rply import ParserGenerator, Token  # noqa:F401
from typing import Iterator, Union  # noqa:F401

from blackbeard import ast
from blackbeard.lexer import Lexer


class LexerWrapper(object):
    def __init__(self, lexer):
        # type: (Iterator[Token]) -> None
        self.lexer = lexer

    def next(self):
        # type: () -> Token
        try:
            return self.lexer.next()
        except StopIteration:
            return None


class Parser(object):
    def __init__(self, lexer):
        # type: (Lexer) -> None
        self.lexer = lexer

    def parse(self):
        # type: () -> ast.ASTNode
        l = LexerWrapper(self.lexer.tokenize())
        return self.parser.parse(l, state=self)

    pg = ParserGenerator(
        ["LEFT_ASSIGN", "EQ_ASSIGN", "RIGHT_ASSIGN", "NEWLINE", "SEMICOLON",
         "MUL", "POW", "DIV", "MOD", "PLUS", "UPLUS", "MINUS", "UMINUS",
         "LBRACE", "RBRACE", "LPAREN", "RPAREN", "LSQUARE", "RSQUARE",
         "STR_CONST", "NUM_CONST", "SYMBOL", "NA", "QUESTION", "COLON"],
        precedence=[
            ("left", ["QUESTION"]),
            ("right", ["LEFT_ASSIGN"]),
            ("right", ["EQ_ASSIGN"]),
            ("left", ["RIGHT_ASSIGN"]),
            ("left", ["PLUS", "MINUS"]),
            ("left", ["MUL", "DIV", "MOD"]),
            ("left", ["COLON"]),
            ("left", ["UPLUS", "UMINUS"]),
            ("right", ["POW"]),
            ("nonassoc", ["LPAREN", "LSQUARE"]),
        ]
    )

    @pg.production("exprlist : ")
    def exprlist_none(self, p):
        # type: (List[Token]) -> ast.Block
        return ast.Block([])

    @pg.production("exprlist : exprlist terms")
    def exprlist_terminate(self, p):
        # type: (List[Union[ast.ASTNode, Token]]) -> ast.Block
        return p[0]

    @pg.production("exprlist : expr_or_assign")
    def exprlist_from_expr(self, p):
        # type: (List[ast.ASTNode]) -> ast.Block
        return ast.Block.from_statement(p[0])

    @pg.production("exprlist : exprlist terms expr_or_assign")
    def exprlist_extend(self, p):
        # type: (List[Union[ast.ASTNode, Token]]) -> ast.Block
        return p[0].append(p[2])

    @pg.production("expr_or_assign : expr")
    def expr_or_assign_from_expr(self, p):
        # type: (List[ast.ASTNode]) -> ast.ASTNode
        return p[0]

    @pg.production("expr_or_assign : equal_assign")
    def expr_from_equal_assign(self, p):
        # type: (List[ast.ASTNode]) -> ast.ASTNode
        return p[0]

    @pg.production("equal_assign : expr EQ_ASSIGN expr_or_assign")
    def equal_assign_expression(self, p):
        # type: (List[Union[ast.ASTNode, Token]]) -> ast.Assign
        return ast.Assign(target=p[0], value=p[2])

    @pg.production("expr : NUM_CONST")
    def expr_num_const(self, p):
        # type: (List[Token]) -> ast.Vector
        return ast.Vector([p[0].getstr()], ast.Vector.FLOAT)

    @pg.production("expr : STR_CONST")
    def expr_str_const(self, p):
        # type: (List[Token]) -> ast.Vector
        return ast.Vector([p[0].getstr()], ast.Vector.CHAR)

    @pg.production("expr : NA")
    def expr_na(self, p):
        # type: (List[Token]) -> ast.Vector
        return ast.Vector([ast.Na()], ast.Vector.BOOL)

    @pg.production("expr : SYMBOL")
    def simple_expr(self, p):
        # type: (List[Token]) -> ast.Symbol
        return ast.Symbol(p[0].getstr())

    @pg.production("expr : expr PLUS expr")
    @pg.production("expr : expr MINUS expr")
    @pg.production("expr : expr MUL expr")
    @pg.production("expr : expr DIV expr")
    @pg.production("expr : expr POW expr")
    @pg.production("expr : expr COLON expr")
    @pg.production("expr : expr MOD expr")
    @pg.production("expr : expr QUESTION expr")
    def expr_binary_op(self, p):
        # type: (List[Union[ast.ASTNode, Token]]) -> ast.BinaryOperation
        return ast.BinaryOperation(p[1], p[0], p[2])

    @pg.production("expr : expr LEFT_ASSIGN expr")
    def expr_left_assign(self, p):
        # type: (List[Union[ast.ASTNode, Token]]) -> ast.Assign
        return ast.Assign(target=p[0], value=p[2])

    @pg.production("expr : expr RIGHT_ASSIGN expr")
    def expr_right_assign(self, p):
        # type: (List[Union[ast.ASTNode, Token]]) -> ast.Assign
        return ast.Assign(target=p[2], value=p[0])

    @pg.production("expr : LBRACE exprlist RBRACE")
    def expr_from_exprlist(self, p):
        # type: (List[Union[ast.Block, Token]]) -> ast.Block
        return p[1]

    @pg.production("expr : LPAREN expr_or_assign RPAREN")
    def expr_from_parens(self, p):
        # type: (List[Union[ast.ASTNode, Token]]) -> ast.ASTNode
        return p[1]

    @pg.production("term : SEMICOLON")
    @pg.production("term : NEWLINE")
    def term(self, p):
        # type: (List[Token]) -> ast.Token
        return p[0]

    @pg.production("terms : term")
    def terms(self, p):
        # type: (List[Token]) -> ast.Token
        return p[0]

    @pg.production("terms : terms SEMICOLON")
    def terms_ext(self, p):
        # type: (List[Token]) -> ast.Token
        return p[0]

    @pg.production("opt_term : terms")
    def opt_term(self, p):
        # type: (List[Token]) -> ast.Token
        return p[0]

    @pg.production("opt_term : ")
    def opt_term_null(self, p):
        # type: (List[Token]) -> ast.Token
        return None

    @pg.production("opt_nl : ")
    def opt_nl_none(self, p):
        # type: (List[Token]) -> None
        return None

    @pg.production("opt_nl : NEWLINE")
    def opt_nl(self, p):
        # type: (List[Token]) -> None
        return None

    parser = pg.build()


def main():
    # type: () -> None
    "NOT_RPYTHON"
    import pdb
    import pprint
    import sys
    buf = open(sys.argv[1]).read().decode("utf-8")
    lexer = Lexer(buf, 1, {})
    parser = Parser(lexer)
    if "--pdb" in sys.argv:
        pdb.set_trace()
    pprint.pprint(parser.parse())
