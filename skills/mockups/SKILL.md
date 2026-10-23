---
name: mockups
description: Create standalone comparisons of static UI design directions. Do not use for production implementation or application behavior.
metadata:
    scope: global
    agents: claude, codex
    machines: all
---

# UI Mocks

Create one self-contained `.html` file that makes UI directions easy to compare.

## Directions

- Render real UI in HTML and CSS, not descriptions or annotated placeholders.
- Show every required element and state in every variant, with the same content, data, viewport, and scope unless the user wants those compared.
- Ask for missing essential content or constraints; do not invent product details.
- Follow any supplied design system, references, and preferences. Otherwise start from the product, its users, their tools, and their main task, not trends.
- Before coding, privately define each direction's target feeling, layout idea, signature element, and restraint rule.
- Give each direction one bold choice and keep the rest calm. Use references as a quality bar, not something to copy.
- If directions still feel alike and the user gave no visual direction, use a different private random-string seed for each.

## Variants

- Make three by default, or the requested count, labelled `A`, `B`, `C`, and so on.
  Show only the label and the mock unless asked, and do not imply a favorite.
- Vary layout, hierarchy, navigation, density, or controls. Color, type, spacing, or decoration alone is not a new direction.
  Do not reuse one page shell or header layout across variants, or restyle the same markup with CSS.
- Keep each variant consistent within itself.
- Stack variants vertically in order unless the user asks for another arrangement. Keep the page neutral and matching surfaces the same size.
- Keep the target viewport; put fixed desktop or mobile surfaces in their own horizontal scroller if needed.

## Build

- Add JavaScript only for a requested state, motion demo, or comparison control. No app logic, persistence, routing, or data fetching.
- Use supplied, generated, inline SVG, or embedded images only when imagery is central to a direction. No filler images.
- Use semantic HTML, accessible labels, and a visible, theme-aligned `:focus-visible` style. Never hide focus.
- Keep the page usable at about 320px wide without page-level horizontal scrolling.
- When fixing a selected design, keep the chosen variant, visualization, and required elements unless asked to change them.

## Motion

- Use motion only for state changes, feedback, hierarchy, or the main design idea.
- Prefer short CSS transitions or inline SVG animation; use canvas or WebGL only for a central visual that CSS and SVG cannot handle.
- Prefer hover, focus, or state triggers over constant loops. Animate `transform` and `opacity`, and avoid large continuous repaints.
- Respect `prefers-reduced-motion`; the mock must still make sense without motion.
- Keep motion the same across variants unless it is what's being compared. Do not use generated video unless asked.

## Verify

- Render and screenshot at narrow and desktop widths. Confirm every requirement is in every variant and the variants differ in structure,
  not only in CSS applied to shared markup.
- Review the screenshots with the `critique` skill's criteria, then make one or two passes that fix the biggest gaps first.
- Remove anything that adds no information, hierarchy, identity, or required behavior, but keep elements the user selected or required.
- Remove generic defaults the direction does not need: stock hero layouts, arbitrary gradients or glows, random accent colors,
  extra containers, decorative labels, and repeated rounded cards.
- Check labels, sizes, clipping, overflow, semantics, focus styles, and reduced motion before delivery.
- Present the variants and wait for the user's pick before touching production code or assets, unless they asked you to choose and implement.
