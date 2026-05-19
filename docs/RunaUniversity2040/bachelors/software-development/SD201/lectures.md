# SD201: Object-Oriented Design & Patterns
## Bachelor of Science in Software Development — University of Yggdrasil, 2040

**Credits:** 4
**Semester:** Year 2, Semester 1
**Prerequisites:** SD101, SD103
**Instructor:** Dr. Eira Lundström, Faculty of Computational Arts

> *"A well-designed object is like a well-forged tool — it does one thing, does it well, and fits the hand of every craftsman who picks it up. The patterns are the sagas of our craft — stories of problems solved, passed down so we need not solve them again."* — Eira Lundström, *Weaving Thought* (2038)

---

## Course Description

Object-Oriented Design & Patterns teaches the art of structuring software as cooperating objects. Building on the programming fundamentals from SD101, this course covers the principles of object-oriented design (encapsulation, inheritance, polymorphism, composition), the SOLID principles that guide good class design, and the Gang of Four design patterns that have proven their value across decades. In 2040, when AI agents can generate classes and apply patterns automatically, the developer's role is not to memorize pattern implementations but to *recognize* when a pattern is needed, *evaluate* whether the AI's application is correct, and *adapt* patterns to the specific constraints of the problem.

The course culminates in a substantial design project where students architect a system using multiple patterns, document their design rationale, and defend their choices in a design review — the same process used in professional software organizations.

---

## Lectures

### ᚠ Lecture 1: The Object Philosophy — Encapsulation, Messages, and Thinking in Objects

**Date:** Week 1, Session 1

#### Overview

Object-oriented programming is not just syntax (`class`, `new`, `extends`). It is a philosophy of software organization: the world is composed of objects that communicate by sending messages. This lecture establishes the conceptual foundations: encapsulation (objects hide their state), messaging (objects interact through well-defined interfaces), and the shift from procedural thinking ("do this, then that") to object thinking ("what objects exist, and how do they collaborate?").

#### Lecture Notes

Alan Kay, who coined the term "object-oriented programming" in 1967, later said: "I'm sorry that I long ago coined the term 'objects' for this topic because it gets many people to focus on the lesser idea. The big idea is messaging." Kay's vision was not about classes and inheritance — those came later, from Simula. His vision was about *independent computational entities that communicate by sending and receiving messages*, like cells in a biological organism or computers on the internet.

This vision remains radical in 2040. Most "object-oriented" code is procedural code with classes — data structures with methods attached. True object-oriented design asks: what are the *autonomous agents* in this system, what do they *know*, and what *messages* do they understand?

**The Three Pillars:**

1. **Encapsulation.** An object bundles data (state) and behavior (methods) and hides its internal workings. You don't ask a `BankAccount` for its internal balance variable; you ask it to `deposit(amount)` or `withdraw(amount)`. The object enforces its own invariants (`balance >= 0`). Encapsulation is not just about `private` keywords — it's about *boundaries*. The object's internals can change completely without affecting any code that uses it, as long as the public interface remains stable.

2. **Inheritance.** A class can *inherit* behavior and structure from a parent class. `SavingsAccount` inherits from `BankAccount` and adds interest calculation. Inheritance models "is-a" relationships. It is the most overused and misunderstood OO feature — the 1990s assumption that deep inheritance hierarchies were the mark of good design led to fragile, incomprehensible codebases. The modern (2040) consensus: **prefer composition over inheritance.**

3. **Polymorphism.** Different objects can respond to the same message in different ways. A `render()` message to a `Button`, a `TextField`, and an `Image` each produces different behavior, but the caller doesn't need to know which type it's dealing with. Polymorphism is what makes OO systems extensible — you can add new types without changing existing code.

**Thinking in Objects.** The shift from procedural to object thinking is the hardest part of learning OO:

- Procedural: "First validate the input, then look up the user, then check permissions, then update the record, then send a notification."
- Object: "The `Request` validates itself. The `UserRepository` finds the user. The `PermissionChecker` verifies access. The `Record` updates itself. The `Notifier` sends the notification."

In the object model, each object is an expert at one thing. The system's behavior emerges from their collaboration. This is harder to trace in a debugger (the control flow jumps between objects) but easier to change (you modify one expert without touching the others).

