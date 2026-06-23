**Determinants Of Psychiatric Rehospitalization In School-Aged Children: A Retrospective Chart Review of Inpatients At An Arizona Inpatient Biobehavioral Unit**

|                            |                                    |
| -------------------------- | ---------------------------------- |
| **Principal Investigator** | Gaby Ritfeld MD, PhD               |
| **Institution**            | Phoenix Children's Hospital        |
| **Department**             | Department of Psychiatry           |
| **Address**                | 1919 E Thomas Rd, Phoenix AZ 85016 |
| **Phone**                  | (602) 933-0990                     |
| **Email**                  | gritfeld@phoenixchildrens.com      |

|                                     |                                    |
| ----------------------------------- | ---------------------------------- |
| **Co-Investigator (Biostatistics)** | M'hamed Temkit, PhD                |
| **Institution**                     | Phoenix Children's Hospital        |
| **Department**                      | Department of Clinical Research    |
| **Address**                         | 1919 E Thomas Rd, Phoenix AZ 85016 |
| **Phone**                           | (602) 933-0199                     |
| **Email**                           | mtemkit@phoenixchildrens.com       |

|                             |                                                            |
| --------------------------- | ---------------------------------------------------------- |
| **Student Co-Investigator** | Matthew Gold                                               |
| **Program**                 | Medical Student, University of Arizona College of Medicine |
| **Email**                   | mdgold@arizona.edu                                         |

**Protocol Version:** 1.3
**Version Date:** 06/01/2026
**IRB Protocol #:**  24-076

---

## Summary of Changes from Version 1.2

| Section                 | Change                                                                                                                                                                          | Reason                                                                                                               |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Study team              | Added Matthew Gold as student co-investigator                                                                                                                                   | Active participation in data analysis and study design throughout study                                              |
| §3.4 Study Population   | Extended study period from December 31, 2023 to June 22, 2027                                                                                                                   | Hospital data extract included 2024 admissions; extending the window increased power and captured more recent trends |
| §3.5 Inclusion Criteria | Updated enrollment window to January 1, 2017 – December 31, 2024                                                                                                                | Consistent with §3.4 amendment                                                                                       |
| §3.7 Study Procedures   | Updated data collection date range                                                                                                                                              | Consistent with §3.4 amendment                                                                                       |
| §3.8 Sample Size        | Updated to reflect actual cohort (N = 2,652); revised observed readmission rate to 9.3%                                                                                         | Enrollment exceeded the 2,000-subject estimate; statistical power is accordingly increased                           |
| §3.9 Analytical Methods | Added machine learning classifiers, bootstrap optimism correction, ICD-10→DSM-5 mapping, and algorithmic fairness analysis; updated statistical platform from SAS 9.4 to Python | Analytical scope expanded to address prediction ceiling and equity questions not specified in v1.2                   |
| §2 Study Objectives     | Added Aim 2 (predictive ceiling) and Aim 3 (algorithmic fairness)                                                                                                               | Reflects expanded analytical scope                                                                                   |
| §8 Publication          | Updated dissemination timeline                                                                                                                                                  | AACAP 2025 poster completed; AACAP 2026 abstract submitted                                                           |

---

## COMPLIANCE STATEMENT

The investigator(s) will perform the study in accordance with this protocol and will report unexpected problems in accordance with Phoenix Children's IRB Policies and Procedures and all federal requirements. Collection, recording, and reporting of data will be accurate and will ensure the privacy, health, and welfare of research subjects during and after the study.

---

## ABSTRACT

**Context (Background):**
The proposed study aims to explore the determinants of psychiatric rehospitalization among school-aged children, focusing on factors that contribute to readmissions to an inpatient biobehavioral unit in Arizona. By examining psychiatric history, symptomatology, adverse childhood experiences, ICD-10 diagnostic profiles, and post-discharge interventions, the research seeks to identify risk factors for rehospitalization. This work is significant for developing targeted interventions and enhancing the quality of psychiatric care for pediatric patients.

**Objectives:**
The study aims to: (1) identify clinical, demographic, and diagnostic factors independently associated with 90-day psychiatric readmission; (2) characterize the achievable ceiling of predictive accuracy from single-site administrative data; and (3) examine algorithmic fairness of predictive models across age, gender identity, insurance type, and adverse childhood experience (ACE) strata.

**Study Design:**
Retrospective chart review of children aged 5–12 admitted to an inpatient biobehavioral unit at Phoenix Children's Hospital between January 1, 2017 and December 31, 2024. Statistical analysis includes multivariable logistic regression, regularized regression (L1/L2), and machine learning classifiers (random forest, gradient boosting) evaluated via bootstrap optimism correction and 10-fold cross-validation. ICD-10 codes were mapped to DSM-5 TR diagnostic categories for aggregated analysis.

