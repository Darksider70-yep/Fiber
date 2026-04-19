# 📚 Fiber Standard Library & DSA

This document serves as a reference for the built-in functions and data structures provided by the Fiber runtime.

## 1. Core Builtins

| Function | Usage | Description |
| --- | --- | --- |
| `print(val)` | `print "Hi"` | Prints a value to standard output. |
| `input(prompt)` | `var n = input("?")` | Reads input from the user. |
| `len(obj)` | `len([1,2,3])` | Returns the length of a list, string, or tensor. |
| `append(list, val)` | `append(arr, 10)` | Adds a value to a list. |
| `range(end)` | `range(10)` | Returns a list from 0 to end - 1. |
| `range(start, end, step)` | `range(1, 10, 2)` | Returns a list with the specified range. |
| `str(val)` | `str(10)` | Converts a value to a string. |
| `int(val)` | `int("10")` | Converts a value to an integer. |
| `float(val)` | `float("1.2")` | Converts a value to a float. |

---

## 2. Native Data Structures (DSA)

Fiber includes high-performance data structures built natively into the global environment.

### Stack
Last-In, First-Out (LIFO) container.
```fiber
var s = Stack()
s.push(10)
s.push(20)
print s.pop()  # 20
print s.peek() # 10
```

### Queue
First-In, First-Out (FIFO) container.
```fiber
var q = Queue()
q.enqueue("Task 1")
q.enqueue("Task 2")
print q.dequeue() # Task 1
```

### Set
A collection of unique values.
```fiber
var mySet = Set()
mySet.add(10)
mySet.add(10) # Ignored
print mySet.size() # 1
print mySet.contains(10) # true
```

---

## 🧪 Math Module (Planned)
Future updates will include a standard `Math` class with common constants and trigonometric functions. Currently, algebraic math should be performed via the symbolic [AI & Symbolic Core](ai_and_symbolic.md).
