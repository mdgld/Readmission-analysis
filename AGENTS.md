# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## What this repo is

A clinical-statistics analysis (not an application) of a single-site Arizona dataset of
pediatric psychiatric rehospitalization — children aged 5–12, admissions 2017–2024,
N=2,652. The end product is a conference abstract (`AACAP_2026_Abstract.md`) plus
supporting figures and reconciliation tables. There is no app to build, no test suite,
and no lint step; "running the code" means executing analysis scripts/notebooks that read
CSVs and write figures + summary tables.

## Environment & how to run

- **uv-managed, Python 3.12.** Dependencies live in `pyproject.toml` + `uv.lock`.
  Rebuild the venv with `uv sync`; never hand-patch a broken `.venv` — regenerate it.
- **Run any script with the project interpreter:** `.venv/bin/python <script>.py`
  (e.g. `.venv/bin/python analysis_2026_subgroup_and_figures.py`). Scripts assume the
  CWD is the repo root — they read CSVs by relative path and write into `./figures/`.
- **`openpyxl` is used ad hoc** (to re-verify rates from the source `.xlsx`) but is **not**
  in `pyproject.toml`. A clean `uv sync` drops it; reinstall with `uv add openpyxl` if the
  xlsx rate-check must stay reproducible.
- `main.py` is a leftover uv scaffold stub (`Hello from jupyter-projects!`) — ignore it.

## Data lineage (read before touching any analysis)

```
With Ages GD1854RVSD_...csv        raw export (messy multi-row header — not analysis-ready)
        │  (ICD-10 → name + DSM-5 TR mapping, done in earlier sessions)
        ▼
annotated_psychiatric_data_complete.csv   ← CANONICAL patient-level input (2,652 rows)
diagnoses_long_form_complete.csv          ← long form, one row per diagnosis (27,884 rows)
ICD10_to_DSM5_Complete_Reference.csv      ← code → description/category lookup (1,863 codes)
        │  (notebooks + scripts)
        ▼
figures/*.png  +  figures/*.csv           ← all generated outputs
```

### Two coexisting schemas — pick the right file
There are **older** and **newer** generations of the annotated data with **different column
names**. All current code uses the newer `_complete` files. Do not mix them:

| Use this (canonical)                          | Not the older sibling          |
|-----------------------------------------------|--------------------------------|
| `annotated_psychiatric_data_complete.csv`     | `annotated_psychiatric_data.csv` |
| cols: `VisitDiags_DSM5Categories`, …          | cols: `VisitDiags_DSM5`, `..._DSM5_Count` |
| `diagnoses_long_form_complete.csv`            | `diagnoses_long_form.csv`      |
| `ICD10_to_DSM5_Complete_Reference.csv`        | `ICD10_to_DSM5_Reference.csv`  |

Reading the wrong file fails *quietly*: the diagnosis-category flags (`dep`, `adhd`, etc.)
all come back zero because the expected column doesn't exist.

## Analysis code map

The original monolithic `Readmission_Full_Analysis.ipynb` was split (2026) into two coherent
notebooks; the three current notebooks each re-run the shared imports + feature-engineering
preamble, so **each runs independently** (no serialized handoff):

- `Readmission_Descriptive_and_Inferential.ipynb` — **Part 1**: feature engineering, the
  date-quality filter, Table 1, descriptive figures (`Fig1`–`Fig6`), and the multivariable
  logistic regression + forest plot (`Fig7`).
- `Readmission_ML_and_Advanced.ipynb` — **Part 2**: LR/RF/CatBoost, SHAP, FAMD/UMAP, HDBSCAN,
  calibration, decision curves, bootstrap AUC, fairness, optimism correction, the clinical
  risk-score tool, and the PyHealth CCS coding supplement (produces `figures/AdvStats_*`,
  `figures/PyHealth_*`). Its preamble re-runs cells {imports, features, modeling-matrix,
  logit, forest} + restores `complexity_q`; the CCS supplement reclassifies the organic codes
  that PyHealth routes to CCS 653 "Residual codes; unclassified" → "Neurocognitive Disorders".
- `Readmission_2026_Extended_Analysis.ipynb` — **2026 extended battery**: bivariate inferential
  tests, diagnosis-subgroup descriptives, multivariable logistic/OLS, the preliminary-subset
  readmission-window + readmission-LOS + provider analyses, and ML augmentation. Outputs use
  `figures/Biv_* Sub_* Mv_* Win_* Prov_* MLx_*` prefixes.
- `Readmission_Full_Analysis.ipynb` / `.py` — **superseded backup** of the pre-split monolith;
  kept until the split is confirmed, then deletable.
