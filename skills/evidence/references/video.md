# Recordings

- Prefer native screen recording of the visible app or desktop region, with the real pointer and any app switches.
- Drive app interactions with computer use. If app control is unavailable, report the blocker without handing the test to the user.
- Before the full take, record a short sample on a screen that changes no data, with pointer travel, a click, a scroll, and a result.
- If the sample shows jumps or holds the available tools cannot avoid, record anyway and note the limitation in the report.
- On the sample, check resolution and bitrate with `ffprobe` and view one frame at full size. Fix unreadable text before the full take.
- Prepare the steps and readable text sizes before recording. Use an unhurried pace, with time to read meaningful changes and results.
- Move the pointer along a visible path to each control, pause briefly, then click. Avoid sudden jumps and unnecessary movement.
- Keep the viewport size stable. Record the visible area and scroll naturally to other areas; do not use full-page captures.
- Show the before state, action, and actual result. Keep one case per clip and use normal playback speed.
- No overlays, captions, or added text are needed.
- Check that the clip decodes, then inspect frames around each action for pointer or scroll jumps, long idle holds, and readable text.
- Frame checks do not prove smooth motion. Say that motion was checked from frames, not playback.
- Inspect frames for secrets and unrelated personal data before delivery.
