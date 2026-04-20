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


if __name__ == "__main__":
    if len(sys.argv) > 1:
        args = sys.argv[1:]
        if "-c" in args or "--compile" in args:
            cli_filename = next((a for a in args if not a.startswith("-")), None)
            if not cli_filename:
                print("Error: Missing filename for compilation.")
                sys.exit(1)
            run_file(cli_filename, compile_only=True)
        else:
            run_file(sys.argv[1])
    else:
        print("Starting Fiber v2.0 REPL...")
        print('Tip: type "exit" to quit\n')
        repl.start_repl()
