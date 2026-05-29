# Concept Callouts — Patterns and Examples

Concept Callouts are short boxed explainers that surface every non-trivial syntactic feature for a Java-background reader. Every Lesson should use callouts liberally; for this audience, over-explaining is preferable to under-explaining.

## Anatomy of a Callout

Each callout has five parts in this order:

1. **Name** of the feature (e.g., "Optional chaining `?.`").
2. **Minimal syntax** in monospace.
3. **Semantic**: what it evaluates to, including edge cases.
4. **Java parallel**: the closest Java equivalent, even if imperfect. Explicitly call out where it diverges.
5. **Gotcha**: one pitfall to remember (often the divergence from the Java parallel).

## HTML structure

Use the **Callout** pattern from `html-document` `references/elements.md` — the `<aside class="callout">` with an `<h4>` heading, a `<pre><code>` for the minimal syntax, and a `<dl>` of `<dt>`/`<dd>` field pairs. That file owns the CSS (class name, tokens, spacing, print rules); do not redefine it here, or the styling will drift from the rest of the document. This skill only owns the *content* of the five fields below.

```html
<aside class="callout">
  <h4>Optional chaining <code>?.</code></h4>
  <pre><code>user?.profile?.name</code></pre>
  <dl>
    <dt>Semantic</dt>
    <dd>
      Returns <code>undefined</code> as soon as any link in the chain is
      <code>null</code> or <code>undefined</code>. Does not short-circuit on
      <code>0</code>, <code>""</code>, or <code>false</code>.
    </dd>
    <dt>Java parallel</dt>
    <dd>
      Like
      <code>Optional.ofNullable(user)
        .map(User::getProfile)
        .map(Profile::getName)
        .orElse(null)</code>.
      The whole expression yields <code>null</code> instead of throwing NPE.
    </dd>
    <dt>Gotcha</dt>
    <dd>
      Distinct from the <code>?</code> in TypeScript optional-property syntax
      (which marks a property as possibly absent). The runtime operator is
      <code>?.</code> with a dot.
    </dd>
  </dl>
</aside>
```

The `<dl>` / `<dt>` / `<dd>` structure renders cleanly, prints well, and is keyboard-accessible without extra work. The Name maps to the `<h4>`, the Minimal syntax to the `<pre><code>`, and Semantic / Java parallel / Gotcha to `<dt>`/`<dd>` pairs.

## Placement guidance

- Render callouts inline with the lesson, *near the line that introduced the feature* — not in a footer or appendix. Proximity is the whole point.
- When multiple callouts cluster around one code block, render them as a vertical stack, not a side-by-side grid. Callouts are read sequentially.
- Use the document's existing accent color for the left border. Don't introduce a new color per callout.

## When to add a callout

Add a callout when *any* of these is true:

- The feature has **no direct Java equivalent** (e.g., destructuring, walrus operator, ownership). Callout is mandatory.
- The feature has a Java equivalent that **differs in important ways** (e.g., `==` vs `===`, `is` vs `==`, move vs copy). Callout is mandatory.
- The feature is **syntactically dense** (destructuring with defaults, spread in object literals, complex pattern matching) even if its semantics are simple. Callout helps.
- The feature is a known **Java-dev tripwire** (e.g., mutable default args in Python, `this`-binding in JS, nil-interface in Go, lifetimes in Rust). Callout is mandatory.

## When *not* to add a callout

- The feature is a **1:1 syntactic equivalent** of a Java construct the reader already knows: a plain `if` statement, a plain `for` loop where the meaning matches, an assignment.
- The feature has **already been introduced** in a previous lesson in the same document. Reference back instead: *"As covered in Lesson 2, `?.` short-circuits on nullish values."*
- The change is purely formatting / whitespace.

## Worked example: an `async` function with await

Suppose the After code includes:

```ts
async function loadUser(id: string): Promise<User | null> {
  const row = await db.user.findUnique({ where: { id } });
  return row ?? null;
}
```

Three callouts are warranted here:

### Callout 1: `async function` returns a Promise

> **`async` function**
> ```ts
> async function f(): Promise<T> { ... }
> ```
> **Semantic.** An `async` function always returns a `Promise`, regardless of whether the body uses `await`. A non-Promise return value is wrapped (`Promise.resolve(x)`); a thrown error becomes a rejected Promise.
> **Java parallel.** Like a method returning `CompletableFuture<T>`. The body looks synchronous because `await` suspends the function (not the thread).
> **Gotcha.** Forgetting `await` returns a `Promise<T>` where you wanted a `T`. The type checker catches some of these; many slip through, especially through `any`.

### Callout 2: `await` suspends until settle

> **`await` operator**
> ```ts
> const x = await promise;
> ```
> **Semantic.** Pauses execution of the surrounding `async` function until the awaited Promise settles. On fulfilment, evaluates to the resolved value. On rejection, throws — propagates as a normal exception that can be caught with `try` / `catch`.
> **Java parallel.** Closest to `CompletableFuture.get()` or `.join()`, but non-blocking — the JavaScript thread continues running other tasks (event loop), and only this *function* is suspended.
> **Gotcha.** Only valid inside `async` functions (or at the top level of an ES module). Inside a regular `function`, it's a syntax error.

### Callout 3: Nullish coalescing `??`

> **Nullish coalescing `??`**
> ```ts
> const value = maybe ?? fallback;
> ```
> **Semantic.** Returns `fallback` if `maybe` is `null` or `undefined`; otherwise returns `maybe`. Distinct from `||`, which falls back on *any* falsy value.
> **Java parallel.** Like `Optional.ofNullable(maybe).orElse(fallback)`.
> **Gotcha.** Using `||` instead of `??` is a frequent bug: `count || 10` returns `10` when `count` is `0`, which is usually wrong. Reach for `??` unless you specifically want falsy-fallback behaviour.

## Library of starter callouts

For specific language features, draw from the language-specific reference files:

- `references/java-typescript-mapping.md` — TS/JS callout-worthy features
- `references/java-python-mapping.md` — Python callout-worthy features
- `references/java-go-mapping.md` — Go callout-worthy features
- `references/java-rust-mapping.md` — Rust callout-worthy features

Each of those files has a *"Common syntax features (always callout-worthy)"* section that lists what to call out routinely in that language. Copy from there; refine the Gotcha to match the actual code in the lesson.
