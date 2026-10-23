---
name: erd
description: Create or edit ERDs from database schemas, migrations, or ORM mappings. Use for database-structure diagrams, not process or system flows.
metadata:
  scope: global
  agents: all
  machines: all
---

# ERD Diagram

Create a source-grounded interactive ERD, either as a standalone HTML file or as part of an HTML document.

## Workflow

1. Establish scope and the source of truth.
   - Prefer DDL and migrations over ORM mappings, and ORM mappings over prose, unless the user names another source.
   - Render only supported tables, columns, constraints, and relationships. Report conflicts instead of merging them; omit unknown relationships.
   - Mark unenforced relationships `logical` or `derived`. Keep composite-key order, nullability, uniqueness, cardinality, and referential actions.
   - Record the key inspected files in the model's source fields.
2. Read [references/schema-model.md](references/schema-model.md) and create the JSON model.
   - Follow the user's scope. Include directly referenced outside tables only when useful, and mark them `existing`.
   - Keep every column for a complete schema; abbreviate only with the user's permission.
   - Group and order tables left to right by domain or dependency without inventing meaning.
3. Validate and render:

   ```bash
   python3 scripts/render_erd.py schema.json --validate-only
   python3 scripts/render_erd.py schema.json --output erd.html
   ```

   For a larger HTML document, include the ERD in that same deliverable. Change the template only for requested behavior it cannot express.
4. Verify against the source and in the browser, and fix failures before delivery.
   - Rendered counts and ordered relationship mappings match the source and model.
   - Desktop and 320–390px widths, light and dark mode, connector alignment, and no console errors.
   - Search, existing-table filtering, zoom, details, Escape, and focus restoration work. Only the diagram scrolls horizontally.

To publish it as a note, use the `notes` skill only after the user approves that external write.