**Study Measures:**
Primary outcome: 90-day psychiatric readmission (binary). Key predictors include demographic factors (age, gender identity, insurance), clinical factors (diagnostic profile by DSM-5 TR category, ACE score, C-SSRS flags, physical restraint use, length of stay), and derived features (diagnostic complexity, presence flags for individual DSM-5 categories, chronic medical comorbidity). Model performance is assessed via AUROC with bootstrap optimism correction and 10-fold cross-validation; fairness is assessed via equalized-odds disparity across demographic strata.

---

## 1. BACKGROUND INFORMATION AND RATIONALE

### 1.1 Relevance and Current Knowledge

Suicide remains a significant public health concern, especially among adolescents and emerging adults. The research shows that severe lifetime suicidal ideation was a strong predictor of rehospitalization among adolescents, emphasizing the critical need for effective post-discharge planning and community-based supports to manage high-risk patients (Joyce et al., 2019). Additionally, there has been an alarming increase in death by suicide among those 10–24 years of age from 2007 to 2018 [22], and hospitalization is a critical intervention to prevent future suicide attempts, address the root cause of ideation, and ultimately improve patient outcomes [10]. These hospital readmissions are common, often preventable, costly, and may indicate an error of diagnosis or treatment. If factors can be identified that predict readmission, it may be possible to focus special attention and interventions on at-risk patients to improve their clinical outcomes.

### 1.2 The Scope of the Problem: Pediatric Psychiatric Rehospitalization

1. **High Rates of Rehospitalization for Depressed Children:** A study reports that depressed children had rehospitalization rates of 35% in the first year and 45% in the second year after discharge, indicating a significant recurrence of severe symptoms requiring readmission. This highlights a critical area for intervention to improve long-term outcomes for these children (Asarnow et al., 1988).

2. **Influence of Trauma and Bullying on Rehospitalization:** Another study found that trauma and ongoing bullying significantly increased the risk of psychiatric rehospitalization in pediatric patients. This underscores the importance of addressing these issues through preventive measures and support systems within psychiatric care protocols (Markota et al., 2018).

3. **Social Determinants Affecting Rehospitalization:** A retrospective cohort analysis of children aged 5 to 18 years identified that non-Hispanic Black children and those with government insurance were significantly more likely to be rehospitalized within 90 days. This study emphasizes the need to consider social determinants in managing and preventing psychiatric rehospitalizations (Carroll et al., 2021).

### 1.3 Commonly Identified Risk Factors for Rehospitalization

- **Suicidal Ideation and Behavior:** Studies by Horwitz et al. (2015), Czyz & King (2015), and Joyce et al. (2019) emphasize the role of suicidal ideation and previous suicide attempts as significant predictors for rehospitalization.

- **Previous Psychiatric Admissions:** Donisi et al. (2016), Phillips et al. (2020), and Doupnik et al. (2018) highlight a history of previous psychiatric admissions as a strong predictor for readmission.

- **Clinical Severity and Psychopathology:** Madden et al. (2020) and Edgcomb et al. (2020) point to clinical severity markers, including diagnoses like psychosis and affective disorders, as risk factors. Berona et al. (2017) also identify specific psychopathology profiles related to suicide outcomes.

- **Mental Health Disorders and Comorbidities:** Zheng et al. (2020) and Su et al. (2020) note that mental health disorders like depression, anxiety, and bipolar disorders are significant features associated with rehospitalization. Phillips et al. (2020) also mention multiple psychiatric comorbidities as a risk factor.

- **Family Factors:** Ramsbottom & Farmer (2018) and Madden et al. (2020) emphasize the role of family mental health history and poor family functioning, respectively, as contributing factors.

- **Treatment and Medication Factors:** Joyce et al. (2019) identify a weak treatment alliance as a risk factor, while Bobier et al. (2005) point to medication non-adherence. Grudnikoff et al. (2019) mention higher antipsychotic treatment rates as associated with readmission.

- **Behavioral Factors:** English et al. (2022) find aggression to be a significant risk factor, while Fite et al. (2008) associate externalizing behavior with more frequent readmissions.

- **Socioeconomic and Demographic Factors:** Feng et al. (2017) and Ramsbottom & Farmer (2018) mention age, race, and insurance status as associated factors. Phillips et al. (2020) also note that youth classified as disabled or in foster care have higher odds of readmission.

- **Hospital and Treatment Characteristics:** Phillips et al. (2020) and Grudnikoff et al. (2019) mention hospital-level factors like the number of beds and treatment rates, respectively, as influencing readmission rates.

- **Other Clinical Indicators:** Su et al. (2020) mention specific ICD-10 codes (R45 — symptoms and signs involving emotional state, and F32 — depressive episode) and antidepressant medications as risk factors, while D'Aiello et al. (2021) point to lower functional scores (C-GAS).

**Clinical Significance and Potential Impact:**

