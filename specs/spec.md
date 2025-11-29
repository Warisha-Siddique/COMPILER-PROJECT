
# 1. **Introduction**

PatternScript is a small, domain-specific language designed for generating text-based and numeric patterns.
It supports:

* loops
* conditionals
* case-selection
* arithmetic
* relational operators
* two special operators:

  * **Stitch (`~`)** for flexible concatenation
  * **Repeat (`*`)** for string repetition

The goal is to provide a minimal, expressive language useful for pattern printing, while keeping compiler implementation simple.
PatternScript excludes arrays, user-defined functions, and complex types to reduce parser and semantic analyzer complexity.

---

# 2. **Lexical Specification**

The lexical analyzer converts raw input characters into a stream of tokens.
Whitespace is ignored except as a separator.

---

## 2.1 **Keywords**

Reserved words that cannot be used as identifiers:

```
loop
check
else
choose
default
display
give
in
```

The lexer must return these as keyword tokens:

```
LOOP, CHECK, ELSE, CHOOSE, DEFAULT, DISPLAY, GIVE, IN
```

---

## 2.2 **Identifiers**

Identifiers name variables.

**Pattern:**

```
IDENT = [A-Za-z_][A-Za-z0-9_]*
```

Identifiers are case-sensitive.
If an IDENT lexeme matches a keyword, it becomes a keyword token.

---

## 2.3 **Literals**

### **Numbers**

```
NUMBER = [0-9]+
```

Always integers.

### **Strings**

```
STRING = "([^"\n])*"
```

Double-quoted, no newlines inside.

Escape sequences like `\"` and `\\` may be allowed depending on implementation.

---

## 2.4 **Operators**

### **Arithmetic & Special Operators**

| Token | Lexeme | Meaning                        |
| ----- | ------ | ------------------------------ |
| PLUS  | `+`    | addition                       |
| MINUS | `-`    | subtraction                    |
| STAR  | `*`    | multiplication / string repeat |
| MOD   | `%`    | modulo                         |
| TILDE | `~`    | stitch operator                |
| RANGE | `..`   | range operator                 |

### **Relational Operators**

| Token | Lexeme |
| ----- | ------ |
| EQ    | `==`   |
| NEQ   | `!=`   |
| LT    | `<`    |
| GT    | `>`    |
| LE    | `<=`   |
| GE    | `>=`   |

---

## 2.5 **Symbols**

| Token  | Lexeme |
| ------ | ------ |
| ASSIGN | `=`    |
| COLON  | `:`    |
| LBRACE | `{`    |
| RBRACE | `}`    |
| LPAREN | `(`    |
| RPAREN | `)`    |

---

## 2.6 **Whitespace**

Whitespace includes:

```
space ( ), tab (\t), newline (\n), carriage return (\r)
```

Ignored except for token separation.

---

## 2.7 **Tokenization Rules**

* The lexer uses **longest match** rule (e.g., `==` before `=`).
* If a lexeme matches IDENT but is in the keyword list → return keyword token.
* Strings preserve inner characters but remove surrounding quotes.
* Invalid characters cause lexical errors.

---

# 3. **Syntax Specification (Grammar)**

PatternScript uses a simplified block structure with `{}` and `:` as statement terminators.

The grammar is written in cleaned, recursive-descent-friendly form.

---

## 3.1 **Program Structure**

```
program → stmt_list
```

```
stmt_list → stmt stmt_list | ε
```

---

## 3.2 **Statements**

```
stmt →
      assign_stmt
    | display_stmt
    | return_stmt
    | loop_stmt
    | check_stmt
    | choose_stmt
```

---

### Assignment

```
assign_stmt → IDENT "=" expr ":"
```

### Display

```
display_stmt → DISPLAY expr ":"
```

### Return

```
return_stmt → GIVE expr ":"
```

### Loop (inclusive range)

```
loop_stmt → LOOP IDENT IN expr RANGE expr "{" stmt_list "}"
```

`RANGE` is the `..` token.

### Conditional

```
check_stmt → CHECK expr "{" stmt_list "}" ELSE "{" stmt_list "}"
```

### Choose-Case Selection

```
choose_stmt → CHOOSE expr "{" case_list default_case "}"
```

```
case_list → case_item case_list | case_item
```

```
case_item → literal ":" stmt_list
```

```
default_case → DEFAULT ":" stmt_list
```

---

## 3.3 **Expressions**

```
expr → relational_expr
```

### Relational

