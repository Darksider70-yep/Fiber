from .ast_nodes import *
from .objects import FiberClass, FiberInstance, FiberFunction, ReturnSignal
from .environment import Environment
from .errors import FiberNameError, FiberRuntimeError
import os
from .lexer import tokenize
from .parser import Parser
from .dsa import FiberStack, FiberQueue, FiberSet


class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass

class Interpreter:
    def __init__(self):
        self.global_env = Environment()

        # Builtins
        self.global_env.set_local('print', print)
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

    def interpret(self, program: Program):
        return self.exec_block(program.stmts, self.global_env)

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
            module_name = node.module_name
            alias = node.alias or module_name
            filename = f"{module_name}.fib"

            search_paths = [
                os.getcwd(),
                os.path.join(os.getcwd(), "lib"),
                os.path.dirname(__file__)
            ]

            file_path = None
            for path in search_paths:
                candidate = os.path.join(path, filename)
                if os.path.exists(candidate):
                    file_path = candidate
                    break

            if not file_path:
                raise FiberRuntimeError(f"Module '{module_name}' not found")

            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read().replace("\r\n", "\n").replace("\r", "\n").strip() + "\n"

            # tokenize, parse, execute module in a new environment
            tokens = tokenize(source)
            p = Parser(tokens, filename=file_path)
            module_ast = p.parse()
            module_env = Environment(self.global_env)
            self.exec_block(module_ast.stmts, module_env)

            # store module's environment in current environment
            env.set_local(alias, module_env.store)
            return None

        if isinstance(node, ImportFrom):
            module_name = node.module_name
            filename = f"{module_name}.fib"

            search_paths = [
                os.getcwd(),
                os.path.join(os.getcwd(), "lib"),
                os.path.dirname(__file__)
            ]

            file_path = None
            for path in search_paths:
                candidate = os.path.join(path, filename)
                if os.path.exists(candidate):
                    file_path = candidate
                    break

            if not file_path:
                raise FiberRuntimeError(f"Module '{module_name}' not found")

            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read().replace("\r\n", "\n").replace("\r", "\n").strip() + "\n"

            tokens = tokenize(source)
            p = Parser(tokens, filename=file_path)
            module_ast = p.parse()
            module_env = Environment(self.global_env)
            self.exec_block(module_ast.stmts, module_env)

            if node.import_all:
                for name, value in module_env.store.items():
                    env.set_local(name, value)
            else:
                for name in node.names:
                    if name in module_env.store:
                        env.set_local(name, module_env.store[name])
                    else:
                        raise FiberRuntimeError(f"Name '{name}' not found in module '{module_name}'")
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
                if node.name in getattr(self.global_env, 'constants', set()):
                    raise FiberRuntimeError(f"Cannot redefine constant '{node.name}'")
                self.global_env.set_local(node.name, val)
                self.global_env.constants = getattr(self.global_env, 'constants', set())
                self.global_env.constants.add(node.name)
                return val

            if node.static:
                self.global_env.set_local(node.name, val)
                self.global_env.statics = getattr(self.global_env, 'statics', set())
                self.global_env.statics.add(node.name)
                return val

            if node.final:
                if node.name in getattr(env, 'finals', set()):
                    raise FiberRuntimeError(f"Final variable '{node.name}' cannot be reassigned")
                env.set_local(node.name, val)
                env.finals = getattr(env, 'finals', set())
                env.finals.add(node.name)
                return val

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
            # execute try block
            try:
                self.exec_block(node.try_block, Environment(env))
            except Exception as e:
                # if a catch block exists, run it with the exception value bound
                if node.catch_block is not None:
                    catch_env = Environment(env)
                    if node.catch_var:
                        # bind the exception object (stringified) to catch_var
                        catch_env.set_local(node.catch_var, str(e))
                    try:
                        self.exec_block(node.catch_block, catch_env)
                    except ReturnSignal:
                        raise
                    except Exception as inner_exc:
                        # if catch raises, propagate unless finally handles it
                        exc_to_propagate = inner_exc
                        # run finally then re-raise
                        if node.finally_block:
                            try:
                                self.exec_block(node.finally_block, Environment(env))
                            except Exception as fin_e:
                                raise fin_e
                        raise exc_to_propagate
                else:
                    # no catch — finally runs and then re-raise
                    if node.finally_block:
                        try:
                            self.exec_block(node.finally_block, Environment(env))
                        except Exception as fin_e:
                            raise fin_e
                    raise
            else:
                # normal completion — run finally if present
                if node.finally_block:
                    self.exec_block(node.finally_block, Environment(env))
            return None

        # Throw
        if isinstance(node, Throw):
            v = self.eval_expr(node.expr, env)
            # convert to string for runtime error message
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
            elif node.else_branch:
                if isinstance(node.else_branch, list) and isinstance(node.else_branch[0], If):
                    return self.exec_stmt(node.else_branch[0], env)
                return self.exec_block(node.else_branch, Environment(env))
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
            for i, item in enumerate(iterable_val):
                if i % int(step_val) != 0:
                    continue
                loop_env = Environment(env)
                loop_env.set_upwards(node.var, item)
                try:
                    self.exec_block(node.body, loop_env)
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

    # Expression evaluation (same robust conversions as before)
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
            l = self.eval_expr(node.left, env)
            r = self.eval_expr(node.right, env)

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
            if node.op == "AND":
                return bool(l) and bool(r)
            if node.op == "OR":
                return bool(l) or bool(r)

        if isinstance(node, ListLiteral):
            return [self.eval_expr(e, env) for e in node.elements]

        if isinstance(node, Index):
            obj = self.eval_expr(node.obj, env)
            idx = self.eval_expr(node.index, env)
            if not hasattr(obj, "__getitem__"):
                raise FiberRuntimeError(f"Object of type {type(obj).__name__} not indexable")
            return obj[idx]

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

                # Fiber class instance
                if isinstance(target, FiberInstance):
                    method = target.klass.find_method(name)
                    if method:
                        return method.call(self, args, this=target)
                    if name in target.fields and callable(target.fields[name]):
                        return target.fields[name](*args)
                    raise FiberNameError(f"Method {name} not found")

                # Dict member
                if isinstance(target, dict):
                    member = target.get(name)
                    if callable(member):
                        return member(*args)
                    raise FiberNameError(f"Member {name} not callable on dict")

                # ✅ Native runtime object (DSA, future VM objects)
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
            raise FiberNameError(f"{node.name} not found")

        raise FiberRuntimeError(f"Unknown node in eval: {type(node)}")
