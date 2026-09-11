---
name: eli5
description: Create visual beginner explanations when explicitly requested. Not for plain-text explanations or code-change walkthroughs.
metadata:
    scope: global
    agents: all
    machines: all
---

Explain like I'm someone who knows nothing about this topic.
Create one visual HTML document explainer with big, purposeful illustrations and few words.

## Guide

- ELI5 means the reader is new to the topic, not that they are a child. Use plain language for adults.
- Do not use image generation unless the user explicitly requests a raster image.
- Prefer progressive disclosure. For a process, sequence, or comparison, use one focused interaction with one short caption per state.
- If something exists to manage a change, show a clear before-and-after example that explains why it is needed.
- Let visuals and interaction replace prose. Do not repeat the same explanation in multiple places.
- Keep diagram elements proportional. Prevent overlaps between text and other diagram elements.
- If the visual uses connectors or arrowheads, use thin connectors and small, fixed-size arrowheads.
- Keep connector labels, when present, and text inside icons clearly smaller than node labels.
- If the visual uses connectors, route them around nodes and labels and leave visible clearance at endpoints.
- Make controls easy to click or tap, even when the visible icon is small.
- Use the `html-document` skill when available.
- Check the document at about 320px wide and at desktop width. Make sure nothing is cut off, overflows, or is misaligned, and test the interaction.
