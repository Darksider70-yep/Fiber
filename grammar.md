# Fiber Language Grammar (Locked Specification)

Version: 0.1  
Status: LOCKED  

This document defines the authoritative grammar of the Fiber programming language.
Any change to the parser or interpreter MUST conform to this specification.

---

## 1. Design Principles

- Grammar must be deterministic and unambiguous
- Keywords never appear inside expressions unless explicitly allowed
- Statements control execution flow
- Expressions compute values only
- All blocks are explicit and use `{ }`
- Every block introduces a new lexical scope
- Grammar is LL(1) at the statement level
- No implicit syntax or shorthand forms are allowed

---

## 2. Lexical Structure

Identifiers  
NAME ::= [A-Za-z_][A-Za-z0-9_]*

Literals  
NUMBER  ::= integer | float  
STRING  ::= " ... "  
BOOLEAN ::= true | false

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

## 3. Program Structure

program ::= { statement }

---

## 4. Statements

statement ::=  
    import_stmt  
  | print_stmt  
  | var_decl  
  | assignment  
  | function_def  
  | class_def  
  | struct_def  
  | enum_def  
  | if_stmt  
  | while_stmt  
  | for_stmt  
  | try_stmt  
  | throw_stmt  
  | assert_stmt  
  | break_stmt  
  | continue_stmt  
  | return_stmt  
  | expr_stmt  

---

## 5. Blocks and Scope

block ::= "{" { statement } "}"

Rules:  
- Blocks are mandatory  
- No single-line blocks  
- No implicit blocks  
- Every block creates a new lexical scope  

---

## 6. Control Flow

If Statement  
if_stmt ::= "if" expr block { "elif" expr block } [ "else" block ]

While Loop  
while_stmt ::= "while" expr block

For Loop (Two Legal Forms Only)

Numeric For Loop  
for_stmt ::= "for" NAME "=" expr "to" expr [ "step" expr ] block

Iterable For Loop  
for_stmt ::= "for" NAME "in" primary [ "step" expr ] block

Rules:  
- After `in`, only a `primary` is allowed  
- Full expressions are forbidden after `in`  
- `step` is a loop modifier, not an operator  

---

## 7. Expressions

expr ::= or_expr

or_expr ::= and_expr { "or" and_expr }  
and_expr ::= not_expr { "and" not_expr }  
not_expr ::= [ "not" ] comparison  

comparison ::= sum { ( "==" | "!=" | "<" | ">" | "<=" | ">=" ) sum }  

sum ::= term { ( "+" | "-" ) term }  
term ::= factor { ( "*" | "/" | "%" ) factor }  

factor ::= "-" factor | primary  

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
  | "(" expr ")"  

Rules:  
- No keywords are allowed inside primary  
- Structural keywords are forbidden in expressions  

---

## 9. Function Calls and Access

call ::= primary "(" [ arguments ] ")"  
arguments ::= expr { "," expr }  

member_access ::= primary "." NAME  
index_access ::= primary "[" expr "]"  

---

## 10. Lists

list_literal ::= "[" [ expr { "," expr } ] "]"

---

## 11. Assignments (Statement Only)

assignment ::=  
    NAME "=" expr  
  | member_access "=" expr  
  | index_access "=" expr  

Rules:  
- Assignments are statements, never expressions  
- Chained assignments are not allowed  

---

## 12. Variable Declarations

var_decl ::=  
    "var" NAME [ "=" expr ]  
  | "const" NAME "=" expr  
  | "final" NAME "=" expr  
  | "static" NAME "=" expr  

---

## 13. Functions

function_def ::= "def" NAME "(" [ parameters ] ")" block  
parameters ::= NAME { "," NAME }

Rules:  
- Functions introduce a new scope  
- return exits the nearest function only  

---

## 14. Classes

class_def ::= "class" NAME [ "extends" NAME ] block

Rules:  
- Single inheritance only  
- Methods follow function grammar  
- this is implicitly bound in methods  

---

## 15. Structs

struct_def ::= "struct" NAME "{" { NAME } "}"

Rules:  
- Structs are value containers  
- No methods allowed  

---

## 16. Enums

enum_def ::= "enum" NAME "{" { NAME } "}"

---

## 17. Error Handling

try_stmt ::= "try" block [ "catch" [ "(" NAME ")" ] block ] [ "finally" block ]  
throw_stmt ::= "throw" expr  
assert_stmt ::= "assert" expr [ "," expr ]

---

## 18. Jump Statements

break_stmt ::= "break"  
continue_stmt ::= "continue"  
return_stmt ::= "return" [ expr ]

Rules:  
- break and continue apply only inside loops  
- return applies only inside functions  

---

## 19. Expression Statements

expr_stmt ::= expr

Rules:  
- Expression statements are evaluated for side effects only  
- Expressions cannot alter control flow  

---

## 20. Grammar Invariants (Non-Negotiable)

1. Keywords never appear inside expressions  
2. All blocks use `{ }`  
3. Assignments are statements only  
4. No implicit syntax  
5. No parser backtracking  
6. Grammar must remain LL(1) at statement level  
7. Any violation is a syntax error  

End of specification.
