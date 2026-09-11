---
name: erd-diagram
description: Create or edit ERDs from database schemas, migrations, or ORM mappings. Use for database-structure diagrams, not process or system flows.
metadata:
  scope: global
  agents: all
  machines: all
---

# ERD Diagram

Create a source-grounded interactive ERD, either as a standalone HTML file or as part of an HTML document.

## Workflow

1. Establish scope and source authority.
   - Prefer DDL and migrations over ORM mappings, and ORM mappings over prose, unless the user names another source of truth.
   - Render only supported tables, columns, constraints, and relationships. Report conflicts instead of merging them. Mark unenforced relationships `logical` or `derived`.
   - Record the important inspected files in the model's source fields.
   - Preserve composite-key order, nullability, uniqueness, cardinality, and referential actions. Omit unknown relationships rather than guessing.
2. Read [references/schema-model.md](references/schema-model.md) and create the normalized JSON model.
   - Follow the user's scope. Include directly referenced external tables only when useful and mark them `existing`.
   - Keep every column for a complete schema. Abbreviate only with the user's permission.
   - Group and order tables from left to right by domain or dependency without inventing semantics.
3. Validate and render:

   ```bash
   python3 scripts/render_erd.py schema.json --validate-only
   python3 scripts/render_erd.py schema.json --output erd.html
   ```

   Include the ERD in the same deliverable when composing a larger HTML document. Modify the template only for requested behavior it cannot express.
4. Verify source and browser behavior.
   - Match rendered counts and ordered relationship mappings to the source and model.
   - Check desktop and 320–390px widths, light and dark appearance, connector alignment, and console errors.
   - Exercise search, existing-table filtering, zoom, details, Escape, and focus restoration. Only the diagram may scroll horizontally.
   - Fix schema, layout, or interaction failures before delivery.

If the artifact will be published as an HTML note, use the HTML-notes workflow only after the user authorizes that external write.
