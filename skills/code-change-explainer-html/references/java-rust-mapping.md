# Java ↔ Rust Mapping

Authoritative parallels for the Java Mental Model section and Concept Callouts in Rust code. Rust has the highest conceptual gap from Java in this skill — be especially careful with ownership, borrowing, and lifetimes. Spend more time on these in callouts than you would on equivalent JS or Python features.

## Module system

| Java | Rust |
|---|---|
| `package com.acme;` | `mod acme;` (in `lib.rs` / `main.rs`) or `acme/mod.rs` |
| `import com.acme.User;` | `use acme::User;` |
| Maven artifact | `crate`, declared in `Cargo.toml` |
| `public` | `pub` |
| package-private (default) | (default) — visible within the current crate, not outside |
| `protected` | no direct equivalent; use `pub(super)` or `pub(crate)` |

Visibility is fine-grained: `pub`, `pub(crate)`, `pub(super)`, `pub(in path)`, or private (default). Items default to private — the opposite of Java's "package-private" default.

## Variables and ownership

| Java | Rust |
|---|---|
| `final var x = ...` | `let x = ...` (immutable by default) |
| `var x = ...` | `let mut x = ...` |
| heap-allocated reference | `Box<Foo>` for heap; stack-by-default for everything else |
| reference (implicit) | `&x` (shared borrow) or `&mut x` (exclusive borrow) |
| `null` | no `null`; use `Option<T>` (`Some(value)` or `None`) |

**Ownership** is Rust's central rule: every value has exactly one owner. When the owner goes out of scope, the value is dropped (deterministic destruction — RAII). Java's garbage collector means you never think about this; Rust makes it the type checker's main job.

**Move semantics**: assigning a non-`Copy` value transfers ownership. The source variable is no longer usable.

```rust
let s = String::from("hello");
let t = s;            // ownership moves from s to t
println!("{}", s);    // compile error: s is invalidated
```

`Copy` types (primitives, `&T`, types where everything is `Copy`) are duplicated on assignment — like Java primitives.

**Borrowing**: a borrow `&x` is a reference that cannot outlive the owner. Two rules enforced at compile time:

1. At any time, either *one* mutable borrow (`&mut T`) or *any number* of immutable borrows (`&T`) — never both.
2. Borrows must not outlive the owner.

This eliminates iterator invalidation, data races on shared state, and use-after-free — at compile time.

**Lifetimes `'a`**: explicit annotations when the compiler can't infer how long a reference lives. Read `&'a Foo` as "a reference to `Foo` valid for at least `'a`." Java doesn't model this — it lets the GC keep things alive.

## Types

| Java | Rust |
|---|---|
| `class Foo` | `struct Foo { ... }` plus `impl Foo { ... }` |
| `interface Foo` | `trait Foo` |
| `implements Foo` | `impl Foo for Bar { ... }` |
| `enum` | `enum` (much more powerful — variants can carry data) |
| `record` | `struct` with `#[derive(Clone, Debug, PartialEq)]` |
| `final` class | no equivalent; sealed traits via private modules |
| Generics `<T>` | Generics `<T>` |
| `T extends Comparable<T>` | `T: Ord` (trait bound) |
| `T super Foo` | no contravariant bounds; use trait bounds instead |
| `Optional<T>` | `Option<T>` (built-in, not a library type) |
| `Class<T>` (reified) | no runtime reflection on generics; use `std::any::TypeId` for limited cases |

**Algebraic data types**: Rust `enum` is a sealed sum type — each variant can carry different data. Pattern matching exhaustiveness is checked at compile time. This is closer to Java 21 sealed interfaces + records than to Java enums.

```rust
enum Shape {
    Circle(f64),               // radius
    Rectangle { w: f64, h: f64 },
    Point,
}
```

**Traits** are like interfaces with optional default methods and the ability to add methods to *existing* types from elsewhere (extension methods — coherence rules apply).

## Null and error handling

| Java | Rust |
|---|---|
| `null` | `None` (variant of `Option<T>`) |
| `Optional<T>` | `Option<T>` |
| checked exception | `Result<T, E>` |
| unchecked exception | `panic!(...)` (rare; reserved for bugs) |
| `try` / `catch` | `match` on `Result`, or the `?` operator |
| `try-with-resources` | RAII via the `Drop` trait — values clean themselves up when dropped |
| stack trace | `RUST_BACKTRACE=1` env var for panics; for `Result` you wrap context with `anyhow` / `eyre` |

**No `null`.** Absence is modelled as `Option::None`, which the type system forces you to handle. There is no way to "accidentally" dereference `None` — `unwrap()` is explicit and panics if called on `None`.

**The `?` operator** propagates `Err` early:

```rust
fn read_user() -> Result<User, io::Error> {
    let bytes = fs::read("user.json")?;   // returns Err early if read fails
    let user: User = serde_json::from_slice(&bytes)?;
    Ok(user)
}
```

Reads like sugar for `if let Err(e) = result { return Err(e.into()); }`. The `.into()` enables automatic error conversion via the `From` trait — like exception chaining.

## Concurrency