- `Readmission_PyHealth_Advanced.ipynb` — PyHealth/CCSR comorbidity work (`figures/PyHealth_*`).
- `Readmission colab Analysis.ipynb` — Colab variant (large; cloud-run path).
- `analysis_2026_reconciliation.py`, `analysis_2026_subgroup_and_figures.py` — standalone 2026
  reconciliation + subgroup scripts (`Fig_Recon_*`).
- `Reconciliation_2025_vs_2026.md`, `Analysis_Comparison_2025_vs_2026.md` — mentor/AACAP-facing
  prose reconciliations of the 2025 vs 2026 findings.

### Execution-order dependency
`analysis_2026_subgroup_and_figures.py` reads `figures/AdvStats_optimism_validation.csv`,
generated by `Readmission_ML_and_Advanced.ipynb` (Part 2). **Run Part 2 first**, or that
script fails on a missing file. (Headless execution: `.venv/bin/python -m nbclient` style via
`nbclient`/`nbformat` — installed locally, not in `pyproject.toml`.)

## Domain facts the analysis depends on (don't silently "fix" these)

- **Per-patient readmission rate = 9.3% (246/2,652), measured within 90 days of discharge.**
  `Readmissions` is the count of readmissions **within 90 days of discharge** (verified: `Readmissions>0`
  is 97% concordant with the XLSX `Readmit 90 days` flag on the 1,206 overlapping patients; it is NOT
  any-time — patients readmitted after 90 days are excluded). value_counts 0→2406, 1→219, 2→25, 3→2;
  `readmitted` = `Readmissions > 0`. The **10.4%** figure is the **event count** (275 = 219×1+25×2+2×3 ÷
  2,652), double-counting the 27 children readmitted >1× within 90 days. The finer window ladder
  (7/30/180/365-day) is only computable on the **preliminary XLSX subset** (N=1,920; 1,206 link to the
  full cohort).
- **`restraints` was tested in the 2025 model, not omitted** — the 2025 submission reported it
  among the variables with no independent effect. On the complete-cohort, category-level
  re-analysis it **is** an independent predictor (OR ≈1.55, p≈0.015) and the largest driver of
  length of stay (~+6 days). The shift is a diagnostic-resolution/power effect (code-level
  collinearity suppressed it), not a corrected omission. It is a binary signal
  (`had_restraints = restraints > 0`), not dose-dependent. See `Reconciliation_2025_vs_2026.md`.
- **Honest predictive ceiling:** best out-of-fold AUC ≈ 0.68. High tree AUCs (CatBoost
  0.85–0.90) are optimism artifacts (drop to ~0.64 out-of-fold). Don't quote apparent
  in-sample AUCs as performance.
- **`AHCCCS` in `Insurance`** denotes public insurance; **C-SSRS flag columns** are coded
  by presence/non-null, not value.
- **`GenderCode` is gender identity recorded at admission, NOT biological sex** — label the
  `gender_male` feature "male gender identity," never "male sex."
- **The `has_*` diagnosis flags (`has_depression`, `has_adhd`, …) are string matches on DSM-5
  *category* labels** (from the `*_DSM5Categories` columns), not ICD codes and not PyHealth CCSR.
  `n_dsm5_categories` counts distinct DSM-5 *categories* (≠ `n_distinct_diagnoses`, the count of
  distinct ICD codes). **`has_medical_comorbidity`** uses a Feudtner Pediatric CCC-aligned chapter
  allowlist (Feudtner et al. 2014, BMC Pediatrics): scans `ChronicDiags` for codes whose first letter
  is in `{C,D,E,G,H,I,J,K,L,M,N,Q}` — neoplasm, blood, metabolic/endocrine, neurological, eye/ear,
  cardiovascular, respiratory, digestive, skin, musculoskeletal, renal, congenital. Excludes F
  (psychiatric), Z (social/admin/ACE codes), R (symptoms/signs), A/B (infectious), P (perinatal),
  S/T/V-Y (injury/external cause). Prevalence ≈42%. OR ≈0.91 (p=0.51, **not significant**) in the
  adjusted Extended Analysis readmission model — omitted from abstract Results. Dominant codes are
  functional/developmental conditions (obesity E66, sleep disorders G47, constipation K59, enuresis
  N39.4, asthma J45). Not a CCS category. **Suicidality** has two
  measures: `csrss_*` flags (a screen) and `has_suicidal_ideation` (ICD R45.851) — they diverge.
- DSM-5 categories only exist for psychiatric (F-)codes; medical comorbidities carry ICD
  chapter only — this is intentional, not missing data.

## Conventions

- Raw data is treated as read-only: clean/transform in memory or write to **new** output
  files; never overwrite the source CSVs.
- Figures are written at publication DPI into `./figures/`; the directory is created with
  `os.makedirs('figures', exist_ok=True)` so it's safe to delete and regenerate.
- `.Codex/`, `.venv/`, `*.db`, `catboost_info/`, and `.DS_Store` are gitignored.
