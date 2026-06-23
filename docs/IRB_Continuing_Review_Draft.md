# IRB Continuing Review Application — Draft

**Submission type:** Continuing Review (Annual Renewal)
**Protocol title:** Psychiatric Rehospitalization in School-Aged Children: Risk Factors, Predictive Modeling, and Equity Analysis
**Short title / running head:** Pediatric Psychiatric Readmission Study
**IRB Protocol #:** [PROTOCOL NUMBER]
**Date of original approval:** [ORIGINAL APPROVAL DATE]
**Expiration date of current approval:** [CURRENT EXPIRATION DATE]
**Date of this submission:** [SUBMISSION DATE]

---

## Section 1 — Principal Investigator and Study Team

| Role | Name | Degree | Institution | Department |
|------|------|--------|-------------|------------|
| Principal Investigator | [PI NAME — Dr. Ritfeld or designated PI] | [DEGREE] | [INSTITUTION] | [DEPARTMENT] |
| Co-Investigator / Student Researcher | Matthew Gold | MS2 (Medical Student) | [INSTITUTION] | [DEPARTMENT] |

**Contact for IRB correspondence:**
Name: [PI NAME]
Email: [PI EMAIL]
Phone: [PI PHONE]

---

## Section 2 — Study Overview

### 2.1 Brief Description

This is a single-site, retrospective cohort study examining risk factors for 90-day psychiatric rehospitalization in children aged 5–12 admitted to [INSTITUTION NAME] between 2017 and 2024. The study uses existing medical record data that were extracted and de-identified (or provided as a limited dataset under a data use agreement) prior to analysis. There is no prospective enrollment, no direct contact with subjects or families, and no intervention of any kind. Analysis is conducted on de-identified administrative and clinical records.

### 2.2 Study Objectives

1. Identify clinical, demographic, and diagnostic predictors of 90-day psychiatric readmission in school-aged children using standard logistic regression (adjusted odds ratios) and regularized / machine-learning classifiers.
2. Quantify the achievable ceiling of predictive accuracy from single-site administrative data, using bootstrap optimism correction and 10-fold cross-validation.
3. Examine algorithmic fairness across age, gender identity, insurance type, and adverse childhood experience (ACE) strata.
4. Characterize the relationship between physical restraint use and index hospitalization length of stay.

### 2.3 Study Design

Retrospective cohort study. Data source: administrative and clinical records for all inpatient psychiatric admissions of children aged 5–12 at [INSTITUTION NAME], 2017–2024.

**Primary outcome:** 90-day psychiatric readmission (binary: any readmission within 90 days of discharge).

**Key variables:**
- Demographics: age at admission, gender identity, insurance type (AHCCCS / private / other)
- Clinical: ICD-10 diagnosis codes (mapped to DSM-5 TR categories), adverse childhood experience (ACE) score, C-SSRS suicidality screening flags, physical restraint episodes, length of stay
- Derived features: diagnostic complexity (count of distinct DSM-5 categories), presence flags for individual diagnostic categories (depressive disorders, ADHD, PTSD, NSSI, suicidal ideation, autism spectrum disorder, etc.), chronic medical comorbidity (Feudtner Pediatric Complex Chronic Condition criteria)

---

## Section 3 — Study Status

**Current status:** ☒ Data analysis only (enrollment/data collection closed)

Data collection was completed as a one-time extraction of existing records. No new subjects are being enrolled, no new data are being collected, and there is no further access to identifiable patient information. The research team is conducting statistical analysis of the de-identified dataset.

**Timeline:**
- Data extraction completed: [DATE]
- Analysis ongoing: 2024 – present
- Anticipated completion: [EXPECTED COMPLETION DATE, e.g., December 2026]
- Dissemination: AACAP 2025 Annual Meeting (abstract submitted); AACAP 2026 Annual Meeting (abstract in preparation); manuscript preparation anticipated following conference

---

## Section 4 — Enrollment and Subject Status

Because this is a retrospective records study, "enrollment" refers to the number of patient records included in the analytic dataset.

