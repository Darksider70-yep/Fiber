import sys
import os
from fiber import repl, interpreter, parser, lexer, errors, compiler


def run_file(filename, compile_only=False):
    try:
        with open(filename, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except OSError as e:
        print(f"Error: Could not read '{filename}': {e}")
        sys.exit(1)

    ast = None
    is_binary = data.startswith(compiler.MAGIC)

    if is_binary:
        if compile_only:
            print(f"Error: '{filename}' is already a compiled Fiber binary.")
            sys.exit(1)
        try:
            ast = compiler.load_from_binary(data)
        except Exception as e:
            print(f"Error: Fail to load Fiber binary '{filename}': {e}")
            sys.exit(1)
    else:
        # Treat as source
        try:
            source = data.decode("utf-8")
            tokens = lexer.tokenize(source)
            p = parser.Parser(tokens, filename=filename)
            ast = p.parse()
        except UnicodeDecodeError:
            print(f"Error: '{filename}' contains invalid characters (not UTF-8).")
            sys.exit(1)
        except errors.FiberSyntaxError as e:
            print(e)
            sys.exit(1)

    if compile_only:
        # Pre-compiled files get .fibc extension
        base = os.path.splitext(filename)[0]
        out_name = base + ".fibc"
        try:
            binary = compiler.compile_to_binary(ast)
            with open(out_name, "wb") as f:
                f.write(binary)
            print(f"Successfully compiled '{filename}' to '{out_name}'")
            return
        except Exception as e:
            print(f"Error: Compilation failed: {e}")
            sys.exit(1)

    # -----------------------------
    # EXECUTION
    # -----------------------------
    try:
        interp = interpreter.Interpreter()
        interp.interpret(ast)
    except errors.FiberNameError as e:
        print(e)
        sys.exit(1)
    except errors.FiberRuntimeError as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(f"[Internal Error] {type(e).__name__}: {e}")
        sys.exit(1)


def init_project(name):
    print(f"Fiber: Initializing Emerald Project: {name}")
    if os.path.exists(name):
        print(f"Error: Directory '{name}' already exists.")
        sys.exit(1)
    
    os.makedirs(name)
    os.makedirs(os.path.join(name, "lib"))
    
    main_content = f"""# {name} - Fiber Emerald Project

def main() {{
    print("Hello from Fiber Emerald!")
}}

main()
"""
    with open(os.path.join(name, "main.fib"), "w") as f:
        f.write(main_content)
    
    print(f"OK: Project '{name}' created successfully.")
    print(f"Usage: fiber run {name}")

def doctor():
    print("Fiber Emerald Doctor - Diagnostic Report")
    print("-" * 40)
    
    deps = [
        ("torch", "Neural Engine"),
        ("sympy", "Symbolic Engine"),
        ("requests", "Networking"),
        ("pyreadline3", "REPL History (Windows)"),
    ]
    
    for module, feature in deps:
        try:
            mod = __import__(module)
            ver = getattr(mod, "__version__", "unknown")
            print(f"[OK] {module:<12} | {feature:<20} | v{ver}")
        except ImportError:
            status = "[MISSING]" if module != "pyreadline3" else "[OPTIONAL]"
            print(f"{status} {module:<12} | {feature:<20}")
    
    print("-" * 40)
    print(f"Fiber Version: 4.0.0-emerald")
    print("Report Complete.")

def run_project(path):
    if os.path.isfile(path):
        run_file(path)
    elif os.path.isdir(path):
        candidates = ["main.fib", "index.fib", "app.fib"]
        for c in candidates:
            cpath = os.path.join(path, c)
            if os.path.isfile(cpath):
                run_file(cpath)
                return
        print(f"Error: No entry point (main.fib, index.fib) found in '{path}'")
        sys.exit(1)
    else:
        print(f"Error: Path '{path}' not found.")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        args = sys.argv[1:]
        
        # 1. COMMANDS
        cmd = args[0]
        
        if cmd == "init":
            if len(args) < 2:
                print("Error: Missing project name. Usage: fiber init <name>")
                sys.exit(1)
            init_project(args[1])
        elif cmd == "doctor":
            doctor()
        elif cmd == "run":
            if len(args) < 2:
                print("Error: Missing path. Usage: fiber run <path>")
                sys.exit(1)
            run_project(args[1])
        elif cmd in ["-c", "--compile"]:
            cli_filename = next((a for a in args if not a.startswith("-")), None)
            if not cli_filename:
                print("Error: Missing filename for compilation.")
                sys.exit(1)
            run_file(cli_filename, compile_only=True)
        elif cmd in ["-b", "--build"]:
            cli_filename = next((a for a in args if not a.startswith("-")), None)
            if not cli_filename:
                print("Error: Missing filename for build.")
                sys.exit(1)
            from fiber import builder
            builder.run_build(cli_filename)
        elif cmd in ["-v", "--version"]:
            print("Fiber v4.0.0-emerald")
        else:
            # Default to running the file provided
            run_project(sys.argv[1])
    else:
        print("Starting Fiber v4.0 (Emerald) REPL...")
        print('Tip: type "exit" or ".help" for assistance\n')
        repl.start_repl()
