import warnings; warnings.filterwarnings('ignore')
import pandas as pd, numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from pathlib import Path

ROOT = Path(__file__).parent  # portable: works wherever the repo lives
df = pd.read_csv(ROOT / 'data' / 'annotated_psychiatric_data_complete.csv')

# ---------- feature engineering ----------
df['readmitted'] = (df['Readmissions'].fillna(0) > 0).astype(int)
df['age'] = pd.to_numeric(df['Pt_Age_Visit'], errors='coerce')
df['male'] = (df['GenderCode'].astype(str).str.strip().str.lower()=='male').astype(int)
df['public_ins'] = df['Insurance'].astype(str).str.contains('AHCCCS', case=False, na=False).astype(int)
v = pd.to_datetime(df['VisitDate'], errors='coerce'); d = pd.to_datetime(df['DischDate'], errors='coerce')
df['los_days'] = (d - v).dt.days
df['restraint_n'] = pd.to_numeric(df['restraints'], errors='coerce').fillna(0)
df['restrained'] = (df['restraint_n'] > 0).astype(int)
df['ace'] = pd.to_numeric(df['ACEscore'], errors='coerce')
for f in ['Yellow flags (C-SRSS)','Orange flags (C-SSRS)','Red flags (C-SSRS)']:
    df[f] = pd.to_numeric(df[f], errors='coerce').fillna(0)
df['csrss_any'] = ((df['Yellow flags (C-SRSS)']+df['Orange flags (C-SSRS)']+df['Red flags (C-SSRS)'])>0).astype(int)

catcols = ['VisitDiags_DSM5Categories','NonSuicidialDiags_DSM5Categories','ChronicDiags_DSM5Categories']
allcat = df[catcols].fillna('').agg(';'.join, axis=1)
def has(cat): return allcat.str.contains(cat, case=False, regex=False).astype(int)
df['dep']      = has('Depressive Disorders')
df['anx']      = has('Anxiety Disorders')
df['adhd']     = has('ADHD')
df['asd']      = has('Autism Spectrum')
df['conduct']  = has('Conduct Disorder')
df['bipolar']  = has('Bipolar')
df['psychotic']= has('Psychotic')
df['trauma']   = has('Trauma and Stressor')
df['nssi']     = has('Non-Suicidal Self-Injury')
# distinct DSM-5 category count
df['n_dsm5'] = allcat.apply(lambda s: len({x.strip() for x in s.split(';') if x.strip()}))

# code-level flags
codecols = ['VisitDiags','NonSuicidialDiags','ChronicDiags']
allcodes = df[codecols].fillna('').agg(','.join, axis=1)
df['code_irritability'] = allcodes.str.contains('R45.4', regex=False).astype(int)   # irritability/anger
df['code_dmdd']         = allcodes.str.contains('F34.81', regex=False).astype(int)  # DMDD

N = len(df); print(f"N={N}, readmit={df['readmitted'].sum()} ({df['readmitted'].mean()*100:.1f}%)\n")

def logit_table(formula, data, title):
    print("="*70); print(title); print("-"*70)
    try:
        m = smf.logit(formula, data=data).fit(disp=0, maxiter=300)
        out = pd.DataFrame({'OR':np.exp(m.params),'CI_lo':np.exp(m.conf_int()[0]),
                            'CI_hi':np.exp(m.conf_int()[1]),'p':m.pvalues})
        out = out.drop('Intercept', errors='ignore')
        out['sig'] = np.where(out['p']<0.05,'*','')
        print(out.round(3).to_string()); print(f"(n={int(m.nobs)})\n")
        return out
    except Exception as e:
        print("FIT ERROR:", e, "\n"); return None

# ---------- 1. READMISSION multivariate (this year's sm.Logit, full N, no ACE to keep N) ----------
preds = ['age','male','public_ins','los_days','restrained','csrss_any','n_dsm5',
         'dep','psychotic','bipolar','conduct','anx','trauma','asd','adhd','nssi']
logit_table('readmitted ~ ' + ' + '.join(preds), df, "1. READMISSION — multivariate logistic (full cohort, ACE excluded)")

