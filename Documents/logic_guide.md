# Fiber Logic & AI Training Guide 🌿🧠

Fiber provides a first-class logic engine that bridges the gap between discrete symbolic reasoning and continuous neural networks. This guide covers the features available in `lib/logic.fib`.

## 1. Propositional Logic
You can create symbolic logical expressions using standard operators or library functions.

```fiber
import logic

var P = expr("P")
var Q = expr("Q")

# Symbols support operators
var formula = P & (P >> Q)

print("Formula: " + str(formula))
print("Is Satisfiable: " + str(logic.sat(formula)))
```

## 2. Knowledge Base (KB)
The `KnowledgeBase` class uses **Resolution** inference to answer queries based on facts and rules.

```fiber
import logic

var kb = logic.KnowledgeBase()

# Rules: If it rains, the ground is wet
kb.tell(expr("Raining >> Wet"))

# Fact: It is raining
kb.tell(expr("Raining"))

# Ask: Is the ground wet?
var result = kb.ask(expr("Wet"))
print("Is the ground wet? " + str(result)) # Output: true
```

## 3. Predicate Logic (FOL)
Fiber supports quantifiers over finite domains, which is ideal for grounding rules in data.

```fiber
import logic

var domain = [1, 2, 3, 4, 5]

# forall x in domain, x > 0
var result = logic.forall(domain, def(x) { return x > 0 })
print("All > 0: " + str(result))
```

## 4. Neuro-Symbolic AI Training
This is the most powerful feature of the library. You can convert logical rules into differentiable loss functions for neural networks using **T-Norms**.

### Loss Conversion Strategies (Norms):
1. **Product**: Probabilistic interpretation ($A \cdot B$).
2. **Godel**: Min/Max interpretation.
3. **Lukasiewicz**: Bounded sum/diff.

### Example: Logic-Constrained Training
```fiber
import logic
import neural

# Define a logic rule: A must be equal to B
var rule = expr("A == B")

# Neural outputs (as tensors)
var out_a = tensor(0.8, true)
var out_b = tensor(0.2, true)

# Convert logic to loss
var loss = logic.as_loss(rule, {"A": out_a, "B": out_b}, "product")

print("Logical Loss: " + str(loss))
# Backward pass works!
backward(loss)
```
