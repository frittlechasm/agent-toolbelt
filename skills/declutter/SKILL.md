---
name: declutter
description: Review existing code for simplification and performance improvements when asked to declutter, simplify, or optimize it.
metadata:
  scope: global
  agents: all
  machines: all
---

# Declutter

Find worthwhile simplifications and performance improvements in the requested code without changing its intended behavior.

## Review

- Follow the requested scope: diff, commit, module, or repository. If unstated, choose a reasonable scope from context and say what you inspected.
- Check callers, existing helpers, and tests before judging code unnecessary.
- Prioritize dead or duplicate code, needless wrappers and abstractions, repeated UI components, and redundant tests.
- Check for avoidable repeated work, inefficient queries or I/O, and unnecessary rendering where relevant.
- Keep a test if it covers a distinct behavior, even when its setup resembles another test. Share a UI component only when its behavior and design are genuinely common.
- Treat performance ideas as hypotheses until a benchmark, profile, or clear complexity analysis supports them. Do not add caching or memoization by default.
- Report the few worthwhile findings with file references, expected benefit, and behavior risk. Say when no change is justified.

## Changes

- Edit only when the user asks for changes. Make the smallest useful change and avoid cleanup unrelated to the requested scope.
- Verify affected behavior with focused checks. Measure before and after when claiming a performance gain.
- Summarize what changed and any worthwhile findings left untouched.
