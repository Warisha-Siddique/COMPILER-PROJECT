
# 🌟 **PatternScript — A Mini Language & Compiler Built from Scratch**

PatternScript is a custom Domain-Specific Language (DSL) designed for generating text-based and numeric patterns.
Built entirely in Python, the project showcases the **full compiler pipeline**—from tokenizing input to generating output patterns—with a clean syntax inspired by scripting languages.

This project was developed as part of the *Compiler Construction* course.

---

## ✨ **Language Highlights**

### 🧵 **Stitch Operator (`~`)**

A flexible concatenation operator that automatically converts numbers to strings.

```
display "Value: " ~ 5:
```

### ✨ **Repeat Operator (`*`)**

Overloaded to support both:

* numeric multiplication
* string repetition

```
display "*" * 5:
```

### 🔁 **Inclusive Looping**

Simple pattern-friendly loop syntax:

```
loop i in 1..3 {
    display i:
}
```

### 🎭 **Conditional Flow**

**check-else** block:

```
check score > 5 {
    display "Pass":
} else {
    display "Fail":
}
```

**choose-case** block:

```
choose day {
    1: display "Mon":
    2: display "Tue":
    default: display "Unknown":
}
```

---

## 🧩 **Compiler Features**

PatternScript demonstrates all formal phases of a compiler:

### **1. Lexical Analysis**

* Custom token definitions
* Full DFA (hand-designed)
* Longest-match rule for multi-character operators (`==`, `!=`, `<=`, `>=`, `..`)

### **2. Syntax Analysis**

* Recursive Descent Parser
* Clean BNF grammar
* Two fully-drawn parse trees
* AST (Abstract Syntax Tree) construction

### **3. Semantic Analysis**

* Type checking (string vs int)
* Stitch/Repeat operator rules
* Proper scoping for loop variables
* Error handling for invalid operations

### **4. Intermediate Code Generation**

* Three-Address Code (TAC)
* Temporary variable generation
* Quads for arithmetic, stitch, and branching

### **5. Optimization**

* Constant folding
* Dead-code elimination after `give`
* Simplified expression reduction

### **6. Execution Engine**

* Interpreter for TAC
* Executes display, loops, conditionals
* Handles early termination via `give`


## ▶️ **Running PatternScript**

### **Option 1 — Run a .ps program**

```
python src/cli.py tests/test1.ps
```

### **Option 2 — Direct Interpreter**

```
python src/interpreter.py
```

---

## 📘 **Basic Syntax Guide**

### **Variables**

```
x = 10:
name = "warisha":
```

### **Output**

```
display "Hello " ~ name:
```

### **Loops**

```
loop i in 1..5 {
    display "*" * i:
}
```

### **check (if/else)**

```
check x % 2 == 0 {
    display "Even":
} else {
    display "Odd":
}
```

### **choose-case**

```
choose x {
    1: display "One":
    2: display "Two":
    default: display "Other":
}
```

---

## 🧠 **Technical Concepts Demonstrated**

* Deterministic Finite Automata (DFA) for lexing
* Left factoring & removal of left recursion
* Recursive Descent parsing
* Symbol table construction
* Semantic error detection
* TAC (Three-Address Code) with temporaries
* Basic compiler optimizations
* Interpreter for execution

This project mirrors the structure of real-world compilers, making PatternScript both an educational exercise and a functional mini-language.

---

## 📜 **Credits**

Developed by **warisha**
for the *Compiler Construction (CS-4031)* project.
