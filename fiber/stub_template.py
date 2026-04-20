import sys
import os
import traceback

# This stub is used by the Fiber Builder to create standalone EXEs.
# It embeds the compiled bytecode and initializes the Fiber runtime.

# --- BUNDLED DATA AREA ---
# The builder replaces the line below with the actual bytecode.
bundled_bytecode = None
# @BYTECODE_DATA@
# -------------------------

def run():
    global bundled_bytecode
    # 1. Handle PyInstaller resource path resolution
    # When running as a bundled EXE, _MEIPASS points to the temp extraction directory.
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    
    # Ensure the bundled 'fiber' and 'lib' directories are discoverable
    if base_path not in sys.path:
        sys.path.insert(0, base_path)
    
    try:
        from fiber import interpreter, compiler, errors
        
        # Check if the builder successfully injected the bytecode
        if 'bundled_bytecode' not in globals():
            print("Error: Internal Consistency Failure - No bundled code found.")
            sys.exit(1)

        # 2. Load the AST from bytecode
        ast = compiler.load_from_binary(bundled_bytecode)
        
        # 3. Setup the interpreter
        interp = interpreter.Interpreter()
        
        # 4. Execute
        interp.interpret(ast)

    except Exception as e:
        print("\n" + "="*50)
        print("FIBER RUNTIME ERROR (BUNDLED APP)")
        print("="*50)
        traceback.print_exc()
        print("="*50)
        input("\nPress Enter to close...")

if __name__ == "__main__":
    run()
