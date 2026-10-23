---
name: critique
description: Review UI screenshots for visual quality, variant comparison, or final critique. Not for implementation, accessibility-only audits, or code review.
metadata:
    scope: global
    agents: all
    machines: all
---

# Visual Design Review

Judge the rendered result as a design critic. Do not change anything unless asked.

## Evidence

- Review screenshots at the intended viewport. Render a supplied URL or runnable UI in a browser first.
- Judge only from screenshots, the product goal, target feeling, constraints, and references.
  Ignore code, implementation effort, earlier rationale, and past critiques.
- If the goal or feeling is missing, state the assumption you used. If visuals are missing, say what you cannot assess and ask only for that.
- Use references as a quality bar, not something to copy.
- Stills cannot show interaction, transitions, smoothness, or performance. For motion, check the resting state, key frames, and reduced motion.
  Ask for a recording or runnable UI only when a conclusion needs it.
- Delegate only when the user asks, and give the reviewer only the evidence above.

## Review

Look at the whole before the details:

1. Does the composition lead to the main task?
2. Does it create the intended feeling for these users?
3. Do layout, type, color, surfaces, images, controls, and motion form one identity?
4. Is it useful and readable, or does novelty get in the way?
5. Which details weaken it: spacing, alignment, type, contrast, controls, imagery, or motion?
6. What adds no information, hierarchy, identity, or feedback and should go?

Flag generic AI patterns only when the design does not justify them: stock hero layouts, arbitrary gradients or glows, too many containers,
decorative labels, random accent colors, repeated rounded cards, filler images, and constant decorative animation.

## Response

- Lead with a one- or two-sentence verdict.
- Give up to three important problems by impact, each with visible evidence, why it matters, and a specific visual fix. If there are none, say so.
- Separate visible defects from preferences, and offer preferences as options.
- Name an element worth keeping when it defines the direction.
- Add a short brief for the next pass only when one is warranted.
- Recommend visual changes, not code, unless asked.
- Score only when asked or given a clear reference, and say what the score measures.
- Rank variants only when asked, with the same criteria for each. Keep real tradeoffs visible instead of forcing a winner.
- Mention visible accessibility problems, but leave a full audit to a dedicated review.
- Do not reward complexity; a restrained design can be the strongest.
- Review the submitted state once, then wait for a new version or a request to continue.
