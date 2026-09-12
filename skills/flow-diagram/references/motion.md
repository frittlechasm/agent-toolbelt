# Animate process flows

Use this for requested animation or a guided walkthrough. The layout rules in `diagrams.md` still apply.

## Cover every scenario

- Cover all flows and scenarios supported by the source, unless the user asks for a narrower scope. Include each decision branch, failure, retry, rollback, and separate background flow that is in scope.
- List the scenarios before building playback. Each needs a starting condition, a path, and an outcome. Cover each distinct branch and outcome; do not enumerate every input combination or repeat a loop forever.
- Let readers choose a scenario. Provide Play all to run each one once, with a clear reset and caption between scenarios.
- Follow the selected scenario's actual path. Keep other paths visible. Do not play mutually exclusive branches as one run or show concurrent work as sequential.
- For code changes, label added, modified, and removed behavior using text as well as style. Cover the supplied Before and After flows; play removed paths only in Before. Do not invent behavior from changed filenames.

## Make playback clear

- Use a small dot following the existing arrows. Say what it represents and describe the active step in a short caption. Keep nodes, labels, and arrowheads still and readable.
- Start static. In HTML, offer Play, Pause/Resume, and Replay. Stop after one pass and show the full diagram. Playback speed does not represent measured timing.
- Keep motion, captions, and highlights driven by the same scenario steps. Switching scenarios or replaying must cancel the old run, including any late completion events.
- Use native SVG animation, such as `<animateMotion>` with `<mpath>` pointing to the existing path. Hide the dot before and after playback. Keep styles, IDs, and scripts scoped to the diagram.
- Stop motion when `prefers-reduced-motion` is enabled or the page is hidden. Keep every scenario's explanation available without animation or JavaScript.
- For SVG shown as an image, check the host's animation support. Use separate labelled scenarios or a finite tour when interactive controls are unavailable.

## Check the result

- Play every scenario. Compare them with the source: every in-scope branch and flow must be covered. State any missing coverage and its reason.
- Check path direction, captions, completion, pause/resume, replay, rapid clicks, and switching scenarios during playback.
- Check keyboard controls, reduced motion on load and during playback, and the static fallback. At desktop and phone widths, check readability and overflow during playback. Report checks you could not run.

Inspired by [PR Lens](https://github.com/coldteadotai/pr-lens/blob/main/packages/renderer/src/svg/dataflow.ts). Use inline SVG; no PR Lens dependency is needed.
