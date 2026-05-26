# Java ↔ Go Mapping

Authoritative parallels for the Java Mental Model section and Concept Callouts in Go code. Pull from this file when drafting lessons.

## Module system

| Java | Go |
|---|---|
| `package com.acme;` | `package acme` (one per directory) |
| `import com.acme.User;` | `import "github.com/acme/foo"` |
| `import com.acme.*;` | n/a — Go imports a whole package, then uses `acme.User` |
| Maven/Gradle artifact | Go module, versioned via `go.mod` |
| `public` (visible everywhere) | identifier starts with uppercase letter |
| package-private (default) | identifier starts with lowercase letter |

**Visibility by capitalization** is the most surprising rule for Java devs. There is no `public`/`private`/`protected` keyword. `User` is exported from its package; `user` is not. This applies to types, functions, variables, and struct fields uniformly.

## Variables and types

| Java | Go |
|---|---|
| `final var x = ...` | `const x = ...` (compile-time constants only) — for non-constants the closest is "declared once, never reassigned" by convention |
| `var x = ...` (Java 10+) | `x := ...` (short declaration, type inferred) or `var x = ...` |
| `Foo x = null;` | `var x *Foo = nil` (pointer); or `var x Foo` (zero value, never null for non-pointer types) |
| `int`, `long` | `int` (platform-sized), `int32`, `int64` |
| `String` | `string` (immutable byte sequence; UTF-8 by convention but not enforced) |
| `boolean` | `bool` |
| `null` | `nil` |
| `Object` (top type) | `interface{}` or, in 1.18+, the alias `any` |

**Pointers are explicit**: Go has values and pointers, like C. Java's references are always "pointers" implicitly; Go makes you choose. `&x` takes the address; `*p` dereferences.

**Zero values**: every type has a zero value used when the variable is declared without an initializer. `int` → `0`, `string` → `""`, pointer/interface/slice/map/channel/function → `nil`. Java's "all fields default to null/0" is the same idea, but Go applies it to *local* variables too.

## Types and interfaces

| Java | Go |
|---|---|
| `class Foo` | `type Foo struct { ... }` plus methods declared on `Foo` |
| `interface Foo { void bar(); }` | `type Foo interface { Bar() }` |
| `implements Foo` | nothing — Go interfaces are *structural*; if you have the method set, you satisfy the interface |
| inheritance | composition via struct embedding |
| `abstract class` | no equivalent; use interfaces + composition |
| Generics `<T>` | Generics `[T any]` (Go 1.18+) |
| `T extends Comparable<T>` | `T constraints.Ordered` (from `golang.org/x/exp/constraints`) |
| `final` field | unexported struct field — package-private |

**Structural interfaces are huge.** You can satisfy an interface without ever knowing it exists. This is duck typing at the type-checker level. `io.Reader` is satisfied by anything with `Read(p []byte) (n int, err error)`.

**Methods, not classes**: methods are declared on a type, outside any class block:

```go
type User struct { Name string }
func (u User) Greet() string { return "Hello, " + u.Name }   // value receiver
func (u *User) Rename(s string) { u.Name = s }               // pointer receiver
```

The receiver `(u User)` is roughly the implicit `this` in Java. Value receivers get a copy; pointer receivers can mutate.

## Error handling

| Java | Go |
|---|---|
| `throw new IOException(...)` | `return nil, fmt.Errorf("...")` |
| `try { ... } catch (IOException e) { ... }` | `result, err := f(); if err != nil { ... }` |
| Checked exceptions | every function that can fail returns `(value, error)` |
| `try-finally` | `defer cleanup()` |
| Unchecked exception | `panic("...")` — rare, for unrecoverable errors |
| `try-with-resources` | `defer file.Close()` immediately after acquiring the resource |
| Exception chaining | `fmt.Errorf("read failed: %w", err)` — the `%w` verb wraps |
| `instanceof IOException` | `errors.Is(err, io.EOF)` (sentinel) or `errors.As(err, &target)` (typed) |

**No exceptions** — every error path is explicit. Reads as verbose to Java devs at first; pays back in clarity. Errors are values; you compose them like any other value.

**`panic` / `recover`**: there is something like exceptions (`panic` unwinds; `recover` inside a `defer` catches), but idiomatic Go reserves them for truly unrecoverable cases (nil dereferences, index out of bounds, programming errors). Don't model checked exceptions with panic.

## Concurrency

| Java | Go |
|---|---|
| `new Thread(() -> ...).start()` | `go func() { ... }()` |
| `ExecutorService.submit(task)` | `go task()` (the runtime schedules onto an OS thread pool) |
| `BlockingQueue<T>` | `chan T` (channel) |
| `queue.put(x)` / `queue.take()` | `ch <- x` / `<-ch` |
| `synchronized(lock) { ... }` | `mu.Lock(); defer mu.Unlock()` |
| `ReentrantReadWriteLock` | `sync.RWMutex` |
| `AtomicInteger` | `sync/atomic.Int64` (and friends) |
| `volatile` | atomic types |
| `CompletableFuture.allOf` | `sync.WaitGroup` or fan-in via channels |
| `Future.get()` | receive from a result channel: `result := <-ch` |
| `Thread.sleep` | `time.Sleep(d)` |

