# 🌿 Fiber — A Lightweight Computational Language

[![Build](https://img.shields.io/badge/build-passing-brightgreen)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()
[![Version](https://img.shields.io/badge/version-0.2--beta-blueviolet)]()

> **Fiber** is a high-performance, expressive programming language built in Python —  
> engineered for **AI reasoning**, **symbolic computation**, and **dynamic graph logic**.

It bridges the divide between pure mathematics and modern software engineering, blending Pythonic clarity with the symbolic rigor of systems like Wolfram or Julia.

---

## 🏛️ Visionary Architecture

Fiber is built as a modular pipeline designed for transparency and mathematical exactness.

```mermaid
graph TD
    A[Source Code .fib] --> B[Lexer]
    B --> C[Recursive Descent Parser]
    C --> D[Abstract Syntax Tree]
    D --> E[Execution Engine]
    E --> F[Symbolic Engine (SymPy)]
    E --> G[Numerical Tensor Stack (NumPy)]
    F --> H[Reasoning Results]
    G --> I[ML Model State]
```

## 🧠 Core Philosophy
- **Reasoning-First**: Code is data. Symbolic expressions are first-class citizens.
- **Explicit Scoping**: Deterministic lexical scoping for safe asynchronous AI logic.
- **Embedded Science**: Native integration with the scientific Python ecosystem (NumPy/SymPy).

---

## 📚 Documentation Suite

Explore our in-depth guides in the `Documents/` folder:

- 🚀 [**Getting Started**](Documents/getting_started.md): Installation & first program.
- 📝 [**Syntax Guide**](Documents/syntax_guide.md): Variables, loops, and logic.
- 🧠 [**AI & Symbolic Reasoning**](Documents/ai_and_symbolic.md): The core engine features.
- 🏗️ [**OOP & Structs**](Documents/oop_and_structs.md): Classes, inheritance, & structs.
- 📚 [**Standard Library**](Documents/standard_library.md): Builtins & native DSA.
- 🚨 [**Error Handling**](Documents/error_handling.md): Exception logic & debugging.

---

## ⚙️ Feature Matrix

| Category | Feature | Status |
|-----------|----------|--------|
| **Core** | Lexer, Parser, AST, Interpreter | ✅ |
| **Logic** | `if/else`, `while`, `for`, `try/catch` | ✅ |
| **Math** | Symbolic Derivatives, Equation Solving | ✅ |
| **Data** | Tensors, Matrix Math, Dictionaries | ✅ |
| **OOP** | Inheritance, Classes, Structs, Enums | ✅ |

---

## 🧪 Quick Demo: Symbolic Logic

```fiber
# Automatic differentiation
var loss = expr("w^2 + 5*w")
var gradient = diff(loss, "w")

# Numerical execution
var w = 10.0
var step = w - (0.1 * subst(gradient, {"w": w}))

print "Updated State: " + str(step)
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
