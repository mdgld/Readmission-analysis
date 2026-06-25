# portfolio-dynamic-rebuild - Work Plan

## TL;DR (For humans)
<!-- Fill this LAST, after the detailed plan below is written, so it summarizes the REAL plan. -->
<!-- Plain English for a non-engineer: NO file paths, NO todo numbers, NO wave/agent/tool names. -->

**What you'll get:** Your portfolio page rebuilt as one polished, self-owned website with genuinely interactive charts (hover details, a one-click "honest vs optimistic" model toggle, a filterable diagnosis ranking, an explorable subgroup panel, a click-to-zoom figure gallery) and tasteful motion as you scroll — keeping the exact same dark look, words, and numbers it has today, and finally fixing the broken publishing setup so the live site actually shows this page.

**Why this approach:** Today's pretty page is machine-generated and can't be hand-edited, and the page that *is* published is missing its homepage — so the cleanest path is to author one clean page you fully control, with no build tools, that drops straight onto GitHub Pages.

**What it will NOT do:** It won't touch any of your analysis, notebooks, or data files; it won't put any patient-level data on the web; and it won't add any developer build step or framework.

**Effort:** Large (16 small, verifiable steps)
**Risk:** Medium — it's a full rewrite of the page, so the safeguards are an automatic "did every number survive?" check and a strict publish-only-safe-files rule (a reviewer caught that the old plan would have leaked the patient data file — now blocked).
**Decisions I made for you:** I treated this as open-ended and chose defaults — interactive charts via Chart.js (no heavy Plotly, no build step), a scroll/reveal motion layer that respects reduced-motion settings, and consolidating everything into the single root page. You explicitly added the restraint-data double-check, which is now a hard gate that recomputes from your source data and every figures file. If you had a specific look or feature in mind, say so and I'll fold it in.

Your next move: approve and say start work, or tell me to adjust scope. Full execution detail follows below.

---

> TL;DR (machine): Large/Medium-risk buildless rebuild → one root index.html (Chart.js interactive charts + motion), source-level restraint reconciliation hard gate, allowlisted `_site` deploy (no patient-data leak), 16 todos + parity-checked fidelity.

## Scope
### Must have
- ONE hand-authored, **buildless** site at repo-root `index.html` (+ modular `assets/css/`, `assets/js/`, root `data.json`) that fully replaces the generated `support.js`/`<x-dc>` runtime page. No npm, no bundler, no framework.
- 100% **content + numeric fidelity** with the current page: every section (hero, premise/pipeline, demographic findings, DSM-5 spectrum, predictors/models, equity, figures, abstract/results/objectives, footer), every label, footnote, OR/CI/p, and star-significance preserved — except where the restraint-reconciliation (T1) corrects a verified-wrong number.
- **Source-level restraint double-check** (explicit user requirement): recompute restraint N, readmission rate, and OR/CI/p directly from `data/annotated_psychiatric_data_complete.csv` AND cross-check every restraint figure in `figures/*.csv`, then converge the site to one authoritative set with an auditable report.
- Real **interactive charts**: Chart.js v4 (demographic bars, DSM-5 spectrum, model AUC, fairness) + D3 v7 (forest plot with CI whiskers on log scale; ROC/calibration). Hover tooltips, legend toggles, an apparent-vs-honest-AUC toggle, and a filterable diagnosis/subgroup explorer driven by `data.json`.
- **Motion layer** signalling front-end craft: IntersectionObserver scroll-reveal, animated stat counters, scrollspy nav, CSS scroll-driven animation (`@supports`-gated), View-Transitions progressive enhancement — all honoring `prefers-reduced-motion`.
- Responsive (mobile→desktop) and accessible (keyboard nav, `role="img"`+`aria-label` on every `<canvas>`, visible focus, WCAG-AA contrast on the dark theme).
- **Fixed deploy**: `.github/workflows/pages.yml` publishes the repo root so the live site is no longer headless; orphaned `portfolio/` app assets retired after parity is confirmed.
- Preserve the existing visual identity (Geist/Geist Mono, `--bg:#0b0d13`, accent `#6fb2f0`, risk/protect/warn palette) — enhance, do not redesign.

### Must NOT have (guardrails, anti-slop, scope boundaries)
- MUST NOT touch any **analysis** artifact: no edits to notebooks (`*.ipynb`), analysis scripts (`*.py` other than NEW files under `tools/`), or any source/derived CSV in `data/` or `figures/`. The restraint double-check and any new helper live under `tools/*.py` (allowed); the analysis pipeline is never modified.
- **MUST NOT publish the repo root wholesale.** The deploy artifact is an **allowlist** only: root `index.html`, root `data.json`, `assets/**` (css/js + the copied web figure PNGs), `.nojekyll`. It MUST NEVER include `data/**` (patient-level CSVs incl. `data/annotated_psychiatric_data_complete.csv`), `figures/*.csv`, `*.ipynb`, `*.py`, `*.chat`, `*.db`, `uv.lock`, or any source CSV. (Reviewers flagged `path: .` / `publish_dir: .` as a patient-data leak — it is forbidden.)
- MUST NOT expose patient-level data: only aggregate metrics + the 12 explicitly-copied published PNGs ship. No MRNs, no row-level data, no source CSV in the web payload.
- MUST NOT introduce a build step, package manager, transpiler, framework, or `node_modules`. CDN `<script>` tags only, version-pinned.
- MUST NOT keep a dependency on the un-editable `support.js` / `<x-dc>` dc-runtime, and MUST NOT leave two competing portfolios live (root vs `portfolio/`).
- MUST NOT invent or "smooth" any statistic; every number traces to `data.json` or the T1 reconciliation report. Unverified numbers are a blocker, not a guess.
- MUST NOT silently change a displayed statistic except restraint values that T1 proves wrong (and every such change is logged in the evidence report).
- MUST NOT add analytics/trackers/cookies or external calls beyond the pinned CDN libs + Google Fonts already in use.

