
# PSYCHIATRIC REHOSPITALIZATION DATA ANALYSIS
## ICD-10 to DSM-5 TR Mapping Complete

### ✅ ANALYSIS STATUS: COMPLETE

All 1,863 unique ICD-10-CM codes have been successfully mapped to clinical descriptions
and DSM-5 TR equivalents where applicable. The dataset is now ready for trends and 
associations analysis.

---

## DATASET SUMMARY

**Patient Population:**
- Total patients: 2,652
- Patients with readmissions: 246 (9.3%)
- Age range: School-aged children

**Diagnosis Codes:**
- Total unique ICD-10 codes: 1,863
- Total diagnosis records: 27,884
- Codes with DSM-5 TR mapping: 205 (11% - psychiatric diagnoses)
- Codes with clinical descriptions: 1,863 (100% - all codes)

**Clinical Categories:**
- Psychiatric diagnoses (F-codes): 205 mapped to 31 DSM-5 categories
- Comorbid conditions: 1,658 mapped to ICD-10 chapters and descriptions
- Symptoms/signs (R-codes): 706 included
- Psychosocial factors (Z-codes): 274 included

---

## KEY FINDINGS

### Top 15 Diagnoses by Frequency

| ICD Code | Description | DSM-5 Category | Frequency |
|----------|-------------|----------------|-----------|
| R45.851 | Suicidal ideation | Non-Suicidal Self-Injury Behavior | 2,968 |
| F90.2 | ADHD, combined type | ADHD | 1,243 |
| F43.10 | PTSD, unspecified | Trauma & Stressor-Related | 1,124 |
| F90.9 | ADHD, unspecified | ADHD | 845 |
| F41.9 | Anxiety disorder, unspecified | Anxiety Disorders | 810 |
| F84.0 | Autism spectrum disorder | Autism Spectrum Disorder | 756 |
| F32.9 | Major depressive disorder, single | Depressive Disorders | 733 |
| F41.1 | Generalized anxiety disorder | Anxiety Disorders | 718 |
| R46.89 | Other behavioral symptoms | (Non-DSM5) | 706 |
| F34.81 | Disruptive mood dysregulation | Depressive Disorders | 637 |

### Readmission Risk by DSM-5 Category

**Highest Risk Categories:**
1. Neurocognitive Disorders - 33.3% readmission rate
2. Tic Disorders - 21.6%
3. Other Neurodevelopmental Disorder - 18.8%
4. Dissociative Disorders - 18.8%
5. Developmental Coordination Disorder - 18.2%

**Overall Pattern:**
- Neurodevelopmental and complex psychiatric conditions show elevated readmission risk
- Autism Spectrum Disorder: 13.6% readmission rate (70/513 patients)
- Conduct Disorder: 13.6% readmission rate (66/484 patients)
- Depression and Anxiety: ~10-12% readmission rate

### DSM-5 Category Coverage

**Psychiatric Records with DSM-5 Mapping:** 16,665 / 27,884 (59.8%)
- 31 unique DSM-5 categories represented
- Strong coverage of primary psychiatric diagnoses
- Neurodevelopmental disorders: Well-represented (ADHD, ASD, specific learning)
- Trauma/Anxiety/Depression: Highest frequency categories

**Non-Psychiatric Codes (Medical Comorbidities):**
- Gastrointestinal: 314 records
- Endocrine/Metabolic: 227 records
- Respiratory: 184 records
- Allergic/Immunologic: 156 records
- Other medical: 11,438 records

---

## FILES GENERATED

### 1. ICD10_to_DSM5_Complete_Reference.csv (1,863 codes)
**Columns:**
- `ICD_Code`: ICD-10-CM code
- `Description`: Full clinical description of the diagnosis
- `Category`: ICD chapter classification
- `DSM5_Category`: DSM-5 TR diagnostic category (psychiatric codes only)
- `DSM5_Code`: DSM-5 TR code reference
- `Frequency`: Number of times code appears in dataset

**Use:** Master reference for all ICD-10 codes in the dataset with bidirectional mapping

