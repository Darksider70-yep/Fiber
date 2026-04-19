# 📚 Fiber Standard Library & LibFiber

Fiber provides a dual-layer standard library: **Builtins** (implemented in Python for performance) and **LibFiber** (implemented in Fiber for maintainability and education).

## 1. Importing Modules

Use the `from` or `import` keywords to access the standard library. Fiber automatically looks in the `lib/` directory relative to the project root.

```fiber
import math
from algo import quick_sort
from graph import bfs, dijkstra
```

---

## 2. LibFiber Modules

### 🔢 `math`
High-level mathematical utilities.
- **Constants**: `PI`, `E`
- **Functions**:
  - `factorial(n)`, `fibonacci(n)`
  - `gcd(a, b)`, `lcm(a, b)`
  - `is_prime(n)`, `power(base, exp)`
  - `abs(n)`, `max(a, b)`, `min(a, b)`

### ⚡ `algo`
Classical computer science algorithms.
- **Sorting**:
  - `quick_sort(arr)`: Recursive divide-and-conquer.
  - `merge_sort(arr)`: Stable sorting algorithm.
  - `bubble_sort(arr)`: Educational sorting.
- **Searching**:
  - `binary_search(arr, target)`: O(log n) search on sorted lists.
  - `linear_search(arr, target)`: Basic iterative search.

### 🕸️ `graph`
Advanced graph reasoning and pathfinding.
- **Traversal**: `bfs(adj, start)`, `dfs(adj, start)`.
- **Shortest Path**:
  - `dijkstra(adj, start, end)`: Classic weighted search.
  - `a_star(adj, start, end, heuristic)`: Informed search with heuristics.
  - `greedy_bfs(adj, start, end, heuristic)`: Best-first search.
- **Data Structures**: Includes a native `PriorityQueue` class.

---

## 3. Core Builtins

| Function | Usage | Description |
| --- | --- | --- |
| `print(val)` | `print x` | Standard output. |
| `None` | `var x = None` | The global null value. |
| `tensor(d, g)`| `tensor([1], true)` | Create a (trainable) tensor. |
| `matmul(a, b)`| `matmul(w, x)` | Matrix multiplication. |
| `len(obj)` | `len([1, 2])` | Length of collection. |
| `append(l, v)`| `append(list, 1)` | Add item to list. |
| `range(end)` | `range(10)` | Generate a sequence. |

---

## 🏗️ Native Data Structures (DSA)

High-performance containers available globally:
- **`Stack()`**: `.push(v)`, `.pop()`, `.peek()`, `.size()`.
- **`Queue()`**: `.enqueue(v)`, `.dequeue()`, `.size()`.
- **`Set()`**: `.add(v)`, `.contains(v)`, `.size()`.
