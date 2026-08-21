---
name: eli5
description: Use when the user asks for ELI5 or an illustrated beginner explanation. Do not use for ordinary concise explanations, code-change walkthroughs, or UI mockups.
metadata:
  scope: global
  agents: all
  machines: all
---

Explain like I'm someone who knows nothing about this topic.
Create one visual HTML document explainer with big, purposeful illustrations and few words.

## Guide
- Do not use image generation unless the user explicitly requests a raster image.
- Prefer progressive disclosure. For a process, sequence, or comparison, use one focused interaction with one short caption per state.
- Let visuals and interaction replace prose. Do not repeat the same explanation in multiple places.
- Keep diagram elements proportional. Prevent overlaps between text and other diagram elements.
- If the visual uses connectors or arrowheads, use thin connectors and small, fixed-size arrowheads.
- Keep connector labels, when present, and text inside icons clearly smaller than node labels.
- If the visual uses connectors, route them around nodes and labels and leave visible clearance at endpoints.