Understanding the determinants of psychiatric rehospitalization can inform the development of targeted interventions aimed at reducing the frequency of readmissions and improving the overall mental health and quality of life for children. This research has the potential to contribute to the design of evidence-based policies and practices that enhance the support systems for at-risk children, leading to better educational outcomes and reduced societal costs associated with psychiatric disorders.

- **Predictors of Readmission:** A systematic review found that prior hospitalizations were consistently significant predictors of psychiatric patient readmission. This aligns with findings that previous admissions increase readmission risks, pointing to the need for focused interventions for these high-risk groups to improve clinical outcomes (Donisi et al., 2016).

- **Clinical and Demographic Factors:** A study highlighted that children who were readmitted were rated as more learning disabled or developmentally delayed and received fewer post-hospital service hours. This emphasizes the importance of post-discharge support to prevent readmissions, showcasing the clinical significance of tailored follow-up care (Romansky et al., 2003).

- **Comprehensive Meta-analysis:** Research incorporating data from multiple studies identified suicidal ideation, psychotic disorders, prior hospitalization, and discharge to residential treatment as significant predictors of readmission. This comprehensive view supports the study's focus on identifying and managing high-risk patients to significantly influence readmission rates and clinical practices (Edgcomb et al., 2019).

### 1.4 Scientific Background and Rationale

**Strengths of Previous Studies:**

1. **Comprehensive Coverage:** Studies like Prince et al. (2008) used large, national datasets, such as Medicare data, providing comprehensive coverage and robust statistical power to identify predictors of psychiatric rehospitalization.

2. **Detailed Analysis:** Joyce et al. (2019) and Mercer et al. (1999) conducted detailed analyses of demographic, clinical, and psychosocial predictors, enhancing the understanding of complex interactions that affect rehospitalization rates.

3. **Diverse Populations:** Research has covered various demographic groups, including adolescents, specifically those with severe mental illnesses, broadening the understanding across different population segments.

**Weaknesses of Previous Studies:**

1. **Generalizability Issues:** Many studies, such as those focusing exclusively on limited adolescent populations, may have limited generalizability to other psychiatric patients.

2. **Short Follow-up Periods:** Studies like those by Joyce et al. (2019) often have relatively short follow-up periods, which may not capture long-term outcomes and predictors of rehospitalization.

**How This Study Will Differ or Add:**

1. **Cross-Population Analysis:** While many studies focus on specific groups, this study includes a diverse sample from various demographic backgrounds to enhance generalizability and applicability of the findings.

2. **Analytical Depth:** This study employs a deeper analytical review of existing data. By synthesizing and comparing various analytical approaches — including standard regression, regularized regression, and machine learning — it provides both inferential and predictive perspectives on readmission risk.

3. **Theoretical Contributions:** This study emphasizes theoretical advancements. It explores and proposes frameworks regarding the causes and predictors of psychiatric rehospitalization and critically addresses the gap between identifying population-level risk factors and achieving clinically deployable individual-level prediction.

4. **Focus on Underexplored Factors:** While previous studies have often focused on more common predictors like clinical diagnosis and previous hospitalizations, this study examines underexplored factors including DSM-5 TR diagnostic category complexity, non-suicidal self-injury, the specific operationalization of suicidality (ICD diagnosis code versus C-SSRS screening flags), and algorithmic fairness across demographic strata.

### 1.5 Conclusion

The proposed study is critical for addressing the significant and growing concern of psychiatric rehospitalization among school-aged children. By identifying the determinants and understanding their interactions — and by honestly characterizing the limits of individual-level prediction from single-site administrative data — the research aims to contribute to the development of targeted interventions and policies that can significantly improve the lives of affected children and their families.

---

## 2. STUDY OBJECTIVES

### 2.1 Primary Objective

To identify and examine the determinants of psychiatric rehospitalization among school-aged children, with the goal of developing targeted interventions to reduce the incidence of readmission and improve mental health outcomes.

The primary hypothesis is that specific clinical and demographic risk factors — including psychiatric diagnostic profile, diagnostic complexity, suicidal ideation, physical restraint use, and adverse childhood experiences — significantly predict the likelihood of 90-day psychiatric readmission in children aged 5–12.

### 2.2 Secondary Objectives

**Aim 1: Identify clinical and demographic risk factors associated with 90-day psychiatric readmission.**

Factors to be examined include: psychiatric history; DSM-5 TR diagnostic category profile and complexity (count of distinct DSM-5 categories); suicidal ideation (ICD R45.851); non-suicidal self-injury (DSM-5 NSSI category); C-SSRS screening flags; ACE score; physical restraint use (any vs. none); length of stay; age at admission; gender identity at admission; and insurance type (AHCCCS/Medicaid vs. private/commercial).

Analytical approach: Multivariable logistic regression with pre-specified covariates; results reported as adjusted odds ratios (OR) with 95% confidence intervals.