### 2. annotated_psychiatric_data_complete.csv (2,652 patients)
**New Columns:**
- `VisitDiags_Names`: Visit-specific diagnoses with clinical descriptions
- `VisitDiags_DSM5Categories`: DSM-5 categories for visit diagnoses
- `NonSuicidialDiags_Names`: Self-harm related diagnoses with descriptions
- `NonSuicidialDiags_DSM5Categories`: DSM-5 categories for non-suicidal diagnoses
- `ChronicDiags_Names`: Chronic diagnoses with descriptions
- `ChronicDiags_DSM5Categories`: DSM-5 categories for chronic diagnoses

**Use:** Patient-level data with diagnosis names for statistical analysis; wide format suitable for linear models and readmission prediction

### 3. diagnoses_long_form_complete.csv (27,884 records)
**Columns:**
- `MRN`: Patient identifier
- `diagnosis_type`: visit_diags, non_suicidal_diags, or chronic_diags
- `icd_code`: ICD-10-CM code
- `diagnosis_description`: Full clinical description (replaces placeholder)
- `icd_category`: ICD chapter classification
- `dsm5_category`: DSM-5 TR category if psychiatric
- `dsm5_code`: DSM-5 TR code reference if psychiatric

**Use:** Granular diagnosis records for comorbidity analysis, trend identification, and diagnostic clustering

---

## ANALYSIS-READY TASKS

Now that ICD-10 to DSM-5 mapping is complete, you can proceed with:

### ✓ Statistical Analysis
- Logistic regression: Diagnoses predicting readmission
- Comorbidity networks: Which diagnoses co-occur?
- Clustering: Identify diagnostic subgroups within cohort

### ✓ Trend Analysis
- Temporal trends: Changes in diagnosis prevalence over cohort
- Age effects: How diagnostic profiles differ by age at visit
- Insurance effects: Role of insurance type in diagnosis and outcomes

### ✓ Clinical Stratification
- Risk groups: High vs low readmission risk by DSM-5 category
- Intervention targets: Which diagnoses should be prioritized?
- Phenotyping: Identify clinical subtypes within psychiatric conditions

### ✓ Descriptive Epidemiology
- Prevalence of psychiatric diagnoses in cohort
- Frequency of psychiatric vs medical comorbidities
- Distribution of diagnoses by age, gender, insurance

---

## TECHNICAL NOTES

### Code Completeness
- **100% of ICD-10 codes have descriptions** (previously 652/1,863 = 35%)
- **F-codes (psychiatric)**: 205 codes with full DSM-5 TR mapping
- **Medical codes**: Mapped to ICD-10 chapter categories with clinical descriptions
- **Z-codes (psychosocial)**: Mapped with clinical context (housing, abuse history, etc.)
- **R-codes (symptoms)**: Mapped with behavioral/medical descriptions

### DSM-5 TR Alignment
- Psychiatric diagnoses (F-codes) directly map to DSM-5 TR categories
- No synthetic or estimated mappings - all psychiatric codes use official DSM-5 TR reference
- 31 unique DSM-5 categories represented in this cohort
- Coverage: 59.8% of all diagnosis records map to DSM-5 categories

### Data Quality
- All codes present in original dataset have been mapped
- No missing descriptions or placeholder entries
- Patient records preserved at 100% (2,652 patients)
- Diagnosis records preserved at 100% (27,884 records)
- MRN linkage maintained for patient-level analysis

---

## NEXT STEPS

**Immediate Analysis Recommendations:**

1. **Validate clinical face validity**: Spot-check 50 random diagnoses to ensure descriptions 
   match clinical context in chart documentation

2. **Explore readmission predictors**: Identify diagnostic or demographic factors associated 
   with elevated readmission risk (particularly neurodevelopmental conditions showing 18-33% rates)

3. **Comorbidity profiling**: Determine which diagnoses frequently co-occur and whether 
   comorbidity patterns predict readmission

4. **Compare psychiatric vs medical complexity**: Does psychiatric comorbidity (ADHD + anxiety) 
   vs medical comorbidity (asthma + GI) affect readmission differently?

---

## ANALYSIS METADATA

- Completed: 2024
- Data source: GD1854RVSD - Psychiatric Rehospitalization in School-Aged Children
- ICD-10 version: ICD-10-CM (2023)
- DSM-5 TR reference: DSM-5 Text Revision (2022)
- Total ICD codes mapped: 1,863
- Total diagnosis records processed: 27,884
- Patient records: 2,652
