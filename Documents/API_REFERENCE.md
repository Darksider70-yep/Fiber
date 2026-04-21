# 📗 Fiber API Reference (ver 4.0.0)

This document provides a comprehensive reference for the Fiber Standard Library (**LibFiber**). All modules listed here are embedded within the standalone Fiber executable.

---

## 🔢 `lib/math.fib` - Advanced Mathematics
High-performance mathematical and trigonometric utilities.

| Function | Description |
| :--- | :--- |
| `sin(n)`, `cos(n)`, `tan(n)` | Trigonometric functions. |
| `asin(n)`, `acos(n)`, `atan(n)` | Inverse trigonometric functions. |
| `sqrt(n)` | Square root of `n`. |
| `ceil(n)`, `floor(n)` | Rounding up or down to the nearest integer. |
| `round(n, p)` | Round `n` to `p` decimal places. |
| `log(n, b)`, `log10(n)` | Logarithmic functions (default base $e$). |
| `pow(a, b)` | Equivalent to `a ** b`. |
| `factorial(n)` | Calculates $n!$. |
| `is_prime(n)` | Boolean check for prime numbers. |

---

## 📂 `lib/io.fib` - File System & I/O
Tools for managing files, directories, and system metadata.

| Function | Description |
| :--- | :--- |
| `read(path)` | Reads entire file content as string. |
| `write(path, content)` | Overwrites a file with content. |
| `mkdir(path)` | Creates a directory (recursive). |
| `list(path)` | Returns a list of strings representing directory contents. |
| `remove(path)` | Deletes a file. |
| `size(path)` | Returns file size in bytes. |
| `is_dir(path)`, `is_file(path)` | Type validation checks. |

---

## 📊 `lib/data.fib` - Structured Data Analysis
High-level classes for manipulating datasets.

### `DataFrame` Class
- **`init(rows)`**: Initialize with a list of dictionaries.
- **`column(name)`**: Extracts a specific column as a list.
- **`filter(col, val)`**: Returns a new `DataFrame` where `col == val`.
- **`sort_by(col, ascending)`**: Returns a sorted `DataFrame`.
- **`mean(col)`, `sum(col)`**: Aggregation statistics.
- **`dropna(col)`, `fillna(col, val)`**: Data cleaning utilities.

---

## 🧠 `lib/neural.fib` - Modular Neural Engine
Classes for building and training neural architectures.

### Layers
- **`Linear(in, out)`**: Fully connected layer.
- **`Conv2D(in, out, k, s, p)`**: 2D Convolutional layer.
- **`ReLU()`, `SigmoidLayer()`**: Activation layers.

### Containers
- **`Sequential(layers)`**: Chains multiple layers together. Automatically aggregates parameters across the entire stack.

---

## 🌐 `lib/net.fib` - Networking
HTTP and URL utilities.

| Function | Description |
| :--- | :--- |
| `get(url, headers)` | Performs a GET request. |
| `post(url, data, headers)` | Performs a POST request. |
| `fetch_json(url)` | Convenience method for JSON APIs. |
| `encode(s)`, `decode(s)` | URL encoding/decoding. |
| `download(url, dest)` | Streams a remote file directly to `dest`. |

---

## 🎲 `lib/random.fib` & `lib/regex.fib`
- **Random**: `rand_int(a, b)`, `choice(list)`, `shuffle(list)`.
- **Regex**: `match(pattern, string)`, `search(pattern, string)`, `replace(pattern, repl, string)`.

---

## 🧩 `lib/logic.fib` - Neuro-Symbolic Logic AI
Advanced utilities for probabilistic and relational reasoning.

### Logic Reasoning
- **`expr(S)`**: Parses a string into a symbolic logic expression.
- **`logic_symbols(E)`**: Returns all variable names in expression `E`.
- **`as_loss(E, M, N)`**: Converts logic `E` to a differentiable tensor using mapping `M` and norm `N`.

### Neuro-Symbolic Classes
- **`LogicTrainer`**: Automated optimizer for logical constraints.
- **`RelationalReasoner(w, h)`**: Grid-based reasoner for problems like Wumpus World.
- **`FuzzyKnowledgeBase`**: Differentiable KB supporting confidence-weighted facts.

### Quantifiers
- **`fuzzy_forall(domain, predicate)`**: Differentiable Universal quantifier.
- **`fuzzy_exists(domain, predicate)`**: Differentiable Existential quantifier.