**Aim 2 (New — Version 1.3): Characterize the achievable ceiling of predictive accuracy from single-site administrative data.**

Rationale: An inferential finding that a variable is associated with readmission does not imply that it supports an actionable clinical prediction tool. This aim explicitly separates association from prediction by evaluating the discriminative performance of regularized and machine-learning classifiers on held-out data.

Analytical approach: Regularized logistic regression (L1/L2 penalty), random forest, and gradient boosting (CatBoost) classifiers trained on clinical and demographic features. Model performance evaluated via 10-fold cross-validation and bootstrap optimism correction. Primary performance metric: area under the ROC curve (AUROC). Secondary metrics: calibration slope, positive predictive value at clinically relevant operating thresholds.

**Aim 3 (New — Version 1.3): Examine algorithmic fairness of predictive models across demographic strata.**

Rationale: Machine learning models trained on administrative data may produce systematically higher error rates for demographic subgroups, which would be clinically harmful if used to triage care. Before any clinical application of these models can be contemplated, disparities in model performance must be characterized.

Analytical approach: Equalized-odds disparity calculated for each model across age, gender identity, insurance type, and ACE category strata. Disparities reported as the difference in true positive rate between the highest- and lowest-performing strata.

### 2.3 Individual Aims and Factor Definitions

**Readmission outcome:** A patient is classified as readmitted if any psychiatric rehospitalization event occurred within 90 days of index discharge (`Readmissions > 0`). The 90-day window was selected a priori and is consistent with Version 1.2. Patients with multiple readmissions within 90 days contribute one observation to the patient-level outcome (binary).

**Discharge and post-discharge support:** Any such note present in the patient's chart.

**Family history of mental illness:** Such a note being present in the patient's chart.

**Psychiatric history:** Any psychiatric disorder in DSM-5 TR or ICD-10 criteria diagnosed upon presentation or previously diagnosed and listed in the chart upon admission.

**Symptom severity:** Measured by C-SSRS (Columbia Suicide Severity Rating Scale) flag columns, coded by presence/non-null per chart documentation. The suicidal ideation ICD code (R45.851) is analyzed separately as a diagnosis rather than a symptom screen, as these two measures capture distinct constructs with divergent associations in this cohort.

**Suicidal ideation:** Presence of ICD-10 code R45.851 in the patient's visit diagnosis list. Analyzed separately from C-SSRS screening flags; not combined into a composite.

**Physical restraint use:** Binary indicator (any restraint episode recorded vs. none); the raw count is not used as the predictor, as the signal is carried by the fact of restraint rather than its frequency.

**Diagnostic complexity:** Count of distinct DSM-5 TR categories represented across a patient's diagnoses. A complementary measure — count of distinct ICD-10 codes — is also reported to confirm robustness.

**Chronic medical comorbidity:** Presence of any ICD-10 code in chapters C, D, E, G, H, I, J, K, L, M, N, or Q in the patient's chronic diagnosis list (Feudtner Pediatric Complex Chronic Condition–aligned chapter allowlist, Feudtner et al. 2014, BMC Pediatrics). Psychiatric (F-), social/administrative (Z-), symptom (R-), infectious (A/B-), and injury (S/T/V-Y) chapters are excluded.

**Insurance status:** AHCCCS (Arizona Medicaid) vs. private/commercial, used as a socioeconomic proxy as specified in Version 1.2.

**Gender identity:** Gender identity as recorded at admission (GenderCode field); not biological sex.

---

## 3. INVESTIGATIONAL PLAN

### 3.1 General Description of Study

This study is observational, retrospective, and correlational in nature. It analyzes existing medical record data to identify associations between clinical, demographic, and diagnostic variables and the likelihood of 90-day psychiatric rehospitalization. No manipulation of variables or conditions is involved.

### 3.2 Investigational Approach

The study employs retrospective analysis of existing medical records from pediatric psychiatric inpatient admissions at Phoenix Children's Hospital. No new data are collected; all data were obtained from a one-time extract of the hospital's electronic health record system.

### 3.3 Analytical Methodology

A quantitative analytical methodology is employed. The analytical approach is expanded in Version 1.3 relative to Version 1.2 to include two complementary components:

**Component 1 — Inferential analysis (association):** Standard and regularized logistic regression to identify which clinical and demographic factors are independently associated with readmission, expressed as adjusted odds ratios.

**Component 2 — Predictive analysis (discrimination):** Machine learning classifiers evaluated on held-out data to determine whether the identified risk factors translate into a clinically actionable individual-level risk prediction tool. This component explicitly tests whether the information ceiling of single-site administrative data is sufficient for clinical deployment.

These two components address distinct research questions and require distinct analytical frameworks. The results of both are reported, and claims regarding association are not conflated with claims regarding prediction.

### 3.4 Study Population *(Amended — Version 1.3)*

