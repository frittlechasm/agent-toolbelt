# Default design

Use this visual system only when the user or invoking skill supplies no template, brand, or design system.

## Foundation

- Use `#0a0a0a` for the page, `#f5f5f5` for primary text, `#a3a3a3` for secondary text, and `#262626` for subtle separators.
- Load Nunito weights 400, 600, and 700 as the one intentional document-design dependency:

```html
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&amp;display=swap" rel="stylesheet">
```

- Use `"Nunito", ui-rounded, "SF Pro Rounded", system-ui, sans-serif` for non-technical text.
- Use a system monospace stack for code and commands. Reserve JetBrains Mono for diagram SVGs.
- Set body text near 17px with a 1.7 line height. Use 400 for prose, 600 for emphasis, and 700 for headings.
- Keep heading line heights compact without crowding them.

## Composition

- Keep the main column around 780px and prose near 68 characters per line.
- Align headings and body content to the same content edge. Use a calm type scale and generous section spacing.
- Let content determine the layout. Use a compact grid only when short metadata or comparisons scan better side by side.
- Prefer whitespace and thin separators over containers. Add a boundary only when grouping would otherwise be unclear.
- Avoid gradients, shadows, badges, decorative cards, ornamental imagery, unnecessary navigation, and a table of contents unless the content requires one.
