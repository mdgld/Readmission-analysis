# Data Portfolio Web UI

Static portfolio page for the pediatric psychiatric readmission analysis.

This folder is intentionally static: it uses the repository's completed notebook/script outputs in `../figures/` and exports only aggregate data plus selected PNG figures. It does not ship row-level patient data, MRNs, or source CSVs.

## Local preview

From the repository root:

```bash
python -m http.server 8000 -d portfolio
```

Then open:

```text
http://localhost:8000
```

## Free hosting recommendation

Best default: GitHub Pages.

Suggested setup:

1. Commit the `portfolio/` folder to a branch.
2. In GitHub repository settings, enable Pages.
3. Use either:
   - branch deploy from `/portfolio` if available in your Pages settings, or
   - GitHub Actions to publish `portfolio/` as the site artifact.

Netlify is also a strong free option: set the publish directory to `portfolio/` and no build command.

## Contents

- `index.html` — portfolio narrative and layout
- `styles.css` — responsive dark visual design
- `app.js` — renders aggregate charts/tables from `data.json`
- `data.json` — aggregate-only metrics derived from completed analysis outputs
- `assets/*.png` — selected generated figures copied from `../figures/`