The study will examine all records from patients admitted to the biobehavioral unit at Phoenix Children's Hospital between January 1, 2017 and **December 31, 2024**.

*Version 1.2 specified December 31, 2023. The data extract provided to the research team included admissions through December 31, 2024. Extending the study window increased sample size and analytical power and captures an additional year of admissions trends without altering the study design, outcome definition, or patient population.*

### 3.5 Eligibility Criteria *(Amended — Version 1.3)*

**Inclusion Criteria:**
1. Patients aged 5–12 years at the time of index admission
2. Patients who received inpatient psychiatric hospitalization services at Phoenix Children's Hospital between January 1, 2017 and **December 31, 2024**
3. Patients with available C-SSRS documentation (screened at admission)
4. Patients with an available ACE score documented in the medical record

**Exclusion Criteria:**
1. Patients aged \<5 years or ≥13 years at index admission
2. Records with implausible admission or discharge dates (date-quality exclusion applied during data processing)

### 3.6 Study Settings

The study site is the inpatient biobehavioral unit at Phoenix Children's Hospital (PCH), 1919 E Thomas Rd, Phoenix, AZ 85016.

### 3.7 Study Procedures *(Amended — Version 1.3)*

Cases were identified through a review of medical records at the inpatient biobehavioral unit, with selection based on the inclusion and exclusion criteria in §3.5. Data were collected from medical records covering admissions from **January 1, 2017 through December 31, 2024**, focusing on psychiatric history, treatment, diagnoses, and outcomes, with confidentiality maintained throughout. All data collection was completed as a one-time extraction from PCH's electronic health record system; no ongoing or prospective data collection is occurring.

ICD-10 codes were mapped to DSM-5 TR diagnostic categories using a comprehensive reference crosswalk (1,863 unique codes), enabling aggregated analysis at the diagnostic-category level in addition to code-level analysis.

### 3.8 Sample Size and Power *(Amended — Version 1.3)*

The Version 1.2 protocol estimated a target sample of 2,000 subjects based on a 10% readmission prevalence and a desired confidence interval margin of error of 1.4%. The actual extracted cohort comprises **2,652 patients**, exceeding this target.

The observed 90-day readmission rate is **9.3%** (246 of 2,652 patients). This reflects the patient-level binary outcome (readmitted yes/no within 90 days). The event-level count is 275 readmission events (219 patients readmitted once, 25 readmitted twice, 2 readmitted three times), yielding an event-level rate of 10.4%; the patient-level rate (9.3%) is the appropriate denominator for the primary outcome.

With N = 2,652 and an observed prevalence of 9.3%, the 95% Wilson score confidence interval for the readmission proportion has a half-width of approximately 1.1 percentage points — narrower than the 1.4% margin specified in Version 1.2. Statistical power for the multivariable model and for detecting clinically meaningful differences in predictor means between readmitted and non-readmitted groups is accordingly at or above the 80% target specified in Version 1.2.

### 3.9 Analytical Methods *(Substantially Amended — Version 1.3)*

**Descriptive statistics:** Frequencies and proportions for categorical variables; mean ± standard deviation or median (interquartile range) for continuous variables. Group comparisons for categorical variables tested using chi-squared or Fisher's exact test; continuous variables compared using Wilcoxon rank-sum test. All tests two-sided; significance level α = 0.05.

**Inferential analysis (Aim 1):** Multivariable logistic regression model with pre-specified predictors (see §2.3). Results reported as adjusted OR with 95% CI and p-values. The model is specified with clinical covariates coded as described in §2.3; restraint is entered as a binary flag (any vs. none); suicidal ideation is entered as the ICD R45.851 diagnosis indicator separately from C-SSRS composite flags. Model convergence is verified; near-constant covariates (\>99% prevalence) are excluded prior to fitting to avoid complete-separation artifacts.

For length of stay as an outcome, a multivariable ordinary least squares (OLS) linear regression is used with the same predictor set, reported as regression coefficients with 95% CI.

**Predictive analysis (Aim 2):** Three classifier types are trained and evaluated:
1. Regularized logistic regression (L1 and L2 penalty; tuned via nested cross-validation)
2. Random forest (scikit-learn implementation; hyperparameter tuning via grid search)
3. Gradient boosting (CatBoost; handles categorical features natively)

All classifiers are evaluated using 10-fold cross-validation (out-of-fold predictions) and bootstrap optimism correction to adjust apparent in-sample performance for over-optimism. Class imbalance (9.3% positive rate) is addressed via class-weight adjustment. Primary performance metric: AUROC. Secondary: calibration slope, positive predictive value (PPV) at operating thresholds corresponding to sensitivity ≥ 0.60. Feature importance assessed via SHAP (SHapley Additive exPlanations) values for the gradient boosting model.