| Java | Rust |
|---|---|
| `Thread` | `std::thread::spawn(|| { ... })` |
| `ExecutorService` | `rayon::spawn` (CPU pool) or `tokio::spawn` (async runtime) |
| `synchronized` | `Mutex<T>` — wraps the *data*, not the code block |
| `Atomic*` | `std::sync::atomic::*` |
| `volatile` | atomic types |
| `CompletableFuture` | `async fn` returning `impl Future<Output = T>` |
| `BlockingQueue` | `std::sync::mpsc::channel` (single producer? in stdlib) or `crossbeam` / `tokio::sync::mpsc` |

**`Send` + `Sync`** are marker traits the compiler checks:

- `Send`: values of this type can be transferred between threads.
- `Sync`: `&T` is `Send` — references can be shared between threads.

Most types implement these automatically. `Rc<T>` (single-threaded ref-counted) is not `Send`; `Arc<T>` (atomically ref-counted) is. The Java Memory Model's concerns are encoded directly in the type system.

**Async is lazy.** A future does nothing until you `.await` it (or hand it to a runtime). Java's `CompletableFuture.supplyAsync` starts immediately. Rust futures are "cold" — created without side effects.

**No GC pauses, no STW.** RAII drops are deterministic. There is no equivalent to Java's stop-the-world GC pauses.

## Common syntax features (always callout-worthy)

These features almost always deserve a Concept Callout when they appear in lesson code:

- **`let mut`** — variables are immutable by default; opt in to mutation.
- **`&` and `&mut`** — borrows. Lifetime-checked references.
- **`'a` lifetime annotations** — explicit when the borrow checker can't infer.
- **Move semantics** `let t = s;` — `s` is invalidated unless `s: Copy`.
- **`match` with exhaustive patterns** — like a strict `switch` over a sealed hierarchy. Pattern guards: `Some(x) if x > 0`.
- **`if let` and `while let`** — pattern matching one branch: `if let Some(x) = opt { ... }`.
- **`?` operator** — propagates `Err` from a `Result`-returning expression, with automatic `From`-based conversion.
- **Traits and `impl`** — like interfaces + extension methods. Trait objects (`dyn Foo`) for dynamic dispatch; generics for static dispatch (monomorphization).
- **`Box<T>`, `Rc<T>`, `Arc<T>`** — heap, single-threaded shared, multi-threaded shared. Java just uses references and lets the GC sort it out.
- **`Cow<'a, T>`** — clone-on-write. Borrow until you need to mutate, then clone. No Java equivalent.
- **`async fn`** — like a method returning `CompletableFuture<T>`, but futures are lazy: nothing runs until `.await`.
- **Pattern destructuring** `let Point { x, y } = p;`. Closest Java is record deconstruction (Java 21+).
- **Macros `vec![1, 2]`, `println!()`, `format!()`** — code generation at compile time. Java has no real macros; closest is annotation processors.
- **`impl Trait` in arg and return position** — "some type that implements `Trait`" without naming it. Closest Java is `<T extends Trait>` in args, `Trait` in returns (with limitations on type inference).
- **Tuple types** `(i32, String)` and tuple structs `struct Pair(i32, String);` — Java has no tuples in the language.
- **`unsafe` blocks** — opt out of the borrow checker for specific operations (raw pointer deref, FFI, etc.). Rare in application code.

## Common framework parallels

| Java (Spring) | Rust |
|---|---|
| `@RestController` | `axum` / `actix-web` / `rocket` handler function |
| `@Service` | a struct with methods, often stored in an `AppState` and shared via `Arc` |
| `@Repository` | a struct over `sqlx` or `diesel` |
| `application.yml` | `config` crate or env via `serde` + `envy` |
| Logger | `tracing` crate (structured) or `log` (lightweight) |
| DI | constructor injection via `AppState`; no DI framework needed |
| `@Transactional` | `let mut tx = pool.begin().await?; ...; tx.commit().await?;` |
| Bean Validation | `validator` crate with `#[validate(...)]` attributes |

## Java-only intuitions that don't translate

- **Reference cycles**: Java's GC handles them; Rust's RAII does not. `Rc<T>` cycles leak. Break with `Weak<T>`.
- **Method overloading**: Rust does not overload by parameter type. Use traits or distinct method names.
- **Implicit conversions**: very few in Rust (`Deref`, numeric `From`/`Into`). Java's auto-boxing is gone.
- **Checked exceptions**: replaced entirely by `Result<T, E>`. There is no parallel hierarchy.
- **Reflection**: minimal. `TypeId` exists but there's no `Class.getDeclaredFields()` equivalent. Use procedural macros for compile-time codegen.

## Useful Rust-only ideas built from Java intuitions

- **RAII as the default pattern**: every resource is freed by its destructor (`Drop` impl). No `finally` blocks.
- **Lifetimes as compile-time scoping**: `&'static` is "lives for the program's lifetime"; smaller lifetimes are inferred at function boundaries.
- **Type-state pattern**: encode state in the type. A `Builder<Unconfigured>` and `Builder<Configured>` are different types; `.build()` only exists on the latter. Compile-time enforcement of state machines.
- **Newtype pattern**: `struct UserId(u32);` — a single-field tuple struct that gives a fresh type. Java's closest is a single-field record class; Rust's is zero-cost (no boxing).
- **Ownership and "move closures"**: `move || { ... }` captures by value (move) rather than by reference. Important when spawning threads.