## Verification strategy
> Zero human intervention - all verification is agent-executed.
- **Test decision: tests-after, harness-free.** No unit-test framework (static site). Verification = three agent-executable checks per todo:
  1. **Static/data checks** — `.venv/bin/python` for JSON validity + numeric assertions; `node --check` for JS syntax; `serena`/grep for content-parity assertions against the OLD inline data block (`index.html` lines 553–780, captured to evidence before any rewrite).
  2. **Live-load checks** — serve with `python3 -m http.server 8099` (repo root) and drive a headless browser via the **playwright** skill: assert zero console errors, presence of expected DOM nodes/text, chart canvases/SVG rendered (non-zero dimensions), and capture a screenshot.
  3. **Interaction checks** — playwright clicks/hovers (AUC toggle, subgroup filter, nav scrollspy, lightbox) assert the expected DOM/text change; reduced-motion path asserted by emulating `prefers-reduced-motion: reduce`.
- **Pre-work snapshot (gate for fidelity):** before T1/T10 touch anything, copy the current root `index.html` to `.omo/evidence/baseline-index.html` and extract the inline data block to `.omo/evidence/baseline-data.txt`. All parity diffs compare against these.
- Evidence: `.omo/evidence/task-<N>-portfolio-dynamic-rebuild.<ext>` (report/log/screenshot per todo).

## Execution strategy
### Parallel execution waves
> Target 5-8 todos per wave. Fewer than 3 (except the final) means you under-split.
- **Wave 0 — Reconcile & found (T0–T4):** baseline snapshot + reusable parity comparator (T0), restraint source double-check (T1), canonical `data.json` + web figure staging (T2), page shell (T3), design-system CSS (T4). T1 is the hard gate for any restraint number; T2 depends on T1.
- **Wave 1 — Data-driven charts (T5–T9):** data loader, Chart.js demographic charts, DSM-5 spectrum, forest + model-AUC toggle, fairness + subgroup explorer. All depend on T2/T3/T4.
- **Wave 2 — Content, figures, motion, a11y (T10–T13):** full narrative content port, figure gallery + lightbox, motion layer, responsive/accessibility pass.
- **Wave 3 — Deploy, verify, retire (T14–T16):** repoint Pages workflow to an allowlisted `_site/` artifact (T14, legacy left in place), cross-browser + final parity (T15), then retire legacy files + post-delete re-verify (T16). Destructive deletion happens ONLY after T15 parity passes.

### Dependency matrix
| Todo | Depends on | Blocks | Can parallelize with |
| --- | --- | --- | --- |
| T0 baseline + parity tool | — | T1,T10,T15 | T3, T4 |
| T1 restraint double-check | T0 | T2 | T3, T4 |
| T2 data.json + figure staging | T1 | T5,T6,T7,T8,T9,T11 | T3, T4 |
| T3 page shell + CDN | — | T5–T13 | T0,T1, T4 |
| T4 design-system CSS | — | T6–T13 | T0,T1, T3 |
| T5 data loader/format | T2, T3 | T6,T7,T8,T9 | — |
| T6 demographic charts | T5, T4 | T10 | T7, T8, T9 |
| T7 DSM-5 spectrum | T5, T4 | T10 | T6, T8, T9 |
| T8 forest + AUC toggle | T5, T4 | T10 | T6, T7, T9 |
| T9 fairness + explorer | T5, T4 | T10 | T6, T7, T8 |
| T10 content port + nav | T3,T4,T6,T7,T8,T9 | T12,T13 | T11 |
| T11 figure gallery+lightbox | T2, T3, T4 | T13 | T10 |
| T12 motion layer | T10 | T13 | T11 |
| T13 responsive + a11y | T10,T11,T12 | T14 | — |
| T14 deploy allowlisted artifact | T13 | T15 | — |
| T15 cross-browser + final parity | T14 | T16 | — |
| T16 retire legacy + post-delete re-verify | T15 | — | — |

### Inlined research facts (self-contained — executor needs NO external brief)
- **Chart.js v4** is the PRIMARY chart library for ALL charts incl. the forest plot (horizontal bars + a small custom error-bar/whisker draw plugin + `type:'logarithmic'` x-axis). CDN: `https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js` (UMD global `Chart`, ~70KB). Dark theme: set `Chart.defaults.color='#cbd5e1'`. Canvas a11y: every `<canvas>` gets `role="img"` + a summarizing `aria-label`. Reduced motion: set chart `options.animation=false`.
- **D3 v7 is OPTIONAL**, only if the forest CI whiskers cannot be expressed cleanly in Chart.js. If used, pin a version and import ONLY needed modules to limit payload; CDN `https://cdn.jsdelivr.net/npm/d3@7`. Default = NOT used (reviewer-recommended simplification: one library, smaller payload).
- **Plotly: forbidden** (≈3MB).
- **Motion support (2026, evergreen):** IntersectionObserver (universal since 2019), `requestAnimationFrame` counters (universal), scrollspy via IntersectionObserver `rootMargin` (universal) — NO fallback needed. CSS scroll-driven `animation-timeline: view()` — gate behind `@supports (animation-timeline: view())` (Firefox <133 lacks it). View Transitions same-document — gate behind `if (document.startViewTransition)` (Firefox <144 lacks it); instant DOM swap otherwise.
- **`prefers-reduced-motion: reduce` contract (mandatory):** global CSS damp block (`animation/transition-duration: .01ms !important`) PLUS a single JS `matchMedia('(prefers-reduced-motion: reduce)').matches` flag that, when true, sets final reveal/counter state instantly and disables Chart.js animation.
- **SRI:** jsDelivr dynamic min files discourage SRI; version-pin is the integrity guarantee. (Optional: cdnjs static file + `integrity` hash if SRI is wanted — not required.)
- **Repo path facts (verified):** canonical patient CSV is `data/annotated_psychiatric_data_complete.csv`; reconciliation prose is `docs/Reconciliation_2025_vs_2026.md`; the 12 web PNGs all exist under root `figures/`; 11 `figures/*.csv` contain restraint tokens (T1 globs them).

