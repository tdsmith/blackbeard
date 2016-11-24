from rply.token import BaseBox, Token  # noqa:F401
from typing import Any, Optional, Tuple  # noqa:F401


class ASTNode(BaseBox):
    def __eq__(self, other):
        # type: (object) -> bool
        if not isinstance(other, ASTNode):
            return NotImplemented
        return type(self) is type(other) and self.__dict__ == other.__dict__

    def __repr__(self):
        # type: () -> bytes
        raise NotImplementedError


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
        return "ast.Block(%s)" % str(self.statements)


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
        return "ast.Vector(%s, type=%d)" % (str(self.values), self.type)


class Na(ASTNode):
    pass


class Symbol(ASTNode):
    def __init__(self, name):
        # type: (str) -> None
        self.name = name.decode("utf-8")

    def __repr__(self):
        # type: () -> bytes
        return "ast.Symbol(%s)" % self.name.encode("utf-8")


class BinaryOperation(ASTNode):
    def __init__(self, operator, left, right):
        # type: (Token, ASTNode, ASTNode) -> None
        self.operator = operator.gettokentype()
        self.left = left
        self.right = right

    def __repr__(self):
        # type: () -> bytes
        return ("ast.BinaryOperation(%s, %s, %s)" %
                (self.operator, str(self.left), str(self.right)))


class Assign(ASTNode):
    def __init__(self, target, value):
        # type: (ASTNode, ASTNode) -> None
        self.target = target
        self.value = value

    def __repr__(self):
        # type: () -> bytes
        return "ast.Assign(target=%s, value=%s)" % (self.target, self.value)


class FormalList(ASTNode):
    def __init__(self, symbol, value=None):
        # type: (Symbol, Optional[ASTNode]) -> None
        self.entries = []  # type: List[Tuple[Symbol, Optional[ASTNode]]]
        self.entries.append((symbol, value))

    def append_formal(self, symbol, value=None):
        # type: (Symbol, Optional[ASTNode]) -> FormalList
        self.entries.append((symbol, value))
        return self

    def __repr__(self):
        # type: () -> bytes
        return "ast.FormalList(%s)" % str(self.entries)


class Function(ASTNode):
    def __init__(self, formals, body):
        # type: (FormalList, ASTNode) -> None
        self.formals = formals
        self.body = body

    def __repr__(self):
        # type: () -> bytes
        return "ast.Function(%s, %s)" % (str(self.formals), str(self.body))
