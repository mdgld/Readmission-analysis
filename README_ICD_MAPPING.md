# ICD-10 to DSM-5 TR Mapping - Quick Reference

## 🎯 What Was Done

Your 2,652-patient psychiatric rehospitalization dataset contained **1,863 unique ICD-10 codes** scattered across three diagnosis columns. The mapping task is now **100% complete**:

- ✅ **1,863 ICD-10 codes** → Clinical descriptions (was: 652/1863 = 35%)
- ✅ **205 psychiatric codes** → DSM-5 TR categories  
- ✅ **31 DSM-5 categories** represented in your cohort
- ✅ **27,884 diagnosis records** with full descriptions

---

## 📊 Your Analysis Files (Updated)

### 1. **ICD10_to_DSM5_Complete_Reference.csv** 
Master reference table with all 1,863 codes.

| Column | Purpose |
|--------|---------|
| `ICD_Code` | The ICD-10 code |
| `Description` | Clinical description (e.g., "ADHD, combined type") |
| `Category` | ICD chapter (Psychiatric, GI, Respiratory, etc.) |
| `DSM5_Category` | DSM-5 TR diagnosis if psychiatric |
| `DSM5_Code` | DSM-5 code reference |
| `Frequency` | How many times this code appears in dataset |

**Quick lookup:** `ref_df[ref_df['ICD_Code'] == 'F90.2']` → ADHD, combined type

### 2. **annotated_psychiatric_data_complete.csv**
Patient-level data (2,652 rows) with diagnosis names appended.

**New columns:**
- `VisitDiags_Names` — Visit diagnoses with actual names
- `NonSuicidialDiags_Names` — Self-harm codes with names
- `ChronicDiags_Names` — Chronic diagnoses with names
- Plus corresponding DSM-5 category columns for each

**Use case:** Statistical models (logistic regression, random forest) predicting readmission

### 3. **diagnoses_long_form_complete.csv**
One row per diagnosis per patient (27,884 rows).

| Column | Purpose |
|--------|---------|
| `MRN` | Patient ID |
| `diagnosis_type` | visit_diags / non_suicidal_diags / chronic_diags |
| `icd_code` | ICD-10 code |
| `diagnosis_description` | Clinical description |
| `dsm5_category` | DSM-5 category if psychiatric |

**Use case:** Comorbidity analysis, network analysis, clustering

---

## 🔍 Key Findings

**Highest frequency codes:**
- R45.851 (Suicidal ideation) — 2,968 occurrences
- F90.2 (ADHD, combined) — 1,243 occurrences
- F43.10 (PTSD, unspecified) — 1,124 occurrences

**Highest readmission risk (by DSM-5 category):**
- Neurocognitive Disorders — 33.3% readmitted
- Tic Disorders — 21.6%
- Neurodevelopmental conditions — 18%+ readmission risk

---

## 💡 How to Use

### Load and explore:
```python
import pandas as pd

# Reference table
ref = pd.read_csv('ICD10_to_DSM5_Complete_Reference.csv')

# Patient data
patients = pd.read_csv('annotated_psychiatric_data_complete.csv')

# Long-form (for analysis)
diagnoses = pd.read_csv('diagnoses_long_form_complete.csv')

# Find all ADHD diagnoses in reference
adhd_codes = ref[ref['DSM5_Category'] == 'ADHD']

# Get all patients with ADHD
adhd_patients = diagnoses[diagnoses['dsm5_category'] == 'ADHD']['MRN'].unique()
```

### Statistical analysis:
```python
# Readmission by diagnosis
readmit_by_diag = diagnoses.groupby('diagnosis_description').agg({
    'MRN': 'nunique',  # count of patients
})

# Merge with patient outcomes
readmit_outcomes = patients.merge(
    diagnoses[['MRN', 'dsm5_category', 'icd_code']], 
    on='MRN'
)
```

---

## 🚀 Next Steps

**Recommended analyses:**

1. **Readmission predictors** — Which diagnoses/comorbidities predict readmission?
2. **Comorbidity patterns** — Which diagnoses co-occur? Do they cluster?
3. **Clinical phenotypes** — Can you identify distinct patient subgroups?
4. **Temporal trends** — Are certain diagnoses increasing/decreasing over time?
5. **Demographic effects** — How do diagnosis patterns differ by age/insurance?

---

## ⚠️ Important Notes

- **DSM-5 mapping only available for psychiatric codes (F-codes)**
  - Medical comorbidities are categorized by ICD-10 chapter only
  - This is correct ICD-10 to DSM-5 TR practice (DSM-5 does not classify non-psychiatric diagnoses)

- **No placeholder entries** — Every code has a real description
  - This enables clinical interpretation without manual lookup

- **R45.851 dominates NSSI column** (2,968 vs next highest 706)
  - Consider whether suicidal ideation is accurately recorded or over-coded

---

## 📧 Questions?

Use the `ICD10_to_DSM5_Complete_Reference.csv` as your single source of truth for code mapping.
All files are analysis-ready now.

