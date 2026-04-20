# 📖 Fiber Language Reference (v2.0)

Welcome to the official technical reference for Fiber. This document covers the core language syntax, the global built-in functions, and the extensive standard library module suite.

---

## ⚡ v2.0 Language Features

### 🏢 Object Orientation & Data
*   **Classes & Inheritance**: Support for full hierarchies using the `extends` keyword.
    ```fiber
    class Animal { def speak() { print "Sound" } }
    class Dog extends Animal { def speak() { print "Bark" } }
    ```
*   **Lightweight Structs**: Fixed-field data containers for high-performance modeling.
    ```fiber
    struct Point { x, y }
    var p = Point(10, 20)
    ```
*   **Symbolic Enums**: Named constants for readable state management.
    ```fiber
    enum Status { ACTIVE, PAUSED, STOPPED }
    ```

### 🎭 Flow Control & Sugaring
*   **Pattern Matching**: The `match` (or `switch`) statement specifically designed for Enums and values.
    ```fiber
    match status {
        case Status.ACTIVE: print "Running"
        default: print "Unknown"
    }
    ```
*   **Ternary Operator**: Inline conditional expressions.
    ```fiber
    var label = (score > 50) ? "Pass" : "Fail"
    ```
*   **List Comprehensions**: Modern list generation and filtering.
    ```fiber
    var evens = [ x for x in range(10) if x % 2 == 0 ]
    ```

---

## 📦 Global Built-in Functions

### 📝 Basic IO & Types
| Function | Description |
| :--- | :--- |
| `print(val)` | Outputs text to the console. |
| `input(prompt)` | Retrieves a string from user input. |
| `int(val)` / `float(val)` | Converts a value to numeric types. |
| `str(val)` | Converts any value to a string. |
| `len(obj)` | Returns the length of a list, string, or collection. |
| `range(start, end, step)` | Generates a numeric list. |

### 🧠 Neural & Symbolic Engine
| Function | Description |
| :--- | :--- |
| `tensor(data, grad)` | Creates a high-performance FiberTensor. |
| `matmul(a, b)` | Performs matrix multiplication. |
| `backward(tensor)` | Triggers automatic differentiation / backpropagation. |
| `optimizer(params, type, lr)` | Initializes SGD or Adam optimizers. |
| `expr("formula")` | Parses a symbolic string into a `FiberSymbolic` object. |
| `diff(expr, var)` | Calculates the symbolic derivative. |

### 📂 File System & OS
| Function | Description |
| :--- | :--- |
| `fs_read(path)` | Reads a file's content as a string. |
| `fs_write(path, data)` | Overwrites a file with the provided data. |
| `fs_exists(path)` | Checks if a path exists on the disk. |
| `os_exec(cmd)` | Executes a shell command and returns the output. |
| `time_now()` | Returns the current system timestamp in seconds. |

---

## 📚 Standard Library Index

Import these modules using `import <module>` to expand Fiber's capability.

### 🔢 `math`
Advanced constants (`PI`, `E`) and trigonometric/rounding functions (`sin`, `cos`, `sqrt`, `ceil`, `floor`). Includes prime checking and factorials.

### 🕸️ `net` & `json`
Sync HTTP requests (`http_req`) supporting GET, POST, etc., and seamless JSON parsing/stringification (`json_parse`, `json_str`).

### 🗄️ `sqlite` & `csv`
Direct SQLite database connectivity (`sql_connect`, `sql_query`) and native CSV file processing.

### 📈 `stats` & `data`
High-level data manipulation including means, standard deviations, and list sorting/filtering.

### 🎨 `ui`
Basic terminal-based UI helpers for creating menus, progress bars, and formatted tables.

---

*Fiber v2.0 — Architected for Intelligence.*
