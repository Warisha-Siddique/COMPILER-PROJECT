from Parser import BinOp, Number, String

class Optimizer:
    def visit(self, node):
        # Dynamic dispatch to visit methods
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        # For most nodes (like Loops, Check), just visit their children
        # We need to reconstruct the node if children change, 
        # but for a simple project, we'll just return the node as-is 
        # unless it's a specific math node we want to optimize.
        return node

    def visit_BinOp(self, node):
        # 1. Optimize children first
        node.left = self.visit(node.left)
        node.right = self.visit(node.right)

        # 2. CONSTANT FOLDING LOGIC
        if isinstance(node.left, Number) and isinstance(node.right, Number):
            result = None
            if node.op == '+': result = Number(node.left.value + node.right.value)
            elif node.op == '-': result = Number(node.left.value - node.right.value)
            elif node.op == '*': result = Number(node.left.value * node.right.value)
            elif node.op == '/': result = Number(node.left.value // node.right.value)
            
            if result:
                # <--- ADD THIS PRINT FOR THE DEMO --->
                print(f"  [OPT] Folded: {node.left.value} {node.op} {node.right.value} -> {result.value}")
                return result

        return node

        # 2. CONSTANT FOLDING LOGIC
        # If both sides are Numbers, calculate it NOW.
        if isinstance(node.left, Number) and isinstance(node.right, Number):
            if node.op == '+': return Number(node.left.value + node.right.value)
            if node.op == '-': return Number(node.left.value - node.right.value)
            if node.op == '*': return Number(node.left.value * node.right.value)
            # Add other operators if needed

        return node

    def optimize(self, ast):
        # Walk through the list of statements in the AST
        new_ast = []
        for stmt in ast:
            # Optimize expressions inside statements
            # (In a full compiler, we would visit every statement type.
            #  For this demo, we assume statements are wrappers)
            if hasattr(stmt, 'expr'):
                stmt.expr = self.visit(stmt.expr)
            new_ast.append(stmt)
        return new_ast