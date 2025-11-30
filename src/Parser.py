import sys
from Lexer import tokenize

# ==========================================
# 1. AST NODES (The Tree Structure)
# ==========================================
class Node: pass

class Number(Node):
    def __init__(self, value): self.value = value

class String(Node):
    def __init__(self, value): self.value = value

class Var(Node):
    def __init__(self, name): self.name = name

class BinOp(Node):
    def __init__(self, left, op, right):
        self.left = left; self.op = op; self.right = right

class UnaryOp(Node):
    def __init__(self, op, expr):
        self.op = op; self.expr = expr

class Assign(Node):
    def __init__(self, name, expr):
        self.name = name; self.expr = expr

class Plot(Node):
    def __init__(self, expr): self.expr = expr

class Ask(Node):
    def __init__(self, name): self.name = name

class Loop(Node):
    def __init__(self, var_name, start_expr, end_expr, body):
        self.var_name = var_name
        self.start_expr = start_expr
        self.end_expr = end_expr
        self.body = body

class Check(Node):
    def __init__(self, condition, if_body, else_body=None):
        self.condition = condition
        self.if_body = if_body
        self.else_body = else_body

class Choose(Node):
    def __init__(self, expr, cases, default_case):
        self.expr = expr
        self.cases = cases        # List of (literal, body)
        self.default_case = default_case

# ==========================================
# 2. THE PARSER CLASS
# ==========================================
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if self.tokens else None

    def eat(self, token_type):
        if self.current_token and (self.current_token.type == token_type or token_type == 'ANY'):
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
            else:
                self.current_token = None
        else:
            raise SyntaxError(f"Expected {token_type}, got {self.current_token}")

    # --- Grammar Rules ---

    def parse_program(self):
        stmts = []
        while self.current_token:
            stmts.append(self.parse_stmt())
        return stmts

    def parse_stmt(self):
        token = self.current_token
        
        # 1. Output: plot "Hi":
        if token.type == 'PLOT':
            self.eat('PLOT')
            expr = self.parse_expr()
            self.eat('S_OP') # Expect ':'
            return Plot(expr)
        
        # 2. Input: ask x:
        elif token.type == 'ASK':
            self.eat('ASK')
            var_name = self.current_token.value
            self.eat('IDENT')
            self.eat('S_OP') # Expect ':'
            return Ask(var_name)

        # 3. Loop: loop i in 1..5 { ... }
        elif token.type == 'LOOP':
            self.eat('LOOP')
            var_name = self.current_token.value
            self.eat('IDENT')
            self.eat('IN')
            start = self.parse_expr()
            
            # --- FIX IS HERE ---
            self.eat('RANGE') # Was previously 'D_OP'
            # -------------------
            
            end = self.parse_expr()
            self.eat('LBRACE')
            body = self.parse_block() 
            return Loop(var_name, start, end, body)

        # 4. Check: check x > 5 { ... } else { ... }
        elif token.type == 'CHECK':
            self.eat('CHECK')
            cond = self.parse_expr()
            self.eat('LBRACE')
            if_body = self.parse_block()
            else_body = None
            if self.current_token and self.current_token.type == 'ELSE':
                self.eat('ELSE')
                self.eat('LBRACE')
                else_body = self.parse_block()
            return Check(cond, if_body, else_body)
            
        # 5. Choose (Switch): choose x { 1 -> plot "a": }
        elif token.type == 'CHOOSE':
            self.eat('CHOOSE')
            expr = self.parse_expr()
            self.eat('LBRACE')
            cases = []
            default_body = None
            
            while self.current_token and self.current_token.type != 'RBRACE':
                if self.current_token.type == 'DEFAULT':
                    self.eat('DEFAULT')
                    self.eat('ARROW') # Expect ->
                    default_body = [self.parse_stmt()] # Simplified: 1 stmt or need { } block logic
                else:
                    # Case literal
                    lit = self.parse_factor() # Number or String
                    self.eat('ARROW') # Expect ->
                    stmt = self.parse_stmt() # Single statement for now
                    cases.append((lit, [stmt]))
            
            self.eat('RBRACE')
            return Choose(expr, cases, default_body)

        # 6. Assignment: x = 10:
        elif token.type == 'IDENT':
            var_name = self.current_token.value
            self.eat('IDENT')
            self.eat('S_OP') # Expect '=' (handled as S_OP in lexer unless specific)
            # Check if it was actually '='
            # Note: simplistic check. Ideally verify value is '='
            expr = self.parse_expr()
            self.eat('S_OP') # Expect ':'
            return Assign(var_name, expr)

        else:
            raise SyntaxError(f"Unexpected token {token}")

    def parse_block(self):
        # Parses statements until '}'
        stmts = []
        while self.current_token and self.current_token.type != 'RBRACE':
            stmts.append(self.parse_stmt())
        self.eat('RBRACE')
        return stmts

    # --- Expression Parsing (Precedence) ---

    def parse_expr(self):
        return self.parse_logic()

    def parse_logic(self):
        # Handles ==, !=, <, >
        left = self.parse_additive()
        while self.current_token and self.current_token.value in ('==', '!=', '<', '>', '<=', '>='):
            op = self.current_token.value
            if self.current_token.type == 'D_OP' or self.current_token.type == 'S_OP':
                self.eat(self.current_token.type)
                right = self.parse_additive()
                left = BinOp(left, op, right)
        return left

    def parse_additive(self):
        # Handles +, -, ~
        left = self.parse_term()
        while self.current_token and self.current_token.value in ('+', '-', '~'):
            op = self.current_token.value
            if op == '~': self.eat('STITCH')
            else: self.eat('S_OP')
            right = self.parse_term()
            left = BinOp(left, op, right)
        return left

    def parse_term(self):
        # Handles *, /, %
        left = self.parse_factor()
        while self.current_token and self.current_token.value in ('*', '/', '%'):
            op = self.current_token.value
            self.eat('S_OP')
            right = self.parse_factor()
            left = BinOp(left, op, right)
        return left

    def parse_factor(self):
        token = self.current_token
        if token.type == 'NUMBER':
            self.eat('NUMBER')
            return Number(int(token.value))
        elif token.type == 'STRING':
            self.eat('STRING')
            return String(token.value[1:-1]) # Remove quotes
        elif token.type == 'IDENT':
            self.eat('IDENT')
            return Var(token.value)
        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            node = self.parse_expr()
            self.eat('RPAREN')
            return node
        elif token.value == '-': # Unary Minus
            self.eat('S_OP')
            node = self.parse_factor()
            return UnaryOp('-', node)
        
        raise SyntaxError(f"Invalid factor: {token}")

# Helper to run parser
def parse(code):
    tokens = tokenize(code)
    parser = Parser(tokens)
    return parser.parse_program()