# ---------- 2. RESTRAINTS vs readmission: univariate, adjusted, rates ----------
print("="*70); print("2. RESTRAINT USE vs READMISSION"); print("-"*70)
ct = df.groupby('restrained')['readmitted'].agg(['mean','sum','count'])
ct['mean']=(ct['mean']*100).round(1); print(ct.rename(columns={'mean':'readmit_%','sum':'n_readmit','count':'n'}).to_string())
logit_table('readmitted ~ restrained', df, "2a. Restraints UNIVARIATE -> readmission")
logit_table('readmitted ~ restrained + age + male + public_ins + los_days + n_dsm5 + dep + psychotic', df,
            "2b. Restraints ADJUSTED (with severity/dx/LOS) -> readmission")
logit_table('readmitted ~ restraint_n', df, "2c. Restraint COUNT (continuous) UNIVARIATE -> readmission")

# ---------- 3. CODE vs CATEGORY: what is lost collapsing DMDD into Depressive Disorders ----------
print("="*70); print("3. CODE-LEVEL vs CATEGORY-LEVEL (information loss on collapse)"); print("-"*70)
for name,colmask in [('Irritability/anger code R45.4','code_irritability'),
                     ('DMDD code F34.81','code_dmdd'),
                     ('DEPRESSIVE DISORDERS category (collapsed)','dep')]:
    sub=df[df[colmask]==1]; rate=sub['readmitted'].mean()*100
    print(f"{name:42s} n={len(sub):4d}  readmit={rate:4.1f}%")
print()
logit_table('readmitted ~ code_irritability', df, "3a. Irritability code R45.4 UNIVARIATE")
logit_table('readmitted ~ code_dmdd', df, "3b. DMDD code F34.81 UNIVARIATE")
logit_table('readmitted ~ dep', df, "3c. Collapsed Depressive Disorders category UNIVARIATE")
# DMDD signal hidden inside the depression category?
dep=df[df['dep']==1]
print(f"Within DEPRESSIVE category (n={len(dep)}): DMDD+ readmit={dep[dep['code_dmdd']==1]['readmitted'].mean()*100:.1f}% (n={int(dep['code_dmdd'].sum())}) "
      f"vs DMDD- readmit={dep[dep['code_dmdd']==0]['readmitted'].mean()*100:.1f}% (n={int((dep['code_dmdd']==0).sum())})\n")

# ---------- 4. LENGTH OF STAY predictors (OLS) ----------
print("="*70); print("4. LENGTH OF STAY predictors (OLS, days)"); print("-"*70)
mlos = smf.ols('los_days ~ age + male + public_ins + restrained + csrss_any + n_dsm5 + dep + psychotic + bipolar + conduct + asd + nssi', data=df).fit()
los_out = pd.DataFrame({'beta':mlos.params,'p':mlos.pvalues}).drop('Intercept',errors='ignore')
los_out['sig']=np.where(los_out['p']<0.05,'*',''); print(los_out.round(3).to_string()); print(f"R2={mlos.rsquared:.3f} (n={int(mlos.nobs)})\n")
# ACE complete-case add-on
acc = df[df['ace'].notna()]
mlos2 = smf.ols('los_days ~ ace + age + male + public_ins + restrained + n_dsm5', data=acc).fit()
print("LOS ~ ACE (complete-case subset):")
print(pd.DataFrame({'beta':mlos2.params,'p':mlos2.pvalues}).drop('Intercept',errors='ignore').round(3).to_string()); print(f"(n={int(mlos2.nobs)})\n")

# ---------- 5. RESTRAINT-USE predictors (logit) ----------
print("="*70); print("5. RESTRAINT-USE predictors (logistic)"); print("-"*70)
logit_table('restrained ~ age + male + public_ins + los_days + csrss_any + n_dsm5 + dep + psychotic + bipolar + conduct + asd + adhd', df,
            "Predictors of any physical restraint")

# ---------- 6. ACE -> readmission (complete-case, comparable to last year p=0.1231) ----------
print("="*70); print("6. ACE -> READMISSION (complete-case, vs last year p=0.1231)"); print("-"*70)
logit_table('readmitted ~ ace', acc, "6a. ACE univariate")
logit_table('readmitted ~ ace + age + male + public_ins + los_days + n_dsm5', acc, "6b. ACE adjusted")
