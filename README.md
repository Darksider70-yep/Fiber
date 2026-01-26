# 🌿 Fiber — A Lightweight Computational Language

[![Build](https://img.shields.io/badge/build-passing-brightgreen)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()
[![Made with ❤️ by Daksh Gehlot](https://img.shields.io/badge/made%20with-%E2%9D%A4-red)]()

> **Fiber** is a small, expressive programming language built from scratch in Python —  
> designed for **AI reasoning**, **symbolic computation**, **data structures**, and **graph-based logic**.  
>  
> It blends the clarity of Python with the mathematical elegance of symbolic systems like **Wolfram** or **Julia**,  
> while staying simple, readable, and fully hackable.

---

## 📚 Table of Contents

- [🚀 Vision](#-vision)
- [⚙️ Features](#️-features)
- [🧠 Philosophy](#-philosophy)
- [🧩 Example Programs](#-example-programs)
- [📦 Project Structure](#-project-structure)
- [🧩 Architecture Overview](#-architecture-overview)
- [🧪 Running Fiber](#-running-fiber)
- [🧱 Future Roadmap](#-future-roadmap)
- [💡 Example Use-Cases](#-example-use-cases)
- [🧑‍💻 Author](#-author)
- [🪄 License](#-license)

---

## 🚀 Vision

Fiber is not just another scripting language — it’s a **computational reasoning engine**.

> 🌱 *Readable as Python. Symbolic like Wolfram.  
> Simple like Lua. Extendable like Lisp.*

### 🎯 Core Objectives

- Build an **interpreted language** focused on:
  - Mathematical and symbolic **expressions**
  - **AI/ML logic**, model reasoning, and evaluation
  - **Data structures** and **graph algorithms**
- Keep the **core minimal and extensible** — new builtins or DSL features can be added easily.
- Act as a **lightweight computational kernel** embeddable in AI platforms like **Theriax**.

---

## ⚙️ Features

| Category | Feature | Status |
|-----------|----------|--------|
| **Language Core** | Lexer, Parser, AST, Interpreter | ✅ |
| **Control Flow** | `if`, `elif`, `else`, `while`, `for`, `return` | ✅ |
| **Loops** | `for i = 1 to 10 step 2`, `for i in range(1,10,2)` | ✅ |
| **Flow Control** | `break`, `continue` | ✅ |
| **Builtins** | `print`, `input`, `int`, `float`, `str`, `range` | ✅ |
| **Environment** | Lexical scope, global variables | ✅ |
| **Error System** | Rich error handling with line tracking | ✅ |
| **Expression Engine** | Symbolic/numeric expressions (`expr`, `simplify`) | 🚧 |
| **Data Structures** | Lists, Maps, Indexing, `len()`, `append()` | 🧩 |
| **Graphs** | Built-in `Graph` class (AI reasoning core) | ⏳ |

---

## 🧠 Philosophy

> “Code should *feel like thought*, and math should *feel like language*.”

Fiber unifies **programming**, **mathematics**, and **data reasoning**  
into a clean, human-readable form.

### Design Principles

- 🧩 **Composability:** Everything is an expression or object  
- 💡 **Readability:** Code looks like logic, not syntax  
- 🧠 **Reasoning-first:** Code is data — symbolic and inspectable  
- ⚙️ **Embeddable:** Runs standalone or inside AI systems  
- 🔁 **Extendable:** New keywords, types, and builtins are easy to add  

---

## 🧩 Example Programs

### 🧮 Basic Condition

```fiber
var x = 10
if x > 5 {
    print "Big number"
} else {
    print "Small number"
}
```

---

### 🔁 Loops and Flow Control

```fiber
for i = 1 to 10 step 2 {
    print "Odd number: " + str(i)
}
```

---

### 📈 Range-based Loop

```fiber
for i in range(1, 10, 3) {
    if i == 7 {
        break
    }
    print "i = " + str(i)
}
```

---

### 🧠 Functions and Return

```fiber
def find_even() {
    for i in range(1, 10) {
        if i % 2 == 0 {
            return i
        }
    }
    return -1
}

print "First even: " + str(find_even())
```

**Output:**
```
First even: 2
```

---

### 🔬 (Coming Soon) Symbolic Math

```fiber
var e = expr("x^2 + 2*x + 1")
print simplify(e)          # → (x + 1)^2
print eval(e, {x: 3})      # → 16
```

---

## 📦 Project Structure

```
fiber/
├── __init__.py          # Core module initialization
├── ast_nodes.py         # AST node definitions
├── environment.py       # Lexical scope system
├── errors.py            # Error definitions
├── lexer.py             # Tokenizer
├── parser.py            # Recursive descent parser
├── interpreter.py       # AST execution engine
├── objects.py           # Runtime objects (classes, functions)
├── repl.py              # Interactive REPL
└── examples/            # Sample .fib scripts
main.py                  # Entry point for REPL or file execution
```

---

## 🧩 Architecture Overview

### 1️⃣ Lexer
Converts source code into a stream of tokens.
```
for i = 1 to 10 { print i }
```
→  
```
[FOR, NAME(i), ASSIGN, NUMBER(1), TO, NUMBER(10), LBRACE, PRINT, NAME(i), RBRACE]
```

---

### 2️⃣ Parser
Builds an Abstract Syntax Tree (AST) from tokens.

---

### 3️⃣ Interpreter
Walks the AST recursively to execute logic:
- Manages environments and scopes
- Handles expressions, conditions, and returns
- Supports builtins and future symbolic features

---

## 🧪 Running Fiber

Run a `.fib` file:
```bash
python main.py examples/test.fib
```

Start the interactive REPL:
```bash
python main.py
```

Exit REPL with:
```
exit
```

---

## 🧱 Future Roadmap

| Phase | Goal | Description |
|--------|------|-------------|
| 🧮 **Expressions Core** | Symbolic + numeric expressions | `expr("a+b*c")`, `simplify()` |
| 📊 **Data Structures** | Lists, Maps, Indexing | `[1,2,3]`, `{x: y}`, `arr[0]` |
| 🔗 **Graphs Module** | Computational Graphs | Nodes, Edges, Traversals |
| 🧠 **AI/ML Primitives** | Model logic layer | `train(model, data)` |
| 🔬 **Symbolic Reasoning** | Equation solving, differentiation | `diff(expr, x)` |
| ⚡ **Optimization Layer** | Bytecode / VM / JIT backend | Speed improvements |
| 🌉 **Python Bridge** | Fiber ↔ Python interop | Call Python libs like NumPy |

---

## 💡 Example Use-Cases

### 🧮 Symbolic & Numeric Computation
```fiber
var e = expr("x^2 + 3*x + 2")
print simplify(e)
```

### 🧠 Machine Learning Logic
```fiber
if confidence(model.predict(x)) < 0.6 {
    retrain(model, data)
}
```

### 🌐 Graph Reasoning
```fiber
var g = Graph()
g.add_edge("A", "B")
print g.shortest_path("A", "B")
```

---

## 🧑‍💻 Author

**Daksh Gehlot**  
Developer • Researcher • Language Architect  
Building Fiber to bridge symbolic reasoning and AI computation.

---

## 🪄 License

Licensed under the **MIT License**.  
You are free to use, modify, and distribute Fiber with attribution.

---

## ⭐ Support & Contribution

Contributions are welcome!  
- Submit ideas, issues, or pull requests.  
- Discuss feature design or symbolic math improvements.  
- Star ⭐ the repo if you like the project!

---

> 🌟 *“Fiber connects reasoning, data, and code —  
> bringing mathematical clarity to the art of programming.”*
