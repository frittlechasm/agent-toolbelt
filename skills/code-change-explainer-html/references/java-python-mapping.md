# Java ↔ Python Mapping

Authoritative parallels for the Java Mental Model section and Concept Callouts in Python code. Pull from this file when drafting lessons.

## Module system

| Java | Python |
|---|---|
| `package com.acme;` | `acme/__init__.py` |
| `import com.acme.User;` | `from acme.user import User` |
| `import com.acme.*` | `from acme import *` (discouraged) |
| `import static ...` | `from acme.user import find_by_email` |
| Maven/Gradle artifact | `pip` / PyPI package |

A Python *module* is a single `.py` file; a *package* is a directory with `__init__.py` (optional in modern Python but still common). There is no class-per-file convention — multiple classes and free functions live together.

## Variables and types

| Java | Python |
|---|---|
| `final var x = ...` | no true `final`; convention: `UPPER_CASE` for constants |
| `var x = ...` (Java 10+) | `x = ...` (no declaration keyword) |
| `Foo x = null;` | `x: Foo \| None = None` (or `Optional[Foo]` from `typing`) |
| `int`, `long`, `double` | `int` (arbitrary precision), `float` |
| `String` | `str` (Unicode, immutable) |
| `boolean` | `bool` (`True`/`False`, capitalised) |

**Type hints are hints**, not enforced at runtime by default. `mypy` / `pyright` / `pylance` check at lint time. There is no `instanceof Foo<Bar>` because generics are erased at runtime — only the raw type remains.

