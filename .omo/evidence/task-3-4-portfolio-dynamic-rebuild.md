# T3 + T4 — Page shell + design-system CSS

## T3 Deliverables
- `index.html` (root) — NEW hand-authored shell replacing the generated `support.js`/`<x-dc>` page
- `assets/js/main.js` — module entry point, imports all chart/gallery/motion modules, exposes `window.__reducedMotion`
- `assets/js/{data,format,charts-demographics,charts-spectrum,charts-models,charts-equity,gallery,motion}.js` — 8 empty ES module stubs

## T4 Deliverables
- `assets/css/tokens.css` — CSS custom properties (--bg:#0b0d13, --accent:#6fb2f0, --risk:#e8927c, --protect:#7cc0a6, --warn:#d8b06a, fonts, radius, max-width)
- `assets/css/base.css` — reset, body grain/glow backdrop, pulse keyframe, selection, typography scale, skip-link, mandatory `@media (prefers-reduced-motion: reduce)` global damp block
- `assets/css/layout.css` — container, section padding, sticky header (backdrop-blur), section-header pattern, panel/card, hero grid, readout panel, pipeline panel, findings legend, demo grid, models grid, clinical-read callout, gallery grid, abstract grid + result chips + objectives, footer, mobile breakpoint
- `assets/css/motion.css` — baseline `.reveal`/`.revealed` classes (visible if JS slow) + `@supports (animation-timeline: view())` scroll-driven entrance (reduced-motion gated)

## Acceptance criteria (all PASS)
1. `node --check` passes on all 9 `assets/js/*.js` files ✓
2. Structure: 1 `<main>`, 1 `<nav>`, 1 `<header>`, 1 `<footer>`, all 7 section ids (methods, findings, spectrum, models, equity, figures, abstract) ✓
3. CDN: `chart.js@4.4.7` present (1 match); `latest` absent (0); `d3@` absent (0); `support.js` absent (0); `x-dc` absent (0) ✓
4. CSS tokens: `--bg: #0b0d13`, `--accent: #6fb2f0`, `--risk: #e8927c`, `--protect: #7cc0a6`, `--warn: #d8b06a` all present ✓
5. `@media (prefers-reduced-motion: reduce)` block in base.css ✓
6. No inline `style="..."` on structural nodes (grep count = 0) ✓
7. `python3 -m http.server 8099` serves the page with all section ids present ✓

## Note
The old `support.js` (55KB generated dc-runtime) is still present but NO LONGER REFERENCED by the new `index.html`. It will be deleted in T16 (retire legacy) after T15 parity passes. The `.omo/evidence/baseline-index.html` backup is untouched.
