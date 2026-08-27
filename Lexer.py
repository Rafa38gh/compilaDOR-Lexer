from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Iterator


class TokenKind(enum.Enum):
    """Classe já implementada: nomes e números não devem ser alterados."""

    EOF = -1

    IDENTIFIER = 1
    INT_LITERAL = 2
    STRING_LITERAL = 3

    KW_INT = 10
    KW_BOOL = 11
    KW_VOID = 12
    KW_TRUE = 13
    KW_FALSE = 14
    KW_IF = 15
    KW_ELSE = 16
    KW_WHILE = 17
    KW_RETURN = 18
    KW_PRINT = 19

    PLUS = 20
    MINUS = 21
    STAR = 22
    SLASH = 23
    PERCENT = 24
    LESS = 25
    LESS_EQUAL = 26
    GREATER = 27
    GREATER_EQUAL = 28
    EQUAL_EQUAL = 29
    NOT_EQUAL = 30
    LOGICAL_AND = 31
    LOGICAL_OR = 32
    LOGICAL_NOT = 33
    ASSIGN = 34

    LEFT_PAREN = 40
    RIGHT_PAREN = 41
    LEFT_BRACE = 42
    RIGHT_BRACE = 43
    COMMA = 44
    SEMICOLON = 45


@dataclass(frozen=True)
class Token:
    kind: TokenKind
    lexeme: str
    value: int | str | bool | None
    line: int
    column: int

    def __str__(self) -> str:
        return (
            f"<{self.kind.value}, {self.kind.name}, {self.lexeme!r}, "
            f"{self.value!r}, {self.line}, {self.column}>"
        )


class LexerError(Exception):
    def __init__(self, message: str, line: int, column: int):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column

    def __str__(self) -> str:
        return f"erro léxico em {self.line}:{self.column}: {self.message}"


class Lexer:
    """Converte texto-fonte MicroC em uma sequência de tokens."""

    def __init__(self, source: str):
        self.source = source
        
        self.pos = 0
        self.line = 1
        self.column = 1
    
    def _peek(self, offset: int = 0) -> str:
        """Lê caractere sem consumir"""
        i = self.pos + offset
        return self.source[i] if i < len(self.source) else ''

    def _advance(self) -> str:
        """Consome e retorna o caractere atual"""
        char = self.source[self.pos]
        self.pos += 1
        
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        return char
    
    def _end(self) -> bool:
        return self.pos >= len(self.source)
    
    def _skip_space(self) -> None:
        """Pula espaço, tab, quebra de linha e comentários"""
        while not self._end():
            char = self._peek()

            if char in (' ', '\t', '\n'):       # Espaço, tab e quebra de linha
                self._advance()
                continue

            if char == '/' and self._peek(1) == '/':        # Comentário de linha
                while not self._end() and self._peek() != '\n':
                    self._advance()
                continue

            if char == '/' and self._peek(1) == '*':        # Comentário de bloco
                start_line, start_column = self.line, self.column
                self._advance()
                self._advance()

                while True:
                    if self._end():
                        raise LexerError("Sem término no comentário de bloco", start_line, start_column)
                    
                    if self._peek() == '*' and self._peek(1) == '/':
                        self._advance()
                        self._advance()
                        break
                    self._advance()
                continue
            break

    def tokens(self) -> Iterator[Token]:
        """Produza todos os tokens significativos e um único EOF ao final."""
        raise NotImplementedError("implemente o analisador léxico")
        yield  # mantém este método como gerador durante o desenvolvimento

    def scan(self) -> list[Token]:
        return list(self.tokens())

