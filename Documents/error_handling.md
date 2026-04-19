# 🚨 Error Handling in Fiber

Fiber provides a robust system for capturing and handling runtime and syntax errors, ensuring that programs can fail gracefully or provide meaningful feedback.

## 1. Try, Catch, and Finally

The `try` block allows you to execute code that might fail, while `catch` provides a way to handle the error.

```fiber
try {
    var x = 10 / 0
} catch (e) {
    print "Error caught: " + e
} finally {
    print "Execution finished"
}
```

- **`try`**: The code to attempt.
- **`catch`**: Executes if an error occurs. The error message is implicitly available or can be named (e.g., `catch (err)`).
- **`finally`**: Always executes, regardless of whether an error occurred.

## 2. Throwing Errors

You can manually trigger an error using the `throw` keyword.

```fiber
def check_age(age) {
    if age < 18 {
        throw "Access denied: Underage"
    }
}
```

## 3. Assertions

Assertions are used to verify that a certain condition is true. If it isn't, Fiber raises a runtime error.

```fiber
assert x > 0, "x must be positive"
```

## 4. Common Error Types

| Error | Cause |
| --- | --- |
| **FiberSyntaxError** | Raised when code doesn't conform to the language grammar (e.g., missing `{`). |
| **FiberNameError** | Raised when accessing a variable or function that hasn't been defined. |
| **FiberRuntimeError** | General errors that occur during execution (e.g., division by zero, invalid tensor operation). |

---

## 💡 Best Practices

- **Validate Inputs**: Use `assert` for internal integrity checks and `throw` for expected error conditions.
- **Cleanup**: Always use `finally` to release resources or reset states, especially when working with global variables (`static`).
- **Granular Catching**: Keep `try` blocks as small as possible to avoid catching unintended errors.
