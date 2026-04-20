import re
from collections import namedtuple
from .errors import FiberSyntaxError

Token = namedtuple("Token", ["type", "value", "line"])

TOKEN_SPEC = [
    # Literals
    ("NUMBER", r"\d+(?:\.\d+)?"),
    ("STRING", r'"[^"\\]*(?:\\.[^"\\]*)*"'),

    # Operators / comparisons (longer before shorter)
    ("EQ", r"=="),
    ("NEQ", r"!="),
    ("LTE", r"<="),
    ("GTE", r">="),
    ("LT", r"<"),
    ("GT", r">"),
    ("ASSIGN", r"="),

    # Punctuation
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("LBRACE", r"\{"),
    ("RBRACE", r"\}"),
    ("LBRACKET", r"\["),
    ("RBRACKET", r"\]"),
    ("COMMA", r","),
    ("COLON", r":"),
    ("SEMICOLON", r";"),
    ("DOT", r"\."),
    ("QUESTION", r"\?"),

    # Math
    ("PLUS", r"\+"),
    ("MINUS", r"-"),
    ("POWER", r"\*\*"),
    ("MUL", r"\*"),
    ("DIV", r"/"),
    ("MOD", r"%"),

    # Names & whitespace
    ("NAME", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("NEWLINE", r"\n"),
    ("SKIP", r"[ \t]+"),
    ("MISMATCH", r"."),
]

KEYWORDS = {
    "var", "const", "static", "final", "def", "class",
    "struct", "enum", "switch", "match", "case", "default", "print", "return", "extends",
    "if", "elif", "else", "while", "for", "in", "to", "step",
    "and", "or", "not", "true", "false",
    "break", "continue", "pass",
    "try", "catch", "finally", "throw", "assert",
    "import", "from", "as", "this",
}

# We'll insert a comment pattern manually while scanning (simple approach)
MASTER = re.compile("|".join("(?P<%s>%s)" % pair for pair in TOKEN_SPEC))


def tokenize(code: str):
    code = code.replace("\r\n", "\n").replace("\r", "\n")
    line = 1
    tokens = []
    i = 0
    n = len(code)

    while i < n:
        # handle comment starting with #
        if code[i] == "#":
            # consume until end of line
            j = code.find("\n", i)
            if j == -1:
                # rest is comment — finish
                break
            else:
                tokens.append(Token("NEWLINE", "\n", line))
                line += 1
                i = j + 1
                continue

        mo = MASTER.match(code, i)
        if not mo:
            raise FiberSyntaxError(f"Unexpected character {code[i]!r} at line {line}")
        kind = mo.lastgroup
        val = mo.group(kind)
        i = mo.end()

        if kind == "NEWLINE":
            tokens.append(Token("NEWLINE", val, line))
            line += 1
            continue
        if kind == "SKIP":
            continue
        if kind == "NUMBER":
            val = float(val) if "." in val else int(val)
            tokens.append(Token("NUMBER", val, line))
            continue
        if kind == "NAME":
            if val in KEYWORDS:
                tokens.append(Token(val.upper(), val, line))
            else:
                tokens.append(Token("NAME", val, line))
            continue
        if kind == "STRING":
            # remove quotes
            tokens.append(Token("STRING", val[1:-1], line))
            continue

        tokens.append(Token(kind, val, line))

    tokens.append(Token("EOF", "", line))
    return tokens
