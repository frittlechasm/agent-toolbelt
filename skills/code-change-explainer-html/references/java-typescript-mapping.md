# Java ↔ TypeScript / JavaScript Mapping

Authoritative parallels for the Java Mental Model section and Concept Callouts in TS/JS code. Pull from this file when drafting lessons.

## Module system

| Java | TypeScript |
|---|---|
| `package com.acme;` | path encodes namespace: `src/acme/user.ts` |
| `import com.acme.User;` | `import { User } from './user';` |
| `public class Foo` (one per file) | `export class Foo` (default or named, multiple per file) |
| `import static ...` | `import * as ns from '...'` |
| Maven/Gradle artifact | npm/pnpm/yarn package on the npm registry |

**ESM vs CommonJS**: modern TS targets ESM (`import`/`export`). Older Node code uses CommonJS (`require`/`module.exports`). They are not freely interchangeable at runtime; mixing them requires careful tooling.

**Default vs named exports**: a file can have at most one *default* export and any number of *named* exports. Java has only "the public class in this file" plus other top-level classes. Default exports are imported without braces (`import Foo from './foo'`); named exports require braces (`import { Foo } from './foo'`).

## Variables and equality

| Java | TS/JS |
|---|---|
| `final var x = ...` | `const x = ...` |
| `var x = ...` (Java 10+) | `let x = ...` |
| `Foo x = null;` | `let x: Foo \| null = null;` |
| `==` (reference for objects) / `.equals()` | `===` (strict) / `==` (loose — *avoid*) |

**Gotcha**: `==` in JS performs type coercion (`0 == "0"` is `true`; `null == undefined` is `true`). Always use `===`. There is no built-in `.equals()` for value-equality on objects; you compare fields manually or use a library (`lodash.isEqual`, `deep-equal`).

**Truthy / falsy**: `if (x)` in JS converts `x` to a boolean. The falsy values are `false, 0, -0, 0n, "", null, undefined, NaN`. Everything else is truthy — including `"0"`, `"false"`, `[]`, and `{}`. This is the single biggest source of "why didn't my null check work" bugs for Java devs.

## Type system

| Java | TS |
|---|---|
| `class Foo` | `class Foo` |
| `interface Foo` | `interface Foo` |
| `record Foo(...)` | `type Foo = { ... }` or `interface Foo` |
| `enum` | `enum` or string literal union: `'a' \| 'b' \| 'c'` |
| Generics `<T>` | Generics `<T>` |
| `T extends Comparable<T>` | `T extends Comparable<T>` |
| `List<? extends Foo>` | no wildcards — use union/intersection types |
| `Optional<T>` | `T \| undefined` (or `T \| null`) |
| sealed class (Java 17+) | discriminated union with a `kind` field |

**Structural vs nominal**: Java is nominal — a class implements an interface only if it declares so. TS is structural — anything with the matching shape *is* that type. This is duck typing at the type-checker level. A `{ name: string }` literal satisfies any interface requiring exactly `{ name: string }` without an `implements` declaration.

**Type erasure**: both languages erase generics at runtime, but TS erases *all* type information. There is no `instanceof Foo<Bar>`, no `Class<T>`, and no reflection on types. `typeof` returns one of seven strings for primitives; `instanceof` works on class instances but not on `interface` or `type`.

**Type assertion `as`**: like a Java cast `(Foo) x`, but unchecked at runtime. The type checker trusts you. `x as unknown as Foo` is the TS equivalent of a forced cast.

## Functions and lambdas

| Java | TS/JS |
|---|---|
| Lambda: `x -> x.foo` | Arrow function: `x => x.foo` |
| Method reference: `User::getName` | `user => user.name` (no syntactic sugar) |
| `Function<A, B>` | `(a: A) => B` |
| `BiFunction<A, B, C>` | `(a: A, b: B) => C` |
| `Runnable` | `() => void` |
| `Supplier<T>` | `() => T` |
| `Consumer<T>` | `(t: T) => void` |
| Anonymous class | object literal with methods, or class expression |
| `this` in lambda = enclosing instance | arrow function `this` = enclosing lexical scope; regular `function` `this` = call site |