**Fairness analysis (Aim 3):** Equalized-odds disparity calculated as the absolute difference in true positive rate (sensitivity) between the highest- and lowest-performing subgroups within each demographic stratum (age tertile, gender identity, insurance type, ACE category). Disparities ≥ 0.10 are flagged as clinically notable.

**Statistical platform:** *(Amended from Version 1.2)* Analyses are conducted in **Python 3.12** using open-source scientific packages: `pandas`, `numpy`, `scipy`, `scikit-learn`, `catboost`, `shap`, `matplotlib`, and `statsmodels`. Analysis code is maintained in a version-controlled repository. Version 1.2 specified SAS 9.4; this platform change does not alter the analytical methods or the hypotheses being tested.

### 3.10 Confounders

1. **Comorbidity Severity:** The severity and type of psychiatric comorbidities (such as externalizing disorders associated with aggressive behavior or PTSD) are acknowledged as variables, but the extent of these conditions could independently influence the likelihood of rehospitalization.

2. **Socioeconomic Factors:** While insurance status (AHCCCS vs. commercial) is considered, other socioeconomic factors such as family income, parental education, and employment status might confound the association between insurance type and rehospitalization rates if not controlled for.

3. **Family Environment:** Family functioning and presence of parents are considered, but broader aspects of the family environment, like parental mental health or familial stability, could also affect rehospitalization rates.

4. **Previous Hospitalizations:** The number of previous psychiatric hospitalizations is a variable, but the reasons for these hospitalizations and the interval between them could have a confounding effect on the current risk of rehospitalization.

5. **Medication Adherence:** While medication status is assessed, actual adherence to medication regimens is critical and could be a confounder if adherence levels are not accurately measured and controlled.

6. **Access to and Quality of Follow-up Care:** The study considers post-discharge interventions and follow-up care, but the quality and accessibility of these services could vary significantly, influencing rehospitalization rates.

7. **Measurement of Variables:** How certain conditions like 'suicidal ideation' or 'non-suicidal self-injury' are measured and reported could vary, potentially confounding the results if not standardized across the study population. This concern is addressed in Version 1.3 by the explicit separate operationalization of suicidal ideation (ICD R45.851 diagnosis code) and C-SSRS screening flags as distinct variables.

### 3.11 Confounder Mitigation

1. **Multivariable Analysis:** Statistical methods including multivariable logistic regression are used to control for potential confounders. This allows for estimation of the effect of the primary independent variables on rehospitalization while accounting for the influence of other covariates.

2. **Propensity Score Matching:** Propensity score matching may be used to balance the distribution of confounding variables between groups that have and have not been rehospitalized, simulating the conditions of a randomized controlled trial by creating comparable groups based on observed covariates.

3. **Standardization of Measurement Techniques:** All conditions such as 'suicidal ideation' and 'non-suicidal self-injury' are defined and measured consistently across all study participants using standardized coding per §2.3. Near-constant covariates (>99% prevalence) are identified and excluded from multivariable models prior to fitting to avoid complete-separation artifacts.

4. **Stratification:** Data analysis is stratified by key demographic factors including age, gender identity, insurance type, and ACE category. This approach identifies how the relationship between study variables and rehospitalization varies across strata and enables the fairness analysis described in Aim 3.

5. **Collection of Comprehensive Data:** Detailed data on all known confounders — including insurance type, ACE score, previous hospitalization history, and treatment documentation — are included in the analytic dataset, allowing for their inclusion as covariates or stratification variables.

6. **Sensitivity Analyses:** Sensitivity analyses are conducted to examine the robustness of findings across different model specifications, covariate subsets, and assumptions. This includes evaluating whether the diagnostic complexity association holds under both DSM-5 category count and ICD-10 code count definitions.

---

## 4. DATA COLLECTION, RETENTION AND MONITORING

### 4.1 Data and Specimen Collection and Management

All data were collected as a one-time extraction from Phoenix Children's electronic health record system. Data are stored in a password-protected, encrypted hard drive with access restricted to authorized study personnel. De-identification of records is maintained throughout data storage and analysis. No new data collection is ongoing. The data retention period adheres to regulatory requirements; data will be securely destroyed following the required retention period.

All data and records generated during this study will be kept confidential in accordance with institutional policies and HIPAA provisions on subject privacy. Data and records will not be used for any purpose other than conducting this study.

---

## 5. REGULATORY AND ETHICAL CONSIDERATIONS

### 5.1 Potential Risks

This study involves no direct contact with human subjects. All data were collected retrospectively from existing medical records and are de-identified for analysis. The principal risk is inadvertent disclosure of confidential information, mitigated by the data security measures described in §4.1. No physical, psychological, social, or economic risks accrue to subjects.

### 5.2 Economic Burden

No costs are foreseen for subjects whose charts are included in the research.

### 5.3 Potential Benefits

