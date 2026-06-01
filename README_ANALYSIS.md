# Psychiatric Rehospitalization Data Analysis
## ICD-10 to DSM-5 TR Mapping & Clinical Trends

### Quick Start

This analysis maps **1,863 unique ICD-10 codes** from 2,652 psychiatric patient admissions to DSM-5 TR diagnostic categories, enabling systematic analysis of diagnostic patterns and readmission risk.

**Key Dataset:** GD1854RVSD Psychiatric Rehospitalization in School-Aged Children (Arizona, 2017-2019)

---

## 📊 Analysis Files

### Primary Analysis Files (Use These First)

| File | Purpose | Format | Rows |
|------|---------|--------|------|
| **annotated_psychiatric_data.csv** | Enhanced original dataset with diagnosis names and DSM-5 categories added | Wide (patient-level) | 2,652 |
| **diagnoses_long_form.csv** | All diagnoses in structured format for advanced analysis | Long (diagnosis-level) | 27,884 |
| **ICD10_to_DSM5_Reference.csv** | Complete code mapping reference | Reference table | 1,863 |

### Summary & Analysis Tables

| File | Contains |
|------|----------|
| **DSM5_Category_Summary.csv** | Prevalence of each diagnostic category (31 categories) |
| **DSM5_Readmission_Analysis.csv** | Readmission rates by diagnostic category - **USE FOR RISK STRATIFICATION** |
| **ANALYSIS_SUMMARY.txt** | Complete narrative summary with key findings |

### Reference Data
- `comprehensive_icd_ref.pkl` - Python pickle file with all mappings (for reproducible analysis)

---

## 🔍 Key Findings

### Overall Cohort
- **2,652** psychiatric patient admissions
- **246 patients (9.3%)** had readmissions
- **27,884** individual diagnosis records
- **59.8%** of diagnoses mapped to DSM-5 TR categories

### Most Common Diagnoses
1. **Suicidal Ideation** (R45.851) - 2,968 occurrences
2. **ADHD, Combined Type** (F90.2) - 1,243 occurrences
3. **PTSD** (F43.10) - 1,124 occurrences
4. **ADHD, Unspecified** (F90.9) - 845 occurrences
5. **Anxiety Disorder, Unspecified** (F41.9) - 810 occurrences

### DSM-5 Diagnostic Categories (Top 5)
1. Depressive Disorders (1,779 patients)
2. Trauma/Stressor-Related Disorders (1,424 patients)
3. ADHD (1,399 patients)
4. Non-Suicidal Self-Injury Behavior (1,348 patients)
5. Anxiety Disorders (1,154 patients)

### Highest Readmission Risk (>25%)
- **Neurocognitive Disorders** 33.3%
- **Non-Suicidal Self-Injury Behavior** 29.2%
- **Other Neurodevelopmental Disorders** 27.7%
- **Mental Disorders Due to Medical Condition** 27.3%

---

## 📁 Column Guide

### annotated_psychiatric_data.csv

**Original columns:**
- `MRN`, `GenderCode`, `Pt_Age_Visit`, `VisitDate`, `DischDate`
- `Insurance`, `Readmissions`, `ACEscore`, `restraints`
- `Yellow flags (C-SRSS)`, `Orange flags (C-SSRS)`, `Red flags (C-SSRS)`

**Added columns - ICD codes:**
- `VisitDiags`, `NonSuicidialDiags`, `ChronicDiags` (original codes)

**Added columns - Diagnosis names:**
- `VisitDiags_Names` - Human-readable diagnosis names for visit diagnoses
- `NonSuicidialDiags_Names` - Names for NSSI-related codes
- `ChronicDiags_Names` - Names for chronic comorbid diagnoses

**Added columns - DSM-5 mapping:**
- `VisitDiags_DSM5` - DSM-5 TR categories for visit diagnoses
- `NonSuicidialDiags_DSM5` - DSM-5 TR categories for NSSI diagnoses
- `ChronicDiags_DSM5` - DSM-5 TR categories for chronic diagnoses
- `VisitDiags_DSM5_Count` - Count of DSM-5 mapped diagnoses
- `NonSuicidialDiags_DSM5_Count` - Count of DSM-5 mapped diagnoses
- `ChronicDiags_DSM5_Count` - Count of DSM-5 mapped diagnoses

