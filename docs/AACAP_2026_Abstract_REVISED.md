# AACAP 2026 Annual Meeting Submission — REVISED DRAFT
**Format:** New Research Poster (Traditional); Data Blitz interest — Yes
**Builds on:** Gold & Ritfeld, AACAP 2025 (Submission #52545)

---

## Working Title
Psychiatric Rehospitalization In Inpatients Aged 5–12: Machine-Learning & The Limits of Prediction In A Single-Site Cohort

---

## Abstract

**Objectives:** Predictors of psychiatric rehospitalization in children are poorly characterized, & predicting readmission in any cohort remains a lofty goal. Standard regression models failed to identify readmission predictors in our prior analysis of 2,652 children aged 5–12. In the current analysis, we used regularized & machine-learning models to identify risk factors for 90-day readmission & to test the achievable ceiling of their predictive performance on small datasets.

<<<<<<< Local Changes
Methods: Patient records for admission & readmission were collected from 2017–2024 at one Arizona hospital. ICD-10 codes were analyzed & aggregated into DSM-5 & CCSR categories. Unpenalized logistic regression provided interpretable odds ratios; regularized logistic regression, random forest (RF), & gradient boosting models were trained on clinical & demographic features with interaction terms, evaluated via bootstrap optimism correction, calibration, & fairness analysis across age, gender, insurance, & adverse childhood experience (ACEs) strata.
||||||| Old File
Methods: Patient records for admission & readmission were collected from 2017–2024 at one Arizona hospital. ICD-10 codes were analyzed & aggregated into DSM-5 & CCSR categories. Unpenalized logistic regression provided interpretable odds ratios; regularized logistic regression, random forest, & gradient boosting models were trained on clinical & demographic features with interaction terms, evaluated via bootstrap optimism correction, calibration, & fairness analysis across age, gender, insurance, & adverse childhood experience (ACEs) strata.
=======
**Methods:** Patient records for admission & readmission were collected from 2017–2024 at 1 Arizona hospital. ICD-10 codes were analyzed & aggregated into DSM-5 & CCSR categories. Unpenalized logistic regression provided interpretable odds ratios; regularized logistic regression, random forest, & gradient boosting models were trained on clinical & demographic features with interaction terms, evaluated via bootstrap optimism correction, calibration, & fairness analysis across age, gender, insurance, & ACE strata.
>>>>>>> External Changes

<<<<<<< Local Changes
Results: Independent associations with readmission were identified for 1)suicidal ideation (OR 1.50, p=0.007);2)diagnostic complexity (OR 1.41 per DSM-5 category, P<0.001);3)physical restraint use (OR 1.59, p=0.009); & 4)younger age (OR 1.10 per year, p=0.013). 1)ACE category;2)C-SSRS flags;3)non-suicidal self-injury; & 4)chronic medical comorbidity were not associated with readmission. Restraint use was also the largest driver of length of stay (LOS, +6 days). Despite these inferential signals, predictive model discrimination was modest (Apparent AUC for RF fellfrom 0.862 to 0.763 after correction) with low precision (PPV ≈20%). Equalized-odds disparity was notable for age (0.221).
||||||| Old File
Results: Independent associations with readmission were identified for 1)suicidal ideation (OR 1.50, p=0.007);2)diagnostic complexity (OR 1.41 per DSM-5 category, P<0.001);3)physical restraint use (OR 1.59, p=0.009); & 4)younger age (OR 1.10 per year, p=0.013). 1)ACE category;2)C-SSRS flags;3)non-suicidal self-injury; & 4)chronic medical comorbidity were not associated with readmission. Restraint use was also the largest driver of length of stay (+6 days). Despite these inferential signals, predictive model discrimination was modest (apparent AUC fell to 0.75 after bootstrap optimism correction) with low precision (PPV ≈20%). Equalized-odds disparities were notable for age (0.24) & gender (0.20).
=======
**Results:** Independent associations with readmission were identified for suicidal ideation (OR 2.59), depressive disorders (OR 1.86), diagnostic complexity (OR 1.26/DSM-5 category), & physical restraint use (OR 1.53). Older age (OR 0.90/year) & NSSI (OR 0.42) were protective, while ACE score, C-SSRS flags, & chronic medical comorbidity were non-predictive. Restraint use was also the largest driver of length of stay (+6 days). Despite these signals discrimination was modest (apparent AUC fell to 0.75 after bootstrap optimism correction) with low precision (PPV ≈20%). Equalized-odds disparities were notable for age (0.24) & gender (0.20).
>>>>>>> External Changes

**Conclusions:** The models surfaced hidden risk factors that standard regression models failed to identify, yet individual readmission remains hard to predict—feature discovery is necessary but not sufficient for a useful risk measure. These findings refine a previous report from this cohort: re-analysis of the data shows that predictors previously reported as null emerge once a non-converging model specification was corrected. Larger, multi-site data & equity-aware validation are needed before clinical use.

---

## Learning Objectives

1. **Identify** the clinical factors independently associated with 90-day psychiatric readmission in children aged 5–12 — suicidal ideation, depressive-disorder burden, diagnostic complexity, physical restraint use, & younger age — & distinguish them from factors (length of stay, C-SSRS screen, chronic medical comorbidity) that are non-predictive or predict LOS rather than readmission.

2. **Explain** why machine-learning & regularized models can surface salient risk factors yet fail to achieve clinically useful sensitivity & specificity in small datasets, interpreting optimism-corrected relative to apparent AUC.

3. **Recognize** age- & gender-based algorithmic disparities that may arise in machine learning-models & the necessity of equity-aware validation before clinical deployment.

---

