# Fixed-page PDF mode

Read this only when the user explicitly wants deliberately composed fixed pages, a deck, page-perfect output, or equivalent.
A request to export ordinary HTML as PDF is not sufficient; keep that document flowing.

## Page contract

- Choose Letter by default or A4 when requested or appropriate for the audience, and state the choice.
- Represent every page as its own section with exact paper width and height, internal padding, hidden overflow, and a page break after it.
- Use the same geometry on screen and in print so the browser preview reveals clipping.
- Preserve that exact page geometry at narrow screen widths. Fit it by scaling the whole page inside a correspondingly sized wrapper.
- Do not reflow the page or change its width, height, padding, type sizes, or internal layout in a narrow-screen media query.
- Emit one matching `@page` size with zero outer margin; page sections own their padding.
- Keep headers and footers inside each page. Do not use fixed-position content.

## Compose to fit

- Give each page one job: title, summary, focused section, comparison, diagram, code excerpt, table, or appendix.
- Prefer another page over smaller type or dense content.
- Shorten or split large code blocks and tables; move supporting evidence to an appendix.

## Required verification

- Open the document in an available browser at print scale.
- For every page, compare `scrollHeight` with `clientHeight` and `scrollWidth` with `clientWidth`, allowing about two pixels for rounding.
- Any positive overflow beyond that tolerance must be fixed by splitting or simplifying the page.

- Inspect screenshots of the first page and every dense, diagram-heavy, code-heavy, or table-heavy page.
- Then inspect print preview and confirm the paper size, page count, breaks, colors, and absence of clipped content.
- Do not describe the result as page-perfect until these checks pass.
