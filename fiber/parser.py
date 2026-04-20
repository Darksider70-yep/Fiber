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
            raise FiberSyntaxError(f"Expected {typ}, got {tok.type} at line {tok.line}")
        self.i += 1
        return tok

    def skip_newlines(self):
        while self.current().type == "NEWLINE":
            self.eat("NEWLINE")

    # -------------------------------------------------
    # ENTRY POINT
    # -------------------------------------------------
    def parse(self):
        stmts = []
        self.skip_newlines()

        while self.current().type != "EOF":
            stmts.append(self.statement())
            self.skip_newlines()

        return Program(stmts, filename=self.filename)

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

            if expr is None:
                if kind != "VAR":
                    raise FiberSyntaxError(f"{kind.lower()} requires an initializer at line {t.line}")
                return VarDecl(name)

            return VarAssign(
                name,
                expr,
                const=(kind == "CONST"),
                final=(kind == "FINAL"),
                static=(kind == "STATIC"),
                declare=True,
            )

        # ---------------- FUNCTION ----------------
        if t.type == "DEF":
            return self.function_def()

        # ---------------- CLASS ----------------
        if t.type == "CLASS":
            return self.class_def()

        # ---------------- STRUCT / ENUM ----------------
        if t.type == "STRUCT":
            return self.struct_def()

        if t.type == "ENUM":
            return self.enum_def()

        # ---------------- IF ----------------
        if t.type == "IF":
            return self.if_stmt()

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

            # iterable for
            if self.current().type == "IN":
                self.eat("IN")
                iterable = self.primary()
                step = Number(1)
                if self.current().type == "STEP":
                    self.eat("STEP")
                    step = self.expr()
                return ForIn(var, iterable, self.block(), step)

            raise FiberSyntaxError(f"Invalid for-loop syntax at line {t.line}")

        # ---------------- MATCH / SWITCH ----------------
        if t.type in ("MATCH", "SWITCH"):
            return self.match_stmt()

        # ---------------- TRY / THROW / ASSERT ----------------
        if t.type == "TRY":
            return self.try_stmt()

        if t.type == "THROW":
            self.eat("THROW")
            return Throw(self.expr())

        if t.type == "ASSERT":
            self.eat("ASSERT")
            cond = self.expr()
            message = None
            if self.current().type == "COMMA":
                self.eat("COMMA")
                message = self.expr()
            return Assert(cond, message)

        # ---------------- BREAK / CONTINUE / PASS / RETURN ----------------
        if t.type == "BREAK":
            self.eat("BREAK")
            return Break()

        if t.type == "CONTINUE":
            self.eat("CONTINUE")
            return Continue()

        if t.type == "PASS":
            self.eat("PASS")
            return Pass()

        if t.type == "RETURN":
            self.eat("RETURN")
            if self.current().type in ("NEWLINE", "RBRACE", "EOF"):
                return Return(None)
            return Return(self.expr())

        # ---------------- ASSIGNMENT / EXPR STMT ----------------
        expr = self.expr()
        if isinstance(expr, (VarRef, MemberAccess, Index)) and self.current().type == "ASSIGN":
            self.eat("ASSIGN")
            val = self.expr()
            if isinstance(expr, VarRef):
                return VarAssign(expr.name, val)
            if isinstance(expr, MemberAccess):
                return MemberAssign(expr.obj, expr.name, val)
            return IndexAssign(expr.obj, expr.index, val)

        if isinstance(expr, (Call, VarRef, MemberAccess, Index)):
            return expr

        raise FiberSyntaxError(f"Unexpected token {t.type} at line {t.line}")

    # -------------------------------------------------
    # COMPOSITE STATEMENT HELPERS
    # -------------------------------------------------
    def parse_params(self):
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
        return params

    def function_def(self):
        self.eat("DEF")
        name = self.eat("NAME").value
        params = self.parse_params()
        return FuncDef(name, params, self.block())

    def method_def(self):
        self.eat("DEF")
        name = self.eat("NAME").value
        params = self.parse_params()
        return Method(name, params, self.block())

    def class_def(self):
        self.eat("CLASS")
        name = self.eat("NAME").value
        parent = None
        if self.current().type == "EXTENDS":
            self.eat("EXTENDS")
            parent = self.eat("NAME").value
        body = self.class_block()
        return ClassDef(name, body, parent)

    def class_block(self):
        self.eat("LBRACE")
        methods = []
        self.skip_newlines()
        while self.current().type != "RBRACE":
            if self.current().type == "DEF":
                methods.append(self.method_def())
            elif self.current().type == "PASS":
                self.eat("PASS")
                methods.append(Pass())
            else:
                tok = self.current()
                raise FiberSyntaxError(
                    f"Only method definitions are allowed in class body, got {tok.type} at line {tok.line}"
                )
            self.skip_newlines()
        self.eat("RBRACE")
        return methods

    def name_list_block(self):
        self.eat("LBRACE")
        names = []
        self.skip_newlines()
        while self.current().type != "RBRACE":
            names.append(self.eat("NAME").value)
            if self.current().type == "COMMA":
                self.eat("COMMA")
            self.skip_newlines()
        self.eat("RBRACE")
        return names

    def struct_def(self):
        self.eat("STRUCT")
        name = self.eat("NAME").value
        return StructDef(name, self.name_list_block())

    def enum_def(self):
        self.eat("ENUM")
        name = self.eat("NAME").value
        return EnumDef(name, self.name_list_block())

    def match_stmt(self):
        if self.current().type == "SWITCH":
            self.eat("SWITCH")
        else:
            self.eat("MATCH")
        discriminant = self.expr()
        self.skip_newlines()
        self.eat("LBRACE")
        cases = []
        default_branch = None
        while self.current().type != "RBRACE":
            self.skip_newlines()
            if self.current().type == "RBRACE":
                break

            if self.current().type == "CASE":
                self.eat("CASE")
                pattern = self.expr()
                self.eat("COLON")
                self.skip_newlines()
                body = self.block() if self.current().type == "LBRACE" else [self.statement()]
                cases.append(Case(pattern, body))
            elif self.current().type == "DEFAULT":
                self.eat("DEFAULT")
                self.eat("COLON")
                self.skip_newlines()
                default_branch = self.block() if self.current().type == "LBRACE" else [self.statement()]
            else:
                raise FiberSyntaxError(f"Expected case or default in match block, got {self.current().type} at line {self.current().line}")
            self.skip_newlines()
        
        self.eat("RBRACE")
        return Match(discriminant, cases, default_branch)

    def if_stmt(self):
        self.eat("IF")
        cond = self.expr()
        then_branch = self.block()

        elif_parts = []
        self.skip_newlines()
        while self.current().type == "ELIF":
            self.eat("ELIF")
            elif_cond = self.expr()
            elif_block = self.block()
            elif_parts.append((elif_cond, elif_block))
            self.skip_newlines()

        else_branch = None
        self.skip_newlines()
        if self.current().type == "ELSE":
            self.eat("ELSE")
            else_branch = self.block()

        for elif_cond, elif_block in reversed(elif_parts):
            else_branch = If(elif_cond, elif_block, else_branch)

        return If(cond, then_branch, else_branch)

    def try_stmt(self):
        self.eat("TRY")
        try_block = self.block()

        catch_var = None
        catch_block = None
        finally_block = None

        if self.current().type == "CATCH":
            self.eat("CATCH")
            if self.current().type == "LPAREN":
                self.eat("LPAREN")
                catch_var = self.eat("NAME").value
                self.eat("RPAREN")
            elif self.current().type == "NAME":
                catch_var = self.eat("NAME").value
            catch_block = self.block()

        if self.current().type == "FINALLY":
            self.eat("FINALLY")
            finally_block = self.block()

        if catch_block is None and finally_block is None:
            tok = self.current()
            raise FiberSyntaxError(f"try must be followed by catch and/or finally near line {tok.line}")

        return TryCatchFinally(try_block, catch_var, catch_block, finally_block)

    # -------------------------------------------------
    # BLOCK
    # -------------------------------------------------
    def block(self):
        self.eat("LBRACE")
        stmts = []
        self.skip_newlines()
        while self.current().type != "RBRACE":
            stmts.append(self.statement())
            self.skip_newlines()
        self.eat("RBRACE")
        return stmts

    # -------------------------------------------------
    # EXPRESSIONS
    # -------------------------------------------------
    def expr(self):
        return self.ternary()

    def ternary(self):
        node = self.or_expr()
        if self.current().type == "QUESTION":
            self.eat("QUESTION")
            true_expr = self.expr()
            self.eat("COLON")
            false_expr = self.ternary()
            return Ternary(node, true_expr, false_expr)
        return node

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
        node = self.power_expr()
        while self.current().type in ("MUL", "DIV", "MOD"):
            op = self.eat().type
            node = BinOp(node, op, self.power_expr())
        return node

    def power_expr(self):
        node = self.factor()
        while self.current().type == "POWER":
            op = self.eat().type
            node = BinOp(node, op, self.factor())
        return node

    def factor(self):
        if self.current().type == "MINUS":
            self.eat("MINUS")
            return UnaryOp("MINUS", self.factor())
        return self.primary()

    # -------------------------------------------------
    # PRIMARY
    # -------------------------------------------------
    def primary(self):
        t = self.current()

        disallowed_keywords = {
            "FOR", "IF", "WHILE", "STEP", "TO", "BREAK", "CONTINUE",
            "RETURN", "ELIF", "ELSE", "TRY", "CATCH", "FINALLY",
            "THROW", "ASSERT", "STRUCT", "ENUM", "CLASS", "DEF",
            "VAR", "CONST", "FINAL", "STATIC", "IMPORT", "FROM", "AS",
        }
        if t.type in disallowed_keywords:
            raise FiberSyntaxError(f"Keyword '{t.value}' not allowed in expression at line {t.line}")

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

        if t.type in ("NAME", "THIS"):
            name = self.eat(t.type).value
            node = VarRef(name)
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
            self.skip_newlines()
            if self.current().type == "RBRACKET":
                self.eat("RBRACKET")
                return ListLiteral([])

            first = self.expr()
            if self.current().type == "FOR":
                self.eat("FOR")
                var = self.eat("NAME").value
                self.eat("IN")
                iterable = self.expr()
                cond = None
                if self.current().type == "IF":
                    self.eat("IF")
                    cond = self.expr()
                self.eat("RBRACKET")
                return ListComprehension(first, var, iterable, cond)

            elems = [first]
            self.skip_newlines()
            while self.current().type == "COMMA":
                self.eat("COMMA")
                self.skip_newlines()
                if self.current().type == "RBRACKET": break
                elems.append(self.expr())
                self.skip_newlines()
            self.eat("RBRACKET")
            return ListLiteral(elems)

        if t.type == "LBRACE":
            self.eat("LBRACE")
            self.skip_newlines()
            pairs = []
            if self.current().type != "RBRACE":
                while True:
                    key = self.expr()
                    self.skip_newlines()
                    self.eat("COLON")
                    self.skip_newlines()
                    val = self.expr()
                    self.skip_newlines()
                    pairs.append((key, val))
                    if self.current().type == "COMMA":
                        self.eat("COMMA")
                        self.skip_newlines()
                        continue
                    break
            self.eat("RBRACE")
            return DictLiteral(pairs)

        raise FiberSyntaxError(f"Unexpected token {t.type} at line {t.line}")
