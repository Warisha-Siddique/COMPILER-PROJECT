import sys
from Parser import parse, Number, String, BinOp, UnaryOp
from optimizer import Optimizer
from icg import TACGenerator

class Interpreter:
    def __init__(self):
        # The Symbol Table: Stores variables like {'x': 10, 'str': "Hello"}
        self.variables = {}

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'No visit_{type(node).__name__} method')

    # --- Visit Methods ---

    def visit_Number(self, node):
        return node.value

    def visit_String(self, node):
        return node.value

    def visit_Var(self, node):
        name = node.name
        if name in self.variables:
            return self.variables[name]
        raise NameError(f"Variable '{name}' is not defined")

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        # --- SEMANTIC TYPE CHECKING START ---
        
        # Rule: Math operations (-, /, %) REQUIRE numbers
        if node.op in ('-', '/', '%'):
            if not isinstance(left, int) or not isinstance(right, int):
                raise TypeError(f"Semantic Error: Operator '{node.op}' requires two Numbers. Got {type(left).__name__} and {type(right).__name__}.")

        # Rule: Addition can be math OR it might be accidental string concatenation
        # In PatternScript, we want strict math for '+'. Use '~' for strings.
        if node.op == '+':
            if isinstance(left, int) and isinstance(right, int):
                return left + right
            else:
                raise TypeError(f"Semantic Error: Use '~' to join strings, not '+'.")

        # --- SEMANTIC TYPE CHECKING END ---

        # Handle The Stitch Operator (~)
        if node.op == '~':
            return str(left) + str(right)

        # Handle The Repeat Logic ("*" used on String)
        if node.op == '*':
            if isinstance(left, str) and isinstance(right, int):
                return left * right
            if isinstance(left, int) and isinstance(right, str):
                return right * left

        # Standard Math
        if node.op == '+': return left + right
        elif node.op == '-': return left - right
        elif node.op == '*': return left * right
        elif node.op == '/': return left // right # Integer division
        elif node.op == '%': return left % right
        
        # Logic Comparisons
        elif node.op == '==': return int(left == right) # 1 for True, 0 for False
        elif node.op == '!=': return int(left != right)
        elif node.op == '<': return int(left < right)
        elif node.op == '>': return int(left > right)
        elif node.op == '<=': return int(left <= right)
        elif node.op == '>=': return int(left >= right)
        elif node.op == '&&': return int(left and right)
        elif node.op == '||': return int(left or right)

        raise Exception(f"Unknown operator: {node.op}")

    def visit_UnaryOp(self, node):
        val = self.visit(node.expr)
        if node.op == '-':
            return -val
        elif node.op == '!':
            return 1 if not val else 0

    def visit_Assign(self, node):
        value = self.visit(node.expr)
        self.variables[node.name] = value

    def visit_Plot(self, node):
        value = self.visit(node.expr)
        print(value)

    def visit_Ask(self, node):
        value = input(f"Enter value for {node.name}: ")
        # Try to convert to int if possible, else keep string
        try:
            self.variables[node.name] = int(value)
        except ValueError:
            self.variables[node.name] = value

    def visit_Loop(self, node):
        start = self.visit(node.start_expr)
        end = self.visit(node.end_expr)
        var_name = node.var_name

        # Python range is exclusive at the end, so we add +1
        # If pattern is 1..5, we want 1,2,3,4,5
        for i in range(start, end + 1):
            self.variables[var_name] = i
            for stmt in node.body:
                self.visit(stmt)

    def visit_Check(self, node):
        condition = self.visit(node.condition)
        # In our language, 0 is False, anything else is True
        if condition:
            for stmt in node.if_body:
                self.visit(stmt)
        elif node.else_body:
            for stmt in node.else_body:
                self.visit(stmt)

    def visit_Choose(self, node):
        match_val = self.visit(node.expr)
        matched = False
        
        for case_lit_node, case_body in node.cases:
            lit_val = self.visit(case_lit_node)
            if match_val == lit_val:
                matched = True
                for stmt in case_body:
                    self.visit(stmt)
                break # Stop after first match
        
        if not matched and node.default_case:
            for stmt in node.default_case:
                self.visit(stmt)
        

def run_file(filename):
    try:
        with open(filename, 'r') as file:
            code = file.read()
        
        print(f"--- Executing {filename} ---")
        ast = parse(code)
        
        # --- PHASE 4: INTERMEDIATE CODE GENERATION ---
        print("\n[Phase 4: Generated 3-Address Code]")
        icg = TACGenerator()
        tac_lines = icg.generate(ast)
        for line in tac_lines:
            print(f"  {line}")
        print("-------------------------------------\n")
        # ---------------------------------------------

        # Phase 5: Optimize
        optimizer = Optimizer()
        ast = optimizer.optimize(ast)
        
        # Phase 6: Run
        interpreter = Interpreter()
        for stmt in ast:
            interpreter.visit(stmt)
            
    except Exception as e:
        print(f"Error: {e}")


def run_repl():
    print("PatternScript Interactive Mode (Type 'exit' to quit)")
    print("----------------------------------------------------")
    interpreter = Interpreter() # Keep memory alive between lines
    
    while True:
        try:
            text = input('PS > ')
            if text.strip() == 'exit': 
                break
            if not text.strip(): 
                continue

            ast = parse(text)
            for stmt in ast:
                interpreter.visit(stmt)
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    # Check if a filename was provided in the command line
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        run_file(filename)
    else:
        # No file provided? Run interactive mode
        run_repl()