| | N |
|--|--|
| Total records in dataset | 2,652 |
| Age range at admission | 5–12 years |
| Study period | January 2017 – December 2024 |
| Records excluded (data quality filter) | [N, if applicable] |
| Analytic cohort (final) | 2,652 |

**Note on data quality:** A date-quality filter was applied to remove records with implausible admission/discharge dates. The final analytic cohort consists of 2,652 unique patient encounters representing children with inpatient psychiatric admissions.

---

## Section 5 — Summary of Findings to Date

### 5.1 Primary Outcome

Of 2,652 children, 246 (9.3%) were readmitted to a psychiatric inpatient unit within 90 days of discharge. An additional 27 children were readmitted more than once within this window, yielding 275 total readmission events (event-level rate: 10.4%).

### 5.2 Key Findings

**Multivariable logistic regression** (adjusted analysis) identified the following independent associations with 90-day readmission:

| Predictor | Adjusted OR | 95% CI | p-value |
|-----------|-------------|--------|---------|
| Suicidal ideation (ICD R45.851) | 2.59 | 1.82–3.66 | <0.001 |
| Depressive disorder burden | 1.73 | 1.21–2.46 | 0.003 |
| Diagnostic complexity (per additional DSM-5 category) | 1.34 | 1.19–1.51 | <0.001 |
| Physical restraint use (any vs. none) | 1.52 | 1.06–2.17 | 0.023 |
| Younger age (per additional year) | 0.91 | 0.84–0.99 | 0.023 (protective) |
| Non-suicidal self-injury (NSSI) | 0.40 | 0.27–0.59 | <0.001 (protective) |

**Variables tested and found non-significant:** ACE score, C-SSRS screening flags, gender identity at admission, insurance type, chronic medical comorbidity, length of stay.

**Physical restraint and length of stay:** Restraint use was the largest independent predictor of index length of stay in a multivariable linear model, associated with approximately six additional inpatient days (median 12 vs. 8 days in restrained vs. non-restrained children; Mann-Whitney p < 0.001).

**Machine-learning models:** Regularized logistic regression, random forest, and gradient-boosting classifiers (CatBoost) were trained and evaluated using 10-fold cross-validation with bootstrap optimism correction. Corrected out-of-fold AUC ranged from 0.64 to 0.68; positive predictive value at clinically relevant operating points was approximately 15–20%. These results indicate that, while population-level risk factors were identified, individual-level readmission prediction with single-site administrative data remains limited.

**Algorithmic fairness:** Equalized-odds disparity was observed across age (0.22) and gender identity (0.20) strata, indicating differential model error rates for younger children and male-identified patients. These disparities underscore the need for equity-aware validation before any clinical deployment.

### 5.3 Relationship to Prior Analysis

