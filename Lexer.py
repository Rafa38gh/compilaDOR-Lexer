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
        # Dicionário para facilitar a identificação de palavras-chave
        keywords = {
            "int": TokenKind.KW_INT, "bool": TokenKind.KW_BOOL, "void": TokenKind.KW_VOID,
            "true": TokenKind.KW_TRUE, "false": TokenKind.KW_FALSE, "if": TokenKind.KW_IF,
            "else": TokenKind.KW_ELSE, "while": TokenKind.KW_WHILE, "return": TokenKind.KW_RETURN,
            "print": TokenKind.KW_PRINT
        }

        # Dicionário para operadores de caractere único
        single_chars = {
            '+': TokenKind.PLUS, '-': TokenKind.MINUS, '*': TokenKind.STAR,
            '/': TokenKind.SLASH, '%': TokenKind.PERCENT, '(': TokenKind.LEFT_PAREN,
            ')': TokenKind.RIGHT_PAREN, '{': TokenKind.LEFT_BRACE, '}': TokenKind.RIGHT_BRACE,
            ',': TokenKind.COMMA, ';': TokenKind.SEMICOLON
        }

        while True:
            self._skip_space()
            
            start_line = self.line
            start_column = self.column
            
            if self._end():
                yield Token(TokenKind.EOF, "", None, start_line, start_column)
                break
                
            char = self._advance()
            
            # --- 1. Operadores de 1 ou 2 caracteres ---
            if char == '=':
                if self._peek() == '=':
                    self._advance()
                    yield Token(TokenKind.EQUAL_EQUAL, "==", None, start_line, start_column)
                else:
                    yield Token(TokenKind.ASSIGN, "=", None, start_line, start_column)
                continue
                
            if char == '<':
                if self._peek() == '=':
                    self._advance()
                    yield Token(TokenKind.LESS_EQUAL, "<=", None, start_line, start_column)
                else:
                    yield Token(TokenKind.LESS, "<", None, start_line, start_column)
                continue
                
            if char == '>':
                if self._peek() == '=':
                    self._advance()
                    yield Token(TokenKind.GREATER_EQUAL, ">=", None, start_line, start_column)
                else:
                    yield Token(TokenKind.GREATER, ">", None, start_line, start_column)
                continue
                
            if char == '!':
                if self._peek() == '=':
                    self._advance()
                    yield Token(TokenKind.NOT_EQUAL, "!=", None, start_line, start_column)
                else:
                    yield Token(TokenKind.LOGICAL_NOT, "!", None, start_line, start_column)
                continue

            if char == '&':
                if self._peek() == '&':
                    self._advance()
                    yield Token(TokenKind.LOGICAL_AND, "&&", None, start_line, start_column)
                    continue
                raise LexerError("Esperado '&' após '&'", start_line, start_column)

            if char == '|':
                if self._peek() == '|':
                    self._advance()
                    yield Token(TokenKind.LOGICAL_OR, "||", None, start_line, start_column)
                    continue
                raise LexerError("Esperado '|' após '|'", start_line, start_column)

            if char in single_chars:
                yield Token(single_chars[char], char, None, start_line, start_column)
                continue
                
            if char.isdigit():
                lexeme = char
                while not self._end() and self._peek().isdigit():
                    lexeme += self._advance()
                yield Token(TokenKind.INT_LITERAL, lexeme, int(lexeme), start_line, start_column)
                continue
                
            if char.isalpha() or char == '_':
                lexeme = char
                while not self._end() and (self._peek().isalnum() or self._peek() == '_'):
                    lexeme += self._advance()
                
                if lexeme in keywords:
                    kind = keywords[lexeme]

                    val = True if kind == TokenKind.KW_TRUE else (False if kind == TokenKind.KW_FALSE else None)
                    yield Token(kind, lexeme, val, start_line, start_column)
                else:
                    yield Token(TokenKind.IDENTIFIER, lexeme, None, start_line, start_column)
                continue

            if char == '"':
                lexeme = '"'
                string_value = ""
                while not self._end() and self._peek() != '"':
                    c = self._advance()
                    lexeme += c
                    string_value += c
                    
                if self._end():
                    raise LexerError("String não finalizada antes do fim do arquivo", start_line, start_column)
                    
                lexeme += self._advance() 
                yield Token(TokenKind.STRING_LITERAL, lexeme, string_value, start_line, start_column)
                continue
                

            raise LexerError(f"Caractere inesperado: {char!r}", start_line, start_column)

    def scan(self) -> list[Token]:
        return list(self.tokens())
