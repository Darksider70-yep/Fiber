# 📝 Fiber Syntax Guide

Fiber's syntax is engineered for clarity and precision, merging a modern lexical structure with a powerful, deterministic execution engine.

## 1. Variable Ecosystem

Fiber utilizes a multi-tiered declaration system to handle memory and mutability exactly as needed.

| Keyword | Mutability | Scope | Lifetime |
| --- | --- | --- | --- |
| `var` | Mutable | Lexical | Scope-bound |
| `const` | Immutable | Lexical | Scope-bound / Compilation |
| `final` | Once-set | Lexical | Scope-bound |
| `static` | Mutable | Global | Persistent |

### The `None` Value
Fiber uses `None` as its first-class null value.
```fiber
var result = None
if result == None {
    print "Pending..."
}
```

---

## 2. Control Logic & Operators

### Short-Circuit Evaluation
The logical operators `and` and `or` utilize short-circuit logic, improving performance and safety.
```fiber
# func_b() is NEVER called if a is false
if a and func_b() { ... }

# func_c() is NEVER called if a is true
if a or func_c() { ... }
```

### Advanced Iteration
Fiber loops are strictly typed for performance:

1. **Deterministic Range**:
   ```fiber
   for i = 0 to 100 step 10 {
       print i # 0, 10, 20...
   }
   ```

2. **Collection Traversal**:
   ```fiber
   var data = [10, 20, 30]
   for val in data {
       print val * 2
   }
   ```

---

## 3. Native Collections

Fiber supports multi-line literals for ease of defining large datasets or configurations.

### List Literals
Ordered, dynamic arrays.
```fiber
var colors = [
    "red", 
    "green", 
    "blue"
]
```

### Dictionary Literals (v0.2)
Key-value mappings, critical for symbolic substitution and configuration.
```fiber
var config = {
    "ip": "127.0.0.1",
    "port": 8080,
    "active": true
}
```

---

## 4. First-Class Functions & Scoping

In Fiber, functions are values. They can be stored in variables, passed to other functions, and returned as results.

### Lexical Closures
Fiber supports lexical closures, allowing functions to "remember" variables from their parent scope.

```fiber
def make_counter(start) {
    var count = start
    def increment() {
        count = count + 1
        return count
    }
    return increment
}

var c = make_counter(10)
print c() # 11
print c() # 12
```
