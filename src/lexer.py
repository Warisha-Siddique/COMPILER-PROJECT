import re
from collections import namedtuple

Token = namedtuple("Token", ["type", "value", "lineno", "col"])

# Keywords set (exact match -> keyword token)
KEYWORDS = {
    "loop": "LOOP",
    "check": "CHECK",
    "else": "ELSE",
    "choose": "CHOOSE",
    "default": "DEFAULT",
    "display": "DISPLAY",
    "give": "GIVE",
    "in": "IN",
}

# Token specification as (NAME, regex). Order matters for longest-match.
TOKEN_SPEC = [
    # Multi-char comparison / range operators first
    ("EQ",       r"=="),
    ("NEQ",      r"!="),
    ("LE",       r"<="),
    ("GE",       r">="),
    ("RANGE",    r"\.\."),      # '..' range operator
    # Strings (double-quoted) - supports simple escapes like \" and \\ inside
    ("STRING",   r'"([^"\\\n]|\\.)*"'),
    # Number and identifier
    ("NUMBER",   r"\d+"),
    ("IDENT",    r"[A-Za-z_][A-Za-z0-9_]*"),
    # Single character tokens / operators
    ("ASSIGN",   r"="),
    ("PLUS",     r"\+"),
    ("MINUS",    r"-"),
    ("STAR",     r"\*"),
    ("MOD",      r"%"),
    ("TILDE",    r"~"),
    ("LT",       r"<"),
    ("GT",       r">"),
    ("COLON",    r":"),
    ("LBRACE",   r"\{"),
    ("RBRACE",   r"\}"),
    ("LPAREN",   r"\("),
    ("RPAREN",   r"\)"),
    # Whitespace and newline (skipped)
    ("NEWLINE",  r"\n"),
    ("SKIP",     r"[ \t\r]+"),
    # Any other single character is a mismatch
    ("MISMATCH", r"."),
]

master_pat = re.compile("|".join(f"(?P<{name}>{pat})" for name, pat in TOKEN_SPEC))

class LexerError(Exception):
    pass

def tokenize(code):
    """
    Generator that yields Token(type, value, lineno, col).
    Strings returned have escape sequences processed (\" -> ", \\ -> \).
    Numbers returned as int.
    Identifiers that match keywords are returned with the keyword token type.
    """
    lineno = 1
    line_start = 0
    for mo in master_pat.finditer(code):
        kind = mo.lastgroup
        val = mo.group()
        col = mo.start() - line_start + 1

        if kind == "NUMBER":
            yield Token("NUMBER", int(val), lineno, col)
        elif kind == "STRING":
            # remove surrounding quotes and unescape simple escapes
            inner = val[1:-1]
            # process escapes: \" \\ \n \t
            inner = inner.encode("utf-8").decode("unicode_escape")
            yield Token("STRING", inner, lineno, col)
        elif kind == "IDENT":
            upper = val
            if val in KEYWORDS:
                yield Token(KEYWORDS[val], val, lineno, col)
            else:
                yield Token("IDENT", val, lineno, col)
        elif kind == "NEWLINE":
            lineno += 1
            line_start = mo.end()
            # newline not emitted
        elif kind == "SKIP":
            # skip spaces/tabs/carriage returns between tokens
            pass
        elif kind == "MISMATCH":
            raise LexerError(f"Unexpected character {val!r} at line {lineno} col {col}")
        else:
            # other operator/symbol tokens: return text as value (useful for debugging)
            yield Token(kind, val, lineno, col)

if __name__ == "__main__":
    # quick test harness: tokenizes a small demo program (your Test Cases)
    demo = r'''
name = "WISH":
level = 7:
display "User: " ~ name:
display "Level " ~ level:
display "ID=" ~ 1 ~ 2 ~ 3:
loop i in 1..3 {
    display "Step " ~ i ~ ": " ~ ("-" * i):
}
'''
    print("Lexing demo program...\n")
    try:
        for t in tokenize(demo):
            print(f"{t.lineno:3}:{t.col:3}  {t.type:10}  {t.value!r}")
    except LexerError as e:
        print("Lexer error:", e)
