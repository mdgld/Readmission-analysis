# Reconciling the 2025 and 2026 Analyses
### Psychiatric Rehospitalization in Children Aged 5–12 (single Arizona site; admissions 2017–2024; 90-day readmission window)

*Prepared for Dr. Ritfeld and AACAP poster development. All 2026 statistics below were re-derived from `annotated_psychiatric_data_complete.csv` (N=2,652; 246 readmissions, 9.3%). The published 2025 study is treated as the reference standard.*

---

## 1. The two studies at a glance

| | **2025 (published, JAACAP)** | **2026 (this re-analysis)** |
|---|---|---|
| Cohort | 2,652 children, ages 5–12, 2017–2024 | **Identical cohort** |
| Outcome | 90-day rehospitalization (reported 10.4%) | Same 90-day variable, correct patient-level rate **9.3%**¹ |
| Diagnosis unit | **Individual ICD-10 codes** | **Aggregated DSM-5 / CCSR categories** |
| Models | Multivariable logistic regression (unpenalized) | (a) Unpenalized logistic regression — *inference*; (b) L2-regularized logistic regression, random forest, gradient boosting (CatBoost) — *prediction* |
| Validation | In-sample p-values | 10-fold CV, bootstrap optimism correction, calibration, fairness panels |
| Headline | *No* independent multivariate predictors except irritability/anger | Several independent predictors emerge (suicidal ideation, depressive burden, complexity, restraint, younger age; NSSI protective); divergence verified as a model-specification difference on the identical cohort (§8 of reconciliation); discrimination remains modest |

¹ **Rate discrepancy resolved (source-verified).** The original export (`1854_…xlsx`, *Summary* sheet) states the 90-day rate as **247/2,652 = 9.3%** (7-day 1.5%; 30-day 4.8%). The previously reported **10.4%** equals **275 readmission *events*** (219 patients ×1 + 25 ×2 + 2 ×3) ÷ 2,652 — it counted events, double-counting the 27 children readmitted more than once. The correct **patient-level** 90-day rate is **9.3%** (current analysis: 246/2,652). This is a numerator-definition correction, not a cohort difference.

---

## 2. Why the "top predictors" differ — and why it is **not** a contradiction

**Important context (read first).** The original 2025 modeling notebook and its source data were recovered; the source file is the **identical 2,652-patient cohort** used here, so the original models were re-run directly. The divergence in predictors is therefore **verified as a model-specification difference on identical data** — not a difference of cohort, outcome, or sample. See `Reconciliation_2025_vs_2026.md` §8 for the reproduced numbers.

The re-derived multivariable logistic regression (full cohort, unpenalized — the same inferential method as 2025) identifies the following, with **suicidality measured by ICD code (R45.851), as the original did** — not by the C-SSRS flags, which are a different construct and are non-predictive:

| Predictor (2026 multivariable logit, full cohort, N=2,652) | OR | 95% CI | p |
|---|---|---|---|
| Suicidal ideation (ICD R45.851) | 2.59 | 1.82–3.66 | <0.001 |
| Depressive-disorder burden | 1.73 | 1.21–2.46 | 0.003 |
| Diagnostic complexity (per added DSM-5 category) | 1.34 | 1.19–1.51 | <0.001 |
| Physical restraint use | 1.52 | 1.06–2.17 | 0.023 |
| Younger age (per additional year) | 0.91 | 0.84–0.99 | 0.023 |
| Non-suicidal self-injury (NSSI) | 0.40 | 0.27–0.59 | <0.001 (protective) |
| ACE score, **C-SSRS flags**, gender (identity at admission), insurance, LOS | n.s. | — | >0.05 |

Three design differences are sometimes invoked to explain why these effects reach significance now. Their explanatory power is limited, and that is stated honestly rather than glossed:

**(a) Unit of analysis — codes vs categories — is insufficient as a general explanation.** Aggregating diagnoses can stabilize the *diagnosis* terms, but it cannot act on the **non-diagnostic** predictors (restraint use, the diagnostic-complexity count, and age), which are null in 2025 yet significant here; and suicidality is predictive under the original's *own* ICD-code measure. The cause is now established directly (§8 of `Reconciliation_2025_vs_2026.md`): re-running the original on its own data shows a **model-specification** difference. Outcome definition and sample size are **excluded** — both analyses use the identical 2,652-patient cohort and the identical outcome (readmission within 90 days of discharge, `Readmissions>0`, verified 97% concordant with the Excel 90-day flag).

**(b) Prediction vs inference.** The same logistic model can be *read for coefficients* (inference) or *cross-validated for AUC* (prediction). The predictive arm additionally used **L2-regularized** LR and tree ensembles. Regularization shrinks coefficients to reduce variance → better generalization, but biases estimates and invalidates naive p-values. Hence: regularized models for prediction; the unpenalized model for the apples-to-apples comparison with 2025.

