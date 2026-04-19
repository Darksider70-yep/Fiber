from .ast_nodes import *
from .objects import FiberClass, FiberInstance, FiberFunction, ReturnSignal, FiberSymbolic, FiberTensor, FiberOptimizer
from .ai import AIBridge
from .environment import Environment
from .errors import FiberNameError, FiberRuntimeError
import os
import re
import sys
import torch
from .lexer import tokenize
from .parser import Parser
from .dsa import FiberStack, FiberQueue, FiberSet


class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass

MODULE_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.module_cache = {}
        self.exec_dir_stack = [os.getcwd()]

        # Builtins
        self.global_env.set_local('print', print)
        self.global_env.set_local('None', None)
        self.global_env.set_local('input', lambda prompt="": input(prompt))
        self.global_env.set_local('int', lambda x: int(float(x)) if str(x).replace('.', '', 1).isdigit() else (_ for _ in ()).throw(FiberRuntimeError(f"Cannot convert {x} to int")))
        self.global_env.set_local('float', lambda x: float(x))
        self.global_env.set_local('str', lambda x: str(x))
        self.global_env.set_local('len', lambda x: len(x))
        self.global_env.set_local('append', lambda arr, val: (arr.append(val), arr)[1])
        self.global_env.set_local('range', lambda start, end=None, step=None: list(range(int(start), int(end) if end is not None else int(start), int(step) if step is not None else 1)) if end is not None else list(range(int(start))))

        # -----------------------------
        # Native Data Structures (DSA)
        # -----------------------------
        self.global_env.set_local("Stack", FiberStack)
        self.global_env.set_local("Queue", FiberQueue)
        self.global_env.set_local("Set", FiberSet)

        # -----------------------------
        # AI & Symbolic Builtins
        # -----------------------------
        self.global_env.set_local('expr', lambda s: FiberSymbolic(AIBridge.parse_expr(s)))
        self.global_env.set_local('diff', lambda e, v: FiberSymbolic(AIBridge.differentiate(e.expr if isinstance(e, FiberSymbolic) else e, v)))
        self.global_env.set_local('simplify', lambda e: FiberSymbolic(AIBridge.simplify(e.expr if isinstance(e, FiberSymbolic) else e)))
        self.global_env.set_local('solve', lambda e, v: [FiberSymbolic(sol) for sol in AIBridge.solve(e.expr if isinstance(e, FiberSymbolic) else e, v)])
        self.global_env.set_local('subst', lambda e, m: AIBridge.subst(e.expr if isinstance(e, FiberSymbolic) else e, m))

        # -----------------------------
        # Neural Engine Builtins
        # -----------------------------
        self.global_env.set_local('tensor', lambda d, grad=False: FiberTensor(AIBridge.to_tensor(d, grad), grad))
        self.global_env.set_local('matmul', lambda a, b: FiberTensor(AIBridge.matmul(a.data if isinstance(a, FiberTensor) else a, b.data if isinstance(b, FiberTensor) else b)))
        self.global_env.set_local('relu', lambda t: FiberTensor(AIBridge.relu(t.data if isinstance(t, FiberTensor) else t)))
        self.global_env.set_local('sigmoid', lambda t: FiberTensor(AIBridge.sigmoid(t.data if isinstance(t, FiberTensor) else t)))
        self.global_env.set_local('mse_loss', lambda p, t: FiberTensor(AIBridge.mse_loss(p.data if isinstance(p, FiberTensor) else p, t.data if isinstance(t, FiberTensor) else t)))
        self.global_env.set_local('backward', lambda t: t.backward() if isinstance(t, FiberTensor) else None)
        self.global_env.set_local('grad', lambda t: t.grad if isinstance(t, FiberTensor) else None)
        self.global_env.set_local('zero_grad', lambda t: t.zero_grad() if isinstance(t, FiberTensor) else None)
        
        # Manual parameter update
        def manual_step(param, lr):
            if not isinstance(param, FiberTensor) or param.grad is None:
                return
            with torch.no_grad():
                param.data -= lr * param.grad.data
        self.global_env.set_local('optimize_step', manual_step)

        # High-Level Optimizer
        self.global_env.set_local('optimizer', lambda params, opt_type="sgd", lr=0.01: FiberOptimizer(params, opt_type, lr))

    def _validate_module_name(self, module_name):
        if not MODULE_NAME_RE.match(module_name):
            raise FiberRuntimeError(f"Invalid module name '{module_name}'")

    def _find_module_file(self, module_name):
        self._validate_module_name(module_name)
        filename = f"{module_name}.fib"
        current_exec_dir = self.exec_dir_stack[-1] if self.exec_dir_stack else os.getcwd()
        search_paths = []
        for candidate in (
            current_exec_dir,
            os.path.join(current_exec_dir, "lib"),
            os.getcwd(),
            os.path.join(os.getcwd(), "lib"),
            os.path.dirname(__file__),
        ):
            if candidate not in search_paths:
                search_paths.append(candidate)

        for path in search_paths:
            root = os.path.abspath(path)
            candidate = os.path.abspath(os.path.join(root, filename))
            try:
                if os.path.commonpath([candidate, root]) != root:
                    continue
            except ValueError:
                continue
            if os.path.isfile(candidate):
                return candidate

        raise FiberRuntimeError(f"Module '{module_name}' not found")

    def _load_module_symbols(self, module_name):
        cached = self.module_cache.get(module_name, "__missing__")
        if cached == "__loading__":
            raise FiberRuntimeError(f"Circular import detected for module '{module_name}'")
        if cached != "__missing__":
            return dict(cached)

        self.module_cache[module_name] = "__loading__"
        try:
            file_path = self._find_module_file(module_name)
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read().replace("\r\n", "\n").replace("\r", "\n")
            if not source.endswith("\n"):
                source += "\n"

            tokens = tokenize(source)
            module_ast = Parser(tokens, filename=file_path).parse()
            module_env = Environment(self.global_env)
            self.exec_dir_stack.append(os.path.dirname(file_path))
            try:
                self.exec_block(module_ast.stmts, module_env)
            finally:
                self.exec_dir_stack.pop()

            symbols = dict(module_env)
            self.module_cache[module_name] = dict(symbols)
            return symbols
        except Exception:
            if module_name in self.module_cache and self.module_cache[module_name] == "__loading__":
                del self.module_cache[module_name]
            raise

    def _find_env_containing(self, env, name):
        current = env
        while current is not None:
            if name in current:
                return current
            current = current.parent
        return None

    def interpret(self, program: Program):
        filename = getattr(program, "filename", None)
        if filename:
            exec_dir = os.path.dirname(os.path.abspath(filename))
        else:
            exec_dir = os.getcwd()
            if len(sys.argv) > 1:
                arg_path = os.path.abspath(sys.argv[1])
                if arg_path.lower().endswith(".fib"):
                    exec_dir = os.path.dirname(arg_path)

        self.exec_dir_stack.append(exec_dir)
        try:
            return self.exec_block(program.stmts, self.global_env)
        finally:
            self.exec_dir_stack.pop()

    def exec_block(self, stmts, env):
        last = None
        for s in stmts:
            try:
                res = self.exec_stmt(s, env)
                last = res
            except ReturnSignal as rs:
                raise rs
        return last

    def exec_stmt(self, node, env):
        if node is None:
            return None
        
        # -----------------------------
        # IMPORT SYSTEM
        # -----------------------------
        if isinstance(node, Import):
            symbols = self._load_module_symbols(node.module_name)
            alias = node.alias or node.module_name
            env.set_local(alias, dict(symbols))
            return None

        if isinstance(node, ImportFrom):
            symbols = self._load_module_symbols(node.module_name)

            if node.import_all:
                for name, value in symbols.items():
                    env.set_local(name, value)
            else:
                for name in node.names:
                    if name in symbols:
                        env.set_local(name, symbols[name])
                    else:
                        raise FiberRuntimeError(f"Name '{name}' not found in module '{node.module_name}'")
            return None

        # Print
        if isinstance(node, Print):
            val = self.eval_expr(node.expr, env)
            try:
                func = env.get('print')
            except KeyError:
                func = self.global_env.get('print')
            if callable(func):
                func(val)
            else:
                print(val)
            return None

        # VarDecl
        if isinstance(node, VarDecl):
            env.set_local(node.name, None)
            return None

        # VarAssign
        if isinstance(node, VarAssign):
            val = self.eval_expr(node.expr, env)

            if node.const:
                target_env = env if node.declare else self.global_env
                if node.name in target_env:
                    raise FiberRuntimeError(f"Cannot redeclare '{node.name}' as constant")
                if node.name in getattr(target_env, 'constants', set()):
                    raise FiberRuntimeError(f"Cannot redefine constant '{node.name}'")
                target_env.set_local(node.name, val)
                target_env.constants = getattr(target_env, 'constants', set())
                target_env.constants.add(node.name)
                return val

            if node.static:
                self.global_env.set_local(node.name, val)
                self.global_env.statics = getattr(self.global_env, 'statics', set())
                self.global_env.statics.add(node.name)
                return val

            if node.final:
                if node.name in env:
                    raise FiberRuntimeError(f"Cannot redeclare final variable '{node.name}'")
                if node.name in getattr(env, 'finals', set()):
                    raise FiberRuntimeError(f"Final variable '{node.name}' cannot be reassigned")
                env.set_local(node.name, val)
                env.finals = getattr(env, 'finals', set())
                env.finals.add(node.name)
                return val

            if node.declare:
                env.set_local(node.name, val)
                return val

            owner_env = self._find_env_containing(env, node.name)
            if owner_env is not None:
                if node.name in getattr(owner_env, 'constants', set()):
                    raise FiberRuntimeError(f"Cannot reassign constant '{node.name}'")
                if node.name in getattr(owner_env, 'finals', set()):
                    raise FiberRuntimeError(f"Final variable '{node.name}' cannot be reassigned")

            env.set_upwards(node.name, val)
            return val

        # StructDef
        if isinstance(node, StructDef):
            def constructor(*args):
                if len(args) != len(node.fields):
                    raise FiberRuntimeError(f"{node.name} expects {len(node.fields)} arguments, got {len(args)}")
                d = {fname: args[i] for i, fname in enumerate(node.fields)}
                d['_struct_type'] = node.name
                return d
            env.set_local(node.name, constructor)
            return constructor

        # EnumDef
        if isinstance(node, EnumDef):
            enum_obj = {}
            for v in node.values:
                enum_obj[v] = f"{node.name}.{v}"
            env.set_local(node.name, enum_obj)
            return enum_obj

        # ClassDef
        if isinstance(node, ClassDef):
            methods = {}
            for m in node.body:
                if isinstance(m, Method):
                    methods[m.name] = FiberFunction(m.name, m.params, m.body, env)
            parent = None
            if node.parent:
                try:
                    parent = env.get(node.parent)
                except KeyError:
                    parent = None
                if not isinstance(parent, FiberClass):
                    parent = None
            klass = FiberClass(node.name, methods, parent)
            env.set_local(node.name, klass)
            return klass

        # FuncDef
        if isinstance(node, FuncDef):
            fn = FiberFunction(node.name, node.params, node.body, env)
            env.set_local(node.name, fn)
            return fn

        # Return
        if isinstance(node, Return):
            val = self.eval_expr(node.expr, env) if node.expr else None
            raise ReturnSignal(val)

        # MemberAssign (dict/instance)
        if isinstance(node, MemberAssign):
            target = self.eval_expr(node.obj, env)
            value = self.eval_expr(node.expr, env)
            if isinstance(target, FiberInstance):
                target.set(node.name, value); return value
            if isinstance(target, dict):
                target[node.name] = value; return value
            raise FiberRuntimeError("Cannot assign to non-instance")

        # Try/Catch/Finally
        if isinstance(node, TryCatchFinally):
            try:
                self.exec_block(node.try_block, Environment(env))
            except (ReturnSignal, BreakSignal, ContinueSignal):
                if node.finally_block:
                    self.exec_block(node.finally_block, Environment(env))
                raise
            except Exception as e:
                if node.catch_block is None:
                    if node.finally_block:
                        self.exec_block(node.finally_block, Environment(env))
                    raise

                catch_env = Environment(env)
                if node.catch_var:
                    catch_env.set_local(node.catch_var, str(e))

                try:
                    self.exec_block(node.catch_block, catch_env)
                except (ReturnSignal, BreakSignal, ContinueSignal):
                    if node.finally_block:
                        self.exec_block(node.finally_block, Environment(env))
                    raise
                except Exception:
                    if node.finally_block:
                        self.exec_block(node.finally_block, Environment(env))
                    raise

                if node.finally_block:
                    self.exec_block(node.finally_block, Environment(env))
                return None

            if node.finally_block:
                self.exec_block(node.finally_block, Environment(env))
            return None

        # Throw
        if isinstance(node, Throw):
            v = self.eval_expr(node.expr, env)
            raise FiberRuntimeError(str(v))

        # Assert
        if isinstance(node, Assert):
            cond_val = self.eval_expr(node.cond, env)
            if not bool(cond_val):
                msg = self.eval_expr(node.message, env) if node.message else "Assertion failed"
                raise FiberRuntimeError(str(msg))
            return None

        # If
        if isinstance(node, If):
            cond_val = bool(self.eval_expr(node.cond, env))
            if cond_val:
                return self.exec_block(node.then_branch, Environment(env))
            if node.else_branch is None:
                return None
            if isinstance(node.else_branch, If):
                return self.exec_stmt(node.else_branch, env)
            return self.exec_block(node.else_branch, Environment(env))

        # Pass
        if isinstance(node, Pass):
            return None

        # While
        if isinstance(node, While):
            result = None
            while bool(self.eval_expr(node.cond, env)):
                try:
                    result = self.exec_block(node.body, Environment(env))
                except BreakSignal:
                    break
                except ContinueSignal:
                    continue
            return result

        # For
        if isinstance(node, For):
            start_val = self.eval_expr(node.start, env)
            end_val = self.eval_expr(node.end, env)
            step_val = self.eval_expr(node.step, env)
            if not isinstance(step_val, (int, float)):
                raise FiberRuntimeError("Step value must be a number")
            if step_val == 0:
                raise FiberRuntimeError("Step value cannot be zero")
            i = start_val
            env.set_local(node.var, i)
            while (step_val > 0 and i <= end_val) or (step_val < 0 and i >= end_val):
                env.set_upwards(node.var, i)
                try:
                    self.exec_block(node.body, Environment(env))
                except BreakSignal:
                    break
                except ContinueSignal:
                    i += step_val; continue
                i += step_val
            return None

        # ForIn
        if isinstance(node, ForIn):
            iterable_val = self.eval_expr(node.iterable, env)
            if not hasattr(iterable_val, "__iter__"):
                raise FiberRuntimeError(f"Object {iterable_val} not iterable")
            step_val = self.eval_expr(node.step, env) if hasattr(node, "step") else 1
            if not isinstance(step_val, (int, float)):
                raise FiberRuntimeError("Step value must be a number")
            if isinstance(step_val, bool) or int(step_val) != step_val:
                raise FiberRuntimeError("Step value must be a whole number")
            step_int = int(step_val)
            if step_int <= 0:
                raise FiberRuntimeError("Step value must be greater than zero")
            env.set_local(node.var, None)
            for i, item in enumerate(iterable_val):
                if i % step_int != 0:
                    continue
                env.set_upwards(node.var, item)
                try:
                    self.exec_block(node.body, Environment(env))
                except BreakSignal:
                    break
                except ContinueSignal:
                    continue
            return None

        # Break/Continue
        if isinstance(node, Break):
            raise BreakSignal()
        if isinstance(node, Continue):
            raise ContinueSignal()

        # IndexAssign
        if isinstance(node, IndexAssign):
            obj = self.eval_expr(node.obj, env)
            idx = self.eval_expr(node.index, env)
            val = self.eval_expr(node.value, env)
            if not hasattr(obj, "__setitem__"):
                raise FiberRuntimeError("Object not subscript-assignable")
            obj[idx] = val
            return val

        return self.eval_expr(node, env)

    # Expression evaluation
    def eval_expr(self, node, env):
        if node is None:
            return None
        if isinstance(node, Number):
            return node.value
        if isinstance(node, String):
            return node.value
        if isinstance(node, Boolean):
            return node.value

        if isinstance(node, VarRef):
            try:
                return env.get(node.name)
            except KeyError:
                try:
                    return self.global_env.get(node.name)
                except Exception:
                    raise FiberNameError(f"Undefined variable '{node.name}'")

        if isinstance(node, UnaryOp):
            v = self.eval_expr(node.expr, env)
            if node.op == "MINUS":
                return -float(v) if isinstance(v, (int, float, str)) else -v
            if node.op == "NOT":
                return not bool(v)

        if isinstance(node, BinOp):
            if node.op == "AND":
                l = self.eval_expr(node.left, env)
                if not bool(l):
                    return False
                return bool(self.eval_expr(node.right, env))
            
            if node.op == "OR":
                l = self.eval_expr(node.left, env)
                if bool(l):
                    return True
                return bool(self.eval_expr(node.right, env))

            l = self.eval_expr(node.left, env)
            r = self.eval_expr(node.right, env)

            # --- AI: Symbolic & Tensor Overloading ---
            if isinstance(l, (FiberTensor, FiberSymbolic)) or isinstance(r, (FiberTensor, FiberSymbolic)):
                raw_l = l.data if isinstance(l, FiberTensor) else (l.expr if isinstance(l, FiberSymbolic) else l)
                raw_r = r.data if isinstance(r, FiberTensor) else (r.expr if isinstance(r, FiberSymbolic) else r)
                
                res = None
                if node.op == "PLUS": res = raw_l + raw_r
                elif node.op == "MINUS": res = raw_l - raw_r
                elif node.op == "MUL": res = raw_l * raw_r
                elif node.op == "DIV": res = raw_l / raw_r
                
                if res is not None:
                    if isinstance(res, torch.Tensor):
                        was_grad = (isinstance(l, FiberTensor) and l.data.requires_grad) or \
                                   (isinstance(r, FiberTensor) and r.data.requires_grad)
                        return FiberTensor(res, requires_grad=was_grad)
                    return FiberSymbolic(res)

            def try_number(v):
                try:
                    if isinstance(v, bool):
                        return v
                    return float(v) if "." in str(v) else int(v)
                except Exception:
                    return v

            if isinstance(l, str) or isinstance(r, str):
                l, r = try_number(l), try_number(r)

            if node.op == "PLUS":
                if isinstance(l, str) or isinstance(r, str):
                    return str(l) + str(r)
                return l + r
            if node.op == "MINUS":
                return l - r
            if node.op == "MUL":
                if isinstance(l, str) and isinstance(r, int):
                    return l * r
                if isinstance(r, str) and isinstance(l, int):
                    return r * l
                return l * r
            if node.op == "DIV":
                return l / r
            if node.op == "MOD":
                return l % r
            if node.op == "EQ":
                return l == r
            if node.op == "NEQ":
                return l != r
            if node.op == "LT":
                return l < r
            if node.op == "GT":
                return l > r
            if node.op == "LTE":
                return l <= r
            if node.op == "GTE":
                return l >= r

        if isinstance(node, ListLiteral):
            return [self.eval_expr(e, env) for e in node.elements]

        if isinstance(node, DictLiteral):
            return {self.eval_expr(k, env): self.eval_expr(v, env) for k, v in node.pairs}

        if isinstance(node, Index):
            obj = self.eval_expr(node.obj, env)
            idx = self.eval_expr(node.index, env)
            if isinstance(obj, dict):
                try:
                    return obj[idx]
                except KeyError:
                    return None
            
            if not hasattr(obj, "__getitem__"):
                raise FiberRuntimeError(f"Object of type {type(obj).__name__} not indexable")
            res = obj[idx]
            if isinstance(obj, FiberTensor) and not isinstance(res, FiberTensor):
                return FiberTensor(res, requires_grad=obj.data.requires_grad)
            return res

        if isinstance(node, Call):
            callee = node.callee
            if isinstance(callee, VarRef):
                try:
                    fn = env.get(callee.name)
                except KeyError:
                    try:
                        fn = self.global_env.get(callee.name)
                    except Exception:
                        raise FiberRuntimeError("Not callable")
                args = [self.eval_expr(a, env) for a in node.args]
                if isinstance(fn, FiberClass):
                    inst = FiberInstance(fn)
                    inst._interpreter = self
                    init_m = fn.find_method("init")
                    if init_m:
                        init_m.call(self, args, this=inst)
                    return inst
                if isinstance(fn, FiberFunction):
                    return fn.call(self, args)
                if callable(fn):
                    return fn(*args)
                raise FiberRuntimeError("Not callable")

            if isinstance(callee, MemberAccess):
                target = self.eval_expr(callee.obj, env)
                name = callee.name
                args = [self.eval_expr(a, env) for a in node.args]

                if isinstance(target, FiberInstance):
                    method = target.klass.find_method(name)
                    if method:
                        return method.call(self, args, this=target)
                    if name in target.fields and callable(target.fields[name]):
                        return target.fields[name](*args)
                    raise FiberNameError(f"Method {name} not found")

                if isinstance(target, dict):
                    member = target.get(name)
                    if callable(member):
                        return member(*args)
                    raise FiberNameError(f"Member {name} not callable on dict")

                # ✅ Native runtime object (DSA, Tensors, Optimizers)
                attr = getattr(target, name, None)
                if callable(attr):
                    return attr(*args)

                raise FiberRuntimeError("Member call on unsupported object")

        if isinstance(node, MemberAccess):
            obj = self.eval_expr(node.obj, env)
            if isinstance(obj, FiberInstance):
                if node.name in obj.fields:
                    return obj.fields[node.name]
                m = obj.klass.find_method(node.name)
                if m:
                    def bound(*args):
                        return m.call(self, list(args), this=obj)
                    return bound
                raise FiberNameError(f"{node.name} not found on instance")
            if isinstance(obj, dict):
                if node.name in obj:
                    return obj[node.name]
                raise FiberNameError(f"{node.name} not found on dict")
            # Support for FiberTensor & FiberOptimizer properties
            if isinstance(obj, (FiberTensor, FiberOptimizer)):
                return getattr(obj, node.name)
            raise FiberNameError(f"{node.name} not found")

        raise FiberRuntimeError(f"Unknown node in eval: {type(node)}")
