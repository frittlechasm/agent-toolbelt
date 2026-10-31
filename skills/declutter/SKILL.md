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
Review the requested diff, commit, module, skill, or repository.
If the user does not say what to review, choose from context and say what you will review before starting.

## Code review

- Before deciding code is unnecessary, check its callers, what creates and uses its files or data, and related helpers and tests.
    - For checks and code kept for older versions or workflows, find what they protect. A working check may no longer be needed.
    - Check whether other protections cover the same risk. Explain what protection would still be lost if the code were deleted.
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
- Delete steps, files, and support for old workflows that are no longer needed instead of just rewriting them.
- Keep non-obvious reasons, limits, rules others rely on, and pitfalls that affect decisions or prevent mistakes.
- Keep setup steps, background, examples, and links only if the skill needs them for its stated job.
- Keep steps handled by scripts out of skill instructions.
- For each instruction, ask what decision or action it changes. Remove it if it changes neither.

## Findings and changes

- Report only findings worth acting on. Include file references, expected benefit, and risks to current behavior. Say when no change is needed.
- Edit only when the user asks. Make the smallest useful change within the requested scope.
- Run checks focused on the changed behavior. Measure before and after if you claim a performance gain.
- Summarize the changes and any useful findings you did not address.