**`this`-binding gotcha** (the largest JS tripwire for Java devs): arrow functions inherit `this` from the surrounding lexical scope (like Java lambdas). Regular `function` declarations and class methods *passed as callbacks* lose `this` — at call time, `this` becomes whatever the caller binds (often `undefined` in strict mode). Fixes:

```ts
setTimeout(this.handler.bind(this), 0);
setTimeout(() => this.handler(), 0);
```

**First-class functions**: JS functions are objects. They have properties (`f.name`, `f.length`), can be assigned, passed, returned, and stored. The closest Java analogue is a `Function<A, B>` interface instance.

**Closures**: JS closures capture variables by reference and can mutate them. Java lambdas can only capture *effectively final* variables. So `for (let i = 0; i < 3; i++) setTimeout(() => console.log(i), 0)` logs `0, 1, 2` because `let` creates a per-iteration binding; using `var` would log `3, 3, 3`.

## Async

| Java | TS/JS |
|---|---|
| `CompletableFuture<T>` | `Promise<T>` |
| `CompletableFuture.supplyAsync(() -> ...)` | `(async () => ...)()` or `Promise.resolve().then(() => ...)` |
| `.thenApply(f)` | `.then(f)` |
| `.thenCompose(f)` | `.then(f)` where `f` returns a Promise (auto-flattens) |
| `.exceptionally(e -> ...)` | `.catch(e => ...)` |
| `.handle((v, e) -> ...)` | `.then(v => ..., e => ...)` or `.finally(() => ...)` |
| `.get()` (blocking) | `await` (non-blocking; only inside `async`) |
| `CompletableFuture.allOf(...)` | `Promise.all([...])` |
| `CompletableFuture.anyOf(...)` | `Promise.race([...])` |

**Async function = Promise**: an `async` function *always* returns a `Promise`, even if the body has no `await`. Forgetting `await` silently leaks a `Promise<T>` where you expected a `T`. The type checker catches some of these; many slip through.

**Event loop, not threads**: Node.js and browsers run JS on a single thread with an event loop. `await` yields control to the loop, not to another thread. `Promise.all` does *not* parallelize CPU work — it overlaps I/O. CPU-bound work must go to a worker thread (Web Worker, Node `worker_threads`).

**Unhandled rejection**: a `Promise` whose rejection is not caught crashes the process (Node) or fires `window.unhandledrejection` (browser). Always attach a `.catch` or `try`/`catch` around `await`.

## Collections and iteration

| Java | TS/JS |
|---|---|
| `List<T>` / `ArrayList<T>` | `Array<T>` or `T[]` |
| `Map<K, V>` / `HashMap` | `Map<K, V>` (built-in) — or plain object `{ [k: string]: V }` (string keys only) |
| `Set<T>` | `Set<T>` (built-in) |
| `Stream<T>.map/filter/reduce/collect` | `Array.prototype.map/filter/reduce` |
| `Optional<T>.map().orElse(...)` | `value?.foo ?? default` |
| `Iterator<T>` | iterable protocol (`[Symbol.iterator]`) and iterator protocol (`next()`) |
| `for (T t : list)` | `for (const t of list)` |
| `list.stream().toList()` | already an `Array`; no terminal needed |

**Plain object is not a Map**: `{}` keys are coerced to strings and the prototype chain pollutes lookups. Use the built-in `Map` for typed keys and a clean key space.

**`Array.sort` mutates**: just like `Collections.sort`, the array is sorted in place *and* returned. Defaults to lexicographic *string* comparison, so `[10, 2].sort()` gives `[10, 2]`. Always pass a comparator: `[10, 2].sort((a, b) => a - b)`.

**No `Comparator` chain**: there is no `.thenComparing()`. Sort by multiple keys with a single comparator: `arr.sort((a, b) => a.x - b.x || a.y - b.y)`.

## Common syntax features (always callout-worthy)

These features almost always deserve a Concept Callout when they appear in lesson code:

- **Optional chaining `?.`** — short-circuits to `undefined` on `null`/`undefined`. Java parallel: `Optional.map(...).map(...)`. Gotcha: distinct from the `?` in TS optional-property syntax.
- **Nullish coalescing `??`** — falls back only on `null`/`undefined` (not on `0`, `""`, `false`). Java parallel: `Optional.orElse(default)`. Gotcha: `\|\|` falls back on any falsy value, including `0` and `""` — a frequent bug source.
- **Destructuring `const { a, b } = obj` / `const [a, b] = arr`** — no Java equivalent; closest is record-pattern deconstruction (Java 21+). Gotcha: renaming uses `: newName` (`const { a: x } = obj`), not `=`.
- **Default values in destructuring** `const { a = 1 } = obj` — applied only when the property is `undefined`, not when `null`.
- **Spread / rest `...args`** — Java equivalent: varargs (`String...`) plus `List.of(...)`. Spread copies *shallow*: `{ ...obj, b: 2 }` clones one level deep, not nested objects.
- **Template literals `` `Hello ${name}` ``** — Java parallel: `String.format` / `MessageFormat`. Multi-line by default — no `\n` joins.
- **Arrow function vs `function` declaration** — different `this`-binding (see above) and hoisting rules.
- **`typeof` / `instanceof`** — `typeof` returns a string for primitives (`"string"`, `"number"`, `"object"`, etc., plus the famous `typeof null === "object"` bug); `instanceof` walks the prototype chain.
- **`as` type assertion** — like an unchecked Java cast. No runtime check; lies are silent until they crash.
- **Discriminated unions** — pattern match via `switch (obj.kind)`. Closest Java is sealed interfaces + `instanceof` patterns (Java 21).
- **Generators `function*` / `yield`** — lazy iteration, like a `Stream` produced one element at a time, or an `Iterator` with explicit `hasNext`/`next`.
- **`for ... of` vs `for ... in`** — `of` iterates values (like Java's enhanced `for`); `in` iterates *keys* (string property names). Using `for...in` over an array is almost always a bug for Java devs.

## Common framework parallels

| Java (Spring) | TS (Express / Next.js / NestJS) |
|---|---|
| `@RestController` | route handler file: `app/api/.../route.ts` (Next.js) or `app.get(...)` (Express); `@Controller` class (NestJS) |
| `@Service` | a module that exports a singleton, or a class with methods; `@Injectable` (NestJS) |
| `@Repository` | a DAO module or a Prisma client / Drizzle / TypeORM repository |
| `@Component` + DI | manual import; or NestJS's `@Injectable` + `@Inject` |
| DTO class | `interface` or `type`, often validated with Zod |
| `@Transactional` | `prisma.$transaction([...])` or `db.transaction(async tx => {...})` |
| `application.yml` | `.env` + Zod validation; or `next.config.js` |
| `Logger logger = LoggerFactory.getLogger(Foo.class)` | `import logger from './logger'` (typically `winston`, `pino`, or `console`) |
| `@Valid` + Bean Validation | Zod / Yup / class-validator schemas |
| `@RequestParam` / `@PathVariable` | `searchParams` + dynamic route segments (Next.js) |

## Java-only intuitions that don't translate

- **Checked exceptions**: JS has no checked exceptions. Any function can throw any value (objects, strings, anything — though `Error` instances are conventional).
- **`final`-by-default fields**: `const` makes the *binding* immutable, not the *object*. `const x = { a: 1 }; x.a = 2;` is legal. Deep immutability needs `Readonly<T>`, `as const`, or libraries (Immer, immutable.js).
- **`synchronized`**: no equivalent — the event loop guarantees no two pieces of JS run at the same time on the same thread. Async interleaving can still cause logical races between awaits.
- **Reflection**: extremely limited. `Object.keys`, `Object.getPrototypeOf`, and `Reflect.*` exist but you cannot enumerate types or generics at runtime.

## Useful TS-only ideas built from Java intuitions

- **IIFE `(() => ...)()`** — a Java instance-initializer block or a one-shot anonymous class invocation.
- **Branded types** `type UserId = string & { __brand: 'UserId' }` — phantom-type pattern; closest Java idea is a single-field record class.
- **Conditional types** `T extends U ? X : Y` — compile-time type-level if/else; no Java parallel.
- **Mapped types** `{ [K in keyof T]: ... }` — compile-time iteration over keys; closest Java is reflection with `Class.getDeclaredFields()`, but at compile time.
- **`unknown`** — a safer `Object` / `Any`. You must narrow before using.
- **`never`** — bottom type. The type of `throw`, of an exhausted switch, of an impossible state.