The study does not offer direct benefits to participants, given its observational retrospective nature. Indirect societal benefits include: a more precise characterization of risk factors for pediatric psychiatric readmission that may inform discharge planning and follow-up interventions; and an honest quantification of the limits of administrative-data–based prediction tools, which may prevent premature deployment of inadequately validated risk scores in clinical practice.

### 5.4 Risk-Benefit Assessment

The study's potential benefits to the scientific and clinical community outweigh the minimal risks involved. The retrospective, de-identified design maintains participant confidentiality while providing population-level insights that may benefit future patients.

### 5.5 Informed Consent/Assent and HIPAA Authorization

Waiver of consent is requested (and was granted in Version 1.2) due to the retrospective chart review nature of the study. No greater than minimal risk is posed to subjects whose charts are included in the study. This determination is unchanged in Version 1.3.

---

## 6. SAFETY MANAGEMENT

### 6.1 Event Reporting

Any event or incident with the potential to be classified as an unanticipated problem posing risks to participants or others (adverse events, protocol deviations, protocol violations, subject complaints, audit results, enforcement actions, breaches of confidentiality, research misconduct, etc.) will be reported to the IRB in a timely fashion per Phoenix Children's IRB Policies and Procedures.

**No unanticipated problems, adverse events, or protocol deviations have occurred as of the date of this submission.**

---

## 7. COMPENSATION

Not relevant. No compensation is involved for subjects whose charts are utilized.

---

## 8. PUBLICATION *(Amended — Version 1.3)*

Results are being disseminated through the following channels:

