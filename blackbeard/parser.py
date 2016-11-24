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

    # R grammar:
    # https://github.com/wch/r-source/blob/af7f52f70101960861e5d995d3a4bec010bc89e6/src/main/gram.y

    pg = ParserGenerator(
        ["LEFT_ASSIGN", "EQ_ASSIGN", "RIGHT_ASSIGN", "NEWLINE", "SEMICOLON",
         "MUL", "POW", "DIV", "MOD", "PLUS", "UPLUS", "MINUS", "UMINUS",
         "GT", "GE", "LT", "LE", "EQ", "NE", "AND", "OR", "AND2", "OR2",
         "LBRACE", "RBRACE", "LPAREN", "RPAREN", "LSQUARE", "RSQUARE",
         "STR_CONST", "NUM_CONST", "SYMBOL", "NA", "QUESTION", "COLON",
         "SPECIAL", "TILDE", "FUNCTION", "COMMA"],
        precedence=[
            ("left", ["QUESTION"]),
            ("right", ["LEFT_ASSIGN"]),
            ("right", ["EQ_ASSIGN"]),
            ("left", ["RIGHT_ASSIGN"]),
            ("left", ["TILDE"]),
            ("left", ["OR", "OR2"]),
            ("left", ["AND", "AND2"]),
            ("nonassoc", ["GT", "GE", "LT", "LE", "EQ", "NE"]),
            ("left", ["PLUS", "MINUS"]),
            ("left", ["MUL", "DIV", "MOD"]),
            ("left", ["SPECIAL"]),
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

    @pg.production("formlist : SYMBOL")
    @pg.production("formlist : SYMBOL EQ_ASSIGN expr")
    def formlist_from_symbol(self, p):
        # type: (List[ast.ASTNode]) -> ast.FormalList
        value = p[2] if len(p) > 1 else None
        return ast.FormalList(p[0], value)

    @pg.production("formlist : formlist COMMA SYMBOL")
    @pg.production("formlist : formlist COMMA SYMBOL EQ_ASSIGN expr")
    def formlist_extend(self, p):
        # type: (List[ast.ASTNode]) -> ast.FormalList
        value = p[4] if len(p) > 3 else None
        return p[0].append_formal(p[2], value)

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
        # TODO: support L, I extensions
        return ast.Vector([
            ast.FloatValue(float(p[0].getstr()))
        ])

    @pg.production("expr : STR_CONST")
    def expr_str_const(self, p):
        # type: (List[Token]) -> ast.Vector
        return ast.Vector([
            ast.CharValue(p[0].getstr().decode("utf-8"))
        ])

    @pg.production("expr : NA")
    def expr_na(self, p):
        # type: (List[Token]) -> ast.Vector
        return ast.Vector([
            ast.BoolValue(False, na=True)
        ])

    @pg.production("expr : SYMBOL")
    def simple_expr(self, p):
        # type: (List[Token]) -> ast.Symbol
        return ast.Symbol(p[0].getstr().decode("utf-8"))

    @pg.production("expr : expr COLON expr")
    @pg.production("expr : expr PLUS expr")
    @pg.production("expr : expr MINUS expr")
    @pg.production("expr : expr MUL expr")
    @pg.production("expr : expr DIV expr")
    @pg.production("expr : expr POW expr")
    @pg.production("expr : expr SPECIAL expr")
    @pg.production("expr : expr MOD expr")
    @pg.production("expr : expr TILDE expr")
    @pg.production("expr : expr QUESTION expr")
    @pg.production("expr : expr LT expr")
    @pg.production("expr : expr LE expr")
    @pg.production("expr : expr EQ expr")
    @pg.production("expr : expr NE expr")
    @pg.production("expr : expr GE expr")
    @pg.production("expr : expr GT expr")
    @pg.production("expr : expr AND expr")
    @pg.production("expr : expr OR expr")
    @pg.production("expr : expr AND2 expr")
    @pg.production("expr : expr OR2 expr")
    def expr_binary_op(self, p):
        # type: (List[Union[ast.ASTNode, Token]]) -> ast.BinaryOperation
        return ast.BinaryOperation(
            p[1].getstr(),
            p[0],
            p[2])

    @pg.production("expr : expr LEFT_ASSIGN expr")
    def expr_left_assign(self, p):
        # type: (List[Union[ast.ASTNode, Token]]) -> ast.Assign
        return ast.Assign(target=p[0], value=p[2])

    @pg.production("expr : expr RIGHT_ASSIGN expr")
    def expr_right_assign(self, p):
        # type: (List[Union[ast.ASTNode, Token]]) -> ast.Assign
        return ast.Assign(target=p[2], value=p[0])

    @pg.production("expr : FUNCTION LPAREN formlist RPAREN expr_or_assign")
    def expr_function_definition(self, p):
        # type: (List[ast.ASTNode]) -> ast.Function
        return ast.Function(p[2], p[4])

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


def parse(source):
    # type: (bytes) -> ast.ASTNode
    lexer = Lexer(source, 1, {})
    parser = Parser(lexer)
    return parser.parse()


def main():
    # type: () -> None
    "NOT_RPYTHON"
    import pdb
    import pprint
    import sys
    buf = open(sys.argv[1]).read()
    lexer = Lexer(buf, 1, {})
    parser = Parser(lexer)
    if "--pdb" in sys.argv:
        pdb.set_trace()
    pprint.pprint(parser.parse().as_dict())
