import tkinter as tk
from tkinter import scrolledtext, simpledialog
import sys
import io
from Lexer import tokenize
from Parser import parse
from optimizer import Optimizer
from interpreter import Interpreter
from icg import TACGenerator

# ==========================================
# 1. CUSTOM INTERPRETER FOR GUI
# ==========================================
# We need to override the 'ask' command so it pops up a window
# instead of freezing the console.
class GuiInterpreter(Interpreter):
    def visit_Ask(self, node):
        # Open a popup dialog to get input
        value = simpledialog.askstring("Input Needed", f"Enter value for '{node.name}':")
        
        # If user cancels, treat as empty string or 0
        if value is None: value = ""
            
        try:
            self.variables[node.name] = int(value)
        except ValueError:
            self.variables[node.name] = value

# ==========================================
# 2. THE GUI APPLICATION
# ==========================================
class PatternScriptIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("PatternScript IDE")
        self.root.geometry("1000x600")
        self.root.configure(bg="#2b2b2b") # Dark Background

        # --- Top Toolbar ---
        toolbar = tk.Frame(root, bg="#1e1e1e", height=40)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        run_btn = tk.Button(toolbar, text="▶ RUN CODE", command=self.run_code, 
                            bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                            activebackground="#45a049", relief=tk.FLAT, padx=15)
        run_btn.pack(side=tk.LEFT, padx=10, pady=5)

        clear_btn = tk.Button(toolbar, text="🗑 CLEAR OUTPUT", command=self.clear_output,
                              bg="#d32f2f", fg="white", font=("Arial", 10, "bold"),
                              activebackground="#b71c1c", relief=tk.FLAT, padx=10)
        clear_btn.pack(side=tk.LEFT, padx=10, pady=5)

        # --- Main Layout (Split Screen) ---
        main_frame = tk.Frame(root, bg="#2b2b2b")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Editor (Left)
        self.editor_label = tk.Label(main_frame, text="Source Code:", bg="#2b2b2b", fg="white")
        self.editor_label.grid(row=0, column=0, sticky="w")
        
        self.editor = scrolledtext.ScrolledText(main_frame, width=50, height=30, 
                                                bg="#1e1e1e", fg="#dcdcdc", 
                                                insertbackground="white", font=("Consolas", 12))
        self.editor.grid(row=1, column=0, sticky="nsew", padx=(0, 5))

        # Output (Right)
        self.output_label = tk.Label(main_frame, text="Console Output:", bg="#2b2b2b", fg="white")
        self.output_label.grid(row=0, column=1, sticky="w")

        self.console = scrolledtext.ScrolledText(main_frame, width=50, height=30, 
                                                 bg="#000000", fg="#00ff00", # Hacker Green
                                                 font=("Consolas", 12), state='disabled')
        self.console.grid(row=1, column=1, sticky="nsew", padx=(5, 0))

        # Configure Grid Weights
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # Pre-load sample code
        sample_code = """note> Welcome to PatternScript IDE
plot "--- Running Fibonacci ---":
a = 0:
b = 1:
loop i in 1..10 {
    plot a:
    temp = a + b:
    a = b:
    b = temp:
}"""
        self.editor.insert(tk.END, sample_code)

    def clear_output(self):
        self.console.config(state='normal')
        self.console.delete(1.0, tk.END)
        self.console.config(state='disabled')

    def run_code(self):
        # 1. Get code from editor
        code = self.editor.get(1.0, tk.END)
        
        # 2. Clear previous output
        self.clear_output()
        self.console.config(state='normal')
        
        # 3. Capture Print Statements (Stdout Redirection)
        # This tells Python: "Don't print to terminal, print to this variable instead"
        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output

        try:
            # --- COMPILER PIPELINE ---
            self.console.insert(tk.END, "[Compiling...]\n", "info")
            
            # Phase 1 & 2
            ast = parse(code)
            
            # Phase 4
            self.console.insert(tk.END, "[Phase 4: Intermediate Code]\n", "info")
            icg = TACGenerator()
            tac_lines = icg.generate(ast)
            for line in tac_lines:
                self.console.insert(tk.END, f"  {line}\n")
            self.console.insert(tk.END, "-"*30 + "\n", "info")
            
            # Phase 5
            optimizer = Optimizer()
            ast = optimizer.optimize(ast)
            
            # Phase 6 (Using GUI Interpreter)
            interpreter = GuiInterpreter()
            for stmt in ast:
                interpreter.visit(stmt)
            
            # Get the text captured from print()
            output_text = redirected_output.getvalue()
            self.console.insert(tk.END, output_text)
            self.console.insert(tk.END, "\n[Finished Successfully]", "success")

        except Exception as e:
            # If error, show in Red
            self.console.insert(tk.END, f"\nRuntime Error: {e}", "error")
        
        finally:
            # Restore standard output so crashes don't break Python
            sys.stdout = old_stdout
            
            # Scroll to bottom
            self.console.see(tk.END)
            self.console.config(state='disabled')

        # Add colors for tags
        self.console.tag_config("error", foreground="red")
        self.console.tag_config("success", foreground="cyan")
        self.console.tag_config("info", foreground="gray")

# Run the App
if __name__ == "__main__":
    root = tk.Tk()
    app = PatternScriptIDE(root)
    root.mainloop()