**(c) Nonlinearity / interactions.** Trees and explicit interaction terms (e.g., complexity×age, ACE×C-SSRS, medical×LOS) capture structure invisible to a main-effects logit.

**The irritability ↔ depression bridge.** 2025's lone signal, *irritability/anger*, is in DSM-5 the core of **Disruptive Mood Dysregulation Disorder (DMDD)**, which this mapping files under **Depressive Disorders** — among 2026's leading predictors. The studies detect the **same clinical signal** at different resolutions.

---

## 3. Information lost when collapsing categories (your intuition, quantified)

| Level | n | Readmission % | Univariate OR (p) |
|---|---|---|---|
| Irritability/anger code **R45.4** | 31 | **19.4%** | 2.38 (0.059) |
| DMDD code **F34.81** | 438 | **14.2%** | 1.82 (<0.001) |
| Collapsed **Depressive Disorders** category | 1,779 | 10.7% | 1.79 (<0.001) |

Within the depressive-disorders category, **DMDD-positive children readmit at 14.2% vs 9.6%** for non-DMDD depression. Collapsing both surfaces a category effect *and* dilutes the high-risk irritable-mood subgroup.

---

## 3b. Within-category subgroup analysis (which codes carry the signal)

Breaking the regex/CCS categories into their constituent ICD codes (univariate readmission rate and OR; cohort baseline 9.3%) shows that **diagnostic categories average over clinically opposite subgroups** — the central methodological message of the re-analysis (`Fig_Recon_4_subgroup_codes.png`; table `Recon_subgroup_codes.csv`).

| Category | Subgroup (code) | n | Readmit % | OR (univariate) | p |
|---|---|---|---|---|---|
| Depressive | **DMDD (F34.81)** | 438 | **14.2** | 1.82 | <0.001 |
| Depressive | MDD recurrent (F33.x) | 406 | 12.1 | 1.43 | 0.036 |
| Depressive | Unspecified mood (F39) | 331 | 10.6 | 1.18 | 0.385 |
| Depressive | **MDD single (F32.x)** | 863 | **9.0** | 0.96 | 0.769 |
| Anxiety | Anxiety, unspecified (F41.9) | 563 | 11.9 | 1.44 | 0.016 |
| Anxiety | GAD (F41.1) | 451 | 8.6 | 0.91 | 0.614 |
| Trauma & Stressor | **PTSD (F43.10)** | 679 | **13.1** | 1.74 | <0.001 |
| Trauma & Stressor | **Adjustment (F43.2x)** | 554 | **6.7** | 0.65 | 0.019 |
| Neurodevelopmental | Autism (F84.0) | 501 | 13.0 | 1.62 | 0.002 |
| Neurodevelopmental | ADHD combined (F90.2) | 761 | 12.1 | 1.55 | 0.002 |
| Conduct / disruptive | Conduct disorder (F91.x) | 484 | 13.6 | 1.74 | <0.001 |
| Behavioral symptom | Irritability/anger (R45.4) | 31 | 19.4 | 2.38 | 0.059 |
| Behavioral symptom | Suicidal ideation (R45.851) | 1,346 | 11.4 | 1.67 | <0.001 |

**Key observations:**
- **Depressive disorders is heterogeneous.** DMDD (irritability; 14.2%) and recurrent MDD (12.1%) elevate risk, but single-episode MDD (9.0%) sits at baseline. The collapsed category (10.7%) understates the high-risk subgroups.
- **Trauma & stressor contains opposing signals.** PTSD raises risk (13.1%, OR 1.74) while adjustment disorder is *protective* (6.7%, OR 0.65). Averaged into one category, they partly cancel — the clearest illustration that category-level modeling can erase real effects.
- **The 2025 irritability/anger finding holds directionally** (R45.4, 19.4%) but is rare (n=31, p=0.059); DMDD is the larger, statistically robust expression of the same construct.

This justifies reporting **code/subcategory-level results in the full analysis** while keeping the abstract at the category level for concision.

---

## 4. Restraints: reconciling 2025 (n.s.) with 2026 (significant)

| Test | Result |
|---|---|
| Readmission rate, restrained vs not | **13.5%** (69/510) vs **8.3%** (177/2,142) |
| Univariate logit | OR 1.74 (1.29–2.34), p<0.001 |
| 2026 multivariable logit (adjusted) | OR 1.58 (1.10–2.21), p=0.012 |
| Restraint **count** (continuous) | OR 1.01, p=0.59 — *not* dose-dependent |
| 2025 multivariable logit | **Not** an independent predictor |

**Interpretation:** restraint use is a marker of acute behavioral dysregulation. The *fact* of restraint (not its frequency) carries the readmission signal. Re-running the original model on the same data shows exactly why 2025 found it null: it was entered as a **frequency count** (OR 1.00, p=0.90) and double-counted inside an "externalizing" composite, inside a non-converging model. Coded as a binary flag on the identical cohort, restraint is significant (OR 1.74 univariate, 1.39 adjusted; see `Reconciliation_2025_vs_2026.md` §8). Restraint is also the **largest driver of length of stay** (below).

