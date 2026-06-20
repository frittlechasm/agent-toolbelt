# Concept Callouts — Patterns and Examples

Concept Callouts are short boxed explainers that surface every non-trivial syntactic feature **of the target language** for a reader who is fluent in the **comparison language** (resolved per `SKILL.md`). Every Lesson should use callouts liberally; for this audience, over-explaining the target language is preferable to under-explaining.

In the examples below the comparison language happens to be Java; substitute whatever was resolved.

## Two rules that override everything

1. **Explain the target language only — never the comparison language.** A callout teaches a construct of the language the code is *written in*. The comparison language appears *only* inside the "Parallel" field, as an anchor. Never write a callout whose subject is a comparison-language construct: the reader already knows it, and explaining it wastes their time and insults their fluency.
2. **Explain each construct once.** The first time a target construct appears in the document, give it a full callout. Every later appearance references back instead — *"as covered in Lesson 2, `?.` short-circuits on nullish values"* — never a second callout for the same feature. Duplicate callouts are the most common way these documents bloat; track what you've already taught.

## Anatomy of a Callout

Each callout has five parts in this order:

1. **Name** of the feature (e.g., "Optional chaining `?.`").
2. **Minimal syntax** in monospace.
3. **Semantic**: what it evaluates to, including edge cases.
4. **Parallel**: the closest equivalent *in the comparison language*, even if imperfect. Explicitly call out where it diverges. (This is the only place the comparison language appears.)
5. **Gotcha**: one pitfall to remember (often the divergence from the parallel).

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
    <dt>Parallel</dt>
    <dd>
      In Java, like
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

The `<dl>` / `<dt>` / `<dd>` structure renders cleanly, prints well, and is keyboard-accessible without extra work. The Name maps to the `<h4>`, the Minimal syntax to the `<pre><code>`, and Semantic / Parallel / Gotcha to `<dt>`/`<dd>` pairs. The "Parallel" `<dd>` should open with the comparison language ("In Python, …", "In C#, …") so the anchor is unmistakable.

## Placement guidance

- Render callouts inline with the lesson, *near the line that introduced the feature* — not in a footer or appendix. Proximity is the whole point.
- When multiple callouts cluster around one code block, render them as a vertical stack, not a side-by-side grid. Callouts are read sequentially.
- Use the document's existing accent color for the left border. Don't introduce a new color per callout.

## When to add a callout

Add a callout when *any* of these is true (and the construct has **not** already been explained earlier in the document):

- The target construct has **no direct equivalent** in the comparison language (e.g., destructuring, walrus operator, ownership). Callout is mandatory.
- The target construct has a comparison-language equivalent that **differs in important ways** (e.g., `==` vs `===`, `is` vs `==`, move vs copy). Callout is mandatory.
- The construct is **syntactically dense** (destructuring with defaults, spread in object literals, complex pattern matching) even if its semantics are simple. Callout helps.
- The construct is a known **tripwire for someone arriving from another language** (e.g., mutable default args in Python, `this`-binding in JS, nil-interface in Go, lifetimes in Rust). Callout is mandatory.

## When *not* to add a callout

- The construct is a **1:1 syntactic equivalent** of something the reader already knows from the comparison language: a plain `if` statement, a plain `for` loop where the meaning matches, an assignment.
- The construct belongs to the **comparison language**, not the target — never in scope (see rule 1 above).
- The construct has **already been introduced** earlier in the same document — reference back instead (rule 2 above).
- The change is purely formatting / whitespace.

## Worked example: an `async` function with await (target TypeScript, comparison Java)

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
> **Parallel.** In Java, like a method returning `CompletableFuture<T>`. The body looks synchronous because `await` suspends the function (not the thread).
> **Gotcha.** Forgetting `await` returns a `Promise<T>` where you wanted a `T`. The type checker catches some of these; many slip through, especially through `any`.

### Callout 2: `await` suspends until settle

> **`await` operator**
> ```ts
> const x = await promise;
> ```
> **Semantic.** Pauses execution of the surrounding `async` function until the awaited Promise settles. On fulfilment, evaluates to the resolved value. On rejection, throws — propagates as a normal exception that can be caught with `try` / `catch`.
> **Parallel.** In Java, closest to `CompletableFuture.get()` or `.join()`, but non-blocking — the JavaScript thread continues running other tasks (event loop), and only this *function* is suspended.
> **Gotcha.** Only valid inside `async` functions (or at the top level of an ES module). Inside a regular `function`, it's a syntax error.

### Callout 3: Nullish coalescing `??`

> **Nullish coalescing `??`**
> ```ts
> const value = maybe ?? fallback;
> ```
> **Semantic.** Returns `fallback` if `maybe` is `null` or `undefined`; otherwise returns `maybe`. Distinct from `||`, which falls back on *any* falsy value.
> **Parallel.** In Java, like `Optional.ofNullable(maybe).orElse(fallback)`.
> **Gotcha.** Using `||` instead of `??` is a frequent bug: `count || 10` returns `10` when `count` is `0`, which is usually wrong. Reach for `??` unless you specifically want falsy-fallback behaviour.

## Finding which constructs to call out

There are no per-language cheat-sheets — a fixed list would surface the same callouts every time, when the point is to react to the non-obvious constructs in *this* code. Run the category sweep in `references/any-language.md` over the actual After code to flag what diverges from the comparison language (absence/null, equality, mutability, async, error model, type-system surprises, syntactic sugar, memory/ownership, metaprogramming, and platform/runtime/framework behaviour). For each flagged construct, fill the five fields below; the Gotcha is usually the precise way it diverges from its comparison-language parallel.
