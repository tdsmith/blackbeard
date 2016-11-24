import os
import sys

import blackbeard.ast
import blackbeard.lexer
import blackbeard.parser

from typing import AnyStr  # noqa


def run(fp):
    # type: (int) -> None
    program = b""
    while True:
        read = os.read(fp, 4096)
        if len(read) == 0:
            break
        program += read
    os.close(fp)
    lexer = blackbeard.lexer.Lexer(program, 1, {})
    parser = blackbeard.parser.Parser(lexer)
    result = parser.parse()
    assert isinstance(result, blackbeard.ast.ASTNode)
    print result.__repr__()


def entry_point(argv):
    # type: (List[AnyStr]) -> int
    try:
        filename = argv[1]
    except IndexError:
        print("You must supply a filename")
        return 1

    run(os.open(filename, os.O_RDONLY, 0o777))
    return 0


def target(*args):
    return entry_point, None


if __name__ == "__main__":
    entry_point(sys.argv)
