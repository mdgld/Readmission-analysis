# AACAP 2026 Annual Meeting Submission
**Meeting:** AACAP Annual Meeting, Atlanta, GA — October 26–31, 2026
**Format:** New Research Poster (Traditional); Data Blitz interest — Yes
**Builds on:** Gold & Ritfeld, AACAP 2025 (Submission #52545), now published (JAACAP special issue)

---

## Working Title
Predicting 90-Day Psychiatric Rehospitalization in Children Aged 5–12: Machine-Learning Risk Factors and the Limits of Prediction in a Single-Site Cohort

---

## Abstract (281 words / 1,881 non-space characters — within AACAP's 2,000-character limit)

**Objectives:** Predictors of psychiatric rehospitalization in school-aged children are poorly characterized, and whether readmission can be predicted at the individual level is unknown. In a cohort of 2,652 children aged 5–12, we used regularized and machine-learning models to identify risk factors for 90-day readmission and to test the achievable ceiling of predictive performance.

**Methods:** Single Arizona site; admissions 2017–2024; 90-day readmission 9.3% (247/2,652, source-verified). The 1,863 ICD-10 codes were aggregated into DSM-5/CCSR categories. We trained regularized logistic regression, random forest, and gradient boosting on 24 features (diagnostic-category burden, ACEs, C-SSRS flags, restraint use, length of stay, demographics) with interaction terms, evaluated by 10-fold cross-validation with bootstrap optimism correction, calibration, and fairness analysis across age, sex, insurance, and ACE strata. Unpenalized logistic regression provided interpretable odds ratios.

**Results:** Independent predictors of readmission were depressive-disorder burden (OR 1.78), diagnostic complexity (OR 1.31 per added category), physical restraint use (OR 1.58), and younger age (OR 0.90/year); adverse childhood experiences and suicidality were non-predictive. Restraint use was also the largest driver of length of stay (+6 days). Despite these signals, honest discrimination was modest (Random Forest: best out-of-fold AUC 0.684; apparent AUC 0.853 fell to 0.752 after bootstrap optimism correction), with low precision (positive predictive value ~15–20% at the optimal threshold). Equalized-odds disparities were notable by age (0.240) and sex (0.195).

**Conclusions:** Machine learning identified coherent, clinically interpretable risk factors—depressive burden, diagnostic complexity, restraint use, younger age—yet individual readmission remained hard to predict, showing that feature discovery is easier than building a deployable tool from a small, single-site sample. These findings refine an earlier analysis of this cohort (90-day rate corrected from 10.4% to 9.3%); larger, multi-site data and equity-aware validation are needed before clinical use.

---

## Learning Objectives

1. **Identify** the clinical and systemic factors independently associated with 90-day psychiatric readmission in children aged 5–12—depressive-disorder burden, diagnostic complexity, physical restraint use, and younger age—and distinguish them from factors that predict length of stay rather than readmission.

2. **Explain** why machine-learning and regularized models can surface salient risk factors yet fail to achieve clinically useful sensitivity and specificity in small, single-site datasets, interpreting optimism-corrected relative to apparent AUC.

3. **Recognize** age- and sex-based algorithmic disparities in pediatric readmission models and their implications for equity-aware validation before any clinical deployment.

---

## Supporting Notes (for poster Discussion / mentor review — NOT part of submitted abstract)

*The poster leads with the new findings and the prediction/ML angle. The reconciliation points below belong in the Discussion as supporting context, not the headline. Full detail and re-derived tables are in `Analysis_Comparison_2025_vs_2026.md`.*

### A. The readmission-rate discrepancy — resolved, source-verified
The original data export (`1854_…xlsx`, *Summary* sheet) gives the definitive 90-day rate: **247/2,652 = 9.3%** (also 7-day 1.5%, 30-day 4.8%). The previously reported **10.4%** equals the **275 readmission *events*** (219 patients ×1 + 25 ×2 + 2 ×3) ÷ 2,652 — i.e., it counted events, double-counting the 27 children readmitted more than once. The correct **patient-level** rate is **9.3%**, matching the current analysis (246/2,652). This is a numerator-definition correction, not a cohort difference. State 9.3% and cite the export.

### B. Why this year's predictors differ from last year's (supporting, not headline)
- **Unit of analysis is the dominant factor.** 2025 modeled many sparse, collinear individual ICD codes → inflated standard errors → no independent predictors. The *same* unpenalized logistic regression on aggregated DSM-5/CCSR categories recovers independent predictors (depressive burden OR 1.78; complexity OR 1.31/category; restraint OR 1.58; younger age OR 0.90/yr).
- **Restraint use was independently associated with readmission** (OR 1.58, p=0.012) in the current model but was not identified in the 2025 multivariable model. The *fact* of restraint carries the signal, not the count (OR 1.01, p=0.59). Worth a direct, collegial conversation with Dr. Ritfeld about the prior model's specification.
- **Irritability ↔ depression bridge.** Irritability/anger (R45.4; n=31, 19.4%) is nosologically DMDD (F34.81; n=438, 14.2%), filed under Depressive Disorders (n=1,779, 10.7%); collapsing surfaces a category effect yet dilutes the high-risk subgroup (DMDD+ 14.2% vs DMDD− 9.6%).
- **"Regularized vs multivariable" is prediction vs inference, not this-year-vs-last.** The inferential model is unpenalized `statsmodels` logit (same family as 2025); regularized (L2) LR and tree ensembles served only the predictive arm.
- **Replication of 2025 nulls.** ACEs (readmission OR 1.04, p=0.35) and suicidality stay non-predictive of readmission, while ACEs/restraint/complexity/public insurance predict longer stays.

### C. Confirmed / remaining items
- **Outcome window & rate:** confirmed 90-day from initial admission; accrual 2017–2024; rate 9.3% (source-verified). Resolved.
- **Age range:** verified 5–12 (median 10).
- **Authorship/order** for the 2026 submission to confirm.
