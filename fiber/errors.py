# fiber/errors.py
"""
Fiber Language — Error System
-----------------------------
Defines the structured error hierarchy used across
the Fiber interpreter, parser, and runtime layers.
Each error can carry contextual info such as line number
and filename for precise debugging feedback.
"""

class FiberError(Exception):
    """Base class for all Fiber language errors."""
    def __init__(self, message, line=None, filename=None):
        self.line = line
        self.filename = filename

        # Construct a unified message with context
        context = []
        if line is not None:
            context.append(f"line {line}")
        if filename is not None:
            context.append(filename)

        if context:
            message = f"{message} ({', '.join(context)})"

        super().__init__(message)

    def __str__(self):
        # Default display format for all Fiber errors
        return f"{self.args[0]}"


# --------------------------
# Specific Fiber Error Types
# --------------------------

class FiberSyntaxError(FiberError, SyntaxError):
    """Raised during lexical or parsing phase."""
    def __str__(self):
        return f"[Syntax Error] {self.args[0]}"


class FiberNameError(FiberError, NameError):
    """Raised for undefined variables or invalid names."""
    def __str__(self):
        return f"[Name Error] {self.args[0]}"


class FiberRuntimeError(FiberError, RuntimeError):
    """Raised during execution or runtime evaluation."""
    def __str__(self):
        return f"[Runtime Error] {self.args[0]}"


# --------------------------
# Utility and Debug Helpers
# --------------------------

def raise_syntax(msg, token=None, filename=None):
    """Helper for raising syntax errors with token context."""
    line = getattr(token, "line", None)
    raise FiberSyntaxError(msg, line=line, filename=filename)


def raise_runtime(msg, node=None, filename=None):
    """Helper for raising runtime errors with AST node context."""
    line = getattr(node, "line", None)
    raise FiberRuntimeError(msg, line=line, filename=filename)


def raise_name(msg, node=None, filename=None):
    """Helper for raising name errors with AST node context."""
    line = getattr(node, "line", None)
    raise FiberNameError(msg, line=line, filename=filename)
