---
name: visual-design-review
description: Review rendered UI screenshots for visual quality, variant comparison, or final critique. Do not use for implementation, accessibility-only audits, or code review.
metadata:
    scope: global
    agents: all
    machines: all
---

# Visual Design Review

Judge the rendered result as a design critic. Do not make changes unless the user asks.

## Evidence

- Review screenshots at the intended viewport. If the user supplies a URL or runnable UI, render it in a browser first.
- For the first pass, use only the screenshots, product goal, target feeling, constraints, and references.
- Ignore the code, implementation effort, earlier rationale, and past critiques. Preserve the agreed product goal and design constraints.
- If the goal or target feeling is missing, state the assumption you used instead of blocking the review.
- If screenshots or other visual evidence are missing, review what is available. Say what you cannot assess and ask only for what you need to finish that part.
- Do not invent findings.
- Use references as a quality bar and visual guide. Do not reward copying them.
- For motion, inspect the resting state and a few key frames. Check the reduced-motion state when available.
- A still image cannot show interaction behavior, transition quality, animation smoothness, or rendering performance.
- Mark any inferences and ask for a runnable UI, recording, or key states when those qualities matter.
- Delegate an independent review only when the user asks and delegation is available and authorized. Give the reviewer fresh context.
- Provide only the visual evidence, product goal, accepted constraints, target feeling, and references. Do not include earlier rationale or critiques.

## Review

Start with the whole design before inspecting details:

1. Does the composition guide attention to the main task?
2. Does the design create the intended feeling and fit the product's users?
3. Do layout, type, color, surfaces, images, controls, and motion create one clear identity?
4. Is the design useful and easy to read, or does visual novelty get in the way?
5. Which details weaken the result: spacing, alignment, type, contrast, control styling, imagery, or motion?
6. What should be removed because it adds no information, hierarchy, identity, or useful feedback?

Flag generic AI-looking patterns only when the design does not justify them.
Examples include:

- generic hero layouts
- arbitrary gradients or glows
- too many containers
- decorative labels
- random accent colors
- repeated rounded cards
- filler images
- constant decorative animation

## Response

- Lead with a direct one- or two-sentence verdict.
- Report up to three important problems, ordered by impact. If there are no important visual problems, say so instead of inventing some.
- For each problem, point to visible evidence, explain why it matters, and give a specific visual change.
- Separate visible defects from subjective preferences. Present preferences as options, not corrections.
- Name an element worth keeping when it helps define the design direction.
- End with a short brief for the next design pass only when another pass is warranted.
- Recommend visual changes, not implementation details, unless the user asks for code guidance.
- Score the work only when the user asks or provides a clear comparison reference. Explain what the score measures.
- Rank variants only when the user asks. Apply the same criteria to every variant and keep real tradeoffs visible instead of forcing a winner.

## Boundaries

- Do not edit files or redesign the UI unless the user asks.
- Mention visible accessibility problems, but use a dedicated accessibility review for a full audit.
- Do not reward complexity for its own sake. A restrained design can be the strongest option.
- Do not start an automatic builder-review loop. Review the submitted state once, then wait for a new version or an explicit request to continue.
