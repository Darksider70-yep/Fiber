from .lexer import tokenize
from .parser import Parser
from .interpreter import Interpreter

PROMPT = 'fiber> '

def start_repl():
    interp = Interpreter()
    print('Fiber REPL v0.1 — type "exit" to quit')
    buffer = ''
    while True:
        try:
            line = input(PROMPT)
        except EOFError:
            print(); break
        if line.strip() == 'exit': break
        buffer += line + '\n'
        # try parse
        try:
            tokens = tokenize(buffer)
            parser = Parser(tokens)
            prog = parser.parse()
            interp.interpret(prog)
            buffer = ''
        except Exception as e:
            # if it's a syntax error due to incomplete input, keep reading
            if 'Unexpected token EOF' in str(e) or 'Expected' in str(e):
                continue
            print(type(e).__name__ + ':', e)
            buffer = ''
