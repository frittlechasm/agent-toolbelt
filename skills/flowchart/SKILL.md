---
name: flowchart
description: Create or edit HTML or inline SVG process flows for steps, decisions, retries, and loops. Not for topologies, sequence or class diagrams, or ERDs.
metadata:
    scope: global
    agents: all
    machines: all
---

# Flow Diagram

Diagram the supplied process, including its decisions, branches, retries, loops, failures, and rollback paths.

## Ground the flow

- Keep the supplied step order, decision conditions, branch labels, loop targets, and end states.
- Do not invent branches, outcomes, or behavior. Label material inferences or proposals; ask only when a gap prevents an accurate diagram.
- Keep the main path easy to scan. Place retry and loop steps beside the main column, not on it, and route their connectors outside it.

## Output

- **Standalone:** build the page with the `html` skill around this skill's SVG.
  Without it, make a minimal HTML page with only the title and context needed to follow the process.
- **Embedded** (an existing HTML document is supplied, or the flow belongs in a larger one): edit the document in place,
  keeping its content, styles, responsive behavior, IDs, and scripts. Insert one inline SVG in a uniquely named wrapper,
  scope added CSS and JavaScript to it, and prefix every SVG ID and reference. Do not create another document or iframe.
- Treat a supplied diagram as the visual system: keep its palette, type, and arrangement unless asked to redesign.
  Adjust geometry only for clear labels, connectors, and responsive legibility.

## Render and verify

Read `references/diagrams.md` completely before rendering.
Keep diagrams static unless animation or a guided walkthrough is requested; then also read `references/motion.md`.
