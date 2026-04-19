# AST node classes

class Node:
    pass

class Program(Node):
    def __init__(self, stmts, filename=None):
        self.stmts = stmts
        self.filename = filename

class Number(Node):
    def __init__(self, value):
        self.value = value

class String(Node):
    def __init__(self, value):
        self.value = value

class Boolean(Node):
    def __init__(self, value):
        self.value = value

class VarDecl(Node):
    def __init__(self, name):
        self.name = name

class VarAssign(Node):
    def __init__(self, name, expr, const=False, final=False, static=False, declare=False):
        self.name = name
        self.expr = expr
        self.const = const
        self.final = final
        self.static = static
        self.declare = declare

class VarRef(Node):
    def __init__(self, name):
        self.name = name

class Print(Node):
    def __init__(self, expr):
        self.expr = expr

class FuncDef(Node):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class Return(Node):
    def __init__(self, expr=None):
        self.expr = expr

class ClassDef(Node):
    def __init__(self, name, body, parent=None):
        self.name = name
        self.body = body
        self.parent = parent

class Method(Node):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class If(Node):
    def __init__(self, cond, then_branch, else_branch=None):
        self.cond = cond
        self.then_branch = then_branch
        self.else_branch = else_branch

class While(Node):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

class For(Node):
    def __init__(self, var, start, end, step, body):
        self.var = var
        self.start = start
        self.end = end
        self.step = step
        self.body = body

class ForIn(Node):
    def __init__(self, var, iterable, body, step=1):
        self.var = var
        self.iterable = iterable
        self.body = body
        self.step = step

class Break(Node):
    pass

class Continue(Node):
    pass

class Pass(Node):
    pass

class MemberAccess(Node):
    def __init__(self, obj, name):
        self.obj = obj
        self.name = name

class MemberAssign(Node):
    def __init__(self, obj, name, expr):
        self.obj = obj
        self.name = name
        self.expr = expr

class Call(Node):
    def __init__(self, callee, args):
        self.callee = callee
        self.args = args

class BinOp(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnaryOp(Node):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

class Index(Node):
    def __init__(self, obj, index):
        self.obj = obj
        self.index = index

class IndexAssign(Node):
    def __init__(self, obj, index, value):
        self.obj = obj
        self.index = index
        self.value = value

class ListLiteral(Node):
    def __init__(self, elements):
        self.elements = elements

class DictLiteral(Node):
    def __init__(self, pairs):
        self.pairs = pairs

class StructDef(Node):
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields

class EnumDef(Node):
    def __init__(self, name, values):
        self.name = name
        self.values = values

class TryCatchFinally(Node):
    def __init__(self, try_block, catch_var=None, catch_block=None, finally_block=None):
        self.try_block = try_block
        self.catch_var = catch_var
        self.catch_block = catch_block
        self.finally_block = finally_block

class Throw(Node):
    def __init__(self, expr):
        self.expr = expr

class Assert(Node):
    def __init__(self, cond, message=None):
        self.cond = cond
        self.message = message

class Import(Node):
    def __init__(self, module_name, alias=None):
        self.module_name = module_name
        self.alias = alias

class ImportFrom(Node):
    def __init__(self, module_name, names, import_all=False):
        self.module_name = module_name
        self.names = names
        self.import_all = import_all
