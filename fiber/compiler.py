# fiber/compiler.py
from .ast_nodes import (
    Number, UnaryOp, BinOp, Print,
    Program, VarAssign, VarRef
)
from .bytecode import Chunk, OpCode
from .errors import FiberRuntimeError


# ============================================================
# AST → BYTECODE COMPILER (Phase 1: Expressions Only)
# ============================================================

class Compiler:
    def __init__(self):
        self.chunk = Chunk()

    # -----------------------------
    # Entry point
    # -----------------------------
    def compile(self, program: Program) -> Chunk:
        for stmt in program.stmts:
            self.compile_stmt(stmt)
        self.chunk.emit(OpCode.RETURN)
        return self.chunk

    # -----------------------------
    # Statements
    # -----------------------------
    def compile_stmt(self, node):
        if isinstance(node, Print):
            self.compile_expr(node.expr)
            self.chunk.emit(OpCode.PRINT)
            return

        if isinstance(node, VarAssign):
            self.compile_expr(node.expr)
            name_idx = self.chunk.add_name(node.name)
            self.chunk.emit(OpCode.STORE_NAME, name_idx)
            return

        self.compile_expr(node)

    # -----------------------------
    # Expressions
    # -----------------------------
    def compile_expr(self, node):
        if isinstance(node, Number):
            idx = self.chunk.add_const(node.value)
            self.chunk.emit(OpCode.LOAD_CONST, idx)
            return

        if isinstance(node, UnaryOp):
            self.compile_expr(node.expr)
            if node.op == "MINUS":
                self.chunk.emit(OpCode.NEGATE)
                return
            raise FiberRuntimeError(f"Unsupported unary op: {node.op}")
        
        if isinstance(node, VarRef):
            name_idx = self.chunk.add_name(node.name)
            self.chunk.emit(OpCode.LOAD_NAME, name_idx)
            return

        if isinstance(node, BinOp):
            self.compile_expr(node.left)
            self.compile_expr(node.right)

            op_map = {
                "PLUS": OpCode.ADD,
                "MINUS": OpCode.SUB,
                "MUL": OpCode.MUL,
                "DIV": OpCode.DIV,
            }

            if node.op not in op_map:
                raise FiberRuntimeError(f"Unsupported binary op: {node.op}")

            self.chunk.emit(op_map[node.op])
            return

        raise FiberRuntimeError(
            f"Unsupported AST node in compiler: {type(node)}"
        )
