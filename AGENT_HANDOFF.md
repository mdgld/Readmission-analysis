# Agent Handoff — Readmission-analysis

**Last updated:** 2026-06-16 (Codex delegation — tasks 3, 4, 7)

This file documents the current state of all known bugs and pending tasks. Start here.

---

## What was completed in recent sessions

### Notebook splits (all files in main project directory `/Users/matthewgold/code/Readmission-analysis/`)

| Original | Split outputs |
|---|---|
| `Readmission_ML_and_Advanced.ipynb` (60 cells) | `ML_A_Models.ipynb` (31 cells), `ML_B_Clinical.ipynb` (29 cells), `ML_C_Supplements.ipynb` (19 cells) |
| `Readmission_2026_Extended_Analysis.ipynb` (50 cells) | `ExtA_Inferential.ipynb` (23 cells), `ExtB_Models.ipynb` (16 cells), `ExtC_Secondary.ipynb` (25 cells) |

### Bug fixes applied

| Bug | File | Fix |
|---|---|---|
| BUG 1 | `ML_B_Clinical.ipynb` | Inserted FAMD+UMAP+HDBSCAN recompute cell before cluster validation cell (`47c4ee41`) — fixes `cluster_labels` NameError |
| BUG 2 | `ML_B_Clinical.ipynb` | Fixed `above: Unknown = (x == 40)` → `above = (x == 40)` in cell `16dc75d8` — was a Python type annotation at module scope that caused NameError, rendering only the first plot line |
| BUG 3 | `ML_A_Models.ipynb` | UMAP overlay `Fig12c` now always generates 6 panels by padding with next-ranked features when top-3 lists overlap |
| BUG 4 | `ML_A_Models.ipynb` | FAMD loadings heatmap xlabel/title clarified: "header shows dominant-loading feature as orientation hint; values are Pearson r; no 1:1 mapping" |
| BUG 5 | `ML_B_Clinical.ipynb` | Age×complexity heatmap: `pd.cut(bins=5)` → `pd.qcut(q=5, duplicates='drop')` — equal-width bins left the highest complexity bin sparse |
| BUG 6 | `ML_A_Models.ipynb` | New markdown cell inserted before UMAP correlation table explaining that UMAP axis labels are Spearman ρ hints, not axis definitions |
| BUG 7 | `ML_A_Models.ipynb` | `has_medical_comorbidity` label shortened to `'Medical comorbidity (Feudtner CCC-aligned)'` |
| BUG 8 | `Readmission_PyHealth_Advanced.ipynb` | CCS 653 "Residual codes; unclassified" reclassification inserted after `code2ccs = {c: code_to_ccs(c) for c in all_codes}` — decomposes heterogeneous bucket into Neurocognitive, Sleep-Wake, Z-status |
| BUG 9 | `Readmission_PyHealth_Advanced.ipynb` | Forest plot `figsize` increased, `fontsize=9` on yticklabels, `plt.subplots_adjust(left=0.42)` — prevents label truncation |
| Task 1 | `Readmission_2026_Extended_Analysis.ipynb` + `ExtB_Models.ipynb` | Removed `n_dsm5_categories` from OLS LOS formula in cell `ext024` — it was the COUNT of the individual flags, causing near-perfect multicollinearity in inferential regression |
| Task 2 | `ML_A_Models.ipynb`, `ExtC_Secondary.ipynb` | Added 5-line documentary comment above FEATURES dict explaining why individual DSM-5 flags are kept for prediction (AUC) but not for inference (ORs) |
| Task 4 | `Readmission_2026_Extended_Analysis.ipynb` + all Ext splits | Added §0Z Z-code covariance analysis cells (`extZ01`/`extZ02`) with: `has_z_code` feature engineering, Spearman(ace_score, has_z_code) correlation, phi(has_z_code, has_trauma), top-Z-code frequency bar chart with ICD descriptions |
| BUG 10 | `Readmission_PyHealth_Advanced.ipynb` | **Option A applied**: deleted Part C code cells (C1–C4: bootstrap CIs, calibration, fairness, optimism-corrected validation); replaced with single markdown pointer at cell `0766811a` directing readers to `Readmission_ML_C_Supplements.ipynb` as the canonical source for all `figures/AdvStats_*` outputs. Notebook reduced from 19 → 12 cells. Portfolio/worktree copies still carry the old 19-cell version — see Task 7 drift report. |

