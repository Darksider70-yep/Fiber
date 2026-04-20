from .environment import Environment
from .ast_nodes import FuncDef
import torch
import numpy as np
import sympy as sp

class FiberFunction:
    def __init__(self, name, params, body, closure, defaults=None):
        self.name = name
        self.params = params
        self.body = body
        self.closure = closure
        self.defaults = defaults or {}

    def call(self, interpreter, args, this=None):
        env = Environment(parent=self.closure)
        for i, p in enumerate(self.params):
            val = None
            if i < len(args):
                val = args[i]
            elif p in self.defaults:
                val = interpreter.eval_expr(self.defaults[p], env)
            
            env.set_local(p, val)

        if this is not None:
            env.set_local('this', this)
        try:
            return interpreter.exec_block(self.body, env)
        except ReturnSignal as r:
            return r.value

class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value

class FiberClass:
    def __init__(self, name, methods, parent=None):
        self.name = name
        self.methods = methods
        self.parent = parent
    def find_method(self, name):
        if name in self.methods:
            return self.methods[name]
        if self.parent:
            return self.parent.find_method(name)
        return None

class FiberInstance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}
    def get(self, name):
        if name in self.fields:
            return self.fields[name]
        m = self.klass.find_method(name)
        if m:
            def bound(*args):
                return m.call(self._interpreter, list(args), this=self)
            bound._fiber_func = m
            return bound
        raise KeyError(name)
    def set(self, name, value):
        self.fields[name] = value
    def __repr__(self):
        return f'<{self.klass.name} instance>'

class FiberSymbolic:
    def __init__(self, expr):
        self.expr = expr
    def __repr__(self):
        return f'Symbolic({self.expr})'
    def __str__(self):
        return str(self.expr)

class FiberTensor:
    def __init__(self, data, requires_grad=False):
        if isinstance(data, torch.Tensor):
            self.data = data
        else:
            dtype = torch.float32 if requires_grad else None
            self.data = torch.tensor(data, requires_grad=requires_grad, dtype=dtype)
    
    def backward(self):
        if self.data.requires_grad:
            self.data.backward()
    
    @property
    def grad(self):
        if self.data.grad is not None:
            return FiberTensor(self.data.grad)
        return None

    def zero_grad(self):
        if self.data.grad is not None:
            self.data.grad.zero_()

    def __repr__(self):
        return f'Tensor({self.data.detach().cpu().numpy() if self.data.requires_grad else self.data.cpu().numpy()}, grad={self.data.requires_grad})'
    
    def __str__(self):
        return str(self.data.detach().cpu().numpy() if self.data.requires_grad else self.data.cpu().numpy())

    def __getitem__(self, idx):
        return FiberTensor(self.data[idx], requires_grad=self.data.requires_grad)
    
    def __setitem__(self, idx, val):
        v = val.data if isinstance(val, FiberTensor) else val
        self.data[idx] = v
        
    def __add__(self, other):
        o = other.data if isinstance(other, FiberTensor) else other
        return FiberTensor(self.data + o, requires_grad=self.data.requires_grad or (isinstance(other, FiberTensor) and other.data.requires_grad))
    
    def __sub__(self, other):
        o = other.data if isinstance(other, FiberTensor) else other
        return FiberTensor(self.data - o, requires_grad=self.data.requires_grad or (isinstance(other, FiberTensor) and other.data.requires_grad))
    
    def __mul__(self, other):
        o = other.data if isinstance(other, FiberTensor) else other
        return FiberTensor(self.data * o, requires_grad=self.data.requires_grad or (isinstance(other, FiberTensor) and other.data.requires_grad))

    def __truediv__(self, other):
        o = other.data if isinstance(other, FiberTensor) else other
        return FiberTensor(self.data / o, requires_grad=self.data.requires_grad or (isinstance(other, FiberTensor) and other.data.requires_grad))

    def __radd__(self, other): return self.__add__(other)
    def __rsub__(self, other): 
        return FiberTensor(other - self.data, requires_grad=self.data.requires_grad)
    def __rmul__(self, other): return self.__mul__(other)
    def __rtruediv__(self, other):
        return FiberTensor(other / self.data, requires_grad=self.data.requires_grad)

class FiberOptimizer:
    def __init__(self, params, opt_type="sgd", lr=0.01):
        # Filter only tensors that require grad
        torch_params = []
        for p in params:
            if isinstance(p, FiberTensor) and p.data.requires_grad:
                torch_params.append(p.data)
        
        if not torch_params:
            raise ValueError("No trainable parameters provided to optimizer")

        if opt_type.lower() == "adam":
            self.optimizer = torch.optim.Adam(torch_params, lr=lr)
        else:
            self.optimizer = torch.optim.SGD(torch_params, lr=lr)

    def step(self):
        self.optimizer.step()

    def zero_grad(self):
        self.optimizer.zero_grad()

    def __repr__(self):
        return f'<Optimizer type={type(self.optimizer).__name__} lr={self.optimizer.param_groups[0]["lr"]}>'

class FiberStruct:
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields
    def __call__(self, *args):
        data = {}
        for i, f in enumerate(self.fields):
            data[f] = args[i] if i < len(args) else None
        return FiberStructInstance(self, data)
    def __repr__(self): return f"<struct {self.name}>"

class FiberStructInstance:
    def __init__(self, struct_def, data):
        self._struct = struct_def
        self._data = data
    def get(self, name):
        if name in self._data: return self._data[name]
        raise KeyError(name)
    def set(self, name, value):
        self._data[name] = value
    def __repr__(self):
        fields_str = ", ".join(f"{k}={v}" for k, v in self._data.items())
        return f"{self._struct.name}({fields_str})"

class FiberEnum:
    def __init__(self, name, members):
        self.name = name
        self.members = {}
        for m in members:
            self.members[m] = FiberEnumItem(self, m)
    def get(self, name):
        if name in self.members: return self.members[name]
        raise KeyError(name)
    def __repr__(self): return f"<enum {self.name}>"

class FiberEnumItem:
    def __init__(self, enum_def, name):
        self.enum = enum_def
        self.name = name
    def __eq__(self, other):
        return isinstance(other, FiberEnumItem) and self.enum == other.enum and self.name == other.name
    def __repr__(self): return f"{self.enum.name}.{self.name}"