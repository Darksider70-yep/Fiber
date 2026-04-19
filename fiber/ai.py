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
    def to_tensor(data, requires_grad=False):
        try:
            # Unwrap if it's already a FiberTensor or similar
            if hasattr(data, "data") and isinstance(data.data, torch.Tensor):
                data = data.data
            
            # If it's already a torch.Tensor, just return it (maybe clone for grad settings)
            if isinstance(data, torch.Tensor):
                if requires_grad and not data.requires_grad:
                    data = data.clone().detach().to(dtype=torch.float32).requires_grad_(True)
                return data
            
            # Otherwise create new from raw data
            return torch.tensor(data, requires_grad=requires_grad, dtype=torch.float32)
        except Exception as e:
            raise FiberRuntimeError(f"Tensor creation error: {e}")

    @staticmethod
    def matmul(a, b):
        try:
            ta = a if isinstance(a, torch.Tensor) else torch.tensor(a, dtype=torch.float32)
            tb = b if isinstance(b, torch.Tensor) else torch.tensor(b, dtype=torch.float32)
            return torch.matmul(ta.to(torch.float32), tb.to(torch.float32))
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
            actual_map = {}
            for k, v in mapping.items():
                sym = sp.Symbol(k) if isinstance(k, str) else k
                actual_map[sym] = v
            return expr.subs(actual_map)
        except Exception as e:
            raise FiberRuntimeError(f"Substitution error: {e}")

    @staticmethod
    def relu(t):
        tt = t if isinstance(t, torch.Tensor) else torch.tensor(t, dtype=torch.float32)
        return torch.relu(tt.to(torch.float32))

    @staticmethod
    def sigmoid(t):
        tt = t if isinstance(t, torch.Tensor) else torch.tensor(t, dtype=torch.float32)
        return torch.sigmoid(tt.to(torch.float32))

    @staticmethod
    def mse_loss(pred, target):
        tp = pred if isinstance(pred, torch.Tensor) else torch.tensor(pred, dtype=torch.float32)
        tt = target if isinstance(target, torch.Tensor) else torch.tensor(target, dtype=torch.float32)
        return torch.nn.functional.mse_loss(tp.to(torch.float32), tt.to(torch.float32))

    @staticmethod
    def randn(dims):
        return torch.randn(dims)

    @staticmethod
    def rand(dims):
        return torch.rand(dims)

    @staticmethod
    def conv2d(input, weight, bias=None, stride=1, padding=0):
        # Ensure bias is float if provided
        if bias is not None and not isinstance(bias, torch.Tensor):
            bias = torch.tensor(bias, dtype=torch.float32)
        return torch.nn.functional.conv2d(input, weight, bias, stride, padding)
