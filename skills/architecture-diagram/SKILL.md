---
name: architecture-diagram
description: Create or edit system architecture diagrams as HTML or inline SVG. Use for topologies, not process flows, sequence or class diagrams, or ERDs.
metadata:
    scope: global
    agents: all
    machines: all
---

# Architecture Diagram

- Create a system-level topology from supplied descriptions, configuration, documentation, or source code.
- Show deployed components, infrastructure, boundaries, and relationships, not process, protocol, sequence, or application flow.

## Ground the topology

- Prefer deployed configuration and executable source over conflicting prose. Report material conflicts instead of merging them.
- Label requested inferences and proposals. Do not present configured state as observed runtime state.
- Preserve meaningful runtime, data, identity, provisioning, build, and deployment relationships.
- Include only supported components and relationships.
- If a requested deployment lacks a target topology, establish the missing scope or label the result as a requested proposal.
- Do not substitute an authentication protocol sequence or login flow.

## Integrate the output

Use embedded mode when an existing HTML document is supplied or the diagram belongs in a larger HTML deliverable. Otherwise use standalone mode.

### Standalone

- When available, use the `html-document` skill for the shell and this skill for the architecture SVG.
- Otherwise create a minimal HTML shell using Nunito at 17px/1.7. Include only the title and context needed to understand the diagram.
- A Google Fonts stylesheet for Nunito and JetBrains Mono is allowed. Inline every other asset.

### Embedded

- Edit the supplied document in place. Preserve its content, hierarchy, typography, colors, responsive behavior, CSS, IDs, and global JavaScript.
- Insert one inline SVG inside a uniquely named wrapper.
- Scope added CSS and JavaScript to that wrapper. Namespace every SVG ID and reference.
- Reuse an identical permitted font stylesheet or add it once.
- Do not create another document or iframe.

### Existing visual design

- Treat a supplied diagram or visual benchmark as the design system.
- Preserve its document shell, palette, typography, relative composition, node and region arrangement unless the user requests a change.
- Apply topology and wording edits within that system.
- Adjust geometry only as needed for clearance, routing, or legibility. Do not arbitrarily redesign it or freeze flawed coordinates.

## Render and verify

Before rendering, read `references/diagrams.md` completely.
It defines the SVG design, layout, responsive, accessibility, mechanics, and verification requirements.
Keep maps static by default. For requested animation or a guided walkthrough, read `references/motion.md` and cover every supported scenario and flow in scope.
