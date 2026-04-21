import numpy as np
import sympy as sp
import torch
from .errors import FiberRuntimeError

class AIBridge:
    @staticmethod
    def parse_expr(expr_str):
        from sympy.parsing.sympy_parser import parse_expr as sp_parse, standard_transformations, implicit_multiplication_application, auto_symbol
        # Transformations to handle logical notation and automatic symbol/function creation
        local_dict = {'And': sp.And, 'Or': sp.Or, 'Not': sp.Not, 'Implies': sp.Implies, 'Equivalent': sp.Equivalent}
        
        # Use bitwise logic transformations for symbols like &, |, ~
        from sympy.parsing.sympy_parser import convert_xor
        
        # We also need to map >> to Implies. Sympify doesn't do this by default for symbols.
        # But we can replace it in the string if it's not and/or/not.
        s = expr_str.replace(">>", " >> ") # Ensure spacing
        
        try:
            # We use standard_transformations but NOT implicit_multiplication_application if we want (Socrates) to be args
            # Actually, standard transformations include auto_symbol which is good.
            return sp_parse(s, local_dict=local_dict, transformations=standard_transformations)
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

    # -----------------------------
    # Logical Operations
    # -----------------------------
    @staticmethod
    def implies(a, b):
        from sympy.logic.boolalg import Implies
        return Implies(a, b)

    @staticmethod
    def equivalent(a, b):
        from sympy.logic.boolalg import Equivalent
        return Equivalent(a, b)

    @staticmethod
    def to_cnf(expr):
        from sympy.logic.boolalg import to_cnf
        return to_cnf(expr)

    @staticmethod
    def to_dnf(expr):
        from sympy.logic.boolalg import to_dnf
        return to_dnf(expr)

    @staticmethod
    def satisfiable(expr):
        from sympy.logic.inference import satisfiable
        return satisfiable(expr)

    @staticmethod
    def get_symbols(expr):
        if hasattr(expr, "free_symbols"):
            return [str(s) for s in expr.free_symbols]
        return []

    @staticmethod
    def logic_to_loss(expr, mappings, norm_type="product"):
        """
        Converts a symbolic logic expression to a differentiable Torch tensor loss.
        mappings: dict of {symbol_name: torch_tensor}
        norm_type: "product", "godel", "lukasiewicz"
        """
        import sympy as sp
        
        def evaluate(node):
            if isinstance(node, bool):
                return torch.tensor(1.0 if node else 0.0)
            if isinstance(node, sp.Symbol):
                return mappings.get(str(node), torch.tensor(0.5, requires_grad=True))
            
            args = [evaluate(arg) for arg in node.args]
            
            if isinstance(node, sp.Not):
                return 1.0 - args[0]
            
            if isinstance(node, sp.And):
                if norm_type == "product":
                    res = args[0]
                    for a in args[1:]: res = res * a
                    return res
                elif norm_type == "godel":
                    return torch.min(torch.stack(args))
                elif norm_type == "lukasiewicz":
                    res = args[0]
                    for a in args[1:]: res = torch.clamp(res + a - 1.0, min=0.0)
                    return res
            
            if isinstance(node, sp.Or):
                if norm_type == "product":
                    res = args[0]
                    for a in args[1:]: res = res + a - (res * a)
                    return res
                elif norm_type == "godel":
                    return torch.max(torch.stack(args))
                elif norm_type == "lukasiewicz":
                    res = args[0]
                    for a in args[1:]: res = torch.min(torch.tensor(1.0), res + a)
                    return res
            
            from sympy.logic.boolalg import Implies, Equivalent
            if isinstance(node, Implies):
                # Reichenbach/Kleene-Dienes variant
                a, b = args[0], args[1]
                if norm_type == "product":
                    return 1.0 - a + (a * b)
                elif norm_type == "godel":
                    return torch.max(1.0 - a, b)
                elif norm_type == "lukasiewicz":
                    return torch.min(torch.tensor(1.0), 1.0 - a + b)
            
            if isinstance(node, Equivalent):
                a, b = args[0], args[1]
                # (A -> B) & (B -> A)
                return evaluate(Implies(node.args[0], node.args[1])) * evaluate(Implies(node.args[1], node.args[0]))

            return torch.tensor(0.0)

        return evaluate(expr)
