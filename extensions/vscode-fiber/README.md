# Fiber: High-Performance Neuro-Symbolic IDE 🌿

Official Visual Studio Code extension for the **Fiber** programming language. Fiber is a next-generation "batteries-included" language designed for seamless integration of Neural Networks and Symbolic Logic.

## 🚀 Features

- **🌈 Gold-Standard Syntax Highlighting**: Precisely colorized keywords, operators, and Fiber-specific types (`tensor`, `expr`, `struct`, `enum`, `match`).
- **🏗️ One-Click Standalone Build**: Right-click any Fiber file to compile it into a production-ready Windows `.exe` instantly.
- **🛡️ Bytecode Integration**: Native support for Fiber Compiled Bytecode (`.fibc`) visualization and distribution.
- **🧠 Expert Snippets**:
  - `fneural`: Instantly scaffold a modular Sequential neural network.
  - `fexpr`: Create and differentiate symbolic expressions.
  - `fmatch`: Professional pattern-matching boilerplate.
- **🌑 Fiber Branded Dark Theme**: A premium, custom-designed dark theme optimized for neuro-symbolic development.
- **⚙️ Integrated Language Support**: Auto-bracket matching, indentation rules, and intelligent comment toggling.

## 🛠️ Getting Started
 
1. **Download Fiber**: Get the latest `fiber.exe` from the [Official Releases](https://github.com/Darksider70-yep/Fiber/releases).
2. **Install Extension**: Search for **Fiber** in the Marketplace and click Install.
3. **Configure Path**: 
   - Open VS Code Settings (`Ctrl+,`).
   - Search for `Fiber Path`.
   - Paste the path to your `fiber.exe` (e.g., `C:\Tools\fiber.exe`).
4. **Select Theme**: Open any `.fib` file and switch to the official theme: **Ctrl+K, Ctrl+T** -> **Fiber Branded Dark**.

## 🏗️ Running Code
- **Option 1 (Built-in)**: Right-click any `.fib` file in the explorer and select **"Build to Executable (EXE)"**.
- **Option 2 (Code Runner)**: If you have the *Code Runner* extension, add the following to your `settings.json` for 1-click execution:
```json
"code-runner.executorMap": {
    "fiber": "cd $dir && fiber $fileName"
}
```

## 🧩 Fiber at a Glance

```fiber
# Symbolic Differentiation
var e = expr("x**2 + 5*x")
print diff(e, "x")

# Neural Architecture
from neural import Linear, ReLU, Sequential
var model = Sequential([
    Linear(10, 32),
    ReLU(),
    Linear(32, 1)
])
```

## 📜 License

This extension is licensed under the [MIT License](LICENSE).

---
**Developed by [daksh-gehlot](https://github.com/Darksider70-yep/Fiber)**