---

## Remaining known issues

### Part 1 ICD prefix label issue
**Status:** Not yet fixed.
**Problem:** In `Readmission_Descriptive_and_Inferential.ipynb`, the §7C 3-character prefix sweep uses 3-char codes like "F32", "Z62" as axis labels without descriptions. The `ICD10_to_DSM5_Complete_Reference.csv` only has full codes (e.g., "F32.0"), not 3-char prefixes.
**Fix needed:** Join on `code[:3]` to get a representative description from the first matching full code, then label as e.g. `"F32 — Major depressive disorder"`.

### Logistic model formula in Extended Analysis (ext022) may need has_z_code
**Status:** Pending.
**Context:** Task 4 added `has_z_code` feature engineering (extZ02) to all Ext notebooks. But the multivariable logistic regression formula in `ext022` does not yet include `has_z_code`. To complete Task 4's original intent:
1. Add `has_z_code` to the `PRED` string in `ext022`
2. Verify OR and p-value for Z-codes in the adjusted model
3. Update ExtB (which has a copy of ext022) accordingly
**Note:** Run §0Z first (extZ02) since it defines `has_z_code`; it will be defined before ext022 runs in ExtB.

---

## File inventory after splits

```
Main project notebooks (each runs independently):
  Readmission_Descriptive_and_Inferential.ipynb   Part 1: descriptive + inferential
  Readmission_ML_A_Models.ipynb                   Part 2A: LR/RF/CatBoost, ROC, SHAP, FAMD/UMAP  (31 cells)
  Readmission_ML_B_Clinical.ipynb                 Part 2B: clinical tool, risk scoring, thresholds (29 cells)
  Readmission_ML_C_Supplements.ipynb              Part 2C: PyHealth CCS + bootstrap/calibration/fairness/optimism (19 cells)
  Readmission_2026_Extended_Analysis.ipynb        Extended: MASTER (50 cells — keep as reference)
  Readmission_2026_ExtA_Inferential.ipynb         Extended A: preamble + §1 bivariate + §2 subgroup (23 cells)
  Readmission_2026_ExtB_Models.ipynb              Extended B: preamble + §3 multivariable models (16 cells)
  Readmission_2026_ExtC_Secondary.ipynb           Extended C: preamble + §4 windows + §5 provider + §6 ML + §7 self-harm (25 cells)
  Readmission_PyHealth_Advanced.ipynb             PyHealth EHR coding + advanced stats (standalone) (19 cells)
  Readmission_Full_Analysis.ipynb                 SUPERSEDED backup — deletable after verification
  Readmission colab Analysis.ipynb                Colab variant (cloud-run path)
```

---

## Cell ID cross-reference for key cells

| Cell ID | Notebook | Purpose |
|---|---|---|
| `a30c3f0d` | ML_A cell 4 | FEATURES dict (ML prediction, intentionally richer than Part 1) |
| `cc1d8266` | ML_A/B/C preamble cell 8 | Model training — produces `lr_probs`, `rf_probs`, `cat_probs` |
| `16dc75d8` | ML_B cell 19 | Threshold/sensitivity plot — `above = (x == 40)` fixed |
| `7c82beed` | ML_B cell 10 | Age×complexity heatmap — `pd.qcut` fixed |
| `47c4ee41` | ML_B cell 25 | Cluster validation — depends on `cluster_labels` from inserted cell |
| `fa7d3e12b8c9` | ML_B cell 24 (inserted) | FAMD+UMAP+HDBSCAN recompute for ML_B independence |
| `ext024` | ExtA-master/ExtB cell 10 | OLS LOS model — multicollinearity fixed |
| `extZ02` | All Ext notebooks, cell 6 | Z-code feature engineering (`has_z_code`) |
| `286c15c1` | PyHealth cell 7 | B2 CCS mapping — `_reclass_residual` block added |
| `73d3e5a2` | PyHealth cell 9 | B4 forest plot — layout fixed |
