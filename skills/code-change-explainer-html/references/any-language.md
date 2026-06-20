# Any target language — finding the non-obvious syntax

Use this for **every** target language — TypeScript, Python, Go, Rust, Swift, Kotlin, C#, Ruby, Scala, Elixir, whatever the code is written in. There are deliberately no per-language cheat-sheets: a fixed list would surface the same callouts every time, when the goal is to react to the non-obvious constructs in *this* code so the reader learns the language's implications over time.

The goal: explain the **target** language's non-obvious constructs, anchored by a **parallel** in the comparison language, without explaining the comparison language itself and without repeating an explanation. You know these languages well — the job is to be disciplined about *what* to surface, not to look anything up.

## How to build the callout list

Walk the After code and flag any construct that is **not** a 1:1 equivalent of something the reader already knows from the comparison language. Sweep these categories — they are where languages differ in ways that bite:

- **Absence / null** — optionals, `nil`/`null`/`None`, null-safety operators (`?.`, `?:`, `!!`, `guard let`, `if let`), force-unwrap.
- **Equality & identity** — value vs reference equality, operator overloading of `==`, structural vs nominal comparison.
- **Mutability & binding** — `val`/`var`/`let`/`const`, immutable-by-default, shadowing, what "constant" actually freezes (binding vs contents).
- **Functions & closures** — lambda/closure syntax, trailing-closure sugar, capture semantics, partial application, named/default/variadic parameters.
- **Async & concurrency** — the language's model (threads, coroutines, actors, async/await, futures, structured concurrency) and whether async is eager or lazy.
- **Error model** — exceptions (checked vs not), result types, `try`/`throws`/`rethrows`, optional-returning failures.
- **Type-system surprises** — inference, generics and variance, union/intersection/sum types, structural vs nominal typing, extension methods, type-state.
- **Syntactic sugar** — destructuring, pattern matching, string interpolation, ranges, comprehensions, operator overloading, property syntax vs getters/setters.
- **Memory / ownership** — value vs reference types, copy semantics, ownership/borrowing, ARC/ref-counting, RAII/`defer`-style cleanup.
- **Metaprogramming** — annotations/attributes, macros, reflection, decorators — and whether they run at compile time or runtime.
- **Platform / runtime / framework** — behaviour that is not in the syntax but bites at runtime: the event-loop and scheduling model, framework lifecycle and render/effect timing, ORM/query semantics (lazy-loading, N+1), thread/UI-thread constraints, GC and retain cycles, library API contracts. Often the real *reason* for a change — surface it even when the syntax looks ordinary.

For each flagged construct, fill the five callout fields (Name, Minimal syntax, Semantic, Parallel, Gotcha) per `concept-callouts.md`. The Gotcha is usually the precise way the construct *diverges* from its comparison-language parallel.

## Keep the discipline

- **Skip the obvious.** A plain `if`, `for`, assignment, or method call that means the same as in the comparison language gets no callout.
- **One callout per construct.** Teach it on first appearance; reference back afterwards. Keep a running list of what you've already explained so the document never repeats itself.
- **Parallel, don't teach, the comparison language.** It appears only in the Parallel field. If a target construct has no honest parallel (e.g. Rust ownership when the reader knows a GC'd language), say so plainly rather than forcing a misleading one.
- **Name the idiom.** If the construct is the language's idiomatic form of a known pattern (Swift's `guard`, Kotlin's `?.let`, C#'s `using`, Ruby's blocks), name it and tie it to the comparison-language pattern.
