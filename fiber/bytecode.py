# fiber/bytecode.py
from enum import IntEnum
from .errors import FiberRuntimeError


# ============================================================
# OPCODES (Fiber VM Instruction Set — v0)
# ============================================================

class OpCode(IntEnum):
    LOAD_CONST = 1     # push constant onto stack
    ADD        = 2
    SUB        = 3
    MUL        = 4
    DIV        = 5
    NEGATE    = 6
    PRINT     = 7
    RETURN    = 8


# ============================================================
# BYTECODE CONTAINER
# ============================================================

class Chunk:
    def __init__(self):
        self.code = []        # list of (opcode, operand)
        self.constants = []   # constant pool

    def add_const(self, value):
        self.constants.append(value)
        return len(self.constants) - 1

    def emit(self, opcode, operand=None):
        self.code.append((opcode, operand))


# ============================================================
# VIRTUAL MACHINE
# ============================================================

class VirtualMachine:
    def __init__(self):
        self.stack = []
        self.ip = 0           # instruction pointer

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

            else:
                raise FiberRuntimeError(f"Unknown opcode: {opcode}")

        return None
