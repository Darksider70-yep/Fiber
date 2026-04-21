from .ast_nodes import *
from .objects import FiberClass, FiberInstance, FiberFunction, ReturnSignal, FiberSymbolic, FiberTensor, FiberOptimizer, FiberStruct, FiberStructInstance, FiberEnum
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
from . import compiler
import codecs
import sympy as sp


class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass

MODULE_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.module_cache = {}
        self.exec_dir_stack = [os.getcwd()]
        self.version = "4.0.1-emerald"
        
        # -----------------------------
        # Core & Versioning
        # -----------------------------
        self.global_env.set_local("fiber_version", self.version)
        self.global_env.set_local('print', print)
        self.global_env.set_local('None', None)
        self.global_env.set_local('input', lambda prompt="": input(prompt))
        self.global_env.set_local('int', lambda x: int(float(x)) if str(x).replace('.', '', 1).isdigit() else (_ for _ in ()).throw(FiberRuntimeError(f"Cannot convert {x} to int")))
        self.global_env.set_local('float', lambda x: float(x))
        self.global_env.set_local('str', lambda x: str(x))
        self.global_env.set_local('len', lambda x: len(x))
        self.global_env.set_local('append', lambda arr, val: (arr.append(val), arr)[1])
        self.global_env.set_local('range', lambda start, end=None, step=None: list(range(int(start), int(end) if end is not None else int(start), int(step) if step is not None else 1)) if end is not None else list(range(int(start))))
        self.global_env.set_local('write_raw', lambda x: sys.stdout.write(str(x)) or sys.stdout.flush())
        self.global_env.set_local('dict_keys', lambda d: list(d.keys()) if isinstance(d, dict) else [])

        def fiber_help(obj=None):
            if obj is None:
                print(f"🌿 Fiber v{self.version} Help")
                print("Available Globals:")
                keys = sorted([k for k in self.global_env.keys() if not k.startswith('_')])
                for i in range(0, len(keys), 4):
                    print("  ".join(f"{k:<15}" for k in keys[i:i+4]))
                print("\nUse help(name) for specific details (experimental).")
            else:
                print(f"Help for {obj}: {type(obj).__name__}")
        self.global_env.set_local('help', fiber_help)

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
        # Logical Builtins
        # -----------------------------
        self.global_env.set_local('logic_implies', lambda a, b: FiberSymbolic(AIBridge.implies(a.expr if isinstance(a, FiberSymbolic) else a, b.expr if isinstance(b, FiberSymbolic) else b)))
        self.global_env.set_local('logic_equiv', lambda a, b: FiberSymbolic(AIBridge.equivalent(a.expr if isinstance(a, FiberSymbolic) else a, b.expr if isinstance(b, FiberSymbolic) else b)))
        self.global_env.set_local('logic_cnf', lambda e: FiberSymbolic(AIBridge.to_cnf(e.expr if isinstance(e, FiberSymbolic) else e)))
        self.global_env.set_local('logic_dnf', lambda e: FiberSymbolic(AIBridge.to_dnf(e.expr if isinstance(e, FiberSymbolic) else e)))
        self.global_env.set_local('logic_sat', lambda e: AIBridge.satisfiable(e.expr if isinstance(e, FiberSymbolic) else e))
        self.global_env.set_local('logic_symbols', lambda e: AIBridge.get_symbols(e.expr if isinstance(e, FiberSymbolic) else e))
        self.global_env.set_local('logic_to_loss', lambda e, m, n="product": AIBridge.logic_to_loss(e.expr if isinstance(e, FiberSymbolic) else e, m, n))

        # -----------------------------
        # Neural Engine Builtins
        # -----------------------------
        self.global_env.set_local('tensor', lambda d, grad=False: FiberTensor(AIBridge.to_tensor(d, grad), grad))
        self.global_env.set_local('matmul', lambda a, b: FiberTensor(AIBridge.matmul(a.data if isinstance(a, FiberTensor) else a, b.data if isinstance(b, FiberTensor) else b)))
        self.global_env.set_local('relu', lambda t: FiberTensor(AIBridge.relu(t.data if isinstance(t, FiberTensor) else t)))
        self.global_env.set_local('sigmoid', lambda t: FiberTensor(AIBridge.sigmoid(t.data if isinstance(t, FiberTensor) else t)))
        self.global_env.set_local('mse_loss', lambda p, t: FiberTensor(AIBridge.mse_loss(p.data if isinstance(p, FiberTensor) else p, t.data if isinstance(t, FiberTensor) else t)))
        self.global_env.set_local('randn', lambda d: FiberTensor(AIBridge.randn(d)))
        self.global_env.set_local('rand', lambda d: FiberTensor(AIBridge.rand(d)))
        self.global_env.set_local('conv2d', lambda i, w, b=None, s=1, p=0: FiberTensor(AIBridge.conv2d(i.data if isinstance(i, FiberTensor) else i, w.data if isinstance(w, FiberTensor) else w, b.data if isinstance(b, FiberTensor) else b, s, p)))
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

        # -----------------------------
        # File System & OS Builtins
        # -----------------------------
        import json
        import subprocess
        import time

        def fs_read(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        
        def fs_write(path, content):
            with open(path, "w", encoding="utf-8") as f:
                f.write(str(content))
        
        def fs_append(path, content):
            with open(path, "a", encoding="utf-8") as f:
                f.write(str(content))
        
        self.global_env.set_local("fs_read", fs_read)
        self.global_env.set_local("fs_write", fs_write)
        self.global_env.set_local("fs_append", fs_append)
        self.global_env.set_local("fs_exists", lambda p: os.path.exists(p))
        self.global_env.set_local("os_env", lambda k: os.getenv(k))
        self.global_env.set_local("os_exec", lambda c: subprocess.check_output(c, shell=True).decode())
        self.global_env.set_local("os_sleep", lambda ms: time.sleep(ms / 1000.0))
        self.global_env.set_local("time_now", lambda: time.time())
        
        # Compiler Support
        def lib_compile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    source = f.read()
                tokens = tokenize(source)
                p = Parser(tokens, filename=path)
                ast = p.parse()
                binary = compiler.compile_to_binary(ast)
                out_name = os.path.splitext(path)[0] + ".fibc"
                with open(out_name, "wb") as f:
                    f.write(binary)
                return out_name
            except Exception as e:
                raise FiberRuntimeError(f"Compilation failed: {e}")
        
        self.global_env.set_local("sys_compile", lib_compile)
        
        # JSON Support
        self.global_env.set_local("json_parse", lambda s: json.loads(s))
        self.global_env.set_local("json_str", lambda o: json.dumps(o, indent=4))
        
        # -----------------------------
        # CSV Support
        # -----------------------------
        import csv
        def lib_csv_read(path, as_dict=False):
            with open(path, "r", encoding="utf-8") as f:
                if as_dict:
                    return list(csv.DictReader(f))
                return list(csv.reader(f))
        
        def lib_csv_write(path, rows):
            with open(path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(rows)
        
        self.global_env.set_local("csv_read_native", lib_csv_read)
        self.global_env.set_local("csv_write_native", lib_csv_write)

        # -----------------------------
        # SQLite Support
        # -----------------------------
        import sqlite3
        def sql_connect(path):
            conn = sqlite3.connect(path)
            conn.row_factory = sqlite3.Row # Allows dict-like access
            return conn
        
        def sql_query(conn, query, params=None):
            cur = conn.cursor()
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            # Convert sqlite3.Row to Python dict
            return [dict(row) for row in cur.fetchall()]
        
        def sql_exec(conn, query, params=None):
            cur = conn.cursor()
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            conn.commit()
            return cur.rowcount
            
        self.global_env.set_local("sql_connect", sql_connect)
        self.global_env.set_local("sql_query", sql_query)
        self.global_env.set_local("sql_exec", sql_exec)
        self.global_env.set_local("sql_close", lambda c: c.close())

        # -----------------------------
        # Networking (Sync Only)
        # -----------------------------
        import requests
        
        def http_req(method, url, data=None, headers=None):
            try:
                res = requests.request(method.upper(), url, json=data, headers=headers, timeout=10)
                return {
                    "status": res.status_code,
                    "text": res.text,
                    "json": res.json() if "application/json" in res.headers.get("Content-Type", "") else None
                }
            except Exception as e:
                return {"status": -1, "error": str(e)}
        
        self.global_env.set_local("http_req", http_req)

        # -----------------------------
        # String & RegEx
        # -----------------------------
        import re
        self.global_env.set_local("str_split", lambda s, sep: s.split(sep))
        self.global_env.set_local("str_join", lambda l, sep: sep.join(str(x) for x in l))
        self.global_env.set_local("str_replace", lambda s, o, n: s.replace(o, n))
        self.global_env.set_local("str_trim", lambda s: s.strip())
        self.global_env.set_local("str_contains", lambda s, sub: sub in s)
        self.global_env.set_local("str_lower", lambda s: s.lower())
        self.global_env.set_local("str_upper", lambda s: s.upper())
        
        # List Statistics
        self.global_env.set_local("list_sum", lambda l: sum(float(x) for x in l))
        self.global_env.set_local("list_mean", lambda l: sum(float(x) for x in l) / len(l) if len(l) > 0 else 0)

        # -----------------------------
        # Math & Trigonometry
        # -----------------------------
        import math as pymath
        self.global_env.set_local("math_sin", lambda n: pymath.sin(n))
        self.global_env.set_local("math_cos", lambda n: pymath.cos(n))
        self.global_env.set_local("math_tan", lambda n: pymath.tan(n))
        self.global_env.set_local("math_asin", lambda n: pymath.asin(n))
        self.global_env.set_local("math_acos", lambda n: pymath.acos(n))
        self.global_env.set_local("math_atan", lambda n: pymath.atan(n))
        self.global_env.set_local("math_atan2", lambda y, x: pymath.atan2(y, x))
        self.global_env.set_local("math_ceil", lambda n: pymath.ceil(n))
        self.global_env.set_local("math_floor", lambda n: pymath.floor(n))
        self.global_env.set_local("math_round", lambda n, p=0: round(n, p))
        self.global_env.set_local("math_sqrt", lambda n: pymath.sqrt(n))
        self.global_env.set_local("math_exp", lambda n: pymath.exp(n))
        self.global_env.set_local("math_log", lambda n, b=pymath.e: pymath.log(n, b))
        self.global_env.set_local("math_log10", lambda n: pymath.log10(n))
        self.global_env.set_local("math_abs", lambda n: abs(n))
        
        # Mathematical Constants
        self.global_env.set_local("math_pi", pymath.pi)
        self.global_env.set_local("math_e", pymath.e)

        # -----------------------------
        # File System Management
        # -----------------------------
        self.global_env.set_local("fs_mkdir", lambda p: os.makedirs(p, exist_ok=True))
        self.global_env.set_local("fs_remove", lambda p: os.remove(p))
        self.global_env.set_local("fs_listdir", lambda p: os.listdir(p))
        self.global_env.set_local("fs_rename", lambda s, d: os.rename(s, d))
        self.global_env.set_local("fs_size", lambda p: os.path.getsize(p))
        self.global_env.set_local("fs_is_dir", lambda p: os.path.isdir(p))
        self.global_env.set_local("fs_is_file", lambda p: os.path.isfile(p))
        self.global_env.set_local("os_path_join", lambda *args: os.path.join(*args))
        self.global_env.set_local("os_path_split", lambda p: os.path.split(p))

        # -----------------------------
        # GUI Support (Tkinter)
        # -----------------------------
        import tkinter as tk
        from tkinter import messagebox
        
        self.gui_root = None
        
        def gui_init(title="Fiber Window", w=400, h=300):
            self.gui_root = tk.Tk()
            self.gui_root.title(title)
            self.gui_root.geometry(f"{w}x{h}")
            return self.gui_root
        
        def gui_label(text):
            if not self.gui_root: return
            lbl = tk.Label(self.gui_root, text=text)
            lbl.pack()
            return lbl
            
        def gui_button(text, func):
            if not self.gui_root: return
            def cmd():
                from .objects import FiberFunction
                if isinstance(func, FiberFunction):
                    try: self.exec_block(func.body, func.env)
                    except Exception as e: print(f"GUI Callback Error: {e}")
                elif callable(func): func()
            btn = tk.Button(self.gui_root, text=text, command=cmd)
            btn.pack()
            return btn

        def gui_entry():
            if not self.gui_root: return
            ent = tk.Entry(self.gui_root)
            ent.pack()
            return ent

        def gui_frame():
            if not self.gui_root: return
            frm = tk.Frame(self.gui_root)
            frm.pack()
            return frm

        def gui_text():
            if not self.gui_root: return
            txt = tk.Text(self.gui_root)
            txt.pack()
            return txt

        def gui_set_grid(widget, r, c):
            if not widget: return
            widget.pack_forget() # Remove from pack if it was there
            widget.grid(row=r, column=c)

        def gui_set_pack(widget, side="top"):
            if not widget: return
            widget.grid_forget() # Remove from grid if it was there
            widget.pack(side=side)

        def gui_get_val(widget):
            if hasattr(widget, "get"):
                if isinstance(widget, tk.Text): return widget.get("1.0", tk.END)
                return widget.get()
            return None

        def gui_loop():
            if self.gui_root:
                self.gui_root.mainloop()
                
        def gui_alert(title, msg):
            messagebox.showinfo(title, msg)

        self.global_env.set_local("gui_init", gui_init)
        self.global_env.set_local("gui_label", gui_label)
        self.global_env.set_local("gui_button", gui_button)
        self.global_env.set_local("gui_entry", gui_entry)
        self.global_env.set_local("gui_frame", gui_frame)
        self.global_env.set_local("gui_text", gui_text)
        self.global_env.set_local("gui_grid", gui_set_grid)
        self.global_env.set_local("gui_pack", gui_set_pack)
        self.global_env.set_local("gui_get", gui_get_val)
        self.global_env.set_local("gui_loop", gui_loop)
        self.global_env.set_local("gui_alert", gui_alert)

        # -----------------------------
        # LLM Support (Gemini)
        # -----------------------------
        def llm_prompt(prompt, api_key=None, system=None):
            if api_key is None:
                api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                return "Error: No GEMINI_API_KEY found in environment."
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            if system:
                payload["system_instruction"] = {"parts": [{"text": system}]}
                
            try:
                res = requests.post(url, json=payload, timeout=30)
                data = res.json()
                if "candidates" in data:
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                return f"Error: {data}"
            except Exception as e:
                return f"Request Error: {e}"

        self.global_env.set_local("llm_prompt_native", llm_prompt)

        # -----------------------------
        # Threading Support
        # -----------------------------
        import threading
        def thread_start(func, args=[]):
            def wrapper():
                from .objects import FiberFunction
                if isinstance(func, FiberFunction):
                    # Create call env
                    call_env = Environment(func.env)
                    for i, param in enumerate(func.params):
                        if i < len(args):
                            call_env.set_local(param, args[i])
                    self.exec_block(func.body, call_env)
                else:
                    func(*args)
            t = threading.Thread(target=wrapper, daemon=True)
            t.start()
            return t
            
        self.global_env.set_local("thread_run", thread_start)

        # -----------------------------
        # URL & Security
        # -----------------------------
        import urllib.parse
        import hashlib
        self.global_env.set_local("url_encode", lambda s: urllib.parse.quote(s))
        self.global_env.set_local("url_decode", lambda s: urllib.parse.unquote(s))
        self.global_env.set_local("hash_sha256", lambda s: hashlib.sha256(str(s).encode()).hexdigest())
        self.global_env.set_local("hash_md5", lambda s: hashlib.md5(str(s).encode()).hexdigest())
        
        # -----------------------------
        # Time Management
        # -----------------------------
        import datetime
        def ts_format(ts, fmt="%Y-%m-%d %H:%M:%S"):
            return datetime.datetime.fromtimestamp(ts).strftime(fmt)
        def ts_parse(s, fmt="%Y-%m-%d %H:%M:%S"):
            return datetime.datetime.strptime(s, fmt).timestamp()
            
        self.global_env.set_local("time_format", ts_format)
        self.global_env.set_local("time_parse", ts_parse)

        # -----------------------------
        # System Hardware
        # -----------------------------
        import platform
        import multiprocessing
        self.global_env.set_local("os_platform", lambda: platform.system())
        self.global_env.set_local("os_cpu_count", lambda: multiprocessing.cpu_count())
        self.global_env.set_local("regex_match", lambda p, s: bool(re.match(p, s)))
        self.global_env.set_local("regex_search", lambda p, s: bool(re.search(p, s)))
        self.global_env.set_local("regex_replace", lambda p, r, s: re.sub(p, r, s))

        # -----------------------------
        # Enhanced Random
        # -----------------------------
        import random
        self.global_env.set_local("rand_int", lambda a, b: random.randint(a, b))
        def vec_shuffle(l):
            random.shuffle(l)
            return l
        self.global_env.set_local("vec_shuffle", vec_shuffle)
        self.global_env.set_local("vec_choice", lambda l: random.choice(l))

    def _validate_module_name(self, module_name):
        if not MODULE_NAME_RE.match(module_name):
            raise FiberRuntimeError(f"Invalid module name '{module_name}'")

    def _find_module_file(self, module_name):
        self._validate_module_name(module_name)
        filename = f"{module_name}.fib"
        current_exec_dir = self.exec_dir_stack[-1] if self.exec_dir_stack else os.getcwd()
        search_paths = []
        
        # 📦 Handling Standalone Bundle (PyInstaller)
        if getattr(sys, 'frozen', False):
            search_paths.append(os.path.join(sys._MEIPASS, "lib"))
            search_paths.append(sys._MEIPASS)

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
                    methods[m.name] = FiberFunction(m.name, m.params, m.body, env, m.defaults)
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
            fn = FiberFunction(node.name, node.params, node.body, env, node.defaults)
            env.set_local(node.name, fn)
            return fn

        # StructDef
        if isinstance(node, StructDef):
            sd = FiberStruct(node.name, node.fields)
            env.set_local(node.name, sd)
            return sd

        # EnumDef
        if isinstance(node, EnumDef):
            ed = FiberEnum(node.name, node.values)
            env.set_local(node.name, ed)
            return ed

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

        # Match (Switch)
        if isinstance(node, Match):
            val = self.eval_expr(node.expr, env)
            for c in node.cases:
                p_val = self.eval_expr(c.pattern, env)
                if val == p_val:
                    return self.exec_block(c.body, Environment(env))
            if node.default_branch:
                return self.exec_block(node.default_branch, Environment(env))
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
            return codecs.decode(node.value, 'unicode_escape')
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
            if node.op == "TILDE":
                raw_v = v.expr if isinstance(v, FiberSymbolic) else (v.data if isinstance(v, FiberTensor) else v)
                res = ~raw_v
                if isinstance(res, torch.Tensor): 
                    return FiberTensor(res, requires_grad=v.data.requires_grad)
                if isinstance(res, sp.Basic):
                    return FiberSymbolic(res)
                return res

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
                elif node.op == "POWER": res = raw_l ** raw_r
                elif node.op == "AMP": res = raw_l & raw_r
                elif node.op == "PIPE": res = raw_l | raw_r
                elif node.op == "CARET": res = raw_l ^ raw_r
                elif node.op == "IMPLIES": res = raw_l >> raw_r
                
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
            if node.op == "POWER":
                return l ** r
            if node.op == "MOD":
                return l % r
            if node.op == "AMP":
                return l & r
            if node.op == "PIPE":
                return l | r
            if node.op == "CARET":
                return l ^ r
            if node.op == "IMPLIES":
                return l >> r
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

        if isinstance(node, Ternary):
            cond = bool(self.eval_expr(node.cond, env))
            if cond:
                return self.eval_expr(node.true_expr, env)
            else:
                return self.eval_expr(node.false_expr, env)

        if isinstance(node, ListLiteral):
            return [self.eval_expr(e, env) for e in node.elements]

        if isinstance(node, ListComprehension):
            iterable = self.eval_expr(node.iterable, env)
            results = []
            comp_env = Environment(env)
            for item in iterable:
                comp_env.set_local(node.var, item)
                if node.condition:
                    if not bool(self.eval_expr(node.condition, comp_env)):
                        continue
                results.append(self.eval_expr(node.expr, comp_env))
            return results

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
            # Special case for method calls on instances to handle 'this'
            callee = node.callee
            args = [self.eval_expr(a, env) for a in node.args]

            if isinstance(callee, MemberAccess):
                target = self.eval_expr(callee.obj, env)
                name = callee.name
                
                if isinstance(target, FiberInstance):
                    method = target.klass.find_method(name)
                    if method:
                        return method.call(self, args, this=target)
                    if name in target.fields and callable(target.fields[name]):
                        return target.fields[name](*args)
                    raise FiberNameError(f"Method {name} not found")

                if isinstance(target, dict):
                    member = target.get(name)
                    if isinstance(member, FiberClass):
                        inst = FiberInstance(member)
                        inst._interpreter = self
                        init_m = member.find_method("init")
                        if init_m: init_m.call(self, args, this=inst)
                        return inst
                    if isinstance(member, FiberFunction):
                        return member.call(self, args)
                    if callable(member):
                        return member(*args)
                    raise FiberNameError(f"Member {name} not callable on dict")

                # Native object methods
                attr = getattr(target, name, None)
                if callable(attr):
                    return attr(*args)
                raise FiberRuntimeError(f"Attribute {name} not callable on {type(target).__name__}")
            
            # Normal variable or expression call
            fn = self.eval_expr(callee, env)
            if isinstance(fn, FiberClass):
                inst = FiberInstance(fn)
                inst._interpreter = self
                init_m = fn.find_method("init")
                if init_m: init_m.call(self, args, this=inst)
                return inst
            if isinstance(fn, FiberStruct):
                return fn(*args)
            if isinstance(fn, FiberFunction):
                return fn.call(self, args)
            if callable(fn):
                return fn(*args)
            raise FiberRuntimeError("Target is not callable")


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

            if isinstance(obj, FiberStructInstance):
                try:
                    return obj.get(node.name)
                except KeyError:
                    raise FiberNameError(f"Field {node.name} not found in struct {obj._struct.name}")

            if isinstance(obj, FiberEnum):
                try:
                    return obj.get(node.name)
                except KeyError:
                    raise FiberNameError(f"Value {node.name} not found in enum {obj.name}")

            if isinstance(obj, dict):
                if node.name in obj:
                    return obj[node.name]
                raise FiberNameError(f"{node.name} not found on dict")
            # Support for FiberTensor & FiberOptimizer properties
            if isinstance(obj, (FiberTensor, FiberOptimizer)):
                return getattr(obj, node.name)
            raise FiberNameError(f"{node.name} not found")

        raise FiberRuntimeError(f"Unknown node in eval: {type(node)}")
