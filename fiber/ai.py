import numpy as np
import sympy as sp
import torch
from .errors import FiberRuntimeError

class AIBridge:
    @staticmethod
    def parse_expr(expr_str):
        try:
            return sp.sympify(expr_str)
        except Exception as e:
            raise FiberRuntimeError(f"Symbolic parsing error: {e}")

    @staticmethod
    def differentiate(expr, var):
        try:
            symbol = sp.Symbol(var) if isinstance(var, str) else var
            return sp.diff(expr, symbol)
        except Exception as e:
            raise FiberRuntimeError(f"Differentiation error: {e}")

    @staticmethod
    def simplify(expr):
        return sp.simplify(expr)

    @staticmethod
    def to_tensor(data):
        try:
            # Handles lists, nested lists, and numpy arrays
            return np.array(data)
        except Exception as e:
            raise FiberRuntimeError(f"Tensor creation error: {e}")

    @staticmethod
    def matmul(a, b):
        try:
            return np.matmul(a, b)
        except Exception as e:
            raise FiberRuntimeError(f"Matrix multiplication error: {e}")

    @staticmethod
    def solve(expr, var):
        try:
            symbol = sp.Symbol(var) if isinstance(var, str) else var
            return sp.solve(expr, symbol)
        except Exception as e:
            raise FiberRuntimeError(f"Solving error: {e}")

    @staticmethod
    def subst(expr, mapping):
        try:
            # mapping should be a dict of {var_name: value}
            actual_map = {}
            for k, v in mapping.items():
                sym = sp.Symbol(k) if isinstance(k, str) else k
                actual_map[sym] = v
            return expr.subs(actual_map)
        except Exception as e:
            raise FiberRuntimeError(f"Substitution error: {e}")

    @staticmethod
    def torch_logic():
        # placeholder for future torch integration
        pass
