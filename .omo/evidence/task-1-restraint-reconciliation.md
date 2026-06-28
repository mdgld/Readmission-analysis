# T1 — Restraint source-level double-check & reconciliation

> USER-REQUIRED HARD GATE. Source recompute = GROUND TRUTH.

**Source CSV:** `data/annotated_psychiatric_data_complete.csv` (N=2,652)

**Rows skipped for NA Readmissions:** 0 (excluded from OR; empty `restraints` counted as not-restrained for descriptive N/rate)


## GROUND TRUTH (recomputed from source)

- Restrained N: **510** (19.2% of cohort)
- Not-restrained N: **2,142**
- Readmission rate (restrained): **13.5294%** (69/510)
- Readmission rate (not restrained): **8.2633%** (177/2,142)
- Cohort 90-day readmission rate: **9.276%** (246/2,652)

- Unadjusted OR (restraint→readmission): **1.737** [1.29–2.34] p=<0.001
  - Method: 2x2 unadjusted OR, Wald 95% CI on log(OR), two-sided z p; Haldane-Anscombe +0.5 iff any cell=0
  - 2×2: a(restrained&readmit)=69, b=441, c=177, d=1965
  - Continuity correction: 0.0

## AUTHORITATIVE (what the site must display)

| Metric | AUTHORITATIVE value | Source |
|---|---|---|
| Restrained N | 510 | source recompute |
| Restrained rate (of cohort) | 19.2% | source recompute |
| Readmission rate (restrained) | 13.5294% | source recompute |
| Adjusted OR (site forest + abstract) | 1.52 [1.06–2.18] p=0.022 | figures/Mv_logit_readmission.csv (`had_restraints`) |

**Selection rule:** Descriptive N & rate = source recompute. The OR the SITE displays (forest plot, abstract Results chip, findings group-stats) = the **adjusted multivariable OR from `figures/Mv_logit_readmission.csv`** (`had_restraints` row) — this is the model the abstract reports.

## Known divergences (baseline vs AUTHORITATIVE)

| Location | Baseline value | AUTHORITATIVE | Status |
|---|---|---|---|
| index.html:637 (inline) | N=312, rate=13.1% | N=510, rate=13.5294% | CORRECT (restrained readmit rate) but N is wrong → use 510 |
| index.html:615 (group OR) | 1.58 [1.10–2.26] p=.013 | 1.52 [1.06–2.18] p=0.022 | CHANGE to AUTHORITATIVE |
| index.html:680 (forest OR) | 1.58 [1.11–2.27] | 1.52 [1.06–2.18] | CHANGE to AUTHORITATIVE |
| index.html:753 (abstract OR) | 1.58, p=0.012 | 1.52, p=0.022 | CHANGE to AUTHORITATIVE |
| portfolio/data.json:13-14 | N=510, 19.2%/13.5% | N=510, 19.2% | N matches; reconcile the 13.5% vs 13.5294% |
| AGENTS.md | OR≈1.55, p≈.015 | 1.52, p=0.022 | AGENTS.md rounds; site uses exact Mv_logit value |

## Values the site MUST change

1. Findings → restraint group-stats OR: `1.58` → **1.52**
2. Findings → restraint group-stats CI: `1.10–2.26` → **1.06–2.18**
3. Findings → restraint group-stats p: `.013` → **0.022**
4. Forest plot → restraint OR/stat: `1.58 [1.11–2.27]` → **1.52 [1.06–2.18]**
5. Abstract Results → restraint: `OR 1.58, p = 0.012` → **OR 1.52, p = 0.022**
6. Findings → restraint N (if shown): `312` → **510**
7. Findings → restraint rate bar: `13.1%` → **13.5294%** (readmission rate among restrained)

**Note on N 312 vs 510:** The inline page's 312 is the source of the error. Source recompute gives 510 patients with ≥1 restraint (restraints > 0; empty = 0 = not restrained). The 13.1% inline is the readmission rate *among* the (wrongly-counted) 312; the correct readmission rate among the 510 restrained is 13.5294%. The 19.2% in data.json is the *prevalence* of restraint in the cohort (510/2,652), not the readmission rate — do not conflate.

## Reconciliation targets discovered (figures/*.csv)

**11** restraint-bearing files found (glob, case-insensitive `restrain`):

