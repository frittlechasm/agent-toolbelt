---
name: flow-diagram
description: Create or edit process flow diagrams as HTML or inline SVG. Use for steps, decisions, retries, and loops, not system topologies, sequence or class diagrams, or ERDs.
metadata:
    scope: global
    agents: all
    machines: all
---

# Flow Diagram

- Turn supplied process descriptions, procedures, or source material into a flow whose steps and paths remain accurate.
- Show process order, decisions, branches, retries, loops, failure paths, and rollback paths when supported.
- Do not substitute a deployment topology, request sequence, data model, or class structure.

## Ground the flow

- Preserve supplied step order, decision conditions, branch labels, loop targets, and terminal outcomes.
- Do not invent missing branches, outcomes, or operational behavior. Ask only when an omission prevents an accurate diagram.
- Label material inferences or proposed behavior instead of presenting them as established process.
- Keep the main path easy to scan and route retries or loops outside it.

## Integrate the output

Use embedded mode when an existing HTML document is supplied or the flow belongs in a larger HTML deliverable. Otherwise use standalone mode.

### Standalone

- When available, use the `html-document` skill for the document shell and this skill for the flow SVG.
- Otherwise create a minimal standalone HTML document with only the title and context needed to understand the process.

### Embedded

- Edit the supplied document in place. Preserve its content, hierarchy, typography, colors, responsive behavior, CSS, IDs, and global JavaScript.
- Insert one inline SVG inside a uniquely named wrapper.
- Scope added CSS and JavaScript to that wrapper. Namespace every SVG ID and reference.
- Do not create another document or iframe.

### Existing visual design

- Treat a supplied diagram as the visual system. Preserve its palette, typography, and relative arrangement unless the user requests a redesign.
- Adjust geometry only as needed for clear labels, connectors, routing, and responsive legibility.

## Render and verify

Before rendering, read [references/diagrams.md](references/diagrams.md) completely. It is the source of SVG layout, typography, connector, responsive, accessibility, and verification requirements.
