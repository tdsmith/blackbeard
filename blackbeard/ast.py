from __future__ import unicode_literals

from rply.token import BaseBox, Token  # noqa:F401


class ASTNode(BaseBox):
    pass


class Block(ASTNode):
    def __init__(self, statements):
        # type: (List[ASTNode]) -> None
        self.statements = [s for s in statements if s]

    @staticmethod
    def from_statement(statement):
        # type: (ASTNode) -> Block
        return Block([statement])

    def extend(self, other):
        # type: (Block) -> Block
        assert isinstance(other, Block)
        self.statements.extend(other.statements)
        return self

    def append(self, statement):
        # type: (ASTNode) -> Block
        self.statements.append(statement)
        return self

    def __repr__(self):
        # type: () -> bytes
        return ("ast.Block(%s)" % repr(self.statements)).encode("utf-8")


class Vector(ASTNode):
    FLOAT = 0
    INT = 1
    CHAR = 2
    BOOL = 3

    def __init__(self, values, type):
        # type: (List, int) -> None
        self.values = values
        self.type = type

    def __repr__(self):
        # type: () -> bytes
        return ("ast.Vector(%s)" % repr(self.values)).encode("utf-8")


class Na(ASTNode):
    pass


class Symbol(ASTNode):
    def __init__(self, name):
        # type: (unicode) -> None
        self.name = name

    def __repr__(self):
        # type: () -> bytes
        return ("ast.Symbol(%s)" % self.name).encode("utf-8")


class BinaryOperation(ASTNode):
    def __init__(self, operator, left, right):
        # type: (Token, ASTNode, ASTNode) -> None
        self.operator = operator.gettokentype()
        self.left = left
        self.right = right

    def __repr__(self):
        # type: () -> bytes
        return (
            "ast.BinaryOperation(%s, %s, %s)" %
            (self.operator, repr(self.left), repr(self.right))).encode("utf-8")


class Assign(ASTNode):
    def __init__(self, target, value):
        # type: (ASTNode, ASTNode) -> None
        self.target = target
        self.value = value

    def __repr__(self):
        # type: () -> bytes
        return ((b"ast.Assign(target=%s, value=%s)" % (self.target, self.value))
                .encode("utf-8"))
