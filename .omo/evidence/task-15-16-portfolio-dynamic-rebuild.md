# T15 + T16 — Final parity verification + legacy retirement

## T15 — Cross-browser + final parity verification (GATE)

### Playwright render test (Chromium, 1280×900)
- **Console errors:** 0
- **Horizontal overflow:** none (scrollWidth === clientWidth)
- **Sections:** 8 (hero + 7 content sections)
- **Chart canvases:** 9 (5 demographic + 1 spectrum + 1 forest + 1 AUC + 1 subgroup explorer)
- **Gallery cards:** 12
- **Metric rows:** 8
- **Pipeline rows:** 5
- **Result chips:** 6
- **Abstract sections:** 3 (Objectives/Methods/Conclusions)
- **Nav display:** flex (scrollspy activated by motion.js)

### Parity gate
```
Parity check: 160 OK, 13 CHANGED (restraint-corrected), 0 MISSING
EXIT=0
```

All 160 non-restraint baseline statistics found in the rendered DOM.
All 13 restraint values corrected to T1 AUTHORITATIVE (N=510, rate=13.5%, OR=1.52[1.06-2.18] p=0.022).
0 unexplained MISSING.

### Scope fidelity
- `git diff --stat` confines changes to: index.html, .github/workflows/pages.yml, .gitignore, README.md
- Deleted: support.js, "Pediatric Readmission Portfolio.dc.html", portfolio/{app.js, styles.css, abstract.html, data.json, visualizations/*.html, assets/*.png, .nojekyll, README.md}
- New: data.json, assets/{css,js,figures}/, tools/{parity_diff.py, verify_restraint.py}, .omo/evidence/
- **No analysis artifact mutated:** zero .ipynb, .py, data/, or figures/ files changed
- `_site` payload contains no patient-level data (allowlist excludes data/** and figures/*.csv)

## T16 — Retire legacy + post-delete re-verify

### Deleted files
- `support.js` (55KB generated dc-runtime — no longer referenced)
- `Pediatric Readmission Portfolio.dc.html` (58KB generated HTML)
- `portfolio/app.js`, `portfolio/styles.css`, `portfolio/abstract.html`, `portfolio/data.json`
- `portfolio/visualizations/{dsm5_readmission_rates,forest_plot,index,model_performance,subgroup_heterogeneity}.html`
- `portfolio/assets/*.png` (12 duplicate figure copies — superseded by assets/figures/)
- `portfolio/.nojekyll`, `portfolio/.DS_Store`, `portfolio/README.md` (folded into root README.md)
- `portfolio/` directory removed entirely

### Post-delete verification
1. **No dangling references:** `grep -rE "support\.js|x-dc|\.dc\.html|portfolio/" _site/` → NO matches ✓
2. **Critical files present:** index.html, data.json, assets/css/tokens.css, assets/js/main.js, figures/, data/, assets/ — all OK ✓
3. **_site clean:** no .csv, .ipynb, .py, or data/ directory in _site ✓
4. **Post-delete parity:** 160 OK, 13 CHANGED, 0 MISSING, EXIT=0 ✓

### Root README.md updated
- Local preview: `python3 -m http.server 8099`
- Deployment: GitHub Pages via allowlisted _site/ artifact
- Contents listing updated to reflect new file structure
