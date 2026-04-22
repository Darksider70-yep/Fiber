# 🌿 Fiber: High-Performance Neuro-Symbolic Language

**Fiber** is a next-generation programming language designed to bridge the gap between high-level symbolic logic and low-level numerical computation. It provides a first-class developer experience for AI researchers, data scientists, and systems engineers.

> **Status**: v4.0.1-emerald 🌿💎 (Stable)

---

## ⚡ Key Features
*   **🧩 Native Neuro-Symbolic Logic**: Blend algebraic symbols (SymPy-backed) with differentiable tensors (PyTorch-backed) in the same line of code.
*   **🏗️ Bytecode Compiler & Builder**: v4.0 supports pre-compiling scripts to binary bytecode (`.fibc`) and building zero-dependency standalone EXEs.
*   **📦 Standalone Distribution**: Generate true, portable binaries that don't require Python or Fiber on the target machine.
*   **🔋 Batteries-Included**: A comprehensive standard library covering everything from SQL and DataFrames to Modular Neural Layers.
*   **🧠 Relational AI Reasoning**: Native support for grid-based logical problems (like Wumpus World) with automatic differentiable learning.
*   **🧹 Automatic Differentiation**: Built-in autograd engine for training complex neural architectures.

---

---

## 🚀 Getting Started

### **1. Portable Installation (Recommended)**
Fiber is designed to be truly portable. You don't need Python or any external dependencies to run it.

1.  Download the official **`fiber.exe`** from the **[v4.0.1 Release Page](https://github.com/Darksider70-yep/Fiber/releases/tag/v4.0.1)**.
2.  Add the folder containing `fiber.exe` to your system **Environment Path**.
3.  Run `fiber your_script.fib` from any terminal!

### **2. IDE Support (VS Code)**
Get the professional developer experience:
- Install the **[Fiber Extension](https://marketplace.visualstudio.com/items?itemName=daksh-gehlot.fiber-vscode)** from the VS Code Marketplace.
- Enjoy syntax highlighting, snippets, and the custom **Fiber Branded Dark** theme.

### **3. Python Installation (Source)**
If you wish to run Fiber directly from source:
```bash
python fiber.py path/to/script.fib
```

---

## 🛠️ The Architecture

```mermaid
graph TD
    A["Fiber Source (.fib)"] --> B["Lexer/Parser"]
    B --> C["Interpreter Core"]
    C --> D["Symbolic Engine (SymPy)"]
    C --> E["Neural Engine (PyTorch)"]
    D --> F["Algebraic Reasoning"]
    E --> G["Tensor Computation"]
    F --> H["Neuro-Symbolic Bridge"]
    G --> H
```

---

## 📚 Standard Library (LibFiber)

Fiber now ships with a production-grade standard library documented in the **[API Reference](file:///C:/Users/Daksh%20Gehlot/OneDrive/Desktop/Fiber/Documents/API_REFERENCE.md)**.

- **`math`**: Full trigonometry and advanced logs.
- **`neural`**: Modular layers (`Linear`, `Conv2D`, `Sequential`).
- **`data`**: `DataFrame` engine with sorting and cleaning.
- **`io` / `sys`**: Complete file system and OS control.
- **`sqlite` / `csv`**: High-level relational and structured data access.

---

## ❓ FAQ (Frequently Asked Questions)

### **Q: Do I need to install Python or PyTorch to run Fiber?**
**A:** No. The standalone `fiber.exe` bundles all necessary scientific libraries (including PyTorch and SymPy) into a single binary. It is completely independent.

### **Q: Can I use Fiber for production-scale Deep Learning?**
**A:** Yes! Fiber's `neural` library is built on top of high-performance C++ backends (via PyTorch). You can build, train, and save models just like you would in Python, but with Fiber's clean, symbolic-aware syntax.

### **Q: How does the "Neuro-Symbolic" part work?**
**A:** In Fiber, an object can be a `Symbolic` expression one moment and a `Tensor` the next. You can differentiate an algebraic formula and immediately use the result as the weight of a neural layer.

### **Q: Where is the Standard Library stored?**
**A:** For the standalone version, the library is embedded inside the executable. For the source version, it resides in the `lib/` directory.

---

## 📄 License
Fiber is released under the **MIT License**.
