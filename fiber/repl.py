import sys
import os
from .lexer import tokenize
from .parser import Parser
from .interpreter import Interpreter

# Try to enable readline for history
try:
    if os.name == 'nt':
        import pyreadline3 as readline
    else:
        import readline
except ImportError:
    readline = None

COLOR_RESET = "\x1b[0m"
COLOR_PRIMARY = "\x1b[92m" # Bright Green
COLOR_ERROR = "\x1b[31m"   # Red
COLOR_DIM = "\x1b[90m"     # Gray

PROMPT = f'{COLOR_PRIMARY}fiber>{COLOR_RESET} '
CONTINUE_PROMPT = f'{COLOR_DIM}...    {COLOR_RESET}'

def start_repl():
    interp = Interpreter()
    print(f'{COLOR_PRIMARY}Fiber Emerald REPL v4.1{COLOR_RESET}')
    print(f'{COLOR_DIM}Tip: Type "exit" to quit, ".help" for help.{COLOR_RESET}')
    
    buffer = ''
    while True:
        try:
            current_prompt = PROMPT if not buffer else CONTINUE_PROMPT
            line = input(current_prompt)
        except (EOFError, KeyboardInterrupt):
            print("\nExiting Fiber..."); break
            
        if line.strip() == 'exit': break
        if line.strip() == '.help':
            interp.global_env.get('help')()
            continue
        if line.strip() == '.clear':
            os.system('cls' if os.name == 'nt' else 'clear')
            continue

        buffer += line + '\n'
        
        # Check for empty input to reset buffer
        if not line.strip() and buffer.strip():
            # Force attempt parse on double enter if stuck
            pass 

        try:
            tokens = tokenize(buffer)
            parser = Parser(tokens)
            prog = parser.parse()
            
            # If we reach here, parsing succeeded
            interp.interpret(prog)
            buffer = ''
        except Exception as e:
            err_str = str(e)
            # If it's a syntax error due to incomplete input, keep reading
            # We look for "Unexpected EOF" or similar hints from the parser
            if 'Unexpected token EOF' in err_str or 'Expected' in err_str:
                # Basic heuristic for multiline: if it looks like we need more, don't crash
                continue
            
            print(f"{COLOR_ERROR}Error: {e}{COLOR_RESET}")
            buffer = ''
