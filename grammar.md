# Fiber Language Grammar (Locked Specification)

Version: 4.0.1
Status: RELEASED  

This document defines the authoritative grammar of the Fiber programming language. Any change to the parser or interpreter MUST conform to this specification.

---

## 2. Lexical Structure

Reserved Keywords (never valid as identifiers)  
class def var const final static  
struct enum  
if elif else  
while for in to step  
break continue pass  
return  
try catch finally throw assert  
true false  
and or not  
import from as

---

## 8. Primary Expressions

primary ::=  
    NUMBER  
  | STRING  
  | BOOLEAN  
  | NAME  
  | call  
  | member_access  
  | index_access  
  | list_literal  
  | dict_literal  
  | "(" expr ")"  

---

## 10. Dictionaries (v4.0.1)

dict_literal ::= "{" [ expr ":" expr { "," expr ":" expr } ] "}"

Rules:
- Dictionary keys must be evaluatable to a hashable primitive.
- Dictionaries are mutable and support member access/indexing.

---

## 21. AI Reasoning Extensions (v0.2)

The following builtins are formally integrated into the core language namespace for symbolic and numerical computation:

### 21.1 Symbolic Operations
`expr(S)` : Parses string `S` into a symbolic representation.  
`diff(E, V)` : Returns the derivative of expression `E` with respect to variable `V`.  
`solve(E, V)` : Returns a list of symbolic roots for `E = 0` with respect to `V`.  
`simplify(E)` : Algebraically simplifies expression `E`.  
`subst(E, M)` : Returns numeric value of `E` by substituting variables according to mapping `M` (Dictionary).
`logic_symbols(E)` : Returns a list of all variable names (strings) found in expression `E`.

### 21.2 Tensor Operations
`tensor(D)` : Converts nested list `D` into a multi-dimensional numerical object.  
`matmul(A, B)` : Performs matrix multiplication between tensors `A` and `B`.

### 21.3 Logic Operations
`A >> B` : Symbolic Implies (equivalent to `!A | B`).
`A & B`, `A | B`, `~A` : Symbolic AND, OR, NOT.

---

## 22. Grammar Invariants (Non-Negotiable)

1. Keywords never appear inside expressions  
2. All blocks use `{ }`  
3. Assignments are statements only  
4. No implicit syntax  
5. No parser backtracking  
6. Grammar must remain LL(1) at statement level  
7. Any violation is a syntax error  

End of specification.
