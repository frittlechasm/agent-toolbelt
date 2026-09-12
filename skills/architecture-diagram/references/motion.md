# Animate architecture maps

Use this for requested animation or a guided walkthrough. The layout rules in `diagrams.md` still apply.

## Cover every flow

- Cover all flows and scenarios supported by the source, unless the user asks for a narrower scope. Include background work, failure paths, and return paths when supplied.
- List the scenarios and their connections before building playback. Let readers choose a scenario, and provide Play all with a clear reset and caption between scenarios.
- Follow each supported path from start to finish. Keep the full topology visible. Do not stop at one highlighted connection when the source describes a larger flow.
- Keep branches separate and preserve concurrent work. When execution order is unknown, present connections as a labelled tour rather than inventing a runtime sequence. Explain non-traffic dependencies with a highlight, not a travelling message.
- For code changes, cover the supplied Before and After flows. Label added, modified, and removed parts with text; keep these labels distinct from component-category colors. Play removed paths only in Before.

## Make playback clear

- Use a small dot along existing arrows and a short caption explaining what it represents. Keep components, labels, and arrowheads still and readable. A design relationship does not prove live traffic or measured timing.
- Start static. In HTML, offer Play, Pause/Resume, and Replay. Stop after one pass and show the full map.
- Keep motion, captions, and highlights driven by the same scenario data. Switching scenarios or replaying must cancel the old run, including any late completion events.
- Use native SVG animation, such as `<animateMotion>` with `<mpath>` pointing to the existing path. Hide the dot before and after playback. Keep styles, IDs, and scripts scoped to the diagram.
- Stop motion when `prefers-reduced-motion` is enabled or the page is hidden. Keep every scenario's explanation available without animation or JavaScript.
- For SVG shown as an image, check the host's animation support. Use separate labelled scenarios or a finite tour when interactive controls are unavailable.

## Check the result

- Play every scenario. Compare them with the source: every in-scope flow and connection must be covered by playback or an explained highlight. State any missing coverage and its reason.
- Check direction, captions, completion, pause/resume, replay, rapid clicks, and switching scenarios during playback.
- Check keyboard controls, reduced motion on load and during playback, and the static fallback. At desktop and phone widths, check readability and overflow during playback. Report checks you could not run.

Inspired by [PR Lens](https://github.com/coldteadotai/pr-lens/blob/main/packages/renderer/src/svg/pulse.ts). Use inline SVG; no PR Lens dependency is needed.
