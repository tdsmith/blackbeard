from __future__ import unicode_literals

from rply.token import BaseBox, Token  # noqa:F401
from typing import Any  # noqa:F401


class ASTNode(BaseBox):
    def as_dict(self):
        # type: () -> Dict[unicode, Any]
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

    def as_dict(self):
        # type: () -> Dict[unicode, Any]
        return {"Block": [s.as_dict() for s in self.statements]}


class Vector(ASTNode):
    FLOAT = 0
    INT = 1
    CHAR = 2
    BOOL = 3

    def __init__(self, values, type):
        # type: (List, int) -> None
        self.values = values
        self.type = type

    def as_dict(self):
        # type: () -> Dict[unicode, Any]
        return {"Vector": {
            "type": self.type,
            "values": str(self.values)
        }}


class Na(ASTNode):
    pass


class Symbol(ASTNode):
    def __init__(self, name):
        # type: (unicode) -> None
        self.name = name

    def as_dict(self):
        # type: () -> Dict[unicode, Any]
        return {"Symbol": self.name}


class BinaryOperation(ASTNode):
    def __init__(self, operator, left, right):
        # type: (Token, ASTNode, ASTNode) -> None
        self.operator = operator.gettokentype()
        self.left = left
        self.right = right

    def as_dict(self):
        # type: () -> Dict[unicode, Any]
        return {"BinaryOperation": {
            "operator": self.operator,
            "left": self.left.as_dict(),
            "right": self.right.as_dict(),
        }}


class Assign(ASTNode):
    def __init__(self, target, value):
        # type: (ASTNode, ASTNode) -> None
        self.target = target
        self.value = value

    def as_dict(self):
        # type: () -> Dict[unicode, Any]
        return {"Assign": {
            "target": self.target.as_dict(),
            "value": self.value.as_dict(),
        }}
