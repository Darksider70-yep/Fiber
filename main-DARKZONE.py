import sys
from fiber import repl, interpreter, parser, lexer, errors


def run_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except OSError as e:
        print(f"Error: Could not read '{filename}': {e}")
        sys.exit(1)

    try:
        tokens = lexer.tokenize(source)
        p = parser.Parser(tokens, filename=filename)
        ast = p.parse()

        interp = interpreter.Interpreter()
        interp.interpret(ast)

    except errors.FiberSyntaxError as e:
        print(e)
        sys.exit(1)
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
        run_file(sys.argv[1])
    else:
        print("Starting Fiber REPL...")
        print('Tip: type "exit" to quit\n')
        repl.start_repl()
