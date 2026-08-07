---
name: ui-mocks
description: Create standalone HTML comparisons of static, fully styled UI mocks. Use for UI mockups, screen designs, layout variants, or visual directions—not production implementation or application behavior.
---

# UI Mocks

Create one self-contained `.html` file that makes interface directions easy to compare and select.
Follow any supplied product design system. Otherwise create coherent, purposeful visual directions from the supplied requirements.

## Content

- Render actual UI with HTML and CSS. Do not substitute descriptions, feature lists, annotations, or prose summaries for the mocks.
- Preserve every supplied requirement, element, value, data row, state, and constraint in every variant.
- Keep content, data, state, target viewport, and functional scope constant across variants unless the user asks to compare one of them.
- If essential product content or constraints are missing and cannot be found in context, ask for them instead of inventing domain details.

## Variants

- Render three variants by default. Use the requested count when specified. When no count is specified, add more only when another distinct direction is necessary to represent the design space.
- Label variants `A`, `B`, `C`, and so on with visible semantic headings.
- Make variants meaningfully different in layout, information hierarchy, navigation, density, or interaction presentation.
- Do not treat changes limited to color, typography, spacing, or decoration as separate directions.
- Do not imply a preferred variant.
- Omit direction names, rationale, captions, and design commentary unless requested. Show only the letter label and the rendered mock.

## Comparison

- Stack variants vertically in alphabetical order by default. Use side-by-side or another arrangement only when the user requests it.
- Keep the comparison wrapper neutral and visually subordinate to the mocks.
- Give equivalent mock surfaces consistent dimensions when practical.
- Preserve a requested target viewport. Keep a fixed desktop or mobile surface intact inside an overflow container when necessary.

## Output

- Keep HTML and CSS in the file. Include only JavaScript needed to depict an explicitly requested static state or comparison control.
- Add no frameworks, web fonts, CDN assets, external images, or other runtime dependencies unless requested.
- Treat controls as static presentation. Do not add application logic, persistence, routing, or data fetching.
- Use semantic structure and accessible labels. Keep visible focus styles for any requested interactive comparison control.
- Keep the containing page usable to about 320px without page-level horizontal scrolling. Give only fixed target mock surfaces their own horizontal scroller.

## Verify

- Render the result in an available browser and inspect it at narrow and desktop widths.
- Confirm every required element and state appears in every variant.
- Compare variants for genuine structural or visual distinction; remove cosmetic duplicates.
- Check alphabetical labels, equivalent dimensions, clipping, mock overflow, page overflow, hierarchy, semantics, and visible focus.
- Fix issues before delivery.
