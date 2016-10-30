from __future__ import unicode_literals

# from rpython.rlib.runicode import unicode_encode_utf_8  # noqa

from rply import Token
from rply.token import SourcePosition
from typing import Any, Iterator  # noqa


class LexerError(Exception):
    def __init__(self, pos, msg=None):
        # type: (int, unicode) -> None
        self.pos = pos
        self.msg = "" if msg is None else msg

tokens = [
    "END_OF_INPUT", "ERROR",
    "STR_CONST", "NUM_CONST", "NULL_CONST", "SYMBOL", "FUNCTION",
    "INCOMPLETE_STR",
    "LEFT_ASSIGN", "EQ_ASSIGN", "RIGHT_ASSIGN", "LBB",
    "FOR", "IN", "IF", "ELSE", "WHILE", "NEXT", "BREAK", "REPEAT",
    "GT", "GE", "LT", "LE", "EQ", "NE", "AND", "OR", "AND2", "OR2",
    "NS_GET", "NS_GET_INT",
    "COMMENT", "LINE_DIRECTIVE",
    "SYMBOL_FORMALS",
    "EQ_FORMALS",
    "EQ_SUB", "SYMBOL_SUB",
    "SYMBOL_FUNCTION_CALL",
    "SYMBOL_PACKAGE",
    "COLON_ASSIGN",
    "SLOT",

    "NEWLINE", "SEMICOLON", "ELLIPSIS", "COMMA", "DOLLAR",
    "INFIX", "TILDE",
    "LBRACE", "RBRACE", "LPAREN", "RPAREN", "LSQUARE", "RSQUARE",
    "MUL", "POW", "DIV", "MOD", "PLUS", "UPLUS", "MINUS", "UMINUS",
    "COLON", "UQUESTION", "QUESTION",
    "NOT", "NA",
]

reserved = [
    "FUNCTION", "FOR", "IN", "IF", "ELSE", "WHILE", "NEXT",
    "BREAK", "REPEAT", "NA"
]