**Falsy values**: `False, 0, 0.0, "", [], {}, set(), None`. Empty containers are falsy, which is a Pythonic idiom (`if not items:`) but a Java-dev tripwire (`if (list)` doesn't mean "is it null" — it means "is it non-empty").

**`is` vs `==`**: `is` is reference identity (like Java `==`); `==` calls `__eq__` (like Java `.equals`). Always use `is None` for None checks, never `== None` — `is` is faster and matches the standard library's expectations.

## Classes

| Java | Python |
|---|---|
| `class Foo { Foo() {...} }` | `class Foo:` + `def __init__(self): ...` |
| Instance method | `def method(self): ...` (explicit `self` parameter) |
| Static method | `@staticmethod` decorator |
| Class method | `@classmethod` decorator (receives `cls`, like `static` with class reflection) |
| Field | assignment in `__init__` or class body |
| `private` | leading underscore by *convention* (`_field`); no enforcement |
| `protected` | also leading underscore; no enforcement |
| name mangling | double leading underscore (`__field`) — name is mangled to `_ClassName__field` |
| `toString()` | `__str__` (user-facing) and `__repr__` (debug — should be unambiguous, ideally reconstructable) |
| `equals` / `hashCode` | `__eq__` and `__hash__` (always implement both together) |
| `Comparable.compareTo` | `__lt__`, `__eq__`, etc. (the "rich comparison" dunders) |
| Iterator interface | `__iter__` (returns iterator) and `__next__` (returns next or raises `StopIteration`) |
| `Closeable.close` | `__enter__` / `__exit__` (context manager protocol) |

**Dunder ("double underscore") methods** are Python's *protocol* mechanism. They map operators and built-in functions to your class:

- `len(x)` → `x.__len__()`
- `x + y` → `x.__add__(y)`
- `x[i]` → `x.__getitem__(i)`
- `for v in x:` → `iter(x).__next__()` repeatedly
- `with x as v:` → `x.__enter__()` then `x.__exit__(...)`

This is closer to Scala's symbolic methods than to anything in Java. The closest Java equivalent is SAM interfaces, but dunders are richer — they let your class slot into existing syntax.

## Collections

| Java | Python |
|---|---|
| `List<T>` / `ArrayList` | `list` (mutable, ordered) |
| `Map<K, V>` / `HashMap` | `dict` (insertion-ordered since 3.7) |
| `Set<T>` | `set` |
| immutable list / tuple | `tuple` (also: `frozenset`, `types.MappingProxyType`) |
| `Optional<T>` | `T \| None` (no wrapping required) |
| `Stream.map(...).collect(toList())` | list comprehension `[f(x) for x in xs]` |
| `Stream.filter(...)` | `[x for x in xs if p(x)]` |
| `Stream.flatMap` | `[y for x in xs for y in f(x)]` |
| `Stream.reduce` | `functools.reduce` |
| `Map.Entry<K,V>` iteration | `for k, v in d.items():` |
| `Map.keySet()` | `d.keys()` (iterating `d` directly also iterates keys) |
| `Map.values()` | `d.values()` |

**List comprehensions** are the idiomatic stream pipeline. `[f(x) for x in xs if p(x)]` reads "the f of x, for each x in xs, where p(x) is true" — concise once you internalize it. They evaluate eagerly. Use `(...)` instead of `[...]` for a *generator expression* — lazy, like a `Stream`.

## Async

| Java | Python |
|---|---|
| `CompletableFuture<T>` | `asyncio.Future` / coroutine object |
| `supplyAsync(() -> ...)` | `async def f(): ...` then `await f()` |
| `.thenApply(f)` | `await` then chain |
| `.get()` (blocking) | `asyncio.run(coro)` (top level) or `await coro` (inside async) |
| `CompletableFuture.allOf` | `await asyncio.gather(*coros)` |
| `Executor` | `asyncio` event loop, or `concurrent.futures.Executor` (`ThreadPoolExecutor`, `ProcessPoolExecutor`) |

**Cooperative async**: Python's async is single-threaded and cooperative. CPU-bound work blocks the event loop unless offloaded to a thread or process pool. Java's `CompletableFuture.supplyAsync` uses a thread pool by default — Python's `asyncio.gather` does *not*.

**GIL**: the Global Interpreter Lock means only one Python bytecode instruction runs at a time per process. True parallelism for CPU work requires `multiprocessing` (separate processes) or native extensions. (Python 3.13+ has experimental "no-GIL" builds; not yet mainstream.)

## Common syntax features (always callout-worthy)

These features almost always deserve a Concept Callout when they appear in lesson code:

- **List / dict / set comprehensions** `[f(x) for x in xs if p(x)]` — terser `Stream.filter(...).map(...).collect(...)`. Eager.
- **Generator expressions** `(f(x) for x in xs)` — lazy, like a `Stream`. Single-pass.
- **`yield` and generator functions** — produce values lazily. Closest Java: a custom `Iterator` or `Stream.generate`. Calling a `yield`-using function does *not* run the body — it returns a generator that runs on iteration.
- **Decorators `@foo`** — Java annotations *plus* AOP. `@app.route("/")` wraps the function; it's runtime, not metadata. `@functools.lru_cache` actually adds caching.
- **Context managers `with open(p) as f:`** — Java's try-with-resources. The `__enter__` / `__exit__` protocol.
- **`*args` and `**kwargs`** — varargs and keyword-args. Java has varargs (`String...`) but no keyword-args.
- **f-strings `f"Hello {name}"`** — `String.format` with embedded expressions. Format specs (`f"{value:.2f}"`) are like Java's `printf` formats.
- **Walrus `:=`** — assign-and-return inside a condition (`if (n := len(xs)) > 0:`). No clean Java equivalent.
- **`is` vs `==`** — `is` is reference identity (like Java `==`); `==` calls `__eq__` (like Java `.equals`). Always `is None`.
- **Mutable default arguments** — `def f(xs=[]):` — the list is shared across *all* calls. *Major Java-dev pitfall.* Use `def f(xs=None): xs = xs or []` or `xs = [] if xs is None else xs`.
- **Slicing `xs[1:5]`, `xs[::-1]`** — sublist views with optional step. Java has `List.subList(from, to)` but no step.
- **Tuple unpacking** `a, b = (1, 2)` and `a, *rest = [1, 2, 3]` — closest Java is record-pattern deconstruction (Java 21+).
- **Chained comparisons** `if 0 < x < 10:` — readable; no Java equivalent.

## Class and object specifics

- **Dataclasses** (`@dataclass`) — like Java `record` for mutable classes; generates `__init__`, `__eq__`, `__repr__`. With `frozen=True`, gives immutable records.
- **Properties** (`@property`) — getter/setter syntax. `obj.x` calls the getter; `obj.x = v` calls the setter. Java's `getX()`/`setX(v)` made transparent.
- **`__slots__`** — restrict an instance to fixed attribute names, saving memory. Like Java fields (Python instances default to a per-instance `__dict__`).
- **Multiple inheritance** is allowed (Java has only interface multi-inheritance). Method resolution uses C3 linearization (`Class.__mro__`); diamond inheritance is well-defined.
- **Duck typing**: a class is "compatible" if it has the right methods. There is no `implements` for protocols (unless using `typing.Protocol` for static checking).

## Common framework parallels

| Java (Spring) | Python (Flask / FastAPI / Django) |
|---|---|
| `@RestController` | `@app.get(...)` (FastAPI/Flask) or `class FooView(APIView)` (DRF) |
| `@Service` | a module with functions, or a class instantiated once |
| `@Repository` | DAO module, ORM Manager (Django) or Session (SQLAlchemy) |
| `application.yml` | `settings.py` (Django) or `pydantic_settings.BaseSettings` (FastAPI) |
| `@Transactional` | `with db.atomic():` (Django/Peewee) or `with session.begin():` (SQLAlchemy) |
| Bean Validation | Pydantic models (FastAPI) or DRF serializers |
| Logger | `logging.getLogger(__name__)` |
| `@RequestParam` | `def handler(name: str = Query(...))` (FastAPI) |

## Java-only intuitions that don't translate

- **Static typing at runtime**: Python doesn't enforce types unless you bolt on a runtime validator (Pydantic, beartype). A function annotated `-> int` can return a string and Python will not object.
- **`final` immutability**: Python has no compile-time `final`. Convention is `UPPER_CASE` for constants and a leading underscore for "internal" things.
- **Method overloading**: Python dispatches purely on name. There is one method per name; you handle multiple shapes via default args, `*args`, or `functools.singledispatch`.
- **Interfaces**: closest is `abc.ABC` + `@abstractmethod` (nominal) or `typing.Protocol` (structural, static-only).
- **Checked exceptions**: Python exceptions are all unchecked. Any function can raise anything.

## Useful Python-only ideas built from Java intuitions

- **`with` blocks as scope hooks** — anything implementing `__enter__`/`__exit__` can hook setup/teardown. Used for transactions, locks, temp files, mocks, timers.
- **Decorators as middleware** — `@functools.wraps`-preserving wrappers stack: `@cache @log @retry def f(): ...`. Read bottom-up.
- **`__init_subclass__`** — class-side hook fired whenever a subclass is created. Loosely like a Java `static {}` block triggered per subclass.
- **Metaclasses** — classes whose instances are classes. Used by ORMs (Django models) to wire up fields. The Java analogue is annotation processors or bytecode manipulation.
