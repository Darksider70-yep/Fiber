from .lexer import tokenize
from .ast_nodes import *
from .errors import FiberSyntaxError


class Parser:
    def __init__(self, tokens, filename=None):
        self.tokens = tokens
        self.i = 0
        self.filename = filename

    def current(self):
        return self.tokens[self.i]

    def eat(self, typ=None):
        tok = self.current()
        if typ and tok.type != typ:
            raise FiberSyntaxError(f"Expected {typ}, got {tok.type} at line {tok.line}")
        self.i += 1
        return tok

    # -------------------------------------------------------------
    # PARSE ENTRY POINT
    # -------------------------------------------------------------
    def parse(self):
        stmts = []

        # skip any leading newlines
        while self.current().type == "NEWLINE":
            self.eat("NEWLINE")

        while self.current().type != "EOF":
            if self.current().type == "NEWLINE":
                self.eat("NEWLINE")
                continue
            stmts.append(self.statement())

            # skip redundant newlines after statements
            while self.current().type == "NEWLINE":
                self.eat("NEWLINE")

        return Program(stmts)

    # -------------------------------------------------------------
    # STATEMENTS
    # -------------------------------------------------------------
    def statement(self):
        t = self.current()

        # --- IMPORTS ---
        if t.type == "IMPORT":
            self.eat("IMPORT")
            module_name = self.eat("NAME").value
            alias = None
            if self.current().type == "AS":
                self.eat("AS")
                alias = self.eat("NAME").value
            if self.current().type == "NEWLINE":
                self.eat("NEWLINE")
            return Import(module_name, alias)

        if t.type == "FROM":
            self.eat("FROM")
            module_name = self.eat("NAME").value
            self.eat("IMPORT")
            if self.current().type == "MUL":
                self.eat("MUL")
                if self.current().type == "NEWLINE":
                    self.eat("NEWLINE")
                return ImportFrom(module_name, [], import_all=True)
            names = []
            while True:
                names.append(self.eat("NAME").value)
                if self.current().type == "COMMA":
                    self.eat("COMMA")
                    continue
                break
            if self.current().type == "NEWLINE":
                self.eat("NEWLINE")
            return ImportFrom(module_name, names)

        # --- PRINT ---
        if t.type == "PRINT":
            self.eat("PRINT")
            expr = self.expr()
            if self.current().type == "NEWLINE":
                self.eat("NEWLINE")
            return Print(expr)

        # --- CONST / FINAL / STATIC ---
        if t.type in ("CONST", "FINAL", "STATIC"):
            kind = t.type
            self.eat(kind)
            name = self.eat("NAME").value
            self.eat("ASSIGN")
            expr = self.expr()
            if self.current().type == "NEWLINE":
                self.eat("NEWLINE")
            return VarAssign(
                name, expr,
                const=(kind == "CONST"),
                final=(kind == "FINAL"),
                static=(kind == "STATIC")
            )

        # --- VAR ---
        if t.type == "VAR":
            self.eat("VAR")
            name = self.eat("NAME").value
            if self.current().type == "ASSIGN":
                self.eat("ASSIGN")
                expr = self.expr()
                if self.current().type == "NEWLINE":
                    self.eat("NEWLINE")
                return VarAssign(name, expr)
            else:
                if self.current().type == "NEWLINE":
                    self.eat("NEWLINE")
                return VarDecl(name)

        # --- DEF ---
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
            body = self.block()
            return FuncDef(name, params, body)

        # --- CLASS ---
        if t.type == "CLASS":
            self.eat("CLASS")
            name = self.eat("NAME").value
            parent = None
            if self.current().type == "EXTENDS":
                self.eat("EXTENDS")
                parent = self.eat("NAME").value
            body = self.block()
            return ClassDef(name, body, parent)

        # --- STRUCT ---
        if t.type == "STRUCT":
            self.eat("STRUCT")
            name = self.eat("NAME").value
            self.eat("LBRACE")
            fields = []
            while self.current().type != "RBRACE":
                if self.current().type == "NEWLINE":
                    self.eat("NEWLINE")
                    continue
                if self.current().type == "VAR":
                    self.eat("VAR")
                f = self.eat("NAME")
                fields.append(f.value)
                if self.current().type == "NEWLINE":
                    self.eat("NEWLINE")
            self.eat("RBRACE")
            return StructDef(name, fields)

        # --- ENUM ---
        if t.type == "ENUM":
            self.eat("ENUM")
            name = self.eat("NAME").value
            self.eat("LBRACE")
            values = []
            while self.current().type != "RBRACE":
                if self.current().type == "NEWLINE":
                    self.eat("NEWLINE")
                    continue
                v = self.eat("NAME").value
                values.append(v)
                if self.current().type == "NEWLINE":
                    self.eat("NEWLINE")
            self.eat("RBRACE")
            return EnumDef(name, values)

        # --- TRY / CATCH / FINALLY ---
        if t.type == "TRY":
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
                else:
                    catch_var = self.eat("NAME").value
                catch_block = self.block()

            if self.current().type == "FINALLY":
                self.eat("FINALLY")
                finally_block = self.block()

            return TryCatchFinally(try_block, catch_var, catch_block, finally_block)

        # --- THROW ---
        if t.type == "THROW":
            self.eat("THROW")
            expr = self.expr()
            if self.current().type == "NEWLINE":
                self.eat("NEWLINE")
            return Throw(expr)

        # --- ASSERT ---
        if t.type == "ASSERT":
            self.eat("ASSERT")
            cond = self.expr()
            message = None
            if self.current().type == "COMMA":
                self.eat("COMMA")
                message = self.expr()
            if self.current().type == "NEWLINE":
                self.eat("NEWLINE")
            return Assert(cond, message)

        # --- IF / ELIF / ELSE ---
        if t.type == "IF":
            self.eat("IF")
            cond = self.expr()
            then_branch = self.block()
            else_branch = None

            while self.current().type == "ELIF":
                self.eat("ELIF")
                elif_cond = self.expr()
                elif_body = self.block()
                else_branch = [If(elif_cond, elif_body)]
                if self.current().type == "ELIF":
                    continue
                break

            if self.current().type == "ELSE":
                self.eat("ELSE")
                else_branch = self.block()

            return If(cond, then_branch, else_branch)

        # --- WHILE ---
        if t.type == "WHILE":
            self.eat("WHILE")
            cond = self.expr()
            body = self.block()
            return While(cond, body)

        # --- FOR ---
        if t.type == "FOR":
            self.eat("FOR")
            var_name = self.eat("NAME").value

            if self.current().type == "ASSIGN":
                self.eat("ASSIGN")
                start = self.expr()
                self.eat("TO")
                end = self.expr()
                step = Number(1)
                if self.current().type == "STEP":
                    self.eat("STEP")
                    step = self.expr()
                body = self.block()
                return For(var_name, start, end, step, body)

            elif self.current().type == "IN":
                self.eat("IN")
                iterable = self.expr()
                step_expr = Number(1)
                while self.current().type == "NEWLINE":
                    self.eat("NEWLINE")
                if self.current().type == "STEP":
                    self.eat("STEP")
                    step_expr = self.expr()
                while self.current().type == "NEWLINE":
                    self.eat("NEWLINE")
                body = self.block()
                return ForIn(var_name, iterable, body, step_expr)

            else:
                raise FiberSyntaxError(f"Invalid for-loop syntax at line {t.line}")

        # --- BREAK / CONTINUE / RETURN / PASS ---
        if t.type == "BREAK":
            self.eat("BREAK")
            if self.current().type == "NEWLINE":
                self.eat("NEWLINE")
            return Break()

        if t.type == "CONTINUE":
            self.eat("CONTINUE")
            if self.current().type == "NEWLINE":
                self.eat("NEWLINE")
            return Continue()

        if t.type == "RETURN":
            self.eat("RETURN")
            expr = None
            if self.current().type not in ("NEWLINE", "RBRACE", "EOF"):
                expr = self.expr()
            if self.current().type == "NEWLINE":
                self.eat("NEWLINE")
            return Return(expr)

        if t.type == "PASS":
            self.eat("PASS")
            if self.current().type == "NEWLINE":
                self.eat("NEWLINE")
            return None

        # --- Expression fallback ---
        node = self.expr()
        if isinstance(node, (VarRef, MemberAccess, Index)) and self.current().type == "ASSIGN":
            self.eat("ASSIGN")
            value = self.expr()
            if isinstance(node, VarRef):
                return VarAssign(node.name, value)
            elif isinstance(node, MemberAccess):
                return MemberAssign(node.obj, node.name, value)
            elif isinstance(node, Index):
                return IndexAssign(node.obj, node.index, value)

        if isinstance(node, (Call, MemberAccess, Index, VarRef)):
            if self.current().type == "NEWLINE":
                self.eat("NEWLINE")
            return node

        raise FiberSyntaxError(f"Unexpected token {self.current().type} at line {self.current().line}")

    # -------------------------------------------------------------
    # BLOCKS
    # -------------------------------------------------------------
    def block(self):
        self.eat("LBRACE")
        stmts = []

        # handle empty blocks or trailing braces cleanly
        while self.current().type != "RBRACE" and self.current().type != "EOF":
            # skip newlines before statements
            while self.current().type == "NEWLINE":
                self.eat("NEWLINE")
                if self.current().type in ("RBRACE", "EOF"):
                    break
            if self.current().type in ("RBRACE", "EOF"):
                break
            stmts.append(self.statement())

        # safely close the block
        if self.current().type == "RBRACE":
            self.eat("RBRACE")
        else:
            raise FiberSyntaxError(
                f"Expected RBRACE, got {self.current().type} at line {self.current().line}"
            )
        return stmts

    # -------------------------------------------------------------
    # EXPRESSIONS
    # -------------------------------------------------------------
    def expr(self):
        return self._or_expr()

    def _or_expr(self):
        node = self._and_expr()
        while self.current().type == "OR":
            op = self.eat().type
            right = self._and_expr()
            node = BinOp(node, op, right)
        return node

    def _and_expr(self):
        node = self._not_expr()
        while self.current().type == "AND":
            op = self.eat().type
            right = self._not_expr()
            node = BinOp(node, op, right)
        return node

    def _not_expr(self):
        if self.current().type == "NOT":
            self.eat("NOT")
            return UnaryOp("NOT", self._not_expr())
        return self._comparison()

    def _comparison(self):
        node = self._sum_expr()
        while self.current().type in ("EQ", "NEQ", "LT", "GT", "LTE", "GTE"):
            op = self.eat().type
            right = self._sum_expr()
            node = BinOp(node, op, right)
        return node

    def _sum_expr(self):
        node = self._term()
        while self.current().type in ("PLUS", "MINUS"):
            op = self.eat().type
            right = self._term()
            node = BinOp(node, op, right)
        return node

    def _term(self):
        node = self._factor()
        while self.current().type in ("MUL", "DIV", "MOD"):
            op = self.eat().type
            right = self._factor()
            node = BinOp(node, op, right)
        return node

    def _factor(self):
        t = self.current()
        if t.type == "MINUS":
            self.eat("MINUS")
            return UnaryOp("MINUS", self._factor())
        return self._primary()

    def _primary(self):
        t = self.current()
        if t.type == "NUMBER":
            return Number(self.eat("NUMBER").value)
        if t.type == "STRING":
            return String(self.eat("STRING").value)
        if t.type == "TRUE":
            self.eat("TRUE"); return Boolean(True)
        if t.type == "FALSE":
            self.eat("FALSE"); return Boolean(False)

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
                                self.eat("COMMA"); continue
                            break
                    self.eat("RPAREN")
                    node = Call(node, args)
                elif self.current().type == "DOT":
                    self.eat("DOT")
                    member = self.eat("NAME").value
                    node = MemberAccess(node, member)
                elif self.current().type == "LBRACKET":
                    self.eat("LBRACKET")
                    index_expr = self.expr()
                    self.eat("RBRACKET")
                    node = Index(node, index_expr)
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
            elements = []
            if self.current().type != "RBRACKET":
                while True:
                    elements.append(self.expr())
                    if self.current().type == "COMMA":
                        self.eat("COMMA"); continue
                    break
            self.eat("RBRACKET")
            return ListLiteral(elements)

        raise FiberSyntaxError(f"Unexpected token {t.type} at line {t.line}")
