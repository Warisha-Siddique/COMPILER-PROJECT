import re
import sys

# ==========================================
# 1. TOKEN SPECIFICATION (Regex Rules)
# ==========================================
# The order matters! 
# We match longer/specific patterns first to avoid conflicts.

TOKEN_SPECS = [
    # --- 1. Unique & High Priority ---
    ('COMMENT', r'note>[^\n]*'),      # Matches 'note>' until end of line (Must be first!)
    ('ARROW',   r'->'),               # Matches '->' before '-' or '>'
    ('RANGE',   r'\.\.'),             # Matches '..' before '.'
    ('STITCH',  r'~'),                # Your unique Stitch operator
    
    # --- 2. Operators & Punctuation ---
    ('D_OP',    r'(==|!=|<=|>=|\|\||&&)'),  # Double-character operators
    ('S_OP',    r'[\+\-\*/%<>=!:]'),        # Single-character operators (includes Colon ':')
    ('LBRACE',  r'\{'),
    ('RBRACE',  r'\}'),
    ('LPAREN',  r'\('),
    ('RPAREN',  r'\)'),

    # --- 3. Literals ---
    ('NUMBER',  r'\d+'),              # Integers
    ('STRING',  r'"[^"]*"'),          # Double-quoted strings

    # --- 4. Words (Keywords or Identifiers) ---
    ('WORD',    r'[A-Za-z_][A-Za-z0-9_]*'),

    # --- 5. Skips & Errors ---
    ('SKIP',    r'[ \t\r]+'),         # Skip spaces and tabs
    ('NEWLINE', r'\n'),               # Track line numbers
    ('MISMATCH',r'.'),                # Catch-all for illegal characters
]

# List of reserved words in PatternScript
KEYWORDS = {
    'loop', 'in', 
    'check', 'else', 
    'choose', 'default', 
    'plot', 'ask'    # I/O commands
}

# ==========================================
# 2. THE TOKENIZER ENGINE
# ==========================================

class Token:
    def __init__(self, type, value, line):
        self.type = type
        self.value = value
        self.line = line
    
    def __repr__(self):
        return f"Token({self.type}, '{self.value}', Line {self.line})"

def tokenize(code):
    tokens = []
    line_num = 1
    
    # Compile all regex rules into one efficient pattern
    token_regex = '|'.join(f'(?P<{name}>{regex})' for name, regex in TOKEN_SPECS)
    get_token = re.compile(token_regex).match
    
    pos = 0
    while pos < len(code):
        match = get_token(code, pos)
        if not match:
            raise RuntimeError(f'Unexpected character at line {line_num}')
        
        kind = match.lastgroup
        value = match.group(kind)
        
        if kind == 'SKIP':
            pass
        elif kind == 'COMMENT':
            pass  # Totally ignore comments
        elif kind == 'NEWLINE':
            line_num += 1
        elif kind == 'MISMATCH':
            raise RuntimeError(f'Unknown character {value!r} on line {line_num}')
        elif kind == 'WORD':
            # Check if it's a Keyword (like 'loop') or Identifier (like 'x')
            if value in KEYWORDS:
                kind = value.upper() # e.g., 'loop' -> 'LOOP' token
            else:
                kind = 'IDENT'
            tokens.append(Token(kind, value, line_num))
        else:
            # Handle Operators, Arrows, Ranges, Literals
            if kind in ('D_OP', 'S_OP', 'RANGE', 'ARROW', 'STITCH'):
                # You can group these as 'OP' or keep them specific. 
                # For the parser, knowing it's an ARROW is useful.
                pass 
            tokens.append(Token(kind, value, line_num))
            
        pos = match.end()
        
    return tokens

# ==========================================
# 3. TEST RUNNER (Execute this file to test)
# ==========================================
if __name__ == '__main__':
    # A test snippet showing off all features
    test_code = """
    note> This is the Lexer Test
    val = 10:
    loop i in 1..5 {
        choose i {
            1 -> plot "One":
            default -> plot val ~ i:
        }
    }
    """
    
    try:
        print("--- Source Code ---")
        print(test_code)
        print("\n--- Generated Tokens ---")
        for t in tokenize(test_code):
            print(t)
            
    except RuntimeError as e:
        print(f"Lexer Error: {e}")