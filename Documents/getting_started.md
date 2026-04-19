# 🚀 Getting Started with Fiber

Fiber is a lightweight, expressive language designed for **AI reasoning**, **symbolic computation**, and **graph-based logic**.

## 🔧 Prerequisites

Fiber is built in Python and leverages several powerful libraries for its AI and mathematical features. Ensure you have Python 3.8+ installed, and then install the required dependencies:

```bash
pip install numpy sympy torch networkx matplotlib
```

## 📦 Running Fiber

### 1. Interactive REPL
To start the Fiber interactive shell:
```bash
python main-DARKZONE.py
```
You can type expressions directly:
```fiber
fiber> var x = 10
fiber> print x * 2
20
fiber> exit
```

### 2. Executing Scripts
Save your code in a `.fib` file (e.g., `hello.fib`) and run it:
```bash
python main-DARKZONE.py hello.fib
```

---

## 👋 Your First Program

Create a file named `hello.fib`:

```fiber
# Standard Fiber variable
var name = "Explorer"

# A basic function
def greet(who) {
    print "Hello, " + who + "!"
}

greet(name)

# A touch of math
var e = expr("x^2 + 1")
print "Mathematical core: " + str(e)
```

Run it using `python main-DARKZONE.py hello.fib`.

## 📚 Next Steps
- [Syntax Guide](syntax_guide.md): Learn about variables, loops, and logic.
- [AI & Symbolic Reasoning](ai_and_symbolic.md): Dive into the math engine.
- [OOP & Structs](oop_and_structs.md): Learn about classes and inheritance.
