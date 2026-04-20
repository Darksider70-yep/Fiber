import os
import sys
import subprocess
import shutil
from . import compiler, parser, lexer

class FiberBuilder:
    def __init__(self, script_path):
        self.script_path = os.path.abspath(script_path)
        self.base_dir = os.path.dirname(self.script_path)
        self.app_name = os.path.splitext(os.path.basename(self.script_path))[0]
        self.build_dir = os.path.join(self.base_dir, "build_fiber")
        self.dist_dir = os.path.join(self.base_dir, "dist")
        
        # Fiber package location (assuming it's a sibling)
        self.fiber_pkg_dir = os.path.dirname(os.path.abspath(__file__))
        self.root_dir = os.path.dirname(self.fiber_pkg_dir)

    def build(self):
        print(f"Starting Fiber Build for: {self.app_name}")
        
        if not os.path.exists(self.build_dir):
            os.makedirs(self.build_dir)
            
        # 1. Compile source to bytecode
        print("Compiling source to bytecode...")
        try:
            with open(self.script_path, "r", encoding="utf-8") as f:
                source = f.read()
                
            tokens = lexer.tokenize(source)
            p = parser.Parser(tokens, filename=self.script_path)
            ast = p.parse()
            bytecode = compiler.compile_to_binary(ast)
        except Exception as e:
            print(f"Syntax/Compilation Error: {e}")
            sys.exit(1)
        
        # 2. Generate Stub
        print("Generating standalone stub...")
        template_path = os.path.join(self.fiber_pkg_dir, "stub_template.py")
        if not os.path.exists(template_path):
            print(f"Internal Error: Stub template not found at {template_path}")
            sys.exit(1)
            
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
            
        # Inject bytecode
        bytecode_line = f"bundled_bytecode = {repr(bytecode)}"
        stub_content = template.replace("# @BYTECODE_DATA@", bytecode_line)
        
        stub_file = os.path.join(self.build_dir, f"{self.app_name}_stub.py")
        with open(stub_file, "w", encoding="utf-8") as f:
            f.write(stub_content)
            
        # 3. Invoke PyInstaller
        print("Forging binary with PyInstaller (this may take a minute)...")
        
        # PyInstaller command
        # We bundle 'fiber' as a package and 'lib' as a data folder
        cmd = [
            "pyinstaller",
            "--onefile",
            "--clean",
            f"--name={self.app_name}",
            f"--workpath={os.path.join(self.build_dir, 'work')}",
            f"--specpath={self.build_dir}",
            f"--distpath={self.dist_dir}",
            # Include the fiber motor package
            f"--add-data={self.fiber_pkg_dir}{os.pathsep}fiber",
            # Include the standard library
            f"--add-data={os.path.join(self.root_dir, 'lib')}{os.pathsep}lib",
            # Hidden imports for common Fiber dependencies
            "--hidden-import=torch",
            "--hidden-import=requests",
            "--hidden-import=sympy",
            stub_file
        ]
        
        try:
            # We use shell=True on windows to find pyinstaller in path if needed
            subprocess.run(cmd, check=True, shell=True)
            print(f"\nSUCCESS! Binary forged at: {os.path.join(self.dist_dir, self.app_name + '.exe')}")
            print(f"Check the 'dist' folder for your standalone app.")
        except subprocess.CalledProcessError as e:
            print(f"\nBuild failed during PyInstaller phase: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            sys.exit(1)

def run_build(path):
    builder = FiberBuilder(path)
    builder.build()
