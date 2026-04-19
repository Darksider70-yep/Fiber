from .environment import Environment
from .ast_nodes import FuncDef
import numpy as np
import sympy as sp

class FiberFunction:
    def __init__(self, name, params, body, closure):
        self.name = name
        self.params = params
        self.body = body
        self.closure = closure
    def call(self, interpreter, args, this=None):
        env = Environment(parent=self.closure)
        # bind params
        for i, p in enumerate(self.params):
            env.set_local(p, args[i] if i < len(args) else None)
        if this is not None:
            env.set_local('this', this)
        # execute body
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
        self.methods = methods  # dict name -> FiberFunction
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
        # field first
        if name in self.fields:
            return self.fields[name]
        # then method bound
        m = self.klass.find_method(name)
        if m:
            # return a bound function wrapper
            def bound(*args):
                return m.call(self._interpreter, list(args), this=self)
            # attach meta for interpreter path
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
    def __init__(self, data):
        self.data = np.array(data)
    def __repr__(self):
        return f'Tensor({self.data})'
    def __str__(self):
        return str(self.data)
    def __getitem__(self, idx):
        return self.data[idx]
    def __setitem__(self, idx, val):
        self.data[idx] = val
    def __len__(self):
        return len(self.data)