# Pediatric Psychiatric Readmission Analytics

Static portfolio page for the pediatric psychiatric readmission analysis.
Aggregate data only — no row-level patient data, MRNs, or source CSVs are shipped.

## Local preview

From the repository root:

```bash
python3 -m http.server 8099
```

Then open <http://localhost:8099>.

## Deployment

GitHub Pages via `.github/workflows/pages.yml`. The workflow builds an
allowlisted `_site/` artifact (root `index.html`, `data.json`, `assets/**`,
`.nojekyll`) and publishes that — never the repo root, so patient CSVs and
analysis files are never exposed.

## Contents

- `index.html` — hand-authored, buildless portfolio page
- `data.json` — aggregate-only metrics (single source of truth)
- `assets/css/` — design-system CSS (tokens, base, layout, motion)
- `assets/js/` — ES modules (data loader, formatters, Chart.js charts, gallery, motion)
- `assets/figures/` — 12 selected PNG figures copied from `figures/`
- `tools/parity_diff.py` — baseline fidelity comparator
- `tools/verify_restraint.py` — restraint source-level reconciliation