| File | Columns | Entries |
|---|---|---|
| `figures/Clinical_Risk_Score_Points.csv` | (row token) | 1 |
| `figures/Clinical_Tool_Weights.csv` | (row token) | 1 |
| `figures/HDBSCAN_cluster_profiles.csv` | Restraints (%) | 4 |
| `figures/Mv_logit_readmission.csv` | (row token) | 1 |
| `figures/Mv_ols_los.csv` | (row token) | 1 |
| `figures/Recon_los_predictors.csv` | (row token) | 1 |
| `figures/Recon_readmission_logit.csv` | (row token) | 1 |
| `figures/Sub_subgroup_outcomes.csv` | restraint_OR, p_restraint, p_restraint_fdr | 57 |
| `figures/Subgroup_AUC.csv` | (row token) | 2 |
| `figures/Z02_zprefix_joint_or.csv` | (row token) | 22 |
| `figures/Z03_zcode_within_prefix_drilldown.csv` | (row token) | 12 |

### Notable files

- `HDBSCAN_cluster_profiles.csv` — `Restraints (%)` per cluster profile.
- `Mv_logit_readmission.csv` — adjusted readmission model; `had_restraints` row = AUTHORITATIVE site OR.
- `Sub_subgroup_outcomes.csv` — per-subgroup `restraint_OR`/`p_restraint` (restraint as covariate within subgroup models).

## Reconciliation prose (docs/Reconciliation_2025_vs_2026.md)

Found 12 restraint-mentioning paragraph(s):

- OR mentioned: None, p mentioned: None
  > The 2025 submission reported three claims that do not all reproduce on careful re-analysis: a
readmission rate of approximately 10%, and a multivariable analysis that "found no independent
predictors ...
- OR mentioned: None, p mentioned: None
  > The most consequential discrepancy concerns the multivariable model, and it has now been resolved
directly by re-running the original on its own data (§8). The 2025 submission reported that ACE score,...
- OR mentioned: None, p mentioned: None
  > | Predictor | Adjusted OR | 95% CI | p |
|---|---|---|---|
| Suicidal ideation (ICD R45.851) | 2.59 | 1.82–3.66 | <0.001 |
| Depressive-disorder burden | 1.73 | 1.21–2.46 | 0.003 |
| Diagnostic comple...
- OR mentioned: None, p mentioned: None
  > Both the comparison and its cause are now established, because the original models were re-run on the
identical cohort (§8). The divergence is demonstrably one of **model specification**, and the spec...
- OR mentioned: None, p mentioned: None
  > ## 5. Restraint use and length of stay: a robust, separable finding...
- OR mentioned: None, p mentioned: None
  > Although restraint use is only a modest predictor of readmission, it is the dominant correlate of
index length of stay. In the multivariable linear model (`figures/Mv_ols_los.csv`) restraint use is
as...
- OR mentioned: 1.00, p mentioned: 1.0
  > The original *primary* multivariable model — the basis for "no independent predictors" — is
demonstrably degenerate. Re-fitting it reproduces a model that **fails to converge**, because one of
its ter...
- OR mentioned: None, p mentioned: None
  > | Specification (original data, N=2,652) | OR | p |
|---|---|---|
| Restraint as a **count** (as the abstract's model used it) | 1.00 | 0.90 |
| Restraint as a **binary** flag (any vs none), univariat...
- OR mentioned: 1.52, p mentioned: None
  > So restraint use and suicidal ideation are both associated with readmission in the original data; the
2025 abstract missed them because of three specification choices — coding restraint as a frequency...
- OR mentioned: 2.59, p mentioned: None
  > | Original 2025 statement | Re-analysis (2026) | Explanation and its standing |
|---|---|---|
| Readmission rate ≈ 10% | 9.3% per patient (246/2,652); 10.4% is the event count (275 events) | **Demonst...
- OR mentioned: None, p mentioned: None
  > Three practical recommendations follow from the sections above (the underlying detail is in §3 and §8
and is not repeated here). First, **report the rate as the patient-level 9.3%**, mentioning the
ev...
- OR mentioned: None, p mentioned: None
  > Precise operationalization matters here, because two of the central disagreements with 2025 turned on
*how* a construct was defined rather than on the data. The readmission outcome is patient-level: a...

## Adjusted OR detail

```json
{
  "source": "figures/Mv_logit_readmission.csv",
  "term": "had_restraints",
  "or": 1.5219410739888202,
  "ci_lo": 1.0618540280187603,
  "ci_hi": 2.1813776390866786,
  "p": 0.02221091936139883,
  "or_kind": "adjusted multivariable (readmission model)"
}
```