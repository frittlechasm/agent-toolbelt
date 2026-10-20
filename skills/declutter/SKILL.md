---
name: declutter
description: Review code or skills for simplification, redundant guidance, and performance improvements when asked to declutter, simplify, or optimize.
metadata:
    scope: global
    agents: all
    machines: all
---

# Declutter

Find worthwhile simplifications in the requested code or skills while preserving intended behavior and essential guidance.

## Review

- Follow the requested scope: diff, commit, module, skill, or repository. If unstated, choose a reasonable scope from context and say what you inspected.
- Check callers, existing helpers, and tests before judging code unnecessary.
- In skills, comments, and documentation, remove generic advice, repetition, and explanations the model can readily infer from the code or surrounding context.
    - Keep non-obvious intent, constraints, contracts, and gotchas that affect decisions or prevent mistakes.
- Prioritize dead or duplicate code, needless wrappers, redundant tests, and custom code a standard library, platform, or current dependency can replace.
- Share a UI component only when its behavior and design are genuinely common.
- Check for avoidable repeated work, inefficient queries or I/O, and unnecessary rendering where relevant.
- Keep tests that cover distinct behavior, even when their setup is similar.
- Treat performance ideas as hypotheses until a benchmark, profile, or clear complexity analysis supports them. Do not add caching or memoization by default.
    - Verify that timed work completes correctly; count errors and skipped work.
    - Compare equivalent workloads and conditions. Repeat consequential comparisons and report variation.
    - Separate measured improvement from inferred cause, and relate microbenchmarks to the complete user path.
- Report the few worthwhile findings with file references, expected benefit, and behavior risk. Say when no change is justified.

## Changes

- Edit only when the user asks for changes. Make the smallest useful change and avoid cleanup unrelated to the requested scope.
- Verify affected behavior with focused checks. Measure before and after when claiming a performance gain.
- Summarize what changed and any worthwhile findings left untouched.
