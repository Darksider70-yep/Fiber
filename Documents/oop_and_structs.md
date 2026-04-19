# 🏗️ OOP, Structs, and Enums in Fiber

Fiber offers multiple ways to structure data and behavior, ranging from simple value containers to complex object hierarchies.

## 1. Classes and Instances

Classes in Fiber support inheritance, constructor logic, and method overriding.

### Defining a Class
```fiber
class Animal {
    def init(name) {
        this.name = name
    }

    def speak() {
        print this.name + " makes a sound"
    }
}
```

### Inheritance and Overriding
```fiber
class Dog extends Animal {
    def speak() {
        print this.name + " barks"
    }
}

var myDog = Dog("Buddy")
myDog.speak() # Buddy barks
```

## 2. Structs

Structs are lightweight data containers with no methods. They are ideal for passing around simple groups of data.

```fiber
struct Point { x, y }

var p = Point(10, 20)
print p.x  # 10
p.y = 30
```

## 3. Enums

Enums provide a way to define a set of named constants.

```fiber
enum Color { RED, GREEN, BLUE }

var myColor = Color.RED
if myColor == Color.RED {
    print "It's red!"
}
```

---

## 🛠️ Comparison Table

| Feature | Class | Struct | Enum |
| --- | --- | --- | --- |
| **Methods** | Yes | No | No |
| **Inheritance** | Yes | No | No |
| **Logic** | Behaviors & Data | Pure Data | Fixed Choice |
| **Usage** | Complex Systems | Points, Configs | States, Types |

### Pro-Tip: Using `this`
Inside a class method, `this` refers to the current instance. You can add new fields to an instance dynamically:
```fiber
def add_metadata(obj) {
    obj.metadata = "Active"
}
```
In Fiber, instances are extensible, similar to JavaScript objects or Python dictionaries.