---

## 5. What predicts **length of stay** (cost driver)

OLS, days (R²=0.145, N=2,652); ACE row from complete-case subset (N=1,569):

| Predictor | β (days) | p |
|---|---|---|
| Physical restraint use | **+6.4** | <0.001 |
| ACE score (per point) | +0.38 | <0.001 |
| Public insurance (AHCCCS) | +0.70 | 0.006 |
| Diagnostic complexity (per category) | +0.23 | 0.044 |
| Bipolar disorder | +1.24 | 0.029 |
| Older age (per year) | +0.14 | 0.047 |

Replicates 2025: ACEs, restraint, diagnostic count, and public insurance all predict **longer stays** but (except restraint) **not** readmission. Restraint dominates — each restrained child averages ~6–7 additional inpatient days.

---

## 6. What predicts **restraint use** (safety / equity concern)

Logistic regression, outcome = any physical restraint (N=2,652):

| Predictor | OR | p |
|---|---|---|
| ADHD | 2.15 | <0.001 |
| Male gender identity (recorded at admission) | 2.13 | <0.001 |
| Longer LOS (per day) | 1.18 | <0.001 |
| Autism spectrum disorder | 1.41 | 0.018 |
| Younger age (per year) | 0.81 | <0.001 |
| Any C-SSRS (suicidality) flag | **0.45** | <0.001 (inverse) |

**A coherent externalizing/neurodevelopmental profile:** younger, male children with ADHD/ASD and longer stays are restrained most; children flagged for suicidality (internalizing) are restrained *less*. This is directly actionable for targeted de-escalation and staffing.

---

## 7. The honest predictive ceiling (the paper's central caution)

Machine learning and regularized LR **surface salient features**, but a **sensitive *and* specific** screen is not achievable in this sample:

| Model | Apparent AUC | Bootstrap-corrected | 10-fold OOF | Calibration |
|---|---|---|---|---|
| Regularized logistic regression | 0.712 | 0.685 | 0.665 | **Well-calibrated raw** (ECE 0.009, HL p=0.24) |
| Random forest | 0.853 | 0.752 | 0.684 | Needs Platt scaling (raw ECE 0.29) |
| CatBoost (gradient boosting) | 0.904 | 0.789 | 0.641 | Needs Platt scaling (raw ECE 0.19) |

- Apparent AUCs of 0.85–0.90 for the tree models are **optimism artifacts**; honest out-of-fold AUC is ~0.64–0.68.
- The simple regularized LR is competitive and the **best-calibrated** — complexity did not help on a small dataset.
- At the optimal (Youden) threshold, **PPV ≈ 15–20%**: flagging ~25–37% of admissions would catch ~45–68% of readmissions while **80–85% of those flagged are never readmitted.**
- **Conclusion:** with 246 events, the model is useful for *understanding* risk factors, not for *triaging* individual patients. A deployable tool needs larger, multi-site data.

---

## 8. Equity findings (new in 2026)

Equalized-odds gaps: **age 0.240**, **gender 0.195**, ACE 0.119, insurance 0.023. Younger children and male-identifying children are flagged at higher true- and false-positive rates. Any future tool requires equity-aware validation before clinical use.

---

## 9. Recommended next steps

1. **Lead the poster with the new findings and the prediction/ML angle** — independently associated risk factors (depressive burden, diagnostic complexity, restraint use, younger age) and the honest predictive ceiling (AUC ≈0.68, PPV ~15–20%). The reconciliation with 2025 belongs in the Discussion as supporting context, not the headline.
2. **Readmission rate is settled: 9.3% (patient-level, 90-day), source-verified.** Report 9.3% and cite the export; the prior 10.4% counted events, not patients (see footnote 1).
3. **Code-level / subcategory sensitivity analysis** (e.g., DMDD and R45.4 broken out of "Depressive Disorders") to recover signal lost on collapse.
4. **Model LOS and restraint use as primary outcomes** (Sections 5–6) — both are clinically and financially consequential and more predictable than readmission.
5. **Multi-site / larger sample** before any predictive-tool claim.
6. **Raise the restraint specification with Dr. Ritfeld** — it is an independent readmission predictor here (OR 1.58, p=0.012) but was absent from the 2025 multivariable model; worth a direct, collegial check of the prior specification.

---

*Methods note: 2026 inferential models are unpenalized `statsmodels` logit; predictive models are sklearn L2-regularized logistic regression, random forest, and CatBoost evaluated with 10-fold CV and 0.632-style bootstrap optimism correction. ACE analyses are complete-case (ACE recorded for 1,569/2,652; 59%).*