class Lexer(object):
    EOF = chr(0)

    EXPR_BEG = 0
    EXPR_ARG = 1

    def __init__(self, source, initial_lineno, symtable):
        # type: (unicode, int, Dict[Any, Any]) -> None
        self.source = source
        self.lineno = initial_lineno
        self.symtable = symtable
        self.current_value = []  # type: List[unicode]
        self.idx = 0
        self.columno = 1
        self.state = self.EXPR_BEG
        self.paren_nest = 0
        self.left_paren_begin = 0
        self.command_start = True
        # self.condition_state = StackState()
        # self.cmd_argument_state = StackState()
        self.unicode_term = None

    def peek(self):
        # type: () -> unicode
        ch = self.read()
        self.unread()
        return ch

    def add(self, ch):
        # type: (unicode) -> None
        self.current_value.append(ch)

    def clear(self):
        # type: () -> None
        del self.current_value[:]

    def current_pos(self):
        # type: () -> SourcePosition
        return SourcePosition(self.idx, self.lineno, self.columno)

    def newline(self, ch):
        # type: (unicode) -> None
        if ch == "\r" and self.peek() == "\n":
            self.read()
        self.lineno += 1
        self.columno = 1

    def emit(self, token):
        # type: (unicode) -> Token
        assert token in tokens
        value = "".join(self.current_value)
        self.clear()
        return Token(token, value, self.current_pos())

    def error(self, msg=None):
        # type: (unicode) -> None
        raise LexerError(self.current_pos(), msg)

    def read(self):
        # type: () -> unicode
        try:
            ch = self.source[self.idx]
        except IndexError:
            ch = self.EOF
        self.idx += 1
        self.columno += 1
        return ch

    def unread(self):
        # type: () -> None
        idx = self.idx - 1
        assert idx >= 0
        self.idx = idx
        self.columno -= 1

    def tokenize(self):
        # type: () -> Iterator[Token]
        while True:
            ch = self.read()
            if ch == self.EOF:
                break
            if ch in " \t":
                continue
            elif ch == "#":
                for token in self.comment(ch):
                    yield token
            elif ch in "\r\n":
                self.newline(ch)
                self.add("\n")
                yield self.emit("NEWLINE")
                self.state = self.EXPR_BEG
            elif ch == "*":
                for token in self.star(ch):
                    yield token
            elif ch == "!":
                for token in self.exclamation(ch):
                    yield token
            elif ch == "=":
                for token in self.equal(ch):
                    yield token
            elif ch == "<":
                for token in self.less_than(ch):
                    yield token
            elif ch == ">":
                for token in self.greater_than(ch):
                    yield token
            elif ch in ("'", '"'):
                for token in self.string_quote(ch):
                    yield token
            elif ch == "?":
                for token in self.question_mark(ch):
                    yield token
            elif ch == "&":
                for token in self.ampersand(ch):
                    yield token
            elif ch == "|":
                for token in self.pipe(ch):
                    yield token
            elif ch == "+":
                for token in self.plus(ch):
                    yield token
            elif ch == "-":
                for token in self.minus(ch):
                    yield token
            elif ch.isdigit():
                for token in self.number(ch):
                    yield token
            elif ch == "(":
                for token in self.left_paren(ch):
                    yield token
            elif ch == ")":
                for token in self.right_paren(ch):
                    yield token
            elif ch == "{":
                for token in self.left_brace(ch):
                    yield token
            elif ch == "}":
                for token in self.right_brace(ch):
                    yield token
            elif ch == "[":
                for token in self.left_square(ch):
                    yield token
            elif ch == "]":
                for token in self.right_square(ch):
                    yield token
            elif ch == ":":
                for token in self.colon(ch):
                    yield token
            elif ch == "/":
                for token in self.slash(ch):
                    yield token
            elif ch == "^":
                for token in self.caret(ch):
                    yield token
            elif ch == ";":
                self.add(ch)
                self.state = self.EXPR_BEG
                yield self.emit("SEMICOLON")
            elif ch == ",":
                self.add(ch)
                self.state = self.EXPR_BEG
                yield self.emit("COMMA")
            elif ch == "~":
                self.add(ch)
                self.state = self.EXPR_BEG
                yield self.emit("TILDE")
            elif ch == ".":
                for token in self.dot(ch):
                    yield token
            elif ch == "\\":
                ch2 = self.read()
                if ch2 in "\r\n":
                    self.newline(ch2)
                    continue
                raise NotImplementedError
            elif ch == "%":
                for token in self.percent(ch):
                    yield token
            elif ch == "$":
                self.add(ch)
                self.state = self.EXPR_BEG
                yield self.emit("DOLLAR")
            elif ch == "`":
                for token in self.backtick(ch):
                    yield token
            else:
                for token in self.symbol(ch):
                    yield token

    def comment(self, ch):
        # type: (unicode) -> Iterator[Token]
        while True:
            self.add(ch)
            ch = self.read()
            if ch == self.EOF or ch in "\r\n":
                self.unread()
                yield self.emit("COMMENT")
                break

    def emit_symbol(self):
        # type: (unicode) -> Token
        value = "".join(self.current_value)
        if value.upper() in reserved:
            return self.emit(value.upper())
        else:
            return self.emit("SYMBOL")

    def symbol(self, ch):
        # type: (unicode) -> Iterator[Token]
        if (ch.isalpha() or ord(ch) > 127):
            self.add(ch)
        else:
            self.error("Unexpected character: %s" % ch)
        while True:
            ch = self.read()
            if ch == self.EOF:
                yield self.emit_symbol()
                self.unread()
                break
            elif (ch.isalnum() or
                  ch in "._" or
                  ord(ch) > 127):
                self.add(ch)
            else:
                self.unread()
                yield self.emit_symbol()
                self.state = self.EXPR_ARG
                break

    def star(self, ch):
        # type: (unicode) -> Iterator[Token]
        if self.state != self.EXPR_ARG:
            self.error("Unexpected *")
        self.state = self.EXPR_BEG
        self.add(ch)
        ch2 = self.read()
        if ch2 == "*":
            yield self.emit("POW")
        else:
            self.unread()
            yield self.emit("MUL")

    def exclamation(self, ch):
        # type: (unicode) -> Iterator[Token]
        self.add(ch)
        ch2 = self.read()
        if ch2 == "=":
            self.add(ch2)
            self.state = self.EXPR_BEG
            yield self.emit("NE")
        else:
            self.unread()
            yield self.emit("NOT")

    def equal(self, ch):
        # type: (unicode) -> Iterator[Token]
        if self.state != self.EXPR_ARG:
            self.error("Unexpected =")
        self.state = self.EXPR_BEG
        self.add(ch)
        ch2 = self.read()
        if ch2 == "=":
            self.add(ch2)
            yield self.emit("EQ")
        else:
            self.unread()
            yield self.emit("EQ_ASSIGN")

    def less_than(self, ch):
        # type: (unicode) -> Iterator[Token]
        if self.state != self.EXPR_ARG:
            self.error("Unexpected <")
        self.state = self.EXPR_BEG
        self.add(ch)
        ch2 = self.read()
        if ch2 == "=":
            self.add(ch2)
            yield self.emit("LE")
        elif ch2 == "-":
            self.add(ch2)
            yield self.emit("LEFT_ASSIGN")
        else:
            self.unread()
            yield self.emit("LT")

    def greater_than(self, ch):
        # type: (unicode) -> Iterator[Token]
        if self.state != self.EXPR_ARG:
            self.error("Unexpected >")
        self.state = self.EXPR_BEG
        self.add(ch)
        ch2 = self.read()
        if ch2 == "=":
            self.add(ch2)
            yield self.emit("GE")
        else:
            self.unread()
            yield self.emit("GT")

    def string_quote(self, ch_begin):
        # type: (unicode) -> Iterator[Token]
        self.state = self.EXPR_ARG
        while True:
            ch = self.read()
            if ch == self.EOF:
                self.error("EOF in string literal")
            elif ch == ch_begin:
                yield self.emit("STR_CONST")
                break
            elif ch == "\\":
                ch2 = self.peek()
                if ch2 == ch_begin:
                    ch = self.read()
                self.add(ch)
            else:
                self.add(ch)

    def question_mark(self, ch):
        # type: (unicode) -> Iterator[Token]
        self.add(ch)
        if self.state == self.EXPR_ARG:
            self.state = self.EXPR_BEG
            yield self.emit("QUESTION")
        else:
            yield self.emit("UQUESTION")

    def ampersand(self, ch):
        # type: (unicode) -> Iterator[Token]
        if self.state != self.EXPR_ARG:
            self.error("Unexpected &")
        self.state = self.EXPR_BEG
        self.add(ch)
        ch2 = self.read()
        if ch2 == "&":
            self.add(ch2)
            yield self.emit("AND2")
        else:
            self.unread()
            yield self.emit("AND")

    def pipe(self, ch):
        # type: (unicode) -> Iterator[Token]
        if self.state != self.EXPR_ARG:
            self.error("Unexpected |")
        self.state = self.EXPR_BEG
        self.add(ch)
        ch2 = self.read()
        if ch2 == "|":
            self.add(ch2)
            yield self.emit("OR2")
        else:
            self.unread()
            yield self.emit("OR")

    def plus(self, ch):
        # type: (unicode) -> Iterator[Token]
        self.add(ch)
        if self.state == self.EXPR_BEG:
            yield self.emit("UPLUS")
        else:
            yield self.emit("PLUS")
            self.state = self.EXPR_BEG

    def minus(self, ch):
        # type: (unicode) -> Iterator[Token]
        self.add(ch)
        ch2 = self.read()
        if ch2 == ">":
            self.add(ch2)
            yield self.emit("RIGHT_ASSIGN")
        else:
            self.unread()
            if self.state == self.EXPR_BEG:
                yield self.emit("UMINUS")
            else:
                yield self.emit("MINUS")
                self.state = self.EXPR_BEG

    def number(self, ch):
        # type: (unicode) -> Iterator[Token]
        self.state = self.EXPR_ARG
        self.add(ch)
        seen_decimal = False
        seen_exponent = False
        while True:
            ch = self.read()
            if ch.isdigit():
                self.add(ch)
            elif ch == ".":
                if seen_decimal:
                    self.unread()
                    yield self.emit("NUM_CONST")
                    break
                else:
                    self.add(ch)
                    seen_decimal = True
            elif ch in "eE":
                if seen_exponent:
                    self.unread()
                    yield self.emit("NUM_CONST")
                    break
                else:
                    seen_exponent = True
                    seen_decimal = True
                    self.add(ch)
                    ch2 = self.peek()
                    if ch2 in "+-":
                        self.add(ch2)
                        self.read()
            else:
                if ch == "L":
                    self.add(ch)
                else:
                    self.unread()
                yield self.emit("NUM_CONST")
                break

    def left_paren(self, ch):
        # type: (unicode) -> Iterator[Token]
        self.add(ch)
        self.state = self.EXPR_BEG
        yield self.emit("LPAREN")

    def right_paren(self, ch):
        # type: (unicode) -> Iterator[Token]
        self.add(ch)
        self.state = self.EXPR_ARG
        yield self.emit("RPAREN")

    def left_brace(self, ch):
        # type: (unicode) -> Iterator[Token]
        self.add(ch)
        self.state = self.EXPR_BEG
        yield self.emit("LBRACE")

    def right_brace(self, ch):
        # type: (unicode) -> Iterator[Token]
        self.add(ch)
        self.state = self.EXPR_ARG
        yield self.emit("RBRACE")

    def left_square(self, ch):
        # type: (unicode) -> Iterator[Token]
        self.add(ch)
        self.state = self.EXPR_BEG
        yield self.emit("LSQUARE")

    def right_square(self, ch):
        # type: (unicode) -> Iterator[Token]
        self.add(ch)
        self.state = self.EXPR_ARG
        yield self.emit("RSQUARE")

    def colon(self, ch):
        # type: (unicode) -> Iterator[Token]
        if self.state != self.EXPR_ARG:
            self.error("Unexpected :")
        self.add(ch)
        self.state = self.EXPR_BEG
        ch2 = self.peek()
        if ch2 == "=":
            self.add(ch2)
            self.read()
            yield self.emit("COLON_ASSIGN")
        else:
            yield self.emit("COLON")

    def slash(self, ch):
        # type: (unicode) -> Iterator[Token]
        if self.state != self.EXPR_ARG:
            self.error("Unexpected /")
        self.state = self.EXPR_BEG
        self.add(ch)
        yield self.emit("DIV")

    def caret(self, ch):
        # type: (unicode) -> Iterator[Token]
        if self.state != self.EXPR_ARG:
            self.error("Unexpected ^")
        self.state = self.EXPR_BEG
        self.add(ch)
        yield self.emit("POW")

    def dot(self, ch):
        # type: (unicode) -> Iterator[Token]
        self.state = self.EXPR_BEG
        ch2 = self.read()
        if ch2 != ".":
            self.error("Unexpected .")
        ch3 = self.read()
        if ch3 != ".":
            self.error("Unexpected ..")
        self.add("...")
        yield self.emit("ELLIPSIS")

    def percent(self, ch):
        # type: (unicode) -> Iterator[Token]
        if self.state != self.EXPR_ARG:
            self.error("Unexpected %")
        self.state = self.EXPR_BEG
        self.add(ch)
        ch2 = self.read()
        self.add(ch2)
        if ch2 == "%":
            yield self.emit("MOD")
        else:
            while True:
                ch = self.read()
                if ch == self.EOF:
                    self.error("EOF in infix operator")
                self.add(ch)
                if ch == "%":
                    yield self.emit("INFIX")
                    break

    def backtick(self, ch_begin):
        # type: (unicode) -> Iterator[Token]
        self.state = self.EXPR_ARG
        while True:
            ch = self.read()
            if ch == self.EOF:
                self.error("EOF in quoted literal")
            elif ch == ch_begin:
                yield self.emit("SYMBOL")
                break
            elif ch == "\\":
                ch2 = self.peek()
                if ch2 == ch_begin:
                    ch = self.read()
                self.add(ch)
            else:
                self.add(ch)


if __name__ == "__main__":
    import pprint
    import sys
    buf = open(sys.argv[1]).read().decode("utf-8")
    lexer = Lexer(buf, 1, {})
    tokens = list(lexer.tokenize())
    pprint.pprint(tokens)
