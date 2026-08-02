# Diagrams

Read this after the user, invoking skill, or generating agent has selected a diagram.
This reference governs rendering, not whether domain content requires one.

## Choose the simplest format

- Prefer inline SVG for small architecture maps and simple flows. It keeps the document standalone and can reuse the document's color tokens.
- Use Mermaid only for dense UML, sequence, state, or branching diagrams and only when the user accepts its runtime or external dependency.
- Because Mermaid cannot consume CSS custom properties directly, mirror the document theme with literal color values.
- Verify print output only when printing was requested.
- Use an existing informational image when it communicates the idea better than a recreated diagram.

## Compose clearly

- Give the diagram one message and a logical reading direction.
- Keep node labels short. Size nodes from their text, use consistent dimensions and spacing within a row, and connect node borders rather than centers.
- Leave enough space for arrowheads and short edge labels. Avoid crossing edges; switch layout or format when the graph becomes dense.
- Size the SVG view box to all content plus padding so labels and markers are not clipped.
- Use document colors and typography. Avoid gradients, shadows, decorative illustrations, and color-only meaning.
- Add a concise accessible name or nearby explanation. Do not duplicate a full prose description in both places.

Scale the diagram to the content column. If it becomes unreadable when reduced, give only the diagram a horizontal scroller.
Inspect labels, edges, clipping, contrast, and narrow-width behavior.
Inspect print output only when printing was requested.
