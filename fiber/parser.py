from .ast_nodes import *
from .errors import FiberSyntaxError


class Parser:
    def __init__(self, tokens, filename=None):
        self.tokens = tokens
        self.i = 0
        self.filename = filename

    # -------------------------------------------------
    # TOKEN HELPERS
    # -------------------------------------------------
    def current(self):
        return self.tokens[self.i]

    def eat(self, typ=None):
        tok = self.current()
        if typ and tok.type != typ:
            raise FiberSyntaxError(
                f"Expected {typ}, got {tok.type} at line {tok.line}"
            )
        self.i += 1
        return tok

    # -------------------------------------------------
    # ENTRY POINT
    # -------------------------------------------------
    def parse(self):
        stmts = []

        while self.current().type == "NEWLINE":
            self.eat("NEWLINE")

        while self.current().type != "EOF":
            stmts.append(self.statement())
            while self.current().type == "NEWLINE":
                self.eat("NEWLINE")

        if self.current().type != "EOF":
            raise FiberSyntaxError(
                f"Unexpected token {self.current().type} at line {self.current().line}"
            )

        return Program(stmts)

    # -------------------------------------------------
    # STATEMENTS
    # -------------------------------------------------
    def statement(self):
        t = self.current()

        # ---------------- IMPORT ----------------
        if t.type == "IMPORT":
            self.eat("IMPORT")
            module = self.eat("NAME").value
            alias = None
            if self.current().type == "AS":
                self.eat("AS")
                alias = self.eat("NAME").value
            return Import(module, alias)

        if t.type == "FROM":
            self.eat("FROM")
            module = self.eat("NAME").value
            self.eat("IMPORT")
            if self.current().type == "MUL":
                self.eat("MUL")
                return ImportFrom(module, [], True)
            names = []
            while True:
                names.append(self.eat("NAME").value)
                if self.current().type == "COMMA":
                    self.eat("COMMA")
                    continue
                break
            return ImportFrom(module, names)

        # ---------------- PRINT ----------------
        if t.type == "PRINT":
            self.eat("PRINT")
            return Print(self.expr())

        # ---------------- VAR / CONST / FINAL / STATIC ----------------
        if t.type in ("VAR", "CONST", "FINAL", "STATIC"):
            kind = t.type
            self.eat(kind)
            name = self.eat("NAME").value
            expr = None
            if self.current().type == "ASSIGN":
                self.eat("ASSIGN")
                expr = self.expr()
            return VarAssign(
                name, expr,
                const=(kind == "CONST"),
                final=(kind == "FINAL"),
                static=(kind == "STATIC")
            ) if expr else VarDecl(name)

        # ---------------- FUNCTION ----------------
        if t.type == "DEF":
            self.eat("DEF")
            name = self.eat("NAME").value
            self.eat("LPAREN")
            params = []
            if self.current().type != "RPAREN":
                while True:
                    params.append(self.eat("NAME").value)
                    if self.current().type == "COMMA":
                        self.eat("COMMA")
                        continue
                    break
            self.eat("RPAREN")
            return FuncDef(name, params, self.block())

        # ---------------- CLASS ----------------
        if t.type == "CLASS":
            self.eat("CLASS")
            name = self.eat("NAME").value
            parent = None
            if self.current().type == "EXTENDS":
                self.eat("EXTENDS")
                parent = self.eat("NAME").value
            return ClassDef(name, self.block(), parent)

        # ---------------- IF ----------------
        if t.type == "IF":
            self.eat("IF")
            cond = self.expr()
            then = self.block()
            else_branch = None

            while self.current().type == "ELIF":
                self.eat("ELIF")
                else_branch = If(self.expr(), self.block())

            if self.current().type == "ELSE":
                self.eat("ELSE")
                else_branch = self.block()

            return If(cond, then, else_branch)

        # ---------------- WHILE ----------------
        if t.type == "WHILE":
            self.eat("WHILE")
            return While(self.expr(), self.block())

        # ---------------- FOR ----------------
        if t.type == "FOR":
            self.eat("FOR")
            var = self.eat("NAME").value

            # numeric for
            if self.current().type == "ASSIGN":
                self.eat("ASSIGN")
                start = self.expr()
                self.eat("TO")
                end = self.expr()
                step = Number(1)
                if self.current().type == "STEP":
                    self.eat("STEP")
                    step = self.expr()
                return For(var, start, end, step, self.block())

            # iterable for (LOCKED)
            if self.current().type == "IN":
                self.eat("IN")
                iterable = self.primary()   # 🔒 grammar enforced
                step = Number(1)
                if self.current().type == "STEP":
                    self.eat("STEP")
                    step = self.expr()
                return ForIn(var, iterable, self.block(), step)

            raise FiberSyntaxError("Invalid for-loop syntax")

        # ---------------- BREAK / CONTINUE / RETURN ----------------
        if t.type == "BREAK":
            self.eat("BREAK")
            return Break()

        if t.type == "CONTINUE":
            self.eat("CONTINUE")
            return Continue()

        if t.type == "RETURN":
            self.eat("RETURN")
            return Return(self.expr() if self.current().type not in ("NEWLINE", "RBRACE") else None)

        # ---------------- ASSIGNMENT ----------------
        expr = self.expr()
        if isinstance(expr, (VarRef, MemberAccess, Index)) and self.current().type == "ASSIGN":
            self.eat("ASSIGN")
            val = self.expr()
            if isinstance(expr, VarRef):
                return VarAssign(expr.name, val)
            if isinstance(expr, MemberAccess):
                return MemberAssign(expr.obj, expr.name, val)
            if isinstance(expr, Index):
                return IndexAssign(expr.obj, expr.index, val)
            raise FiberSyntaxError("Invalid assignment target")

        if isinstance(expr, (Call, VarRef, MemberAccess, Index)):
            return expr

        raise FiberSyntaxError(f"Unexpected token {t.type}")

    # -------------------------------------------------
    # BLOCK
    # -------------------------------------------------
    def block(self):
        self.eat("LBRACE")
        stmts = []
        while self.current().type != "RBRACE":
            stmts.append(self.statement())
        self.eat("RBRACE")
        return stmts

    # -------------------------------------------------
    # EXPRESSIONS
    # -------------------------------------------------
    def expr(self):
        return self.or_expr()

    def or_expr(self):
        node = self.and_expr()
        while self.current().type == "OR":
            self.eat("OR")
            node = BinOp(node, "OR", self.and_expr())
        return node

    def and_expr(self):
        node = self.not_expr()
        while self.current().type == "AND":
            self.eat("AND")
            node = BinOp(node, "AND", self.not_expr())
        return node

    def not_expr(self):
        if self.current().type == "NOT":
            self.eat("NOT")
            return UnaryOp("NOT", self.not_expr())
        return self.compare()

    def compare(self):
        node = self.sum_expr()
        while self.current().type in ("EQ", "NEQ", "LT", "GT", "LTE", "GTE"):
            op = self.eat().type
            node = BinOp(node, op, self.sum_expr())
        return node

    def sum_expr(self):
        node = self.term()
        while self.current().type in ("PLUS", "MINUS"):
            op = self.eat().type
            node = BinOp(node, op, self.term())
        return node

    def term(self):
        node = self.factor()
        while self.current().type in ("MUL", "DIV", "MOD"):
            op = self.eat().type
            node = BinOp(node, op, self.factor())
        return node

    def factor(self):
        if self.current().type == "MINUS":
            self.eat("MINUS")
            return UnaryOp("MINUS", self.factor())
        return self.primary()

    # -------------------------------------------------
    # PRIMARY (KEYWORD-FREE ZONE)
    # -------------------------------------------------
    def primary(self):
        t = self.current()

        if t.type in {
            "FOR", "IF", "WHILE", "STEP", "TO",
            "BREAK", "CONTINUE", "RETURN", "ELIF", "ELSE"
        }:
            raise FiberSyntaxError(
                f"Keyword '{t.value}' not allowed in expression at line {t.line}"
            )

        if t.type == "NUMBER":
            return Number(self.eat("NUMBER").value)

        if t.type == "STRING":
            return String(self.eat("STRING").value)

        if t.type == "TRUE":
            self.eat("TRUE")
            return Boolean(True)

        if t.type == "FALSE":
            self.eat("FALSE")
            return Boolean(False)

        if t.type == "NAME":
            node = VarRef(self.eat("NAME").value)
            while True:
                if self.current().type == "LPAREN":
                    self.eat("LPAREN")
                    args = []
                    if self.current().type != "RPAREN":
                        while True:
                            args.append(self.expr())
                            if self.current().type == "COMMA":
                                self.eat("COMMA")
                                continue
                            break
                    self.eat("RPAREN")
                    node = Call(node, args)
                elif self.current().type == "DOT":
                    self.eat("DOT")
                    node = MemberAccess(node, self.eat("NAME").value)
                elif self.current().type == "LBRACKET":
                    self.eat("LBRACKET")
                    idx = self.expr()
                    self.eat("RBRACKET")
                    node = Index(node, idx)
                else:
                    break
            return node

        if t.type == "LPAREN":
            self.eat("LPAREN")
            node = self.expr()
            self.eat("RPAREN")
            return node

        if t.type == "LBRACKET":
            self.eat("LBRACKET")
            elems = []
            if self.current().type != "RBRACKET":
                while True:
                    elems.append(self.expr())
                    if self.current().type == "COMMA":
                        self.eat("COMMA")
                        continue
                    break
            self.eat("RBRACKET")
            return ListLiteral(elems)

        raise FiberSyntaxError(f"Unexpected token {t.type} at line {t.line}")