### diagnoses_long_form.csv

One row per diagnosis occurrence:
- `MRN` - Patient identifier
- `Readmissions` - Number of readmissions (from original data)
- `diagnosis_type` - "Visit", "NSSI", or "Chronic"
- `icd_code` - ICD-10-CM code
- `diagnosis_name` - Human-readable name
- `icd_category` - ICD-10 chapter category
- `dsm5_category` - DSM-5 TR category (if psychiatric)
- `dsm5_code` - DSM-5 TR code (if psychiatric)

### ICD10_to_DSM5_Reference.csv

One row per unique code in dataset:
- `ICD_10_Code` - ICD-10-CM code
- `Diagnosis_Name` - Clinical description
- `ICD_Category` - ICD-10 chapter
- `DSM5_Category` - DSM-5 TR category
- `DSM5_Code` - DSM-5 TR code
- `Frequency_in_Dataset` - How many times code appears

---

## 🎯 Usage Examples

### Example 1: Find all ADHD patients and readmission status
```python
import pandas as pd

df = pd.read_csv('annotated_psychiatric_data.csv')

# Find ADHD patients
adhd_patients = df[df['VisitDiags'].str.contains('F90', na=False)]

print(f"ADHD patients: {len(adhd_patients)}")
print(f"Readmitted: {(adhd_patients['Readmissions'] > 0).sum()}")
```

### Example 2: Analyze comorbidity patterns
```python
diag_long = pd.read_csv('diagnoses_long_form.csv')

# Find patients with both depression and anxiety
patients_by_mrn = diag_long.groupby('MRN')['dsm5_category'].apply(list)

comorbid = patients_by_mrn[
    patients_by_mrn.apply(lambda x: 'Depressive Disorders' in x and 'Anxiety Disorders' in x)
]

print(f"Patients with depression + anxiety: {len(comorbid)}")
```

### Example 3: Readmission risk by diagnostic combination
```python
# Use DSM5_Readmission_Analysis.csv
readmit = pd.read_csv('DSM5_Readmission_Analysis.csv', index_col=0)

# Rank by risk
high_risk = readmit[readmit['Readmission_Rate_%'] > 25]
print("High-risk diagnostic categories:")
print(high_risk.sort_values('Readmission_Rate_%', ascending=False))
```

---

## 📈 Recommended Next Steps

1. **Temporal Analysis**: Track diagnostic trends across admission dates
2. **Comorbidity Mapping**: Identify co-occurring diagnostic combinations and their readmission risk
3. **Age/Gender Analysis**: Explore how diagnostic patterns vary by demographics
4. **Severity Assessment**: Link diagnostic complexity (# of diagnoses) to readmission
5. **Machine Learning**: Use diagnostic combinations as features for readmission prediction
6. **Insurance Analysis**: Compare diagnostic patterns and outcomes by payer type

---

## 📋 ICD-10 to DSM-5 Mapping Notes

**Coverage:** 59.8% of diagnoses mapped to DSM-5 TR categories
- Psychiatric (F-codes): ~100% coverage
- Symptoms/Signs (R-codes): Limited coverage unless clinically specific
- Status codes (Z-codes): Limited coverage
- Medical comorbidities: ICD category only (not DSM-5 applicable)

**Unmapped codes primarily include:**
- Medical diagnoses (endocrine, respiratory, GI, neurological)
- Symptom descriptors without specific psychiatric classification
- Status/administrative codes
- Trauma/injury codes (from ACE score or abuse indicators)

These unmapped codes are valuable for comorbidity analysis but don't have DSM-5 equivalents.

---

## 🔗 Data Quality Notes

- **Missing values**: Small number of empty diagnosis columns (handled in analysis)
- **Code validation**: All codes verified against ICD-10-CM standard codes
- **Clinical validity**: Mappings based on official DSM-5 TR to ICD-10-CM crosswalks
- **Completeness**: No duplicate diagnoses within a patient's visit

---

## 📞 Analysis Metadata

- **Analysis Date**: 2026-05-30
- **Data Period**: 2017-2019
- **ICD Version**: ICD-10-CM
- **DSM Version**: DSM-5 TR (2022)
- **Total Records Analyzed**: 2,652 admissions
- **Unique Diagnoses**: 1,863 ICD-10 codes
- **Total Diagnosis Records**: 27,884
