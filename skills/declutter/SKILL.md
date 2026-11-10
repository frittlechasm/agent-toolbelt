---
name: declutter
description: Review code or skills for simpler approaches, better performance, and weak or unreliable tests when asked to declutter, simplify, or optimize.
metadata:
    scope: global
    agents: claude, codex
    machines: all
---

# Declutter

Find worthwhile ways to simplify the requested code or skills. Keep the intended behavior and essential guidance.
Existing code, tests, and instructions must earn their place. Keep one only when you can say what it does that nothing else covers.
Review the requested diff, commit, module, skill, or repository.
If the user does not say what to review, choose from context and say what you will review before starting.

## Code review

- Before deciding code is unnecessary, check its callers, what creates and uses its files or data, and related helpers and tests.
    - Code can be used without a direct caller: framework wiring, reflection, config, scheduled jobs, or consumers outside the repo.
    - For checks and code kept for older versions or workflows, find what they protect. A working check may no longer be needed.
    - Check whether other protections cover the same risk. Explain what protection would still be lost if the code were deleted.
    - If these checks find no use, delete it. "Might be needed later," "it's harmless," and "the tests pass" are not uses.
- Start with unused or duplicate code, needless wrappers, and custom code that the standard library, platform, or a current dependency can replace.
- Look for duplicate or unreliable tests, weak checks, tests that copy the code's logic, and mocks that skip the behavior being tested.
- Remove tests that add little confidence. Fix useful tests.
- Share a UI component only when its uses need the same behavior and design.
- Look for repeated work, inefficient queries, unnecessary reads and writes, and needless rendering where relevant.
- Treat performance ideas as unproven until a benchmark, profile, or clear analysis of how work grows with input size supports them.
    - Make sure timed runs finish correctly. Count errors and skipped work.
    - Compare the same work under the same conditions. Repeat comparisons that guide decisions, and report how much results vary.
    - Separate measured gains from possible explanations. Explain what small benchmarks mean for the full user flow.
- Do not add caching by default.

## Skills, comments, and documentation

- Remove advice that fits almost any task, repeated points, and explanations already clear from the code or context.
- Use other skills and scripts where needed. Do not list them in advance or repeat their instructions.
- Delete what is not needed instead of rewording it, including steps, files, and support for old workflows.
- Keep non-obvious reasons, limits, rules others rely on, and pitfalls that affect decisions or prevent mistakes.
- Keep setup steps, background, examples, and links only if the skill needs them for its stated job.
- Keep steps handled by scripts out of skill instructions.
- For each instruction, ask what decision or action it changes. Remove it if it changes neither.

## Findings and changes

- Report only findings worth acting on. Include file references, expected benefit, and risks to current behavior. Say when no change is needed.
- Edit only when the user asks. Then delete without asking about each item, and stay within the requested scope.
  Ask first only when use is unclear and the code is a public API, schema, or stored data format.
- Run checks focused on the changed behavior. Measure before and after if you claim a performance gain.
- Summarize the changes and any useful findings you did not address.
