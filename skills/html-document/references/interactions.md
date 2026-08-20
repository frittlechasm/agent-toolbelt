# Interactions

Use interactions only when the user requests them. Prefer native HTML and add only the JavaScript required.

## Tabs

- Use tabs only for long, mutually exclusive views that readers do not need to compare, search, or print together.
- Keep short alternatives, sequential steps, comparisons, and essential content visible.
- Implement semantic relationships, pointer and keyboard navigation, managed focus and selected state, and a fallback that keeps the content usable without JavaScript.

## Copy controls

- Add copy controls only when the user explicitly asks for a copy control or equivalent interaction.
- Omit them for logs, quotations, diffs, illustrative pseudocode, inline fragments, or content that is not useful to reuse.
- Copy only the raw payload, not labels, line numbers, shell prompts, or explanation.
- Give every control a unique accessible name that identifies its payload.
- Place visible and announced feedback next to the control. Report clipboard failure honestly.
- Initialize controls independently so one feature cannot disable another.
- Keep controls visually secondary and verify their exact payload with pointer and keyboard input.
