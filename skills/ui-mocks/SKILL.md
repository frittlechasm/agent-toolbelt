---
name: ui-mocks
description: Use to create standalone comparisons of static, fully styled UI mocks, screen designs, layout variants, or visual directions. Do not use for production implementation or application behavior.
metadata:
    scope: global
    agents: all
    machines: all
---

# UI Mocks

Create one self-contained `.html` file that makes UI directions easy to compare.

## Requirements

- Render the UI with HTML and CSS. Do not replace it with descriptions or annotated placeholders.
- Show every required element and state in every variant. Keep the content, data, viewport, and scope the same unless the user wants to compare them.
- Ask for missing essential content or constraints. Do not invent product details.

## Directions

- Follow the supplied design system, references, and design preferences. Otherwise, base the design on the product, its users, and their main task.
- Before coding, define each direction with a target feeling, layout idea, signature element, and restraint rule.
- Keep these notes private unless the user asks for them.
- Take ideas from the product's users, tools, language, and common actions. Do not start from generic trends.
- Give each direction one bold choice. Keep the rest calm and consistent.
- Use references as a quality bar and moodboard. Do not copy them.
- If the directions still feel alike and the user gave no visual direction, use a different random string as a private creative seed for each one.
- Do not show the strings or let randomness hurt usability.

## Variants

- Render three variants by default, or the count the user requests. Label them `A`, `B`, `C`, and so on.
- Change the layout, hierarchy, navigation, density, or controls between variants. Color, type, spacing, or decoration alone do not make a new direction.
- Keep each variant consistent across layout, type, color, surfaces, images, and controls.
- Do not imply a preferred option. Unless asked, show only the letter label and the mock.
- Stack variants vertically in alphabetical order by default. Use side-by-side or another arrangement only when the user requests it.
- Keep the comparison page neutral and give matching surfaces the same dimensions when practical.
- Preserve the target viewport. Put fixed desktop or mobile surfaces in their own horizontal scroller when needed.

## Build

- Keep HTML and CSS in the file. Add JavaScript only for a requested state, motion demo, or comparison control.
- When imagery, illustration, iconography, or texture is central to a direction, use supplied, generated, inline SVG, or embedded assets.
- Do not add images as filler.
- Keep controls presentational. Do not add application logic, persistence, routing, or data fetching.
- Use semantic HTML, accessible labels, and visible focus styles.
- Keep the page usable at about 320px wide without page-level horizontal scrolling for mobile devices.

## Motion

- Use motion only when it shows a state change, gives feedback, explains hierarchy, or carries the main design idea.
- Prefer short CSS transitions, keyframes, or inline SVG animation.
- Use canvas or WebGL only for a central visual that cannot be expressed well with CSS or SVG.
- Prefer motion triggered by hover, focus, or a state change. Avoid constant loops unless requested or central to the direction.
- Animate `transform` and `opacity` when practical. Avoid effects that continuously repaint large areas.
- Respect `prefers-reduced-motion`. The mock must still make sense when motion is off.
- Keep motion the same across variants unless it is part of the design direction or is being compared.
- Do not use generated video unless the user asks for it.

## Verify

- Render the file and inspect screenshots at narrow and desktop widths. Judge the result, not the code or effort.
- Check that every requirement appears in every variant and that the variants are truly different.
- Review composition and hierarchy first, then type, spacing, color, controls, and polish. Compare with supplied references without copying them.
- If independent review is allowed and available, use `visual-design-review` with fresh context.
- Give the reviewer only the screenshots, product goal, target users and task, constraints, desired feeling, and references. Do not include earlier implementation rationale.
- Make one or two improvement passes. Fix the largest gaps first.
- Remove anything that adds no information, hierarchy, identity, or required behavior.
- Remove generic hero layouts, arbitrary gradients or glows, excess containers, decorative labels, random accent colors, and repeated rounded cards unless the direction calls for them.
- Check labels, dimensions, clipping, overflow, semantics, focus styles, and reduced motion before delivery.