A prior analysis of this cohort was presented at AACAP 2025 (Gold & Ritfeld, Submission #52545). Re-analysis of the identical 2,652-patient dataset, using corrected model specification (restraint coded as a binary indicator; suicidal ideation analyzed as ICD code R45.851 rather than within a composite; exclusion of a near-constant near-zero-variance covariate that caused model non-convergence), reveals that the predictors reported as null in 2025 were present in the original data but obscured by the original model specification. The 2025 finding that ACE score is non-predictive of readmission is replicated. Findings are being prepared for dissemination with transparent acknowledgment of the specification correction.

---

## Section 6 — Unanticipated Problems, Adverse Events, and Protocol Deviations

**Unanticipated problems involving risks to subjects or others:** None.

**Adverse events (subject harm):** None. This is a retrospective records study with no direct subject contact; adverse events in the traditional sense are not applicable.

**Protocol deviations:** None. There have been no deviations from the approved protocol.

**Privacy/confidentiality breach:** None known.

---

## Section 7 — Risk/Benefit Assessment

### 7.1 Risks

This study involves no direct contact with human subjects, no administration of any intervention, and no collection of new biological specimens or identifiable data. The dataset provided to the research team is [de-identified per HIPAA Safe Harbor standards / provided under a HIPAA-compliant data use agreement as a limited dataset — SELECT APPROPRIATE]. The principal risks are therefore limited to:

- **Confidentiality breach:** Residual risk from the storage of research data files. Mitigated by data security measures described in Section 8.
- **Risk of re-identification:** Minimal, given the de-identified or limited-dataset nature of the data and the aggregate level at which results are reported.

**Overall risk level:** Minimal.

### 7.2 Benefits

There is no direct benefit to individual subjects. The potential indirect benefits include improved understanding of risk factors for pediatric psychiatric readmission, which may inform discharge planning, targeted follow-up care, and resource allocation for high-risk children.

### 7.3 Risk/Benefit Balance

The risks of this retrospective records analysis are minimal. The potential contribution to the scientific literature on pediatric psychiatric readmission — a clinically important and understudied outcome — justifies continuation of the research.

---

## Section 8 — Data Security and Confidentiality

**Storage:** Research data files are stored on [DESCRIPTION OF STORAGE — e.g., password-protected personal computer / encrypted institutional server / REDCap instance]. [IF CLOUD STORAGE: cloud storage is encrypted and access-controlled to authorized study personnel only.]

**Access:** Access to the dataset is restricted to the PI and co-investigators named on this protocol.

**Transmission:** Data are not transmitted to external parties. Aggregate statistical results and de-identified summary tables are shared with collaborators for purposes of manuscript and abstract preparation.

**Retention:** Data will be retained in accordance with institutional policy for [NUMBER] years following study completion or publication, whichever is later.

**Publication:** No individual-level data will be presented in any publication or presentation. All reported results are aggregate statistics; no cell sizes < [INSTITUTIONAL THRESHOLD, commonly 5 or 10] will be reported.

---

## Section 9 — Consent

**Consent waiver previously granted:** ☒ Yes ☐ No

Because this study uses existing records and meets the criteria for waiver of informed consent under 45 CFR 46.116(f) (minimal risk to subjects; waiver will not adversely affect the rights and welfare of subjects; research could not practicably be carried out without the waiver; where appropriate, subjects will be provided with pertinent information after participation), the IRB previously approved a waiver of informed consent. No changes to this determination are requested.

---

## Section 10 — Proposed Changes to Protocol

☒ No changes to the protocol are requested at this time.

The study is proceeding as described in the approved protocol. Ongoing activities consist entirely of statistical analysis of the previously obtained de-identified dataset and preparation of manuscripts and conference abstracts.

*If the IRB requires notification: Results are being prepared for presentation at the American Academy of Child and Adolescent Psychiatry (AACAP) 2026 Annual Meeting and for subsequent journal submission. These activities are consistent with the dissemination plan described in the original protocol.*

---

## Section 11 — Statement of Compliance

The study has been conducted in accordance with the approved protocol, applicable federal regulations (45 CFR 46), and institutional policy. No deviations, unanticipated problems, or adverse events have occurred. All personnel with direct access to research data have completed required human subjects research training ([CITIPROGRAM / INSTITUTIONAL EQUIVALENT]).

---

## Section 12 — Requested Action

The research team requests **annual renewal** of IRB approval for one additional year to allow completion of statistical analysis, manuscript preparation, and dissemination of results.

*Alternatively, given that data collection is closed and the dataset is de-identified, the research team requests that the IRB consider whether this study now qualifies for reclassification to **Exempt** status under 45 CFR 46.104(d)(4) (secondary research for which consent is not required), which would eliminate the requirement for future continuing reviews.*

---

## Attachments

- [ ] Current IRB-approved protocol (attached or on file)
- [ ] Current IRB-approved consent/waiver documentation (attached or on file)
- [ ] CITI training completion certificates for all study personnel
- [ ] Data use agreement (if applicable)
- [ ] AACAP 2025 abstract (for reference, documenting prior dissemination)
- [ ] Draft AACAP 2026 abstract (for reference, documenting current dissemination plans)

---

*Draft prepared for PI review. All bracketed fields require completion with institution-specific information before submission. Percentages, sample sizes, and statistical findings reflect the current state of analysis and should be verified against the final analytic outputs before submission.*