**The 2040 Perspective.** AI code generation can produce classes and methods on demand. It can even suggest which objects should exist based on a problem description. What the AI cannot do — what requires human judgment — is decide the *granularity* of objects (how many? how large?), the *boundaries* between them (what does each know?), and the *evolution strategy* (how will this design accommodate changes we haven't anticipated yet?). These are the skills this course develops.

#### Required Reading

- Kay, A. (1993). "The Early History of Smalltalk." *ACM SIGPLAN Notices*, 28(3), 69-95. [Read for the vision, not the syntax.]
- Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley. Chapter 1: "Introduction." [We'll read this book throughout the course.]
- Lundström, E. (2038). *Weaving Thought*. Chapter 5: "Objects as Norns."

#### Discussion Questions

1. Alan Kay said "the big idea is messaging." How is messaging different from method calling? What capabilities does a true message-passing system have that method calls lack?
2. Encapsulation means hiding internal state. But many modern languages (Python, JavaScript) don't enforce privacy — they use conventions (`_private`). Is convention-based encapsulation sufficient, or does it lead to abuse?
3. "Prefer composition over inheritance" has been the consensus since the 1990s. Are there domains where deep inheritance hierarchies are genuinely the right choice?

---

### ᚢ Lecture 2: The SOLID Principles — Five Rules for Good Design

**Date:** Week 1, Session 2

#### Overview

Robert C. Martin's SOLID principles (2000) are the most influential set of object-oriented design guidelines ever published. This lecture explains each principle with concrete examples, counterexamples, and the reasoning behind them. By 2040, these principles have been refined and debated for two generations of developers — they are not dogma but *heuristics* that, when followed, produce code that is easier to understand, test, and change.

#### Lecture Notes

SOLID is an acronym for five design principles:

- **S**ingle Responsibility Principle
- **O**pen/Closed Principle
- **L**iskov Substitution Principle
- **I**nterface Segregation Principle
- **D**ependency Inversion Principle

**Single Responsibility Principle (SRP).** "A class should have only one reason to change." This does not mean "a class should do only one thing" — that's the Unix philosophy. SRP means: a class should be responsible to only one *stakeholder* or *axis of change*.

Consider an `Employee` class that calculates pay AND generates a report AND saves to the database. Three reasons to change: the payroll algorithm changes, the report format changes, the database schema changes. These changes come from different stakeholders (finance, management, operations). Coupling them means a change for one stakeholder can break functionality for another.

The fix: separate into `Employee` (data), `PayrollCalculator` (pay logic), `ReportGenerator` (formatting), and `EmployeeRepository` (persistence). Each class has one reason to change.

**Open/Closed Principle (OCP).** "Software entities should be open for extension but closed for modification." You should be able to add new behavior without changing existing code. This is achieved through polymorphism: define an interface (closed for modification) and add new implementations (open for extension).

Example: A `Shape` interface with `area()` method. `Circle` and `Rectangle` implement it. To add `Triangle`, you create a new class — you don't modify `Shape` or the existing implementations. The system is extended without modifying what already works.

OCP is the principle behind plugin architectures, strategy patterns, and dependency injection. It is the reason object-oriented systems can grow without becoming proportionally harder to maintain.

**Liskov Substitution Principle (LSP).** "Subtypes must be substitutable for their base types." If `Square` inherits from `Rectangle`, any code that works with `Rectangle` must work with `Square` without knowing the difference. This seems obvious until you realize: a `Square` with `setWidth(5)` and `setHeight(10)` is either no longer a square or violates the expectation that width and height are independent. The Square/Rectangle problem is the classic LSP violation: inheritance seems natural but produces surprising behavior.

LSP forces you to think about *behavioral contracts*, not just type signatures. A subclass must: accept the same inputs (or wider), produce the same outputs (or narrower), not throw unexpected exceptions, and preserve the invariants of the base class.

**Interface Segregation Principle (ISP).** "Clients should not be forced to depend on interfaces they do not use." A `Worker` interface with `work()`, `eat()`, and `sleep()` forces a `Robot` to implement `eat()` (which does nothing) or throw an exception. The fix: split into `Workable` (work) and `Living` (eat, sleep). `Human` implements both; `Robot` implements only `Workable`.

ISP prevents "fat interfaces" — interfaces with too many methods. Small, focused interfaces are easier to implement, test, and understand. In 2040, with AI-generated code, ISP is doubly important: the AI needs clear, minimal contracts to implement correctly.

**Dependency Inversion Principle (DIP).** "Depend on abstractions, not on concretions." High-level modules (business logic) should not depend on low-level modules (database access, file I/O). Both should depend on abstractions (interfaces).

```python
# BAD: high-level depends on low-level
class OrderService:
    def __init__(self):
        self.db = MySQLDatabase()  # concrete dependency

# GOOD: both depend on abstraction
class OrderService:
    def __init__(self, db: Database):  # depends on interface
        self.db = db
```

DIP enables: testing (inject a mock database), flexibility (swap MySQL for PostgreSQL without changing `OrderService`), and independent development (the database team and the business logic team work against the same interface).

**SOLID as a System.** The principles reinforce each other. SRP → small, focused classes. OCP → extend without modifying. LSP → subtypes that work. ISP → small interfaces. DIP → depend on those interfaces. Together, they produce systems that are *soft* — easy to change, because each change is localized to a small number of classes.

#### Required Reading

- Martin, R.C. (2000). "Design Principles and Design Patterns." *objectmentor.com*. [The original SOLID articles. Read the SRP and DIP ones especially.]
- Martin, R.C. (2017). *Clean Architecture*. Prentice Hall. Chapters 7-11 (the SOLID chapters).
- Lundström, E. (2040). "SOLID in the Age of AI: Does It Still Matter?" *Journal of Software Craftsmanship*, 6(4), 55-78.

#### Discussion Questions

1. SRP says "one reason to change." But "reason" is subjective — is a change to the payroll calculation formula one reason or two (formula change vs. tax rule change)? How do you determine the right granularity?
2. OCP requires that you anticipate the directions of extension. How do you know what to make "open"? If you make everything extendable, you get over-engineered abstractions. How do you find the balance?
3. DIP says "depend on abstractions." But abstractions can leak (every database abstraction eventually exposes database-specific behavior). Is DIP always achievable, or is it an asymptotic ideal?

---

### ᚦ Lecture 3: Creational Patterns — Factories, Builders, and the Art of Making Objects

**Date:** Week 2, Session 1

#### Overview

Creating objects is more subtle than calling `new`. Creational patterns abstract the instantiation process, decoupling client code from concrete classes and complex construction logic. This lecture covers the five creational patterns from the Gang of Four (Singleton, Factory Method, Abstract Factory, Builder, Prototype), plus the 2040-era Dependency Injection Container pattern that has largely subsumed them.

#### Lecture Notes

"New is glue." Every time you write `new ConcreteClass()`, you are permanently binding your code to that specific class. If you ever want to use a different class, you must change the code. Creational patterns break this binding — they let you create objects without specifying their exact class.

**Singleton.** Ensure a class has exactly one instance and provide global access to it. The most controversial pattern: it introduces global state (making testing and concurrency harder) and is often overused. In 2040, dependency injection containers manage instance lifetimes, making explicit Singletons rare. But the pattern's *intent* — "there should be only one" — remains valid for resources like database connection pools and configuration managers.

```python
class DatabasePool:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
```

**Factory Method.** Define an interface for creating an object, but let subclasses decide which class to instantiate. The "virtual constructor." A `Document` class has an abstract `create_page()` method; `Resume` and `Report` subclasses each create the appropriate type of page.

```python
class Document(ABC):
    @abstractmethod
    def create_page(self) -> Page:
        pass
    
    def render(self):
        page = self.create_page()  # factory method
        return page.render()
```

**Abstract Factory.** Provide an interface for creating *families* of related objects. A `UIFactory` interface with `create_button()` and `create_textfield()` methods; `WindowsFactory` and `MacFactory` each create widgets that match the platform. The client works with the abstract factory and never knows which platform it's on.

**Builder.** Separate the construction of a complex object from its representation. A `PizzaBuilder` accumulates crust, sauce, toppings, and cheese step by step, then `build()` returns the finished `Pizza`. Useful when an object has many optional parameters or when the construction process must be sequenced.

```python
pizza = PizzaBuilder()
    .crust("thin")
    .sauce("marinara")
    .add_topping("pepperoni")
    .add_topping("mushrooms")
    .cheese("mozzarella")
    .build()
```

**Prototype.** Create new objects by cloning an existing prototype. Useful when object creation is expensive (loading from a database or file) and you need many similar instances. The prototype is created once, then cloned — each clone can be customized.

**Dependency Injection (2040).** In modern practice, the DI Container has subsumed most creational patterns. You declare dependencies in constructors; the container resolves and injects them. The "factory" is the container's configuration. This doesn't make the patterns obsolete — it means you use them *declaratively* rather than imperatively:

```python
@Injectable
class OrderService:
    def __init__(self, db: Database, notifier: Notifier):
        self.db = db
        self.notifier = notifier
```

The container knows that `Database` means the PostgreSQL implementation and `Notifier` means the email implementation. Changing implementations means changing configuration, not code.

#### Required Reading

- Gamma et al. (1994). *Design Patterns*. Chapters on Singleton, Factory Method, Abstract Factory, Builder, Prototype.
- Fowler, M. (2004). "Inversion of Control Containers and the Dependency Injection Pattern." *martinfowler.com*. [The article that named DI.]
- University of Yggdrasil Hermes Documentation. "The Hlín Dependency Injection Container." *docs.yggdrasil.university/hermes/hlin*.

#### Discussion Questions

1. Singleton is widely considered an anti-pattern today. Is this a fair judgment, or are there legitimate uses? What are they?
2. The Builder pattern is verbose — a separate builder class for each complex object. In Python, keyword arguments and dataclasses often achieve the same result with less code. Is Builder still relevant in languages with rich literal syntax?
3. DI containers "just work" until they don't — circular dependencies, missing bindings, incorrect lifetimes. Is the complexity of DI containers worth the decoupling they provide?

---

### ᚨ Lecture 4: Structural Patterns — Adapters, Decorators, and the Art of Composition

**Date:** Week 2, Session 2

#### Overview

Structural patterns describe how objects and classes can be composed to form larger structures. This lecture covers the Gang of Four's structural patterns (Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy) with emphasis on the ones that remain most relevant in 2040: Adapter for legacy integration, Decorator for adding behavior without subclassing, and Composite for tree structures.

#### Lecture Notes

"The whole is greater than the sum of its parts." Structural patterns are about *composition* — how you combine simple pieces into complex wholes while keeping the pieces simple and independent.

**Adapter.** Convert the interface of a class into another interface clients expect. The universal translator. When you need to use a library that returns XML but your system expects JSON, you write an `XmlToJsonAdapter` that wraps the library and translates. The adapter is the pattern that makes the polyglot ecosystem of 2040 work — every service, every API, every library can be adapted to any interface.

```python
class StripePaymentAdapter(PaymentProcessor):
    def __init__(self, stripe_client: StripeClient):
        self.stripe = stripe_client
    
    def process_payment(self, amount: Money, source: PaymentSource) -> Receipt:
        # Translate our interface into Stripe's interface
        stripe_response = self.stripe.charge(
            amount=amount.cents,
            currency=amount.currency,
            source=source.token
        )
        # Translate Stripe's response into our format
        return Receipt.from_stripe(stripe_response)
```

**Decorator.** Attach additional responsibilities to an object dynamically. A `CompressionDecorator` wraps a `DataStream` and compresses data before writing. A `LoggingDecorator` wraps a `Repository` and logs every query. Decorators stack: you can have `LoggingDecorator(CachingDecorator(DatabaseRepository()))`.

Decorators follow the same interface as the objects they wrap, so they're transparent to clients. This is the pattern behind Python's `@decorator` syntax and middleware in web frameworks. In 2040, AI-generated middleware chains are composed of decorators — each adding one concern (auth, logging, rate limiting, caching).

**Composite.** Compose objects into tree structures to represent part-whole hierarchies. A `File` and a `Directory` both implement `FileSystemNode`. `Directory` contains a list of `FileSystemNode` children. The client treats individual files and entire directory trees uniformly.

```
FileSystemNode (interface)
├── File (leaf)
└── Directory (composite)
    ├── File
    ├── File
    └── Directory
        └── File
```

Composite is the pattern behind GUI widget trees, document object models, and the nested component hierarchies of modern web frameworks. If you've ever written `<div><p>Hello</p><p>World</p></div>`, you've used the Composite pattern.

**Facade.** Provide a simplified interface to a complex subsystem. A `VideoConverter` facade exposes `convert(source, format)` while internally orchestrating: demuxing, decoding, filtering, encoding, and muxing. The facade is the pattern for making complex systems approachable.

**Flyweight.** Share common state across many objects to reduce memory. A text editor stores one `CharacterStyle` object for "12pt Arial Bold" and thousands of characters reference it, rather than each character storing its own style. The pattern behind string interning, connection pooling, and cache deduplication.

**Proxy.** Provide a placeholder for another object to control access. `LazyProxy` loads the real object only when first accessed. `RemoteProxy` communicates with an object on another machine. `ProtectionProxy` checks permissions before forwarding method calls. Proxies are everywhere in 2040's distributed systems — every remote service call goes through a proxy that handles network failures, retries, and authentication.

**2040 Insight: Decorator vs. Inheritance.** The Decorator pattern is the practical expression of "prefer composition over inheritance." Instead of creating `CachingDatabaseRepository`, `LoggingDatabaseRepository`, and `CachingLoggingDatabaseRepository` subclasses, you compose decorators: `LoggingDecorator(CachingDecorator(DatabaseRepository()))`. Every combination is available without combinatorial subclass explosion. AI code generators in 2040 excel at suggesting decorator compositions: "Add caching to this repository" → the AI wraps it in a `CachingDecorator`.

#### Required Reading

- Gamma et al. (1994). *Design Patterns*. Chapters on Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy.
- Freeman, E. & Robson, E. (2035). *Head First Design Patterns* (3rd ed.). O'Reilly Media. Chapters on Decorator and Adapter. [These chapters are particularly well-explained.]
- Lundström, E. (2041). "Decorators in the Age of AI: Stacking Behaviors." *IEEE Software*, 58(4), 34-42.

#### Discussion Questions

1. The Decorator pattern requires that all decorators implement the same interface. This makes them composable but can lead to long chains. At what point is a decorator chain too long? How do you debug a stack of 10 decorators?
2. Adapter vs. Facade — both wrap something. What's the difference? When would you use one vs. the other?
3. Flyweight trades complexity (shared state management) for memory efficiency. In 2040, when memory is abundant and cheap, is Flyweight still relevant? When would you reach for it?

---

### ᚱ Lecture 5: Behavioral Patterns — Strategies, Observers, and the Flow of Control

**Date:** Week 3, Session 1

#### Overview

Behavioral patterns describe how objects interact and distribute responsibility. This lecture covers the Gang of Four's behavioral patterns with focus on the ones that dominate 2040 software: Strategy (pluggable algorithms), Observer (event-driven architecture), Command (undo/redo, job queues), and State (finite state machines). We examine how modern async/await and reactive programming have evolved these patterns.

#### Lecture Notes

If structural patterns are about *what* objects are made of, behavioral patterns are about *how* they communicate. They define the protocols of collaboration — the messages, the handoffs, the chains of responsibility.

**Strategy.** Define a family of algorithms, encapsulate each one, and make them interchangeable. A `SortStrategy` interface with `BubbleSort`, `QuickSort`, and `MergeSort` implementations. The client chooses the appropriate strategy based on data characteristics — small data gets insertion sort, large data gets quicksort, nearly-sorted data gets Timsort.

```python
class PaymentProcessor:
    def __init__(self, strategy: PaymentStrategy):
        self.strategy = strategy
    
    def process(self, amount: Money):
        return self.strategy.pay(amount)

# Usage
processor = PaymentProcessor(CreditCardStrategy())
processor.process(Money(100, "USD"))  # pays by credit card

processor.strategy = PayPalStrategy()
processor.process(Money(50, "USD"))   # pays by PayPal
```

Strategy is the pattern behind dependency injection, plugin architectures, and the "composition over inheritance" principle. It is the most widely used behavioral pattern in 2040 — every service that accepts a configurable algorithm uses Strategy.

**Observer.** Define a one-to-many dependency: when one object changes state, all its dependents are notified automatically. The `WeatherStation` (subject) notifies `PhoneDisplay`, `WebDashboard`, and `AlertSystem` (observers) whenever the temperature changes.

In 2040, Observer has evolved into:
- **Event buses and message queues:** RabbitMQ, Kafka, Redis Pub/Sub — the Observer pattern at infrastructure scale
- **Reactive programming:** RxJS, ReactiveX, Combine — declarative Observer with operators for filtering, transforming, and combining event streams
- **The VERÐANDI nervous system:** Hermes' event architecture is the Observer pattern applied to AI agent state — "when a memory is stored, notify all interested subsystems"

**Command.** Encapsulate a request as an object. A `SaveCommand` stores all information needed to save a document. Commands can be queued, logged, undone, and replayed.

```python
class SaveCommand(Command):
    def __init__(self, document: Document, path: str):
        self.document = document
        self.path = path
        self.backup = None  # for undo
    
    def execute(self):
        self.backup = self.document.content
        save_to_disk(self.document, self.path)
    
    def undo(self):
        self.document.content = self.backup
```

Command is the pattern behind: undo/redo in editors (maintain a stack of executed commands), job queues (serialize commands to a queue for async processing), macro recording (record a sequence of commands and replay them), and the CQRS (Command Query Responsibility Segregation) architecture used in Hermes' memory well operations.

**State.** Allow an object to alter its behavior when its internal state changes. A `Document` with states `Draft`, `Review`, and `Published`. `publish()` transitions Draft→Review→Published. The same method behaves differently depending on state.

```python
class DraftState(DocumentState):
    def publish(self, doc):
        doc.state = ReviewState()
        return "Document submitted for review"
    
    def edit(self, doc, content):
        doc.content = content
        return "Draft updated"

class PublishedState(DocumentState):
    def publish(self, doc):
        raise InvalidTransition("Already published")
    
    def edit(self, doc, content):
        raise InvalidTransition("Cannot edit published document")
```

State is the pattern behind: workflow engines, game AI (patrol → chase → attack → retreat), TCP connection states, and the lifecycle management in Hermes subagents.

**2040 Evolution: Async and Reactive.** The behavioral patterns of 1994 assumed synchronous method calls. In 2040, asynchronous and reactive programming have transformed them:
- Observer → `AsyncIterator` and `Stream`: observers that yield control back to the event loop
- Command → async command handlers with retry and timeout
- Strategy → strategies that can be hot-swapped without restarting the system
- Chain of Responsibility → middleware pipelines in async web frameworks (FastAPI, Axum)

The patterns remain; their implementation has evolved.

#### Required Reading

- Gamma et al. (1994). *Design Patterns*. Chapters on Strategy, Observer, Command, State, Template Method, Chain of Responsibility.
- Freeman & Robson (2035). *Head First Design Patterns*. Chapters on Strategy, Observer, Command, State.
- Hermes Agent Documentation. "The VERÐANDI Event Architecture and the Observer Pattern." *docs.yggdrasil.university/hermes/verdandi*.

#### Discussion Questions

1. The Observer pattern can lead to cascading updates — one change triggers observers that trigger more observers. How do you prevent infinite loops or excessive computation in Observer chains?
2. The State pattern replaces conditional logic (`if state == DRAFT: ... elif state == REVIEW: ...`) with polymorphism. Is this always an improvement, or are there cases where a simple conditional is clearer?
3. In 2040, event-driven architectures (Kafka, VERÐANDI) have replaced the in-process Observer pattern for most systems. Is the in-process Observer still relevant outside of GUI programming?

---

### ᚲ Lecture 6: Composition Over Inheritance — The Modern OO Paradigm

**Date:** Week 3, Session 2

#### Overview

"Prefer composition over inheritance." This maxim, from the Gang of Four's introduction, has become the defining principle of 21st-century object-oriented design. This lecture explains *why* inheritance fails at scale (the fragile base class problem, the diamond problem, deep hierarchy rigidity) and *how* composition, interfaces, and delegation achieve the same goals with better outcomes.

#### Lecture Notes

Inheritance seems elegant. A `Bird` class with `fly()` and `eat()`. An `Eagle` that inherits from `Bird` — it gets flying and eating for free. An `Ostrich`... wait. Ostriches don't fly. We could override `fly()` to throw an exception — but that violates Liskov Substitution. We could restructure the hierarchy — `FlyingBird` and `FlightlessBird` under `Bird`. But then where does `Bat` (a flying mammal) fit? The hierarchy, which seemed natural, becomes a tangle of special cases.

**The Problems with Inheritance:**

1. **The Fragile Base Class Problem.** Changing a method in the base class can break subclasses in unexpected ways. The subclass author assumed certain behavior; the base class author (who may be on a different team, or a different version of the library) changed it. The subclass breaks without any code change on the subclass side.

2. **The Diamond Problem.** `Scanner` and `Printer` both inherit from `PoweredDevice`. `MultiFunctionPrinter` inherits from both `Scanner` and `Printer`. Does it have one `power_on()` method or two? Different languages resolve this differently (C++ virtual inheritance, Python MRO, Java single inheritance for classes), but the conceptual tangle remains.

3. **Deep Hierarchy Rigidity.** A five-level inheritance hierarchy (`Entity → Character → PlayerCharacter → Mage → FireMage`) encodes assumptions at each level. Changing the third level affects everything below. Adding a new middle category requires restructuring. The hierarchy becomes frozen.

4. **Overexposure.** Subclasses inherit everything — including implementation details that should have been private. Protected members are "public to subclasses, private to everyone else" — a leaky distinction that exposes internals.

**Composition to the Rescue.** Instead of inheriting behavior, *compose* objects that *have* the behavior:

```python
# Inheritance (brittle)
class Bird:
    def fly(self): ...
    def eat(self): ...

class Eagle(Bird):  # inherits fly and eat
    pass

class Penguin(Bird):  # overrides fly to do nothing — LSP violation
    def fly(self):
        raise NotImplementedError("Penguins don't fly")

# Composition (flexible)
class FlyBehavior(Protocol):
    def fly(self): ...

class SoarBehavior:
    def fly(self): return "Soaring high"

class NoFlyBehavior:
    def fly(self): return "Can't fly"

class Bird:
    def __init__(self, fly_behavior: FlyBehavior):
        self.fly_behavior = fly_behavior
    
    def fly(self):
        return self.fly_behavior.fly()

eagle = Bird(SoarBehavior())
penguin = Bird(NoFlyBehavior())
```

The composed `Bird` can have any flying behavior, swapped at runtime. Adding a new flying behavior doesn't affect existing code. The `Bird` class is closed for modification, open for extension — OCP achieved through composition.

**Interfaces and Delegation.** Composition works best with interfaces (protocols in Python, traits in Rust, typeclasses in Haskell). An interface declares *what* an object can do without specifying *how*. Classes implement interfaces. Objects delegate to each other through interface references.

```python
class PaymentProcessor:
    def __init__(self, gateway: PaymentGateway):  # depends on interface
        self.gateway = gateway
    
    def process(self, payment: Payment):
        # Delegate to the gateway
        return self.gateway.charge(payment.amount, payment.source)
```

**When Inheritance IS Appropriate.** Inheritance still has its place:
- **Framework integration:** Django models inherit from `Model`; React components extend `Component`. The framework provides behavior through a well-defined, stable base class.
- **True "is-a" relationships:** A `Square` truly *is* a `Rectangle` (mathematically). If the behavioral contract holds, inheritance is fine.
- **Mixin classes:** Small, focused classes that add one capability (e.g., `Comparable`, `Serializable`, `Logging`) — used with multiple inheritance in Python or as traits in Rust.

The heuristic: **inherit from abstractions (interfaces, abstract base classes); compose concrete behavior.** If the base class has implementation, prefer composition.

#### Required Reading

- Gamma et al. (1994). *Design Patterns*. Introduction, "Favor object composition over class inheritance."
- Bloch, J. (2018). *Effective Java* (4th ed.). Addison-Wesley. Item 18: "Favor composition over inheritance."
- Lundström, E. (2039). "The Inheritance Hangover: Recovering from Deep Hierarchies." *Communications of the ACM*, 62(8), 38-46.

#### Discussion Questions

1. Is "always use composition" as dogmatic as "always use inheritance"? Are there situations where composition makes code harder to understand than a simple inheritance hierarchy?
2. Mixins/traits blur the line between inheritance and composition — they allow inheriting behavior without deep hierarchies. Are mixins a solution to inheritance's problems, or do they introduce new ones?
3. The Rust language has no class inheritance at all — only traits (interfaces) and composition. Is Rust evidence that inheritance is entirely unnecessary? Or does Rust's model have its own pain points?

---

### ᚷ Lecture 7: Domain-Driven Design — Objects in Their Natural Habitat

**Date:** Week 4, Session 1

#### Overview

Object-oriented design is not just about code structure — it's about modeling the real world (or the business domain) in software. Domain-Driven Design (Eric Evans, 2003) provides a vocabulary for this: entities, value objects, aggregates, repositories, bounded contexts, and the ubiquitous language. This lecture connects OO principles to domain modeling, the practice that turns business requirements into maintainable software.

#### Lecture Notes

The hardest problem in software is not writing code. It is understanding what the code should do. Domain-Driven Design (DDD) addresses this by centering the *domain* — the business, the problem space, the real world the software serves.

**The Ubiquitous Language.** Developers and domain experts (the people who understand the business) must share a common vocabulary. Not "the `tbl_user_account` table" but "a Customer." Not "set the `is_active` flag" but "activate the Account." This language is used in conversation, in documentation, in code. When the code says `customer.activate()`, everyone — developer, product manager, accountant — knows what it means.

The ubiquitous language eliminates the translation step where requirements are misunderstood, then coded incorrectly, then discovered to be wrong months later.

**Entities vs. Value Objects:**

- **Entity:** An object defined by its *identity*, not its attributes. A `Customer` is the same customer even if they change their email, address, and name. Identity persists through change. Entities have lifecycles — created, modified, archived. Entities are mutable.

- **Value Object:** An object defined by its *attributes*, not its identity. A `Money` object with amount 100 and currency USD — two `Money(100, "USD")` objects are interchangeable because they have the same value. Value objects are immutable. Change a value object by replacing it: `price = price.with_discount(0.1)` returns a new `Money`, doesn't modify the old one.

Getting this distinction right is the single most important DDD skill. Confusing entities and value objects leads to: identity crises (what identifies this thing?), unnecessary complexity (managing identity for things that don't need it), and mutation bugs (modifying a value object that's shared).

**Aggregates.** A cluster of entities and value objects treated as a unit. An `Order` aggregate contains `OrderLine` value objects. External objects reference only the aggregate root (`Order`), not its internals. The aggregate root enforces invariants: "an order's total must equal the sum of its line item totals."

Aggregates define *transaction boundaries*. When you save an aggregate, all its internals are saved together. When you load an aggregate, you get a consistent snapshot. This is the pattern that makes DDD work with databases.

**Repositories.** Mediate between the domain and data storage. A `CustomerRepository` provides `find_by_id(id)`, `save(customer)`, `find_by_email(email)`. The domain code never touches SQL or ORM calls — it works entirely through repositories. This keeps the domain pure and testable.

**Bounded Contexts.** A large system contains multiple models. The `Customer` in the Sales context (name, contact info, credit rating) is different from the `Customer` in the Support context (ticket history, satisfaction score, support tier). They may share an ID, but they are different models with different meanings.

Bounded contexts are DDD's answer to the monolith: you don't need one unified model of the entire enterprise. Each subsystem has its own model, optimized for its own concerns. Context maps define how contexts relate: shared kernel, customer/supplier, conformist, anti-corruption layer.

**DDD in 2040.** The Hermes framework itself is a DDD system: `Memory` is an entity (identity by hash), `ConversationTurn` is an entity, `EmotionalState` is a value object. The `MimirRepository` mediates between the domain and the memory database. `BoundedContexts` separate the chat system from the task system from the personality system. DDD is not a methodology you choose — it's the architecture that emerges when you take the domain seriously.

#### Required Reading

- Evans, E. (2003). *Domain-Driven Design: Tackling Complexity in the Heart of Software*. Addison-Wesley. Part II: "The Building Blocks of a Model-Driven Design."
- Vernon, V. (2013). *Implementing Domain-Driven Design*. Addison-Wesley. Chapters 5 (Entities), 6 (Value Objects), 7 (Services), 10 (Aggregates).
- Hermes Architecture Documentation. "Domain Model: Entities, Values, and Aggregates." *docs.yggdrasil.university/hermes/domain-model*.

#### Discussion Questions

1. Entities have identity; value objects don't. Is a phone number an entity or a value object? What about a reservation? What about a programming language keyword? The line is fuzzier than it seems.
2. Bounded contexts require defining boundaries — which parts of the system share a model and which don't. What happens when bounded contexts are too large (everything is one model) or too small (every class is its own context)?
3. In 2040, AI can generate domain models from requirements documents. What can the AI get right? What requires human judgment about the domain?

---

### ᚹ Lecture 8: Testing Object-Oriented Systems — Mocks, Fixtures, and Testability

**Date:** Week 4, Session 2

#### Overview

Object-oriented code should be testable code. This lecture connects OO design to automated testing: how SOLID principles enable unit testing, how dependency injection enables mocking, and how to write tests that verify behavior without coupling to implementation. We cover the testing pyramid, test doubles (mocks, stubs, fakes), and the 2040-era AI-augmented test generation.

#### Lecture Notes

"If it's hard to test, it's badly designed." This heuristic — known as the testability heuristic — is one of the most powerful feedback loops in software development. Code that is hard to test has design problems: too many dependencies, hidden state, tight coupling. Fixing testability often fixes the design.

**Why OO Code Is Testable (When Done Right).** The SOLID principles directly enable testing:

- **SRP:** A class with one responsibility has few dependencies and clear behavior. Easy to test.
- **DIP:** Depend on abstractions. Tests can substitute mock implementations for real ones (`MockDatabase` instead of `PostgreSQL`).
- **ISP:** Small interfaces mean small mocks. A `UserRepository` with 3 methods is easier to mock than a `DataAccessLayer` with 50 methods.
- **LSP:** Any mock that implements the interface should be substitutable for the real implementation. The tests are valid.

**The Testing Pyramid.**  

```
        ╱  E2E  ╲        — Few: slow, expensive, fragile
      ╱ Integration ╲    — Some: verify interactions
    ╱   Unit Tests    ╲  — Many: fast, cheap, reliable
```

- **Unit tests:** Test individual classes in isolation. Fast (milliseconds), no network, no database. 70% of your tests should be unit tests.
- **Integration tests:** Test interactions between classes, or between your code and real infrastructure. A few seconds each. 20% of tests.
- **End-to-end tests:** Test the entire system from the user's perspective. Slow (minutes), flaky, expensive. 10% or fewer.

The pyramid ratios are aspirational — real projects have whatever test mix keeps them confident. But the principle holds: prefer fast, isolated tests.

**Test Doubles.** When testing a class, replace its dependencies with doubles:

- **Stub:** Returns fixed data. "When asked for user 42, always return `User('Alice')`."
- **Mock:** Records interactions and verifies they happened. "Assert that `notifier.notify()` was called exactly once with the correct message."
- **Fake:** A simplified but functional implementation. An in-memory `UserRepository` instead of a PostgreSQL one.
- **Spy:** A hybrid — a stub that also records. "Return this data, and let me check afterward whether the method was called."

The 2040 consensus: **prefer fakes over mocks where possible.** Mocks verify *how* something was done (implementation detail). Fakes verify *what* was done (behavior). Mocks couple tests to implementation; fakes verify outcomes.

**Test-Driven Development (TDD).** Red → Green → Refactor. Write a failing test (Red), write the minimum code to make it pass (Green), improve the design without changing behavior (Refactor). TDD is not about testing — it's about *design*. The test is the first client of your code. If the test is awkward to write, the code's interface is awkward to use.

In 2040, AI test generation has transformed TDD: you describe the desired behavior, the AI generates the test and the implementation, and you verify both. But the discipline of specifying behavior before implementation — of thinking about *what* before *how* — remains as valuable as ever.

**Testability Anti-Patterns:**
- `new` in constructors (can't substitute dependencies)
- Static methods that access global state (can't isolate)
- `System.currentTimeMillis()` called directly (can't control time)
- `new Thread()` (can't control concurrency)
- Singletons with mutable state (tests interfere with each other)

Each anti-pattern is a design smell. Fixing it for testability improves the design for production.

#### Required Reading

- Beck, K. (2002). *Test-Driven Development: By Example*. Addison-Wesley. Part I: "The Money Example."
- Fowler, M. (2007). "Mocks Aren't Stubs." *martinfowler.com*.
- Hermes Testing Guide. "Testing Subagents and the NornOrchestrator." *docs.yggdrasil.university/hermes/testing*.

#### Discussion Questions

1. Mocks verify interactions; fakes verify outcomes. Mocks are more precise but more brittle. When is each appropriate?
2. "Don't mock what you don't own" — don't mock third-party libraries; wrap them in your own interface and mock that. Is this always practical? What's the cost?
3. AI test generation can produce 100% code coverage. Does 100% coverage mean the code is well-tested? What can AI-generated tests miss?

---

### ᚺ Lecture 9: Refactoring — Improving Design Without Changing Behavior

**Date:** Week 5, Session 1

#### Overview

Design is not a one-time activity — it evolves as requirements change and understanding deepens. Refactoring is the discipline of improving internal structure without changing external behavior. This lecture covers Fowler's catalog of refactorings, the "code smells" that indicate when to refactor, and the safety net of tests that makes refactoring safe. In 2040, AI can perform many refactorings automatically — the human's role is deciding *what* to refactor and *when*.

#### Lecture Notes

"First make it work. Then make it right. Then make it fast." Refactoring is the "make it right" step. You have working code. It has tests. Now you improve its design — rename confusing variables, extract helper methods, break large classes into smaller ones, replace inheritance with composition. The tests ensure you haven't broken anything.

**Code Smells.** Martin Fowler's catalog of "smells" — indicators that code might need refactoring:

- **Long Method:** A method longer than ~10-15 lines. Extract smaller methods with descriptive names.
- **Large Class:** A class with too many responsibilities. Extract classes for each responsibility (SRP).
- **Long Parameter List:** More than 3-4 parameters. Introduce a parameter object.
- **Divergent Change:** One class changes for different reasons. Split it (SRP again).
- **Shotgun Surgery:** One change requires modifying many classes. The responsibility is scattered — consolidate it.
- **Feature Envy:** A method uses another class's data more than its own. Move the method to the other class.
- **Data Clumps:** The same group of fields appears together in multiple places. Extract them into a class.
- **Primitive Obsession:** Using primitive types (strings, ints) for domain concepts. Replace with value objects (`Email` instead of `str`, `Temperature` instead of `float`).
- **Switch Statements:** Complex conditionals based on type. Replace with polymorphism (Strategy or State patterns).
- **Comments:** Comments that explain *what* the code does (as opposed to *why*). The code should be clear enough that the comment is unnecessary. Extract the commented block into a well-named method.

**The Refactoring Catalog.** Key refactorings everyone should know:

- **Extract Method:** Turn a code fragment into a method with a descriptive name.
- **Rename:** Change a variable, method, or class name to better express its purpose.
- **Move Method/Field:** Move a method or field to a more appropriate class.
- **Extract Class:** Split one class into two when it has too many responsibilities.
- **Inline Class/Temp:** The reverse — merge a class or variable that isn't pulling its weight.
- **Replace Temp with Query:** Replace a temporary variable with a method call.
- **Replace Conditional with Polymorphism:** Replace `if type == 'circle': ... elif type == 'square': ...` with `circle.area()` and `square.area()`.
- **Replace Inheritance with Delegation:** When a subclass doesn't truly "is-a" the base, replace inheritance with composition.

**The Safety Net.** You cannot refactor without tests. The definition of refactoring is "changing structure without changing behavior." Without tests, you don't know if behavior changed. With tests, refactoring is safe and even enjoyable — a rhythmic cycle of small improvements, each verified by the green bar.

**Refactoring in 2040.** AI refactoring tools (Hermes Refactor, Sourcery, GitHub Copilot Refactor) can suggest and perform many refactorings automatically:
- "Extract this block into a method" → one click
- "Replace this conditional with polymorphism" → AI generates the strategy pattern
- "Rename this variable to better express its purpose" → AI suggests names based on usage

But the AI cannot decide *whether* the refactoring is worth doing. Extract Method costs a level of indirection — the code is clearer but now requires jumping to another method. Every refactoring is a tradeoff. The human decides: does this refactoring improve the design enough to justify the added complexity? The AI executes; the human judges.

#### Required Reading

- Fowler, M. (2018). *Refactoring: Improving the Design of Existing Code* (2nd ed.). Addison-Wesley. Chapters 1-3 (the refactoring example is worth reading in detail).
- Kerievsky, J. (2004). *Refactoring to Patterns*. Addison-Wesley. [Read for understanding how refactoring leads toward patterns, not away from them.]
- Lundström, E. (2040). "AI-Assisted Refactoring: A Year in Practice." *IEEE Software*, 57(3), 66-75.

#### Discussion Questions

1. "Refactoring should never be scheduled — it should be continuous, part of every change." Is this realistic? When does refactoring need dedicated time?
2. Some refactorings (Extract Method) make code more readable but add indirection. How do you decide when the indirection is worth it?
3. AI can perform refactorings, but it doesn't understand the domain. Could an AI-driven refactoring make the code technically cleaner but domain-confusing? Give an example.

---

### ᚾ Lecture 10: Object-Oriented Anti-Patterns — What Not to Do

**Date:** Week 5, Session 2

#### Overview

For every good pattern, there is a bad one — an *anti-pattern* that looks like a good idea but leads to pain. This lecture surveys the classic OO anti-patterns: the God Object, the Anemic Domain Model, the Poltergeist, the Singleton Overuse, the Yo-Yo Problem, and the 2040-era AI-generated anti-patterns that emerge when AI writes OO code without architectural oversight.

#### Lecture Notes

Anti-patterns are seductive. They often start as reasonable solutions that grow unchecked. Recognizing them — in your own code and in code reviews — is a critical skill.

**The God Object.** A single class that knows too much and does too much. It manages the database, handles HTTP requests, formats reports, and sends emails. It has 5,000 lines and 200 methods. It is the single point of failure for the entire system.

Symptoms: the class name ends in `Manager`, `Handler`, `System`, or `Context`. Nobody wants to touch it. Every change requires understanding all 5,000 lines.

Cure: apply SRP. Extract `DatabaseManager`, `RequestHandler`, `ReportFormatter`, `EmailSender`. The God Object becomes a coordinator that delegates to specialists.

**The Anemic Domain Model.** Classes that have data (getters and setters) but no behavior. All the behavior is in "service" classes that operate on the data. This is procedural programming in OO clothing.

```python
# Anemic: data without behavior
class Order:
    def get_total(self): return self._total
    def set_total(self, total): self._total = total
    def get_status(self): return self._status
    def set_status(self, status): self._status = status

class OrderService:
    def cancel(self, order: Order):
        if order.get_status() == "pending":
            order.set_status("cancelled")
```

Versus:

```python
# Rich domain model
class Order:
    def cancel(self):
        if self.status == "pending":
            self.status = "cancelled"
        else:
            raise InvalidTransition(f"Cannot cancel {self.status} order")
```

The anemic model's logic is scattered across services. The rich model encapsulates behavior with data. The anemic model violates the fundamental OO principle: objects should have behavior.

**The Poltergeist.** A class that exists only to call another class, adding no value. `UserController` receives an HTTP request, extracts parameters, and passes them to `UserService` — without any transformation, validation, or decision-making. The Poltergeist is pure overhead.

Cure: eliminate the middleman. If the controller adds nothing, the framework should route directly to the service. Or: the controller should actually do something (validate, transform, authorize).

**Singleton Overuse.** Singletons everywhere: `Config.getInstance()`, `Logger.getInstance()`, `DatabasePool.getInstance()`, `Cache.getInstance()`. Global state makes testing a nightmare (tests interfere through shared singletons), concurrency dangerous (shared mutable state), and dependencies invisible (you can't tell from the constructor what a class depends on).

Cure: dependency injection. Pass `Config`, `Logger`, `DatabasePool` as constructor parameters. The DI container manages their lifetimes.

**The Yo-Yo Problem.** Deep inheritance hierarchies where you must bounce up and down the hierarchy to understand behavior. `FireMage → Mage → PlayerCharacter → Character → Entity → GameObject`. To understand what `attack()` does, you trace through six classes, each overriding part of the behavior.

Cure: flatten the hierarchy. Compose behaviors. A `Character` *has* an `AttackBehavior`, rather than inheriting it from a five-level chain.

**2040 AI Anti-Patterns:**

- **Class Explosion:** AI generates a separate class for every minor variation — `RedButton`, `BlueButton`, `LargeButton`, `SmallRedButton`. The combinatorial explosion that OO patterns were designed to avoid.
- **Decorator Flood:** AI wraps every service in 15 decorators (logging, caching, retry, auth, validation, metrics, tracing, rate limiting, circuit breaking, timeout...) creating chains that are impossible to debug.
- **Pattern Misapplication:** AI applies patterns mechanically without understanding context. "This looks like a Strategy pattern situation" — even when a simple `if` statement would be clearer.
- **Over-Abstraction:** AI generates interfaces for everything — `IString`, `IUser`, `IUserRepository`, `IUserRepositoryFactory`. Interfaces that have exactly one implementation and will never have another. "Abstraction for abstraction's sake."

The antidote to AI anti-patterns is the same as for human anti-patterns: code review, simplicity heuristics (YAGNI — You Aren't Gonna Need It), and the willingness to delete abstractions that aren't pulling their weight.

#### Required Reading

- Brown, W.J. et al. (1998). *AntiPatterns: Refactoring Software, Architectures, and Projects in Crisis*. Wiley. Chapters on The Blob (God Object) and Poltergeists.
- Fowler, M. (2003). "Anemic Domain Model." *martinfowler.com*. [Read this to understand why "rich" domain models matter.]
- Lundström, E. (2042). "AI-Generated Anti-Patterns: A Taxonomy." *Proceedings of the International Conference on Software Engineering*, 2042.

#### Discussion Questions

1. The Anemic Domain Model is the default in many frameworks (Spring, ASP.NET) because they encourage service classes operating on data objects. Is this a framework problem or a developer education problem?
2. "Over-abstraction" — interfaces that have one implementation — is widely condemned. But what if the second implementation arrives next year? Is it worth adding an interface preemptively?
3. AI anti-patterns are new, but they rhyme with old anti-patterns (Class Explosion = Combinatorial Inheritance). Are AI anti-patterns fundamentally different, or just faster versions of human mistakes?

---

### ᛁ Lecture 11: Beyond Objects — Functional, Reactive, and Agent-Oriented

**Date:** Week 6, Session 1

#### Overview

Object-oriented programming is not the only paradigm, and in 2040, it is rarely used in isolation. This lecture examines how OO integrates with other paradigms: functional programming (immutability, pure functions, monads), reactive programming (streams, observables, dataflow), and the 2040-era agent-oriented programming where autonomous AI agents replace passive objects.

#### Lecture Notes

The programming paradigms of the 20th century — procedural, object-oriented, functional, logic — were seen as competing. The 21st century revealed they are complementary. Modern systems use all of them, each where it fits best.

**Functional in an OO World.** Functional programming emphasizes:
- **Immutability:** Data doesn't change; transformations create new data. An `Order` value object is never modified — `order.with_discount(0.1)` returns a new `Order`.
- **Pure functions:** Functions that depend only on their inputs and produce only their outputs. No side effects. Easier to test, reason about, and parallelize.
- **Higher-order functions:** Functions that take or return functions. `map`, `filter`, `reduce` — processing collections without loops.

In 2040's hybrid code, the rule of thumb is: **immutable value objects, pure functions for business logic, mutable entities only where necessary.** This combines OO's domain modeling with functional's safety and testability.

```python
# Functional style in an OO context
@dataclass(frozen=True)  # immutable
class Money:
    amount: Decimal
    currency: str
    
    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise CurrencyMismatch()
        return Money(self.amount + other.amount, self.currency)
```

**Reactive Programming.** Objects don't just respond to method calls — they react to *streams of events*. A `StockPriceDisplay` subscribes to a `PriceUpdateStream` and updates automatically whenever a new price arrives. The Observer pattern, generalized and declarative:

```python
# Reactive: declare how data flows
price_stream
    .filter(lambda p: p.symbol == "AAPL")
    .map(lambda p: p.price)
    .buffer_with_time(1.0)  # group into 1-second windows
    .map(lambda prices: sum(prices) / len(prices))  # average
    .subscribe(display.update)
```

Reactive programming is the paradigm behind: real-time dashboards, live collaboration (Google Docs, Figma), event-sourced architectures, and the VERÐANDI nervous system in Hermes (AI agent state as an event stream).

**Agent-Oriented Programming (2040).** The newest paradigm. Traditional OO treats objects as passive — they do things when methods are called. Agent-oriented programming treats components as *autonomous agents* with goals, beliefs, and the ability to initiate action.

An `InventoryAgent` doesn't just respond to `check_stock(product_id)`. It monitors inventory levels, predicts shortages, and proactively orders more stock. It has:
- **Beliefs:** Its model of the world (current inventory, supplier lead times, demand forecasts)
- **Goals:** Maintain stock above safety thresholds
- **Plans:** Sequences of actions to achieve goals (if low, order from cheapest supplier)
- **Communication:** Send messages to other agents (notify `OrderAgent` about incoming stock)

The Hermes framework itself is agent-oriented: each subagent is an autonomous entity with goals, memory, and the ability to use tools. The `NornOrchestrator` manages agent lifecycles. `MemoryWells` store agent beliefs.

**The Paradigm Spectrum.** In 2040, a well-designed system uses:
- **OO** for domain modeling and system structure
- **Functional** for business logic, data transformation, and value objects
- **Reactive** for event handling, real-time updates, and inter-component communication
- **Agent-oriented** for autonomous components with goals and proactive behavior

None of these replace OO. They complement it. The 2040 developer is poly-paradigmatic — choosing the right paradigm for each part of the system.

#### Required Reading

- Gamma et al. (1994). *Design Patterns*. Discussion of how patterns relate to functional programming in the Conclusion.
- Vernon, V. (2018). *Reactive Messaging Patterns with the Actor Model*. Addison-Wesley. Chapters 1-3.
- Shoham, Y. (1993). "Agent-Oriented Programming." *Artificial Intelligence*, 60(1), 51-92. [The original paper, re-read in 2040 as prophecy.]
- Hermes Agent Documentation. "Agent Lifecycle and the NornOrchestrator." *docs.yggdrasil.university/hermes/agents*.

#### Discussion Questions

1. Is agent-oriented programming truly a new paradigm, or is it OO with autonomy added? What makes it fundamentally different?
2. Functional programming purists argue that immutable data and pure functions eliminate entire classes of bugs. Should OO developers adopt immutability everywhere, or are there legitimate reasons for mutable state?
3. In 2040, AI agents can be treated as "intelligent objects" — objects that use LLMs to determine their behavior at runtime. Does this break OO principles (the behavior of an object should be predictable from its class), or extend them?

---

### ᛃ Lecture 12: The Object-Oriented Life — Design as Craft

**Date:** Week 6, Session 2

#### Overview

The final lecture places object-oriented design in the broader context of software craft. We trace the arc from Simula 67 through the OO boom of the 1990s, the pattern movement, the Agile revolution, and the 2040 era of AI-augmented design. We conclude with a vision of OO design as a *craft* — a practice that improves with experience, guided by principles rather than rules, and ultimately judged by the quality of the systems it produces.

#### Lecture Notes

Object-oriented programming has been declared dead many times. In the 2000s, functional programming was the successor. In the 2010s, microservices and "dumb pipes, smart endpoints." In the 2020s, serverless and "functions as a service." Each wave claimed OO was obsolete. Each wave was absorbed into the OO ecosystem.

Why does OO endure? Because the *objects* in OO are not about syntax — they're about *modeling*. Software models the world. The world contains entities with identity, behavior, and relationships. OO provides the vocabulary for describing them. Until the world stops containing entities, OO will have a place.

**The Arc of Understanding.** Learning OO design follows a predictable arc:

1. **Novice:** Everything is a class. Deep inheritance hierarchies. Lots of `get`/`set`. 
2. **Intermediate:** Discovered patterns. Using them everywhere. Code looks like the Gang of Four book.
3. **Experienced:** Patterns are tools, not goals. Some classes are simple. Some use patterns. Design follows the domain, not the pattern catalog.
4. **Master:** Patterns have become invisible. You don't think "I'll use Strategy here" — you naturally structure the code that way because it's the obvious way to make it flexible. The patterns are in your fingers, not your conscious mind.

This course aims to take you from novice to experienced. Mastery takes years of practice — but knowing the patterns gives you a map for the journey.

**Design Review as Ritual.** In the Norse tradition, a crafted object was presented to the community before it was used. A sword was examined, tested, discussed. The same is true of software design. Design review — presenting your architecture to peers for critique — is the single best way to improve as a designer.

In 2040, design review has evolved: AI design assistants generate initial designs. Human designers review them, challenge assumptions, and refine. Peers review the refined design. The cycle of critique and improvement is continuous. The skill of *giving* design feedback — identifying the weak points in a design without prescribing specific solutions — is as important as the skill of creating designs.

**What Endures.** Technology changes. Languages rise and fall. Frameworks are fashionable for five years and embarrassing after ten. What endures:
- **The principles:** SOLID, composition over inheritance, separation of concerns — these were true in 1994 and will be true in 2094.
- **The patterns:** The Gang of Four patterns have been implemented in a dozen languages across three decades. They survive because they solve *structural* problems, not syntactic ones.
- **The mindset:** Thinking in objects — identifying entities, defining boundaries, managing dependencies — is a transferable skill. Learn it once, apply it everywhere.
- **The humility:** Good design is discovered through iteration, not prescribed from the start. The best designers are the ones most willing to change their minds.

**A Closing Charge.** Go design something. Choose a problem — a game, a tool, a simulation — and model it in objects. Start simple. Refactor as you learn. Show it to someone and ask "what's wrong with this design?" Then fix it.

The patterns are not the destination. They are signposts along the way — evidence that others have walked this path before and found a reliable route. Your own path will be different. Your own designs will be yours. But the craft is shared, and every object you design well adds to the common wealth of our profession.

#### Required Reading

- Gamma et al. (1994). *Design Patterns*. Conclusion.
- Fowler, M. (2018). *Refactoring*. Chapter 13: "Refactoring, Reuse, and Reality."
- Your own final project design document. Read it one month after submitting it. What would you change?

#### Discussion Questions

1. "OO is dead" articles appear every few years. Why does OO persist despite these declarations? What is the kernel of truth in the "OO is dead" argument?
2. Design review is essential but time-consuming. In 2040, can AI design review replace human review? What aspects of design review are inherently human?
3. At the end of this course, what is your personal philosophy of object-oriented design? Summarize it in three sentences.

---

## Final Examination Preparation

### Part I: Written Examination (60%)

Choose **four** of the following **eight** essay questions.

1. **SOLID Analysis.** Select a non-trivial class from your own code or an open-source project. Analyze it against all five SOLID principles. For any violations, propose a refactoring that brings it into compliance, and explain the tradeoffs.

2. **Pattern Selection.** You are designing a text editor with: multiple file format support, undo/redo, real-time spell checking, and plugin support for custom tools. Select at least four design patterns that would be appropriate for this system. For each, explain: what problem it solves, how you would implement it, and why you chose it over alternatives.

3. **Composition vs. Inheritance Case Study.** Present a realistic scenario where inheritance initially seems appropriate but leads to problems. Show the inheritance-based solution and its flaws. Then present a composition-based alternative and explain why it is superior. Address any genuine advantages the inheritance approach had.

4. **Domain-Driven Design in Practice.** Choose a domain you understand well (e.g., a university course registration system, a library, an e-commerce platform). Identify the entities, value objects, aggregates, and bounded contexts. Draw a context map showing how the contexts relate. Justify your aggregate boundaries.

5. **Refactoring Narrative.** Take a piece of poorly structured code (your own or provided). Walk through a sequence of refactorings that improve its design. At each step, explain: what smell you're addressing, which refactoring you're applying, and how the design improves. Include before-and-after code.

6. **Testing and Design.** Argue for or against the claim: "Test-driven development leads to better object-oriented design." Use specific examples of design decisions that TDD influenced (positively or negatively). Address the role of AI-generated tests in this argument.

7. **Anti-Pattern Autopsy.** Select an anti-pattern (God Object, Anemic Domain Model, or Poltergeist). Find or create a realistic example of it. Diagnose: how did this anti-pattern emerge? What maintenance problems has it caused? Prescribe: what refactorings would cure it, and in what order should they be applied?

8. **The Future of OO.** In 2040, AI can generate classes, apply patterns, and suggest refactorings. What remains uniquely human about object-oriented design? What skills should the next generation of developers cultivate that AI cannot replicate?

### Part II: Design Project (40%)

Design and implement a system of moderate complexity. Deliverables:

1. **Domain model** (class diagram or equivalent) showing entities, value objects, aggregates, and their relationships.
2. **Implementation** demonstrating at least: 2 SOLID principles explicitly applied, 3 design patterns used, composition used instead of inheritance at least once, and full unit test coverage of the domain logic.
3. **Design document** (1500-2500 words) explaining: the domain and its bounded contexts, the key design decisions, the patterns chosen and why, the refactorings performed during development, and what you would do differently with more time.
4. **Design review presentation** (10-15 minutes) presenting your design to peers and responding to their critique.

---

**ᛟ ᛞ ᚨ — From pattern, form. From form, function. From function, craft.**

*SD201: Object-Oriented Design & Patterns — University of Yggdrasil, 2040*
*Instructor: Dr. Eira Lundström*
*Course version: 1.0 — 2040 Academic Year*