# Changelog - Fiber

All notable changes to the Fiber language and its standard library will be documented in this file.

## [4.0.1] - "Emerald" - 2026-04-21
### Added
- **Core Language**:
    - Introduced the `>>` (Implies) operator for symbolic logic expressions.
    - Added `logic_symbols(expr)` built-in for variable discovery.
    - Implemented operator overloading for `FiberSymbolic` (`&`, `|`, `~`, `>>`, `==`).
- **Standard Library (`logic.fib`)**:
    - **Neuro-Symbolic Training**: New `LogicTrainer` and `Constraint` classes for differentiable logic optimization.
    - **Relational Reasoner**: Added `RelationalReasoner` for solving grid-based logical problems like Wumpus World.
    - **Fuzzy Quantifiers**: Added `fuzzy_forall` and `fuzzy_exists` to handle domain-wide truth aggregation.
    - **Knowledge Base**: Upgraded to `FuzzyKnowledgeBase` with differentiable inference support (`ask_differentiable`).
- **Utilities**:
    - Added `soft_predicate(name, x, y)` for natural relational logic construction.
- **VS Code Extension**:
    - Updated syntax highlighting to support the `>>` operator.
    - Updated snippets for new AI logic features.

### Changed
- **Lexer**: Optimized token order to prioritize logical operators.
- **Interpreter**: Improved `BinOp` execution to handle mixed Symbolic/Tensor operations more robustly.

### Fixed
- Fixed keyword collision where `step` (from for-loops) conflicted with method names in user code.
- Resolved issues with symbolic expression construction via strings in the AI bridge.

---

## [3.0.0] - "Gold" - 2026-04-20
### Added
- Bytecode compiler (`.fibc`) support.
- Standalone executable builder (`builder.py`).
- Official VS Code extension release.
- Added `sql`, `dataframe`, and `neural` libraries.