**Goroutines are cheap.** ~2KB initial stack (grows dynamically) vs. ~1MB per Java thread. Spawning thousands of goroutines is normal; spawning thousands of threads is not.

**Channels for communication, mutexes for state.** The Go proverb: *"Don't communicate by sharing memory; share memory by communicating."* In practice, both have their place — channels for pipelines and signaling, mutexes for protected shared state.

**`select`**: a multi-channel `switch`. No Java equivalent. Waits on whichever channel is ready first; `default` clause means non-blocking.

## Common syntax features (always callout-worthy)

These features almost always deserve a Concept Callout when they appear in lesson code:

- **`:=`** — short variable declaration with type inference. Only inside functions.
- **Multiple return values** `a, b := f()` — Java has only one return; you'd return a record/tuple. Idiomatic Go pairs a value with `error`.
- **Named return values** `func f() (count int, err error) { ... return }` — pre-declared returns; `return` without arguments returns the named ones. Used sparingly.
- **`defer`** — schedules a function call to run when the surrounding function returns. Like `finally` but stackable: deferred calls run in LIFO order. Captures arguments at defer time, *not* at call time.
- **Channels `chan T`** — typed blocking queue. `<-` is the channel operator. Closing a channel (`close(ch)`) signals end-of-stream to receivers.
- **`select`** — multi-channel `switch`; no Java equivalent.
- **Goroutines `go f()`** — lightweight thread; no `start()` ceremony.
- **Pointer receivers `func (f *Foo) Bar()`** — method can mutate `f` and avoid copying. Value receiver `func (f Foo) Bar()` operates on a copy.
- **Struct embedding** — composition that looks like inheritance:

  ```go
  type Animal struct { Name string }
  func (a Animal) Greet() { ... }
  type Dog struct { Animal; Breed string }  // Dog embeds Animal
  d.Greet()  // promoted method
  ```

  Not the same as inheritance — embedding is *has-a* with method promotion.
- **`iota`** — enumerated constants generator. Java's `enum` is richer (each value can carry fields and methods); `iota` is closer to C `enum`.
- **Slices vs arrays** — `[5]int` is a fixed-size array (value semantics on copy); `[]int` is a slice (reference-like view over an array). Almost all real code uses slices.
- **Maps** — `map[string]int`. The zero value of a map is `nil` and *not writable* — initialize with `make(map[string]int)`.
- **Type assertion** `x.(*Foo)` — like a Java cast, but with a two-value comma-ok form: `v, ok := x.(*Foo)`.
- **Type switch** `switch v := x.(type) { case *Foo: ... }` — dispatch by concrete type.

## Common framework parallels

| Java (Spring) | Go |
|---|---|
| `@RestController` | `http.HandlerFunc` on `*http.ServeMux`, or a router (gin, chi, echo, gorilla/mux) |
| `@Service` | a struct with methods; pass in via constructor function |
| `@Repository` | a struct holding a `*sql.DB` or an ORM (GORM, ent, sqlc-generated code) |
| `@Component` + DI | manual constructor wiring or a DI library (wire, fx) |
| `application.yml` | env vars + `viper` or a hand-rolled config struct |
| Logger | `log` (stdlib) or structured (`zap`, `zerolog`, `log/slog`) |
| `@Transactional` | `tx, _ := db.BeginTx(ctx, nil); defer tx.Rollback(); ...; tx.Commit()` |
| `RestTemplate` / `WebClient` | `net/http.Client` or `resty` |
| `@Async` | `go func() { ... }()` |
| `@Scheduled` | `time.Ticker` + a goroutine, or `cron` library |

## Java-only intuitions that don't translate

- **Constructors**: Go has no constructors. Convention is `NewFoo(...) *Foo` — a regular function. There's no special initialization syntax beyond the struct literal.
- **Method overloading**: Go does not overload. One method per name on a type.
- **Generics constraints with `super`**: Go has no contravariant bounds. `[T any]` and `[T constraints.Ordered]` are the common shapes.
- **Annotations**: Go has *struct tags* (string literals after a field, used by reflection-based libraries like JSON encoding) but no general annotation system. Code generation (`go generate` + tools) plays a similar role to annotation processors.
- **Inheritance**: Go offers composition via embedding only. There is no `extends`.

## Useful Go-only ideas built from Java intuitions

- **Context propagation** `ctx context.Context` — explicit `Context` parameter threaded through call chains for cancellation, deadlines, and request-scoped values. Java's `ThreadLocal` is the closest analogue, but Go makes it explicit.
- **`io.Reader` / `io.Writer`** — single-method interfaces that compose. `bufio.NewReader(io.MultiReader(a, b))` is the Go way of building pipelines that a Java dev would express with `InputStream` wrapping.
- **Nil interface gotcha**: an interface value with a typed nil pointer is *not* `nil`. `var p *MyError = nil; var err error = p; err != nil`. Subtle and important.
- **Closing channels signals**: a closed channel returns the zero value and `ok = false`. `for v := range ch` ends when the channel closes. There's no Java analogue — you'd use a sentinel.
