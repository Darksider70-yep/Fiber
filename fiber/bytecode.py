# fiber/bytecode.py
from enum import IntEnum
from .errors import FiberRuntimeError


# ============================================================
# OPCODES (Fiber VM Instruction Set — v0)
# ============================================================

class OpCode(IntEnum):
    LOAD_CONST = 1
    LOAD_NAME  = 2     # push variable value
    STORE_NAME = 3     # pop → variable

    ADD        = 10
    SUB        = 11
    MUL        = 12
    DIV        = 13
    NEGATE    = 14

    PRINT     = 20
    RETURN    = 21


# ============================================================
# BYTECODE CONTAINER
# ============================================================

class Chunk:
    def __init__(self):
        self.code = []
        self.constants = []
        self.names = []   # 🔹 NEW

    def add_const(self, value):
        self.constants.append(value)
        return len(self.constants) - 1

    def add_name(self, name):
        if name not in self.names:
            self.names.append(name)
        return self.names.index(name)

    def emit(self, opcode, operand=None):
        self.code.append((opcode, operand))


# ============================================================
# VIRTUAL MACHINE
# ============================================================

class VirtualMachine:
    def __init__(self):
        self.stack = []
        self.ip = 0
        self.globals = {}           # instruction pointer

    def run(self, chunk: Chunk):
        self.ip = 0
        self.stack.clear()

        while self.ip < len(chunk.code):
            opcode, operand = chunk.code[self.ip]
            self.ip += 1

            # -----------------------------
            # STACK / CONSTANTS
            # -----------------------------
            if opcode == OpCode.LOAD_CONST:
                self.stack.append(chunk.constants[operand])

            # -----------------------------
            # ARITHMETIC
            # -----------------------------
            elif opcode == OpCode.ADD:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a + b)

            elif opcode == OpCode.SUB:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a - b)

            elif opcode == OpCode.MUL:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a * b)

            elif opcode == OpCode.DIV:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a / b)

            elif opcode == OpCode.NEGATE:
                self.stack.append(-self.stack.pop())

            # -----------------------------
            # OUTPUT
            # -----------------------------
            elif opcode == OpCode.PRINT:
                value = self.stack.pop()
                print(value)

            # -----------------------------
            # RETURN
            # -----------------------------
            elif opcode == OpCode.RETURN:
                return self.stack.pop() if self.stack else None
            
            elif opcode == OpCode.LOAD_NAME:
                name = chunk.names[operand]
                if name not in self.globals:
                    raise FiberRuntimeError(f"Undefined variable '{name}'")
                self.stack.append(self.globals[name])

            elif opcode == OpCode.STORE_NAME:
                name = chunk.names[operand]
                self.globals[name] = self.stack.pop()

            else:
                raise FiberRuntimeError(f"Unknown opcode: {opcode}")

        return None