## Todos
> Implementation + Test = ONE todo. Never separate.
<!-- APPEND TASK BATCHES BELOW THIS LINE WITH edit/apply_patch - never rewrite the headers above. -->
- [ ] 0. Baseline fidelity snapshot + reusable parity comparator (pre-work gate)
  What to do: (a) Copy current root `index.html` → `.omo/evidence/baseline-index.html`. (b) Extract the inline data block (`index.html` lines 553–780) verbatim → `.omo/evidence/baseline-data.txt`. (c) Produce `.omo/evidence/baseline-numbers.md` listing EVERY displayed statistic grouped by section (metrics, each demographic panel's rates+OR/CI/p, all 17 dx-spectrum rates+stars, 6 forest OR/CI, 9 model AUC cells, 4 fairness gaps, abstract results) — one row each: `value | label | source-line`. (d) Write `tools/parity_diff.py` (a NEW read-only helper, allowed): given a rendered-DOM text dump and `baseline-numbers.md` + a restraint-whitelist file, it tokenizes numeric/percent/OR tokens and reports `MISSING`/`CHANGED`/`OK` per baseline statistic, exit non-zero on any unexplained `MISSING`/`CHANGED`. This is the single comparator T2/T10/T15 reuse. MUST NOT modify any repo file outside `.omo/evidence/` and the NEW `tools/parity_diff.py`.
  Parallelization: Wave 0 | Blocked by: none | Blocks: T1, T10, T15
  References: `index.html:553-780` (inline data), `index.html:73-549` (rendered sections), AGENTS.md "Domain facts" (restraint, 9.3% rate, gender-identity labelling).
  Acceptance criteria (agent-executable): `test -f .omo/evidence/baseline-index.html && test -f .omo/evidence/baseline-numbers.md && test -f tools/parity_diff.py`; `baseline-numbers.md` has ≥1 row for EACH of the 8 section groups above and a total row count ≥ 70 (the page renders ~80 distinct statistics); every row matches regex `.+\|.+\|.+` (value|label|source); `python3 tools/parity_diff.py --selftest` exits 0 (proves the comparator flags a known-missing token on a fixture, NON-destructively).
  QA scenarios: happy — `--selftest` on an internal fixture string (NOT the product) reports the planted missing token; failure — re-run is idempotent (overwrites, no dup rows). Evidence `.omo/evidence/task-0-portfolio-dynamic-rebuild.md`
  Commit: Y | chore(verify): baseline statistic oracle + reusable parity comparator

- [ ] 1. Restraint source-level double-check & reconciliation (USER-REQUIRED HARD GATE)
  What to do: Write a **read-only** Python script `tools/verify_restraint.py` (run with `.venv/bin/python`) that:
  (a) **Locates** the source CSV by glob (`data/**/annotated_psychiatric_data_complete.csv` then repo-root fallback); fail loud with the searched paths if absent.
  (b) **Recomputes from source = GROUND TRUTH:** `had_restraints = restraints > 0`, `readmitted = Readmissions > 0`; report restrained N, readmitted-N + 90-day rate for restrained vs not, and the **unadjusted** restraint→readmission OR via a 2×2 table — method stated explicitly: drop rows with NA in either field, Haldane–Anscombe +0.5 continuity correction only if any cell is 0, Wald 95% CI on log-OR, two-sided z p-value. Source recompute is authoritative EVEN IF no figure agrees (figures are reconciliation TARGETS, not validators).
  (c) **Discovers ALL reconciliation targets:** glob `figures/*.csv`, scan case-insensitively for any column/row matching `restrain|restraints|had_restraints|restrained`, and tabulate the restraint value found in EACH (the 11 known: `Mv_logit_readmission.csv`, `Recon_readmission_logit.csv`, `Recon_restraint_predictors.csv` [note: predicts WHO is restrained, NOT readmission — label it distinctly], `Sub_subgroup_outcomes.csv`, `Subgroup_AUC.csv`, `Mv_ols_los.csv`, `Recon_los_predictors.csv`, `Clinical_Risk_Score_Points.csv`, `Clinical_Tool_Weights.csv`, `HDBSCAN_cluster_profiles.csv`, `Z02_zprefix_joint_or.csv`/`Z03_*` — plus any others the glob finds). A listed file with no restraint row → emit a `not-present` row, do NOT crash.
  (d) Also tabulate the **adjusted** multivariable OR from `figures/Mv_logit_readmission.csv` (`had_restraints` row) and parse `docs/Reconciliation_2025_vs_2026.md` restraint prose.
  (e) Emit `.omo/evidence/task-1-restraint-reconciliation.md`: one table {source → N, rate, OR[CI] p, kind=unadjusted/adjusted/predicts-restraint}, the known divergences (N 312 vs 510; rate 13.1/13.5/19.2%; OR 1.52[1.06–2.18]p=.022 in Mv_logit vs 1.58[1.11–2.27]p=.012 displayed vs AGENTS.md "≈1.55, p≈.015"), and a row literally labelled **AUTHORITATIVE** with the selection rule: descriptive N & rate = source recompute; the OR the SITE displays = the **adjusted multivariable OR from `Mv_logit_readmission.csv`** (the model the abstract reports), reconciling the 1.52↔1.55↔1.58 gap in prose. Plus an explicit "values the site must change" list. Write a machine-readable `.omo/evidence/restraint-authoritative.json` for downstream consumption.
  MUST NOT edit any CSV/notebook/analysis `*.py`; only writes `tools/verify_restraint.py` + the two evidence files.
  Parallelization: Wave 0 | Blocked by: T0 | Blocks: T2
  References: AGENTS.md "restraints was tested…" + "had_restraints = restraints > 0" + "Readmissions within 90 days"; `figures/Mv_logit_readmission.csv` (`had_restraints` OR row); `figures/Recon_restraint_predictors.csv` (predicts restraint, NOT readmission — do not confuse); `figures/Sub_subgroup_outcomes.csv` (cols `subgroup,n,readmit_pct,...,restraint_OR,p_restraint`); `portfolio/data.json:13-14,370-377` (510/19.2%/13.5%); `index.html:615,636-638,680` (312/13.1%/OR1.58); `docs/Reconciliation_2025_vs_2026.md`.
  Acceptance criteria (agent-executable): `.venv/bin/python tools/verify_restraint.py` exits 0, writes both evidence files; report enumerates EVERY `figures/*.csv` the glob found containing a restraint token (count ≥ 11); `restraint-authoritative.json` has keys `n, rate, or, ci_lo, ci_hi, p, or_kind` populated; `git status --porcelain data/ figures/` is EMPTY (no source mutated); recompute is deterministic across two runs (same N/rate).
  QA scenarios: happy — report's AUTHORITATIVE N/rate equal the deterministic source recompute and the "must change" list names every displayed value that differs; failure — if the source CSV lacks `restraints`/`Readmissions`, script exits non-zero naming the missing column (never guesses). Evidence `.omo/evidence/task-1-restraint-reconciliation.md`
  Commit: Y | chore(verify): add read-only restraint reconciliation (source recompute + all figures/*.csv)

- [ ] 2. Canonical root `data.json` + allowlisted web figure staging (single source of truth)
  What to do: (a) Create root `data.json` superseding `portfolio/data.json`, carrying EVERY datum the page renders: summary metrics, pipeline steps, demographic groups (age 8-band, gender, insurance, C-SSRS, restraint) each with n/readmit/rate/OR/CI/p, DSM-5 spectrum (17 cats, rate + two-prop-z significance level), forest predictors (6, OR/lo/hi/p/kind), models (LR/RF/CatBoost apparent/corrected/oof + Δ), fairness (4 pairings), subgroups (12, AUCs), figures (12, id/title/tag/file), abstract/results/objectives text. Fold T1's `restraint-authoritative.json` values; add a top-level `"_provenance"` note. Numbers come from `baseline-numbers.md` + `portfolio/data.json` + T1 — NEVER invented. (b) **Stage web figures into the allowlist:** copy the 12 referenced PNGs from `figures/` → `assets/figures/` (web-only, keeps the deploy artifact clean of `figures/*.csv`); `data.json` figure `file` paths reference `assets/figures/<name>.png`. (c) Extend `tools/verify_restraint.py` (or add `tools/check_datajson.py`) with a `--check-datajson data.json` mode that asserts the restraint fields equal `restraint-authoritative.json`.
  Parallelization: Wave 0 | Blocked by: T1 | Blocks: T5,T6,T7,T8,T9,T11
  References: `portfolio/data.json` (full structure to extend), `index.html:566-777` (inline values incl. CI/p the json lacks), `.omo/evidence/restraint-authoritative.json`, the 12 PNGs verified present under `figures/`.
  Acceptance criteria: `.venv/bin/python -c "import json;d=json.load(open('data.json'));assert d['summary']['n']==2652"` exits 0; `.venv/bin/python tools/verify_restraint.py --check-datajson data.json` exits 0 (restraint fields == AUTHORITATIVE); all 12 `data.json` figure `file`s exist under `assets/figures/`; `python3 tools/parity_diff.py` (from T0) reports 0 unexplained discrepancies vs `baseline-numbers.md` with the restraint whitelist applied.
  QA scenarios: happy — JSON parses + both checks green; failure — a figure `file` missing under `assets/figures/` fails the assertion; a restraint field not matching AUTHORITATIVE fails `--check-datajson`. Evidence `.omo/evidence/task-2-portfolio-dynamic-rebuild.log`
  Commit: Y | feat(data): reconciled root data.json + staged web figures

- [ ] 3. Page shell + pinned CDN libs + asset structure
  What to do: Author new root `index.html` skeleton: semantic landmarks (`<header><nav>`, `<main>`, `<section id=…>` per current section, `<footer>`), `<head>` meta/SEO/Open-Graph + Google Fonts (Geist/Geist Mono, as today), version-pinned CDN `<script defer>` for Chart.js `4.4.7` (jsDelivr) and D3 `7` (jsDelivr), and `<script type="module" src="assets/js/main.js">`. Create `assets/css/` and `assets/js/` dirs with empty module stubs imported in dependency order. NO `support.js`, NO `<x-dc>`. Keep section `id`s (`methods,findings,spectrum,models,equity,figures,abstract`) for nav anchors.
  Parallelization: Wave 0 | Blocked by: none | Blocks: T5–T13
  References: `index.html:1-71` (head + sticky header/nav to reproduce), "### Inlined research facts" above (Chart.js `https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js`; D3 optional/off by default).
  Acceptance criteria: `node --check` passes on each `assets/js/*.js`; served page returns 200 and has exactly one `<main>`, one `<nav>`, and all 7 section ids (playwright DOM query); CDN script tags carry explicit version (grep asserts `@4.4.7` and `d3@7`, no `latest`).
  QA scenarios: happy — playwright load → 0 console errors, all section ids present; failure — a missing module path surfaces a 404 in console and fails the check. Evidence `.omo/evidence/task-3-portfolio-dynamic-rebuild.png`
  Commit: Y | feat(site): scaffold buildless index.html shell + asset modules

- [ ] 4. Design-system CSS (port + tokenize dark identity)
  What to do: Create `assets/css/tokens.css` (CSS custom props from current `:root`: `--bg:#0b0d13`, `--accent:#6fb2f0`, `--risk/--protect/--warn`, fonts, line/panel tokens) + `assets/css/base.css` (reset, body grain/gradient backdrop, typography scale, `::selection`, smooth-scroll) + `assets/css/layout.css` (container `max-width:1240px`, section padding `clamp()`, grid primitives, card/panel, sticky header w/ backdrop-blur). Include the canonical `@media (prefers-reduced-motion: reduce)` global damp block. Replace ALL inline styles from the old page with classes.
  Parallelization: Wave 0 | Blocked by: none | Blocks: T6–T13
  References: `index.html:14-38` (`:root` tokens, body::before/after backdrop, pulse keyframe), `index.html:57-71` (sticky header styles), `portfolio/styles.css` (existing class patterns to reuse/improve).
  Acceptance criteria: stylesheets referenced and load 200; computed `--bg` == `#0b0d13` and `--accent` == `#6fb2f0` (playwright `getComputedStyle`); reduced-motion media block present (grep); no remaining `style="..."` inline blocks on structural nodes in `index.html` (grep count == 0 except dynamic chart sizing).
  QA scenarios: happy — screenshot matches dark identity, header blurs on scroll; failure — emulate reduced-motion → no transitions fire (playwright asserts transition-duration ~0). Evidence `.omo/evidence/task-4-portfolio-dynamic-rebuild.png`
  Commit: Y | feat(site): design-system CSS (tokens/base/layout) porting dark identity

- [ ] 5. Data loader + format helpers
  What to do: `assets/js/data.js` — `async loadData()` fetches `data.json` (relative path, works at Pages sub-path), caches, throws a visible on-page banner on failure. `assets/js/format.js` — number/percent/CI formatters (`Intl.NumberFormat`), log-scale helper for OR axis, two-proportion-z significance→stars helper (port from `index.html:558-564,595-598`), color-by-direction (risk/protect/neutral vs 9.3% baseline). Pure functions, unit-checkable.
  Parallelization: Wave 1 | Blocked by: T2, T3 | Blocks: T6,T7,T8,T9
  References: `index.html:555-610` (fmt/logScale/pTwoSided/mkDemo logic to reproduce faithfully), `portfolio/app.js:1-33` (existing fmt/num/table patterns).
  Acceptance criteria: `node --check assets/js/*.js` passes; an inline throwaway smoke check `node --input-type=module -e "import {stars,logScale} from './assets/js/format.js'; if(stars(0.002)!=='**')process.exit(1); if(Math.abs(logScale(1)-50)>40)process.exit(1)"` exits 0 (asserts stars(p=.002)=='**' and logScale(1) lands mid-axis); `loadData()` resolves with `summary.n===2652` under the local server (playwright eval).
  QA scenarios: happy — console eval `await loadData()` returns object; failure — rename data.json → on-page error banner appears (playwright asserts visible `[data-error]`). Evidence `.omo/evidence/task-5-portfolio-dynamic-rebuild.log`
  Commit: Y | feat(site): data loader + statistical format helpers

- [ ] 6. Chart.js demographic small-multiples (interactive)
  What to do: `assets/js/charts-demographics.js` — render age-band, gender, insurance, C-SSRS, restraint readmission-rate bar charts via Chart.js, each: 9.3% cohort baseline reference line, risk/protect coloring, hover tooltip (n, readmit count, rate, OR/CI/p), significance stars, `aria-label` summarizing the series on each `<canvas>`. Restraint chart uses T2 AUTHORITATIVE numbers. Set `animation:false` when reduced-motion.
  Parallelization: Wave 1 | Blocked by: T5, T4 | Blocks: T10
  References: `index.html:143-272` (5 demographic panels + legend + OR/CI/p footers), `data.json` groups, "### Inlined research facts" above (Chart.js dark-theme `Chart.defaults.color`, canvas a11y pattern).
  Acceptance criteria: playwright — 5 canvases with non-zero size render; hovering a bar shows a tooltip containing `%` and `n=` (assert tooltip text); each canvas has non-empty `aria-label`; restraint bar value == T2 authoritative rate.
  QA scenarios: happy — tooltip + baseline line visible in screenshot; failure — reduced-motion emulation → chart `options.animation===false` (eval). Evidence `.omo/evidence/task-6-portfolio-dynamic-rebuild.png`
  Commit: Y | feat(charts): interactive demographic readmission charts

- [ ] 7. DSM-5 diagnostic spectrum (interactive ranked bars + filter)
  What to do: `assets/js/charts-spectrum.js` — horizontal ranked bar of all 17 DSM-5 categories by 90-day rate, significance shading (n.s.→sig gradient as today), cohort baseline marker, hover tooltip (n, readmit, rate, z-test p), and a control to sort by rate/n and toggle "significant only". 
  Parallelization: Wave 1 | Blocked by: T5, T4 | Blocks: T10
  References: `index.html:274-316` (spectrum panel, legend, two-prop z-test note), `index.html:641-674` (dxRaw values + significance levels), `data.json` diagnoses.
  Acceptance criteria: playwright — 17 rows render; toggling "significant only" reduces visible rows (assert count drops); sort control reorders DOM (assert first label changes); tooltip shows p-value.
  QA scenarios: happy — sorted + filtered states screenshot; failure — empty/garbage filter still leaves a valid chart (no console error). Evidence `.omo/evidence/task-7-portfolio-dynamic-rebuild.png`
  Commit: Y | feat(charts): interactive DSM-5 risk spectrum with filter/sort

- [ ] 8. Forest plot + model-AUC apparent/honest toggle
  What to do: `assets/js/charts-models.js` — (a) **Forest plot in Chart.js** (primary; D3 only if Chart.js cannot render CI whiskers cleanly — see Inlined research facts): 6 predictors, point OR + 95% CI whiskers via a small custom error-bar draw plugin on a `type:'logarithmic'` x-axis (ticks 0.6/1.0/1.5/2/3), OR=1 reference line, risk/protect/null coloring, `role="img"`+`aria-label` per chart; restraint OR uses T2 AUTHORITATIVE value. (b) Chart.js grouped AUC bars (apparent/corrected/oof) per model with an interactive toggle switching "Apparent" ↔ "Honest (out-of-fold)" + Δ-optimism callout. **The toggle is a NEW/additive interaction** (not in the baseline) — it must not be parity-checked against the old page; values themselves come from `data.json`.
  Parallelization: Wave 1 | Blocked by: T5, T4 | Blocks: T10
  References: `index.html:318-417` (forest + AUC panels, ticks, Δ legend), `index.html:677-712` (forest/model raw values + logScale), `data.json` models/odds_ratios, "### Inlined research facts" above (Chart.js primary; D3 optional).
  Acceptance criteria: playwright — forest renders 6 point marks + 6 CI whiskers (assert via chart instance data or SVG/canvas overlay node counts); OR=1 reference present; AUC toggle click swaps the rendered values so that each model's shown AUC equals its `data.json` apparent value in one state and its oof value in the other (assert apparent > oof for CatBoost by >0.2); forest restraint OR == `data.json`/AUTHORITATIVE.
  QA scenarios: happy — both toggle states screenshot; failure — toggle keyboard-operable (Enter/Space activates, playwright asserts state change). Evidence `.omo/evidence/task-8-portfolio-dynamic-rebuild.png`
  Commit: Y | feat(charts): forest plot (Chart.js) + apparent/honest AUC toggle

- [ ] 9. Fairness chart + filterable subgroup explorer
  What to do: `assets/js/charts-equity.js` — (a) equalized-odds gap bars for the 4 pairings (warn color, AUC-gap subtext). (b) A `data.json`-driven **subgroup explorer** (NEW/additive — has no baseline counterpart, so it is NOT parity-checked): dropdown/segmented control over the 12 subgroups rendering N, readmission rate, and the three model AUCs (CatBoost/RF/LR) as a small comparative chart + readout. The "With Restraints" subgroup's N/rate come from `data.json` (= T1 AUTHORITATIVE).
  Parallelization: Wave 1 | Blocked by: T5, T4 | Blocks: T10
  References: `index.html:427-460` (equity panel + metric note), `index.html:714-726` (fairRaw), `data.json` fairness + subgroups (12 entries).
  Acceptance criteria: playwright — 4 fairness bars render; selecting a different subgroup updates the readout text (assert the displayed N/rate for the selected subgroup equal that subgroup's values in `data.json` — no hard-coded literal); no console error on rapid switching.
  QA scenarios: happy — explorer state change screenshot; failure — selecting then reselecting the first subgroup restores its `data.json` values. Evidence `.omo/evidence/task-9-portfolio-dynamic-rebuild.png`
  Commit: Y | feat(charts): fairness gaps + interactive subgroup explorer

- [ ] 10. Content port — all narrative sections + nav (fidelity-locked)
  What to do: Populate every section's prose/labels/footnotes verbatim from baseline: hero headline + cohort readout metrics, premise + 5-step pipeline, findings legend + OR/CI/p footers, spectrum intro (incl. DMDD 14.2% note), models "CLINICAL READ" callout, equity narrative, abstract (Objectives/Methods/Conclusions) + Results chips + Learning objectives, footer. Wire sticky `<nav>` anchors. Insert chart containers from T6–T9 in their sections. Apply T1 restraint corrections wherever restraint appears in prose.
  Parallelization: Wave 2 | Blocked by: T3,T4,T6,T7,T8,T9 | Blocks: T12,T13
  References: `.omo/evidence/baseline-index.html`, `.omo/evidence/baseline-numbers.md`, `index.html:73-549` + `:744-764` (abstract/results/objectives text).
  Acceptance criteria: serve the page, dump rendered `innerText` to a file, then `python3 tools/parity_diff.py --dom <dump> --baseline .omo/evidence/baseline-numbers.md --restraint-whitelist .omo/evidence/restraint-authoritative.json` exits 0 — i.e. every NON-restraint baseline statistic appears in the rendered DOM, and restraint statistics equal T1 AUTHORITATIVE (not baseline). NEW/additive interactions (AUC toggle, subgroup explorer, motion) are out of parity scope by design. All 7 nav anchors scroll to their section (playwright).
  QA scenarios: happy — full-page screenshot top→bottom + green parity report; failure — run `parity_diff.py` against a TEMP COPY of the dump with one statistic deleted (in `/tmp`, never the product) to prove the comparator reports MISSING. Evidence `.omo/evidence/task-10-portfolio-dynamic-rebuild.md`
  Commit: Y | feat(site): port all narrative content with fidelity lock + restraint fixes

- [ ] 11. Figure gallery + accessible lightbox
  What to do: `assets/js/gallery.js` — render the 12-figure catalogue from `data.json` (id/title/tag), lazy-loaded thumbnails from `assets/figures/` (the web-staged copies from T2), click → accessible modal lightbox (focus-trap, Esc/overlay close, arrow-key prev/next, `alt` text). White backplate for the matplotlib PNGs (as today).
  Parallelization: Wave 2 | Blocked by: T2, T3, T4 | Blocks: T13
  References: `index.html:462-492` (figure index markup + tags), `portfolio/app.js:36-45` (renderGallery), `assets/figures/*.png` (the 12 files staged in T2).
  Acceptance criteria: playwright — 12 figure cards render; clicking one opens modal with matching `alt`; Esc closes and returns focus to the trigger; arrow key advances image.
  QA scenarios: happy — open/close lightbox screenshots; failure — focus is trapped (Tab cycles inside modal, playwright asserts activeElement stays within). Evidence `.omo/evidence/task-11-portfolio-dynamic-rebuild.png`
  Commit: Y | feat(site): figure gallery with accessible lightbox

- [ ] 12. Motion layer (reveal, counters, scrollspy, scroll-driven, view-transitions)
  What to do: `assets/js/motion.js` — IntersectionObserver scroll-reveal (`.reveal`→`.revealed`), animated stat counters (RAF, count-up on enter), scrollspy nav highlight (`rootMargin` sentinel). `assets/css/motion.css` — `@supports (animation-timeline: view())` scroll-driven entrance, hover/focus micro-interactions. Optional View-Transitions for in-page anchor navigation behind `document.startViewTransition` existence check. ALL gated by a single `prefersReducedMotion` check that, when true, sets final state instantly (no observers/animation) and Chart.js `animation:false`.
  Parallelization: Wave 2 | Blocked by: T10 | Blocks: T13
  References: "### Inlined research facts" above (IntersectionObserver, RAF counters, scrollspy, scroll-driven `@supports`, View Transitions gating, reduced-motion contract), `index.html:35` (existing pulse keyframe).
  Acceptance criteria: playwright (default motion) — scrolling adds `.revealed` to off-screen cards, the hero "Patients" counter counts up and ends exactly at `2,652` (assert final text), active nav link updates per section on scroll; playwright (emulate `prefers-reduced-motion:reduce`) — elements start `.revealed`, the 2,652 counter shows its final value immediately (no tween), and the JS reduced-motion branch is taken (assert an exposed `window.__reducedMotion===true` flag).
  QA scenarios: happy — scrollspy + reveal captured mid-scroll; failure — reduced-motion path asserted (no animation, content fully visible). Evidence `.omo/evidence/task-12-portfolio-dynamic-rebuild.png`
  Commit: Y | feat(site): motion layer with full prefers-reduced-motion contract

- [ ] 13. Responsive + accessibility pass
  What to do: Verify/zfix layouts at 360/768/1280px (charts reflow, nav collapses, no horizontal scroll). A11y: keyboard-operate every control (toggle/filter/explorer/lightbox/nav), visible focus rings, `role="img"`+`aria-label` on all canvases, SVG forest title/desc, AA contrast audit on dark theme, skip-to-content link.
  Parallelization: Wave 2 | Blocked by: T10,T11,T12 | Blocks: T14
  References: "### Inlined research facts" above (canvas a11y `role="img"`+`aria-label`, AA contrast), `index.html` clamp-based responsive patterns.
  Acceptance criteria: playwright at 360/768/1280px → no horizontal overflow (`document.documentElement.scrollWidth<=clientWidth`), screenshots captured; axe-core (injected via playwright `addScriptTag` from the cdnjs axe build) reports 0 serious/critical violations; every interactive control reachable by Tab + operable by Enter/Space.
  QA scenarios: happy — 3 responsive screenshots + axe JSON saved; failure — run axe against a TEMP COPY of the page with one `aria-label` stripped (in `/tmp`, never the product file) to prove axe flags it. Evidence `.omo/evidence/task-13-portfolio-dynamic-rebuild.json`
  Commit: Y | fix(site): responsive + accessibility hardening

- [ ] 14. Deploy an ALLOWLISTED static artifact (no root publish, no deletion yet)
  What to do: Rewrite `.github/workflows/pages.yml` to build a clean `_site/` staging dir and publish THAT — never the repo root. The workflow step copies ONLY the allowlist into `_site/`: root `index.html`, root `data.json`, `assets/**` (css/js + `assets/figures/*.png`), and a `.nojekyll`. Then publish `_site/` via `actions/upload-pages-artifact` (`path: _site`) + `actions/deploy-pages` (or peaceiris with `publish_dir: ./_site`). Legacy files are LEFT IN PLACE this todo (deletion is T16, after parity). MUST NOT set `path: .`/`publish_dir: .`; MUST NOT copy `data/**`, `figures/*.csv`, `*.ipynb`, `*.py`, `*.chat`, `*.db`, `uv.lock`, or any source CSV into `_site/`.
  Parallelization: Wave 3 | Blocked by: T13 | Blocks: T15
  References: `.github/workflows/pages.yml` (current peaceiris, `publish_dir: ./portfolio`), repo root `.nojekyll`, Scope "MUST NOT publish the repo root".
  Acceptance criteria: workflow YAML parses (`python3 -c "import yaml;yaml.safe_load(open('.github/workflows/pages.yml'))"`); the publish path is `_site` (grep asserts `path: _site` or `publish_dir: ./_site`, and NO `path: .`/`publish_dir: .`); a local dry-run of the copy step produces `_site/` that CONTAINS `index.html`,`data.json`,`assets/`,`.nojekyll` and contains ZERO of `data/`,`*.csv`,`*.ipynb`,`*.py` (assert via `find _site -name '*.csv' -o -name '*.ipynb' -o -name '*.py'` is empty and `data/` absent).
  QA scenarios: happy — `find _site` listing shows only allowlisted files (saved to evidence); failure — the dry-run copy is re-run after planting a stray `data/x.csv` reference and the allowlist still excludes it. Evidence `.omo/evidence/task-14-portfolio-dynamic-rebuild.log`
  Commit: Y | ci(pages): publish allowlisted _site artifact (exclude patient/source data)

- [ ] 15. Cross-browser, performance & final parity verification (gate before any deletion)
  What to do: Build `_site/` locally (run the T14 copy step), serve it, and run playwright across Chromium + WebKit + Firefox: 0 console errors, all charts render (non-zero size), all interactions work (AUC toggle, spectrum filter/sort, subgroup explorer, lightbox, scrollspy), reduced-motion honored. Payload budget: sum served asset bytes via the playwright network log and assert no single first-party asset >300KB and Plotly absent. Run the FINAL parity: `python3 tools/parity_diff.py` over the `_site` DOM dump — every baseline statistic present except restraint values, which equal AUTHORITATIVE. Produce `.omo/evidence/task-15-final-parity.md`. This is the GATE: T16 deletion may proceed only if this todo is fully green.
  Parallelization: Wave 3 | Blocked by: T14 | Blocks: T16
  References: `.omo/evidence/baseline-numbers.md`, `.omo/evidence/restraint-authoritative.json`, `tools/parity_diff.py`, "### Inlined research facts" (browser support matrix).
  Acceptance criteria: 3-engine playwright all green (0 console errors, charts non-zero size, each interaction asserted); `parity_diff.py` exits 0 (0 unexplained diffs); `_site` payload contains no `plotly` and no `support.js` (grep); restraint numbers in the `_site` DOM == AUTHORITATIVE everywhere they appear.
  QA scenarios: happy — per-engine screenshots + parity report saved; failure — any engine console error, any parity MISSING/CHANGED, or any >300KB first-party asset blocks the gate (and thus T16). Evidence `.omo/evidence/task-15-final-parity.md`
  Commit: Y | test(site): cross-browser + final parity verification (pre-deletion gate)

- [ ] 16. Retire legacy + post-delete re-verify (only after T15 is green)
  What to do: ONLY after T15 passes: delete the un-editable `support.js`, the generated `Pediatric Readmission Portfolio.dc.html`, and all legacy/orphaned web entry points — `portfolio/app.js`, `portfolio/styles.css`, `portfolio/abstract.html`, `portfolio/visualizations/*.html`, and stale `portfolio/data.json` (fold `portfolio/README.md` notes into root `README.md` + add "Local preview: `python3 -m http.server 8099`"). MUST NOT delete `figures/`, `data/`, `assets/`, the new root `index.html`/`data.json`, notebooks, or analysis scripts. Then re-run the T14 `_site` build + a quick single-engine playwright smoke + `parity_diff.py` to prove the live artifact is unaffected by the deletions and no shipped HTML references a removed file.
  Parallelization: Wave 3 | Blocked by: T15 | Blocks: none
  References: T14 (`_site` allowlist), T15 (parity gate), `portfolio/README.md`, repo root `.nojekyll`.
  Acceptance criteria: `git rm` removes the listed legacy files; `git grep -lE "support\.js|x-dc|\.dc\.html"` returns nothing in any shipped/staged HTML; post-delete `_site` build + `parity_diff.py` still exit 0; `figures/`, `data/`, root `index.html`/`data.json`, `assets/` all still present (asserted).
  QA scenarios: happy — post-delete parity report green + `git status` shows only legacy deletions; failure — a dangling reference to a removed file in any HTML fails the grep gate (revert the deletion). Evidence `.omo/evidence/task-16-portfolio-dynamic-rebuild.log`
  Commit: Y | chore(cleanup): retire dc-runtime + orphaned portfolio assets after parity

## Final verification wave
> Runs in parallel after ALL todos. ALL must APPROVE. Surface results and wait for the user's explicit okay before declaring complete.
- [ ] F1. Plan compliance audit — every todo's acceptance criteria met with evidence file present; dependency order honored; restraint HARD GATE (T1) produced an AUTHORITATIVE set and T2/T6/T8/T9/T10/T15 all consume it. Evidence: `.omo/evidence/F1-compliance.md`.
- [ ] F2. Code quality review — `node --check` clean on all `assets/js/*.js`; no inline structural styles; no `support.js`/`<x-dc>`/Plotly references; modular CSS/JS; CDN libs version-pinned; no dead `portfolio/` references. Evidence: `.omo/evidence/F2-quality.md`.
- [ ] F3. Live-site agent QA (agent-driven, zero human) — build `_site/`, serve it, drive playwright through the live artifact: every chart renders, every interaction (AUC toggle, spectrum filter/sort, subgroup explorer, lightbox, scrollspy) works, reduced-motion path verified, 3-engine pass. Evidence: `.omo/evidence/F3-agent-qa/` (screenshots + logs).
- [ ] F4. Scope fidelity — final `parity_diff.py` = 0 unexplained discrepancies vs `baseline-numbers.md`; ONLY restraint numbers changed and they equal T1 AUTHORITATIVE; NO analysis artifact mutated — `git diff --stat` confines changes to web files (`index.html`,`data.json`,`assets/**`), the Pages workflow, `README.md`, NEW `tools/*.py`, and `.omo/` (notebooks `*.ipynb`, analysis `*.py`, `data/**`, `figures/*.csv` untouched); the `_site` payload contains no patient-level data. Evidence: `.omo/evidence/F4-scope.md`.

## Commit strategy
- Conventional Commits; one commit per todo (per each todo's `Commit:` line), small and reviewable; restraint verification (T1) lands as its own `chore(verify)` commit so the reconciliation is auditable in history.
- Order follows the dependency matrix: T0 (verify+parity tool) → T1 (restraint) → T2 (data+figures) → shell/CSS → charts → content/figures/motion/a11y → T14 deploy artifact → T15 parity GATE → T16 legacy deletion.
- Deletions of legacy assets (`support.js`, `.dc.html`, orphaned `portfolio/` files) happen ONLY in the T16 `chore(cleanup)` commit, strictly AFTER the T15 parity gate is green, so a revert of T16 restores the prior live page cleanly. T14 (deploy) never deletes.
- No commit may include source CSVs, notebooks, patient-level data, or the `_site/` build output (gitignore `_site/`). Do not commit `.omo/evidence/` screenshots unless the user wants them tracked (default: keep local).
- Branch: work on `feat/dynamic-portfolio`; do not push/PR unless the user asks.

## Success criteria
- A single buildless root `index.html` is the live, deployed portfolio — the Pages workflow publishes an allowlisted `_site/` artifact (NOT the repo root), the old `portfolio/` is retired, and the generated `support.js`/`<x-dc>` dependency is gone.
- The page is demonstrably "more dynamic": real interactive Chart.js charts (tooltips, legend toggles, apparent/honest AUC toggle, DSM-5 filter/sort, subgroup explorer, figure lightbox) plus a scroll-reveal/counter/scrollspy motion layer — all honoring `prefers-reduced-motion`.
- **Restraint data is verified at the source**: `tools/verify_restraint.py` recomputes from `data/annotated_psychiatric_data_complete.csv` (ground truth) and cross-checks every restraint-bearing `figures/*.csv` (≥11, discovered by glob); the site displays one AUTHORITATIVE set, and `.omo/evidence/task-1-restraint-reconciliation.md` documents every prior divergence (N 312↔510, rate 13.1↔13.5↔19.2%, OR 1.52↔1.55↔1.58) and the correction.
- 100% content/numeric fidelity vs the old page except the T1 restraint corrections; the automated `parity_diff.py` reports 0 unexplained diffs. NEW interactions (AUC toggle, subgroup explorer, motion) are additive and exempt.
- Accessible (axe 0 serious/critical, keyboard-operable, canvas labelled) and responsive (no overflow at 360/768/1280px); 3-engine playwright green with 0 console errors.
- **No patient-level data ever shipped** (the `_site` allowlist excludes `data/**` and `figures/*.csv`); no analysis code/data touched (only NEW `tools/*.py`); no build step introduced.
