# AACAP 2026 Annual Meeting Submission
**Meeting:** AACAP Annual Meeting, Atlanta, GA — October 26–31, 2026
**Format:** New Research Poster

---

## Abstract 

**Objectives:** Pediatric psychiatric rehospitalization is a critical quality indicator, yet validated risk stratification tools for school-aged children are lacking. This study aimed to characterize diagnostic predictors of readmission and evaluate the performance and equity of machine learning models in a pediatric inpatient cohort.

**Methods:** Retrospective cohort study of 2,652 pediatric psychiatric admissions at a single Arizona institution (2017–2024). All 1,863 ICD-10-CM codes were mapped to DSM-5-TR categories using pyhealth and manual regex. Three prediction models (logistic regression, random forest, CatBoost) were trained on 24 features including DSM-5 category burden, ACE scores, C-SSRS severity flags, length of stay, and insurance status. Discrimination was assessed via 10-fold cross-validation and bootstrap-corrected optimism estimates with calibration by Brier score and Hosmer–Lemeshow test. Fairness was evaluated across age, sex, insurance, and ACE-score subgroups using equalized-odds disparity metrics.

**Results:** Readmission occurred in 9.3% of patients (246/2,652). The most prevalent DSM-5 categories among them were depressive disorders (67.1%), trauma/stressor-related disorders (53.7%), ADHD (52.7%), and anxiety disorders (43.5%). Diagnostic groups with the highest readmission rates were non-suicidal self-injury behavior (29.2%), other neurodevelopmental disorders (27.7%), and bipolar disorders (21.8%). Random forest achieved the best discrimination (AUC-ROC 0.684, 95% CI 0.649–0.717); apparent AUC was markedly overestimated without cross-validation (0.853 vs. bootstrap-corrected 0.752). The strongest readmission predictors were depressive disorders, psychotic disorders, and medical comorbidity. Fairness analysis revealed meaningful disparities: age-stratified equalized-odds gap of 0.240 and sex-stratified gap of 0.195, with younger children and males disproportionately flagged.

**Conclusions:** Readmission risk concentrated in our sample among children with comorbid depression, psychosis, neurodevelopmental disorders, and medical complexity. Machine learning models applied to small datasets demonstrate modest honest discrimination and exhibit clinically significant age and sex disparities. These findings highlight the need for use of suitably large data sets and equity-aware validation before implementing algorithmic risk tools in clinical settings.

---

## Learning Objectives

1. **Identify** the DSM-5-TR diagnostic categories associated with the highest 30-day psychiatric readmission risk in a sample of school-aged children, distinguishing the differential risk profiles of neurodevelopmental, internalizing, and self-injurious behavior diagnoses.

2. **Describe** The dangers of overfitting when using small datasets, and how machine learning readmission risk models can substantially overestimate predictive performance in the absence of rigorous cross-validation. Interpret bootstrap-corrected AUC estimates relative to apparent AUC.

3. **Recognize** age- and sex-based algorithmic disparities that can occur when building prediction models, and discuss their implications for equitable deployment of clinical risk stratification tools.