```
relational_expr → additive_expr (rel_op additive_expr)?
rel_op → == | != | < | > | <= | >=
```

### Additive, Concatenation, Stitching

```
additive_expr → multiplicative_expr ((+ | - | ~) multiplicative_expr)*
```

### Multiplication / Modulo

```
multiplicative_expr → factor ((* | %) factor)*
```

### Factors

```
factor → NUMBER
       | STRING
       | IDENT
       | "(" expr ")"
```

---

# 4. **Semantic Rules**

Semantic analysis defines how expressions behave, type rules, and runtime meaning.

---

## 4.1 **Types**

PatternScript has two primitive types:

```
int
string
```

No arrays, booleans, or custom types exist.
Booleans are represented as integers `0` (false) and `1` (true).

---

## 4.2 **Assignment Rules**

* Assigning an expression sets the identifier’s type.
* Reassignments must match the established type.
* Example: `x = 4:` → `x` becomes `int`.

---

## 4.3 **Operator Semantics**

### **Stitch Operator (~)**

| Left   | Right  | Result                 |
| ------ | ------ | ---------------------- |
| number | number | string (concatenation) |
| number | string | string                 |
| string | number | string                 |
| string | string | string                 |

Always converts both sides to string → concatenates.

Result type: **string**

---

### **Repeat Operator (*)**

Two meanings:

| Type         | Meaning                | Result |
| ------------ | ---------------------- | ------ |
| int * int    | numeric multiplication | int    |
| string * int | string repetition      | string |
| int * string | string repetition      | string |

Rules:

* repetition count must be a non-negative integer
* otherwise → semantic error

---

### **Relational Operators**

* Only valid for integers (`int`).
* Result is integer: `0` (false) or `1` (true).

---

## 4.4 **Loop Semantics**

```
loop i in a..b { ... }
```

* Loop variable `i` is local to the loop block.
* Iterates from `a` to `b` **inclusive**.
* Each iteration shadows any outer variable named the same.

---

## 4.5 **choose-case Semantics**

* Expression is evaluated once.
* Literal comparison is strict (string or number).
* First matching case executes.
* Only one case runs.
* `default` must always be present.

---

## 4.6 **Return (give)**

```
give expr:
```

* Immediately terminates program execution.
* Returns value (optional for your interpreter).

---

# 5. **Examples**

# Test Case 1 — Basic Math + Display
x = 4:
y = x * 5:
display y:

Output
20


# Test Case 2 — Stitch Operator (~)
name = "Taqwa":
level = 7:
display "User: " ~ name:
display "Level " ~ level:
display "ID=" ~ 1 ~ 2 ~ 3:

Output
User: Taqwa
Level 7
ID=123


# Test Case 3 — Repeat Operator (*)
display "*" * 5:
display 3 * "Yo":
display ("Hi" ~ "!") * 3:

Output
*****
YoYoYo
Hi!Hi!Hi!


# Test Case 4 — Mixed Logic
name = "Love":
score = 8:

check score > 5 {
    display name ~ " passed!":
} else {
    display name ~ " failed!":
}

Output
Love passed!


# Test Case 5 — Loop + Stitch + Repeat
loop i in 1..3 {
    display "Step " ~ i ~ ": " ~ ("-" * i):
}

Output
Step 1: -
Step 2: --
Step 3: ---


# Test Case 6 — choose-case
day = 3:

choose day {
    1: display "Mon":
    2: display "Tue":
    3: display "Wed":
    default: display "Unknown":
}

Output
Wed


# Test Case 7 — Combined Example
name = "Love":
stars = 5:

display "Welcome " ~ name ~ "!":

loop i in 1..stars {
    check i % 2 == 0 {
        display "Even: " ~ ("*" * i):
    } else {
        display "Odd: " ~ ("#" * i):
    }
}

Output
Welcome Love!
Odd: #
Even: **
Odd: ###
Even: ****
Odd: #####


---

# 6. **Error Handling**

### **Lexical Errors**

* Illegal characters
* Unterminated strings

### **Syntax Errors**

* Missing `:` terminators
* Unbalanced `{ }`
* Wrong token order

### **Semantic Errors**

* Type mismatch
* Using relational ops on strings
* Negative string repetition
* Using variables before assignment

---

# 7. **Conclusion**

This specification defines the complete lexical, syntactic, and semantic structure of PatternScript.
The compiler phases (lexer, parser, semantic analysis, IR generation, optimization, and execution) must adhere to these rules to ensure consistent and correct language behavior.

