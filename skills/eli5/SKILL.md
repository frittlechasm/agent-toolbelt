---
name: eli5
description: Create visual beginner explanations when explicitly requested. Not for plain-text explanations or code-change walkthroughs.
metadata:
    scope: global
    agents: all
    machines: all
---

Create one visual HTML explainer, built with the `html` skill, for an adult who knows nothing about the topic.
Use big, purposeful illustrations, few words, and plain language. ELI5 means new to the topic, not a child.

- Do not generate raster images unless the user asks for one.
- Reveal ideas step by step. For a process, sequence, or comparison, use one focused interaction with one short caption per state.
- If something exists to manage a change, show a before-and-after that explains why it is needed.
- Let visuals replace prose, and say each thing once.
- Keep diagram elements proportional, with no text overlapping other elements.
- Keep any connectors thin, with small fixed-size arrowheads, routed around nodes and labels with clear space at the ends.
- Keep connector labels and icon text clearly smaller than node labels.
- Make controls easy to click or tap, even when the icon is small.
- Check at about 320px and desktop widths for clipping, overflow, and misalignment, and test the interaction.