1. **AACAP 2025 Annual Meeting (Completed):** Poster presentation — "Psychiatric Rehospitalization in School-Aged Children: Preliminary Risk Factor Analysis" (Gold & Ritfeld, Submission #52545).

2. **AACAP 2026 Annual Meeting (submitted):** Abstract submitted — "Psychiatric Rehospitalization In Inpatients Aged 5–12: Machine-Learning & The Limits of Prediction In A Single-Site Cohort." This abstract presents the full expanded analysis including the machine learning predictive ceiling and fairness results and addresses a model-specification correction relative to the 2025 submission.

3. **Peer-reviewed manuscript (In Preparation):** Submission to a peer-reviewed journal (candidate journals include *Journal of Child Psychology and Psychiatry*, *Journal of the American Academy of Child and Adolescent Psychiatry*, *Psychiatric Services*). Target submission: October 2026.

*Version 1.2 specified a target submission date of Fall 2025. The analytical scope was expanded to include machine learning modeling and fairness analysis (Aims 2 and 3), which required additional time for development, validation, and documentation. An amendment is in progress that intends to increase the sample size and analyze additional factors. The revised completion target is December 2026.

---

## 9. REFERENCES

1. Bobier C, Warwick M. Factors associated with readmission to adolescent psychiatric care. *Aust N Z J Psychiatry*. 2005;39(7):600-606. doi:10.1080/j.1440-1614.2005.01632.x

2. Connell SK, To T, Arora K, Ramos J, Haviland MJ, Desai AD. Perspectives of Parents and Providers on Reasons for Mental Health Readmissions: A Content Analysis Study. *Adm Policy Ment Health*. 2021;48(5):830-838. doi:10.1007/s10488-021-01134-6

3. Grudnikoff E, McNeilly T, Babiss F. Correlates of psychiatric inpatient readmissions of children and adolescents with mental disorders. *Psychiatry Research*. 2019;282:112596. doi:10.1016/j.psychres.2019.112596

4. D'Aiello B, Menghini D, Averna R, Labonia M, Vicari S. Risk Factors for Revolving Door in Children and Adolescents with Psychiatric Disorders. *J Clin Med*. 2021;10(21):5004. doi:10.3390/jcm10215004

5. Feng JY, Toomey SL, Zaslavsky AM, Nakamura MM, Schuster MA. Readmission After Pediatric Mental Health Admissions. *Pediatrics*. 2017;140(6):e20171571. doi:10.1542/peds.2017-1571

6. English M, McCullough S, Sommerhalder MS, et al. Factors Associated with Readmissions to a Child Psychiatric Inpatient Unit. *Evidence-Based Practice in Child and Adolescent Mental Health*. 2022;7(4):493-502. doi:10.1080/23794925.2022.2127135

7. Ramsbottom H, Farmer LC. Reducing pediatric psychiatric hospital readmissions and improving quality care through an innovative Readmission Risk Predictor Tool. *Journal of Child and Adolescent Psychiatric Nursing*. 2018;31(1):14-22. doi:10.1111/jcap.12203

8. Edgcomb JB, Sorter M, Lorberg B, Zima BT. Psychiatric Readmission of Children and Adolescents: A Systematic Review and Meta-Analysis. *PS*. 2020;71(3):269-279. doi:10.1176/appi.ps.201900234

9. Joyce VW, King CD, Nash CC, Lebois LAM, Ressler KJ, Buonopane RJ. Predicting Psychiatric Rehospitalization in Adolescents. *Adm Policy Ment Health*. 2019;46(6):807-820. doi:10.1007/s10488-019-00982-7

10. Madden A, Vajda J, Llamocca EN, et al. Factors associated with psychiatric readmission of children and adolescents in the U.S.: A systematic review of the literature. *General Hospital Psychiatry*. 2020;65:33-42. doi:10.1016/j.genhosppsych.2020.05.004

11. Doupnik S, Rodean J, Zima BT, et al. Readmissions after Pediatric Hospitalization for Suicide Ideation and Suicide Attempt. *J Hosp Med*. 2018;13(11):743-751. doi:10.12788/jhm.3070

12. Phillips MS, Steelesmith DL, Campo JV, Pradhan T, Fontanella CA. Factors Associated With Multiple Psychiatric Readmissions for Youth With Mood Disorders. *Journal of the American Academy of Child & Adolescent Psychiatry*. 2020;59(5):619-631. doi:10.1016/j.jaac.2019.05.024

13. Fite PJ, Stoppelbein L, Greening L, Dhossche D. Child internalizing and externalizing behavior as predictors of age at first admission and risk for repeat admission to a child inpatient facility. *American Journal of Orthopsychiatry*. 2008;78(1):63-69. doi:10.1037/0002-9432.78.1.63

14. Berona J, Horwitz AG, Czyz EK, King CA. Psychopathology profiles of acutely suicidal adolescents: Associations with post-discharge suicide attempts and rehospitalization. *Journal of Affective Disorders*. 2017;209:97-104. doi:10.1016/j.jad.2016.10.036

15. Zheng L, Wang O, Hao S, et al. Development of an early-warning system for high-risk patients for suicide attempt using deep learning and electronic health records. *Transl Psychiatry*. 2020;10(1):1-10. doi:10.1038/s41398-020-0684-2

16. Su C, Aseltine R, Doshi R, Chen K, Rogers SC, Wang F. Machine learning for suicide risk prediction in children and adolescents with electronic health records. *Transl Psychiatry*. 2020;10(1):1-10. doi:10.1038/s41398-020-01100-0

17. Donisi V, Tedeschi F, Salazzari D, Amaddeo F. Pre- and post-discharge factors influencing early readmission to acute psychiatric wards: implications for quality-of-care indicators in psychiatry. *General Hospital Psychiatry*. 2016;39:53-58. doi:10.1016/j.genhosppsych.2015.10.009

18. Fazel S, Wolf A, Larsson H, Mallett S, Fanshawe TR. The prediction of suicide in severe mental illness: development and validation of a clinical prediction rule (OxMIS). *Transl Psychiatry*. 2019;9(1):1-10. doi:10.1038/s41398-019-0428-3

19. Kessler RC, Bossarte RM, Luedtke A, Zaslavsky AM, Zubizarreta JR. Suicide prediction models: a critical review of recent research with recommendations for the way forward. *Mol Psychiatry*. 2020;25(1):168-179. doi:10.1038/s41380-019-0531-0

20. Czyz EK, King CA. Longitudinal Trajectories of Suicidal Ideation and Subsequent Suicide Attempts among Adolescent Inpatients. *J Clin Child Adolesc Psychol*. 2015;44(1):181-193. doi:10.1080/15374416.2013.836454

21. Horwitz AG, Czyz EK, King CA. Predicting Future Suicide Attempts Among Adolescent and Emerging Adult Psychiatric Emergency Patients. *Journal of Clinical Child & Adolescent Psychology*. 2015;44(5):751-761. doi:10.1080/15374416.2014.910789

22. Curtin S, Garnett M. Suicide and Homicide Death Rates Among Youth and Young Adults Aged 10–24: United States, 2001–2021. Published online June 2023. doi:10.15620/cdc:128423

23. Asarnow JR, Goldstein MJ, Carlson GA, Perdue S, Bates S, Keller J. Childhood-onset depressive disorders: A follow-up study of rates of rehospitalization and out-of-home placement among child psychiatric inpatients. *Journal of Affective Disorders*. 1988;15(3):245-253. doi:10.1016/0165-0327(88)90022-5

24. Markota M, McKean A, Romanowicz M, Schak K, Croarkin P, Voort JV. Rehospitalization to a child and adolescent psychiatry unit: Role of trauma and bullying. *Gen Hosp Psychiatry*. 2018;55:10-14. doi:10.1016/j.genhosppsych.2018.08.010

25. Carroll A, Hall M, Brown C, et al. Association of Race/Ethnicity and Social Determinants with Rehospitalization for Mental Health Conditions at Acute Care Children's Hospitals. *J Pediatr*. 2021. doi:10.1016/j.jpeds.2021.08.078

---
