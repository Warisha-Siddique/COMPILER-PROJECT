from Parser import BinOp, Number, String, Var

class TACGenerator:
    def __init__(self):
        self.temp_count = 0
        self.label_count = 0
        self.code = [] # List to store quadruples/TAC lines

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, op, arg1, arg2, result):
        # Store as a Quadruple: (OP, ARG1, ARG2, RESULT)
        # We format it nicely as a string immediately for display
        if arg2:
            self.code.append(f"{result} = {arg1} {op} {arg2}")
        elif result:
            self.code.append(f"{result} = {op} {arg1}")
        else:
            self.code.append(f"{op} {arg1}")

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        pass

    # --- Math & Logic ---
    def visit_BinOp(self, node):
        addr_left = self.visit(node.left)
        addr_right = self.visit(node.right)
        
        temp = self.new_temp()
        self.emit(node.op, addr_left, addr_right, temp)
        return temp

    def visit_Number(self, node):
        return str(node.value)

    def visit_String(self, node):
        return f'"{node.value}"'

    def visit_Var(self, node):
        return node.name

    # --- Statements ---
    def visit_Assign(self, node):
        val_addr = self.visit(node.expr)
        self.emit("ASSIGN", val_addr, None, node.name)

    def visit_Plot(self, node):
        val_addr = self.visit(node.expr)
        self.code.append(f"PLOT {val_addr}")

    def visit_Ask(self, node):
        self.code.append(f"ASK {node.name}")

    # --- Control Flow (The Tricky Part) ---
    def visit_Check(self, node):
        # 1. Evaluate Condition
        cond_addr = self.visit(node.condition)
        
        l_else = self.new_label()
        l_end = self.new_label()

        # 2. Jump if False
        self.code.append(f"IF_FALSE {cond_addr} GOTO {l_else}")

        # 3. True Body
        for stmt in node.if_body:
            self.visit(stmt)
        self.code.append(f"GOTO {l_end}")

        # 4. Else Label & Body
        self.code.append(f"{l_else}:")
        if node.else_body:
            for stmt in node.else_body:
                self.visit(stmt)
        
        # 5. End Label
        self.code.append(f"{l_end}:")

    def visit_Loop(self, node):
        # loop i in 1..5
        start_addr = self.visit(node.start_expr)
        end_addr = self.visit(node.end_expr)
        
        l_start = self.new_label()
        l_end = self.new_label()

        # Initialize i = start
        self.emit("ASSIGN", start_addr, None, node.var_name)

        # START LABEL
        self.code.append(f"{l_start}:")
        
        # Condition: i <= end
        t_cond = self.new_temp()
        self.emit("<=", node.var_name, end_addr, t_cond)
        
        # Jump out if False
        self.code.append(f"IF_FALSE {t_cond} GOTO {l_end}")

        # Body
        for stmt in node.body:
            self.visit(stmt)

        # Increment i = i + 1
        t_inc = self.new_temp()
        self.emit("+", node.var_name, "1", t_inc)
        self.emit("ASSIGN", t_inc, None, node.var_name)

        # Jump back to start
        self.code.append(f"GOTO {l_start}")

        # END LABEL
        self.code.append(f"{l_end}:")

    def generate(self, ast):
        self.code = []
        self.temp_count = 0
        self.label_count = 0
        for stmt in ast:
            self.visit(stmt)
        return self.code