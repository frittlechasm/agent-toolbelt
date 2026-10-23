# Animate architecture maps

Use this for requested animation or a guided walkthrough. The rules in `diagrams.md` still apply.

## Cover every flow

- Cover every flow and scenario the source supports, including background work, failure, and return paths, unless the user narrows the scope.
- List the scenarios and their connections before building playback.
- Let readers pick a scenario, and offer Play all with a clear reset and caption between scenarios.
- Follow each path from start to finish with the full map visible. Do not stop at one highlighted connection when the source describes more.
- Keep branches separate and preserve concurrent work. When execution order is unknown, present a labelled tour, not an invented runtime sequence.
- Calls, publishes, and deliveries get a travelling dot even when they are design relationships, not observed traffic.
  Use a highlight instead only for dependencies that carry no messages, such as configuration.
- For code changes, cover the Before and After flows. Label added, modified, and removed parts with text, kept distinct from component-category colors.
  Play removed paths only in Before.

## Playback

- Move a small dot along existing arrows with a short caption. Keep components, labels, and arrowheads still.
  A design relationship does not prove live traffic or measured timing.
- Give captions a fixed height so the map does not shift between steps.
- Start static. In HTML, offer Play, Pause/Resume, and Replay; stop after one pass and show the full map.
- Drive motion, captions, and highlights from the same scenario data.
- Switching scenarios or replaying cancels the old run, including late completion events.
- Use native SVG animation, such as `<animateMotion>` with `<mpath>` pointing at the existing path. Hide the dot before and after playback.
- Keep styles, IDs, and scripts scoped to the diagram.
- Stop motion under `prefers-reduced-motion` or when the page is hidden. Every scenario's explanation must work without animation or JavaScript.
- For SVG shown as an image, check the host's animation support. Without interactive controls, use separate labelled scenarios or a finite tour.

## Check

- Play every scenario and confirm each source flow and connection is covered by playback or highlight. Report any gaps and why.
- Test direction, captions, completion, the Play all reset between scenarios, pause/resume, replay, rapid clicks, and switching mid-run.
- Test keyboard controls, reduced motion on load and during playback, and the static fallback.
- Check readability and overflow during playback at desktop and phone widths. Report checks you could not run.
