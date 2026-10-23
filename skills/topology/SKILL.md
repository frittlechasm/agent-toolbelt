---
name: topology
description: Create or edit system architecture diagrams as HTML or inline SVG. Use for topologies, not process flows, sequence or class diagrams, or ERDs.
metadata:
    scope: global
    agents: all
    machines: all
---

# Architecture Diagram

Map system components, infrastructure, boundaries, and relationships from supplied descriptions, configuration, docs, or source code.

## Ground the topology

- Prefer deployed configuration and executable source over conflicting prose, and report material conflicts instead of merging them.
- Include only supported components and relationships, keeping runtime, data, identity, provisioning, build, and deployment links.
- Label inferences and proposals. Configured state is not observed runtime state.
- If a requested deployment has no target topology, settle the scope or label the result a proposal.
- Do not substitute an authentication sequence or login flow.

## Output

- **Standalone:** build the page with the `html` skill around this skill's SVG.
  Without it, make a minimal page in Nunito at 17px/1.7 with only the title and context needed to read the diagram.
  Only the Google Fonts stylesheet for Nunito and JetBrains Mono may load externally; inline everything else.
- **Embedded** (an existing HTML document is supplied, or the map belongs in a larger one): edit the document in place,
  keeping its content, styles, responsive behavior, IDs, and scripts. Insert one inline SVG in a uniquely named wrapper,
  scope added CSS and JavaScript to it, and prefix every SVG ID and reference. Reuse a matching font stylesheet or add it once.
  Do not create another document or iframe.
- Treat a supplied diagram or benchmark as the visual system: keep its shell, palette, type, composition, and node and region layout unless asked.
  Adjust geometry only for clearance, routing, or legibility; do not redesign it or keep flawed coordinates.

## Render and verify

Read `references/diagrams.md` completely before rendering.
Keep maps static unless animation or a guided walkthrough is requested; then also read `references/motion.md`.
