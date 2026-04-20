# 🛡️ Fiber Compiler (fibc) Technical Reference

Fiber v2.1 introduces a high-performance **Bytecode Compiler** that transforms human-readable Fiber source code (`.fib`) into optimized binary bytecode (`.fibc`).

---

## 🚀 Overview
The Fiber Compiler shifts the language from a pure interpreter to a **hybrid model**. By pre-compiling your scripts, you skip the time-consuming Lexing and Parsing phases during execution, leading to significantly faster application startup.

## 🛠️ Usage

### Command Line Interface (CLI)
Use the `-c` or `--compile` flag with the Fiber binary to build your project.

```powershell
# Compile a script
fiber -c main.fib

# The compiler creates 'main.fibc' in the same directory.
```

### Running Compiled Code
Fiber automatically detects binary files. You can run them just like source files:

```powershell
# Run the binary version
fiber main.fibc
```

### Programmatic API
You can trigger the compiler from within a Fiber script using the `sys` library.

```fiber
import sys

# Compiles 'module.fib' and returns the path to the resulting .fibc
var binPath = sys.compile("module.fib")
print "Compiled to: " + binPath
```

---

## 🏗️ Internal Architecture

### 1. Magic Header
All Fiber binaries start with a 4-byte "Magic Number" sequence: `\x46\x49\x42\x02` (`FIB\x02`). This prevents the engine from attempting to execute incompatible files.

### 2. AST Serialization
The compiler serializes the Abstract Syntax Tree (AST) using an optimized object protocol. This ensures that the exact logical structure of your program is preserved without the overhead of re-parsing text.

### 3. Compression
To minimize disk footprint and speed up I/O, the serialized AST is compressed using the **Zlib** algorithm before being written to disk.

---

## 💎 Benefits
*   **Performance**: Massive reduction in overhead for large codebases.
*   **Security**: Provides a layer of obfuscation by distributing binary ASTs instead of plain text.
*   **Reliability**: Pre-compilation ensures that syntax errors are caught before the deployment phase.

---
*Fiber v2.1 — Building for the Future.*
