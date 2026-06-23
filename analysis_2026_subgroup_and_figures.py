"""
2026 reconciliation analysis — within-category subgroup breakdown + figures.

Adds to analysis_2026_reconciliation.py:
  (1) Subgroup analysis of DSM-5/CCS (regex) categories to pick out the
      individual ICD codes that carry the readmission signal (e.g., DMDD
      within Depressive Disorders).
  (2) Publication-quality visualizations of the updated analyses
      (rate correction, corrected multivariable forest plot, code-vs-category
      information loss, LOS predictors, restraint-use predictors, predictive ceiling).

Run:  .venv/bin/python analysis_2026_subgroup_and_figures.py
Outputs: figures/Fig_Recon_*.png  and  figures/Recon_*.csv
"""
import warnings; warnings.filterwarnings('ignore')
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.api as sm, statsmodels.formula.api as smf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).parent  # portable: works wherever the repo lives
FIG  = ROOT / 'figures'
BLUE, ORANGE, GREEN, GRAY = '#2166ac', '#d6604d', '#1a9850', '#999999'
plt.rcParams.update({'figure.dpi':130, 'savefig.dpi':200, 'font.size':11, 'axes.titlepad':12,
                     'axes.spines.top':False, 'axes.spines.right':False})

# ---------------- feature engineering (mirrors reconciliation script) ----------------
df = pd.read_csv(ROOT / 'data' / 'annotated_psychiatric_data_complete.csv')
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
def hascat(c): return allcat.str.contains(c, case=False, regex=False).astype(int)
for nm,cat in [('dep','Depressive Disorders'),('anx','Anxiety Disorders'),('adhd','ADHD'),
               ('asd','Autism Spectrum'),('conduct','Conduct Disorder'),('bipolar','Bipolar'),
               ('psychotic','Psychotic'),('trauma','Trauma and Stressor'),('nssi','Non-Suicidal Self-Injury')]:
    df[nm] = hascat(cat)
df['n_dsm5'] = allcat.apply(lambda s: len({x.strip() for x in s.split(';') if x.strip()}))

codecols = ['VisitDiags','NonSuicidialDiags','ChronicDiags']
allcodes = df[codecols].fillna('').agg(','.join, axis=1)
def hascode(pat, exact=True):
    toks = allcodes.str.split(',')
    if exact:
        return toks.apply(lambda L: int(any(t.strip()==pat for t in L)))
    return allcodes.str.contains(pat.replace('.','\\.'), regex=True).astype(int)

N = len(df); base = df['readmitted'].mean()
print(f"N={N}  readmit={df['readmitted'].sum()} ({base*100:.1f}%)")

def uni_or(mask):
    """univariate OR for a 0/1 mask -> (n, readmit%, OR, lo, hi, p). Guards tiny/separated subgroups."""
    s = pd.Series(mask).astype(int)
    sub = df.loc[s==1,'readmitted']
    events = int(sub.sum()) if len(sub) else 0
    # underpowered or perfect separation -> report n/rate only, no OR
    if s.sum() < 20 or events < 5 or events == len(sub):
        return int(s.sum()), (sub.mean()*100 if len(sub) else np.nan), np.nan, np.nan, np.nan, np.nan
    m = smf.logit('readmitted ~ x', data=df.assign(x=s)).fit(disp=0)
    sub = df.loc[s==1,'readmitted']
    return int(s.sum()), sub.mean()*100, np.exp(m.params['x']), np.exp(m.conf_int().loc['x',0]), np.exp(m.conf_int().loc['x',1]), m.pvalues['x']

# ============================================================
# 1. WITHIN-CATEGORY SUBGROUP ANALYSIS (pick out driving codes)
# ============================================================
# (category, label, code pattern, exact?)
SUBGROUPS = [
 ('Depressive Disorders','DMDD (F34.81)','F34.81',True),
 ('Depressive Disorders','MDD single (F32.x)','F32',False),
 ('Depressive Disorders','MDD recurrent (F33.x)','F33',False),
 ('Depressive Disorders','Unspecified mood (F39)','F39',True),
 ('Anxiety Disorders','GAD (F41.1)','F41.1',True),
 ('Anxiety Disorders','Anxiety, unspecified (F41.9)','F41.9',True),
 ('Trauma & Stressor','PTSD (F43.10)','F43.10',True),
 ('Trauma & Stressor','Adjustment (F43.2x)','F43.2',False),
 ('Neurodevelopmental','ADHD combined (F90.2)','F90.2',True),
 ('Neurodevelopmental','Autism (F84.0)','F84.0',True),
 ('Conduct / Disruptive','Conduct disorder (F91.x)','F91',False),
 ('Behavioral symptom (R)','Irritability/anger (R45.4)','R45.4',True),
 ('Behavioral symptom (R)','Suicidal ideation (R45.851)','R45.851',True),
]
rows = []
for cat,label,pat,exact in SUBGROUPS:
    n, rate, orr, lo, hi, p = uni_or(hascode(pat, exact))
    rows.append(dict(Category=cat, Subgroup=label, n=n, ReadmitPct=round(rate,1),
                     OR=round(orr,2) if orr==orr else np.nan,
                     CI=f"{lo:.2f}-{hi:.2f}" if lo==lo else "—",
                     p=round(p,3) if p==p else np.nan))
subg = pd.DataFrame(rows)
subg.to_csv(FIG / 'Recon_subgroup_codes.csv', index=False)
print("\n--- within-category subgroup codes ---"); print(subg.to_string(index=False))

# DMDD vs non-DMDD within depression
dep = df[df['dep']==1]; dmdd = df['dep'].eq(1) & hascode('F34.81',True).eq(1)
within = {'DMDD+':(df[dmdd]['readmitted'].mean()*100, int(dmdd.sum())),
          'DMDD-':(dep[hascode('F34.81',True).loc[dep.index].eq(0)]['readmitted'].mean()*100,
                   int((dep.shape[0]-dmdd.sum())))}

# ============================================================
# 2. CORRECTED MULTIVARIABLE LOGISTIC REGRESSION (readmission)
# ============================================================
preds = ['age','male','public_ins','los_days','restrained','csrss_any','n_dsm5',
         'dep','psychotic','bipolar','conduct','anx','trauma','asd','adhd','nssi']
m = smf.logit('readmitted ~ '+' + '.join(preds), data=df).fit(disp=0, maxiter=300)
LAB = {'age':'Age (per yr)','male':'Male sex','public_ins':'Public insurance','los_days':'Length of stay (per day)',
       'restrained':'Physical restraint use','csrss_any':'Any C-SSRS flag','n_dsm5':'Diagnostic complexity (per category)',
       'dep':'Depressive disorders','psychotic':'Psychotic disorders','bipolar':'Bipolar disorders','conduct':'Conduct disorder',
       'anx':'Anxiety disorders','trauma':'Trauma/PTSD','asd':'Autism spectrum','adhd':'ADHD','nssi':'NSSI behavior'}
fr = pd.DataFrame({'feature':m.params.index,'OR':np.exp(m.params),'lo':np.exp(m.conf_int()[0]),
                   'hi':np.exp(m.conf_int()[1]),'p':m.pvalues}).query("feature!='Intercept'")
fr['label'] = fr['feature'].map(LAB); fr['sig'] = fr['p']<0.05
fr = fr.sort_values('OR')
fr.to_csv(FIG / 'Recon_readmission_logit.csv', index=False)

# ============================================================
# 3. LOS predictors (OLS) & 4. RESTRAINT-USE predictors (logit)
# ============================================================
mlos = smf.ols('los_days ~ age + male + public_ins + restrained + csrss_any + n_dsm5 + dep + psychotic + bipolar + conduct + asd + nssi', data=df).fit()
los = pd.DataFrame({'feature':mlos.params.index,'beta':mlos.params,'p':mlos.pvalues}).query("feature!='Intercept'")
los['label']=los['feature'].map({**LAB}); los['sig']=los['p']<0.05; los=los.sort_values('beta')
los.to_csv(FIG / 'Recon_los_predictors.csv', index=False)

mr = smf.logit('restrained ~ age + male + public_ins + los_days + csrss_any + n_dsm5 + dep + psychotic + bipolar + conduct + asd + adhd', data=df).fit(disp=0, maxiter=300)
rst = pd.DataFrame({'feature':mr.params.index,'OR':np.exp(mr.params),'lo':np.exp(mr.conf_int()[0]),
                    'hi':np.exp(mr.conf_int()[1]),'p':mr.pvalues}).query("feature!='Intercept'")
rst['label']=rst['feature'].map(LAB); rst['sig']=rst['p']<0.05; rst=rst.sort_values('OR')
rst.to_csv(FIG / 'Recon_restraint_predictors.csv', index=False)

# optimism table (from advanced pipeline)
opt = pd.read_csv(FIG / 'AdvStats_optimism_validation.csv')

# ============================================================
# FIGURES
# ============================================================
def forest(ax, d, title, xlabel='Odds ratio (95% CI)', logx=True):
    y = range(len(d)); cols = [ORANGE if s else GRAY for s in d['sig']]
    ax.scatter(d['OR'], y, color=cols, s=55, zorder=3)
    ax.hlines(list(y), d['lo'], d['hi'], color=cols, lw=2, alpha=.7)
    ax.axvline(1, color='k', ls='--', lw=1)
    ax.set_yticks(list(y)); ax.set_yticklabels(d['label'], fontsize=9.5)
    if logx: ax.set_xscale('log'); ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v,_:f'{v:.2g}'))
    ax.set_xlabel(xlabel); ax.set_title(title, fontweight='bold', fontsize=12)
    for i,(_,r) in enumerate(d.iterrows()):
        if r['sig']: ax.text(r['hi']*1.04, i, f"p={r['p']:.3f}", va='center', fontsize=8, color=ORANGE)

# Fig 1 — readmission rate correction (windows + events vs patients)
fig, ax = plt.subplots(1,2, figsize=(11,4.2))
ax[0].bar(['7-day','30-day','90-day'], [1.5,4.8,9.3], color=[GRAY,GRAY,BLUE])
for i,val in enumerate([1.5,4.8,9.3]): ax[0].text(i, val+0.2, f'{val}%', ha='center', va='bottom', fontweight='bold')
ax[0].set_ylim(0,11); ax[0].set_ylabel('Patients readmitted (%)'); ax[0].set_title('Readmission by window\n(source export, patient-level)', fontweight='bold', fontsize=11)
ax[1].bar(['Patient-level\n(correct)','Event-level\n(prior 10.4%)'], [9.3,10.4], color=[BLUE,ORANGE])
ax[1].text(0,9.5,'9.3%\n246–247 patients',ha='center',fontweight='bold',fontsize=9)
ax[1].text(1,10.6,'10.4%\n275 events',ha='center',fontweight='bold',fontsize=9)
ax[1].set_ylim(0,12); ax[1].set_ylabel('Rate (%)'); ax[1].set_title('90-day rate: numerator definition', fontweight='bold', fontsize=11)
plt.tight_layout(); plt.savefig(FIG / 'Fig_Recon_1_rate_correction.png'); plt.close()

# Fig 2 — corrected multivariable forest plot
fig, ax = plt.subplots(figsize=(8.5,7))
forest(ax, fr, 'Corrected multivariable logistic regression:\nindependent predictors of 90-day readmission')
plt.tight_layout(); plt.savefig(FIG / 'Fig_Recon_2_readmission_forest.png'); plt.close()

# Fig 3 — code vs category information loss
fig, ax = plt.subplots(1,2, figsize=(11,4.4))
labs=['Irritability\nR45.4','DMDD\nF34.81','Depressive\nDisorders\n(collapsed)']
vals=[19.4,14.2,10.7]; ns=[31,438,1779]
b=ax[0].bar(labs, vals, color=[ORANGE,'#f4a582',BLUE])
ax[0].axhline(base*100, color='k', ls='--', lw=1, label=f'cohort {base*100:.1f}%')
for i,(val,n) in enumerate(zip(vals,ns)): ax[0].text(i, val+0.3, f'{val}%\nn={n}', ha='center', va='bottom', fontsize=9, fontweight='bold')
ax[0].set_ylim(0, max(vals)*1.25); ax[0].set_ylabel('Readmission (%)'); ax[0].legend(loc='upper right'); ax[0].set_title('Signal diluted when collapsing to category', fontweight='bold', fontsize=11)
wvals=[within['DMDD+'][0], within['DMDD-'][0]]
ax[1].bar(['DMDD +','DMDD −'], wvals, color=['#f4a582',BLUE])
ax[1].axhline(base*100, color='k', ls='--', lw=1)
for i,k in enumerate(['DMDD+','DMDD-']): ax[1].text(i, within[k][0]+0.25, f"{within[k][0]:.1f}%\nn={within[k][1]}", ha='center', va='bottom', fontsize=9, fontweight='bold')
ax[1].set_ylim(0, max(wvals)*1.30); ax[1].set_ylabel('Readmission (%)'); ax[1].set_title('Within depressive disorders:\nDMDD (irritability) vs non-DMDD', fontweight='bold', fontsize=11)
plt.tight_layout(); plt.savefig(FIG / 'Fig_Recon_3_code_vs_category.png'); plt.close()

# Fig 4 — within-category subgroup readmission rates
sg = subg.dropna(subset=['ReadmitPct']).copy().sort_values('ReadmitPct')
fig, ax = plt.subplots(figsize=(10,6.8))
colors=[ORANGE if (p==p and p<0.05) else GRAY for p in sg['p']]
ax.barh(sg['Subgroup']+'  ('+sg['Category']+')', sg['ReadmitPct'], color=colors)
ax.axvline(base*100, color='k', ls='--', lw=1, label=f'cohort {base*100:.1f}%')
for i,(_,r) in enumerate(sg.iterrows()): ax.text(r['ReadmitPct']+0.25, i, f"{r['ReadmitPct']}% (n={int(r['n'])})", va='center', fontsize=8)
ax.set_xlim(0, 23); ax.set_xlabel('Readmission (%)'); ax.legend(loc='lower right')
ax.text(0.5, 1.5, 'Orange = univariate p<0.05', fontsize=9, style='italic', color=ORANGE)
ax.set_title('Within-category subgroup analysis: which codes drive readmission', fontweight='bold', fontsize=12)
plt.tight_layout(); plt.savefig(FIG / 'Fig_Recon_4_subgroup_codes.png'); plt.close()

# Fig 5 — LOS predictors (days)
fig, ax = plt.subplots(figsize=(8,5.5))
cols=[GREEN if s else GRAY for s in los['sig']]
ax.barh(los['label'], los['beta'], color=cols)
ax.axvline(0, color='k', lw=1)
for i,(_,r) in enumerate(los.iterrows()):
    if r['sig']: ax.text(r['beta']+(0.05 if r['beta']>=0 else -0.05), i, f"{r['beta']:+.2f}d", va='center', ha='left' if r['beta']>=0 else 'right', fontsize=8, color=GREEN)
ax.set_xlabel('Change in length of stay (days)'); ax.set_title('Predictors of length of stay (OLS)\ngreen = p<0.05', fontweight='bold', fontsize=12)
plt.tight_layout(); plt.savefig(FIG / 'Fig_Recon_5_los_predictors.png'); plt.close()

# Fig 6 — restraint-use predictors (OR)
fig, ax = plt.subplots(figsize=(8,5.5))
forest(ax, rst, 'Predictors of physical restraint use (logistic)')
plt.tight_layout(); plt.savefig(FIG / 'Fig_Recon_6_restraint_predictors.png'); plt.close()

# Fig 7 — predictive ceiling: apparent vs honest AUC
fig, ax = plt.subplots(figsize=(8.5,5))
mods=opt['Model'].tolist(); x=np.arange(len(mods)); w=0.27
ax.bar(x-w, opt['Apparent AUC'], w, label='Apparent (in-sample)', color=ORANGE)
ax.bar(x,   opt['Bootstrap-corrected AUC'], w, label='Bootstrap-corrected', color='#f4a582')
ax.bar(x+w, opt['10-fold OOF AUC'], w, label='10-fold out-of-fold', color=BLUE)
ax.axhline(0.5, color='k', ls=':', lw=1, label='chance')
ax.set_xticks(x); ax.set_xticklabels(mods, fontsize=9); ax.set_ylim(0.45,0.95)
ax.set_ylabel('AUC-ROC'); ax.legend(fontsize=8, loc='upper right')
ax.set_title('Predictive ceiling: apparent AUC is optimism-inflated\nHonest out-of-fold AUC ≈ 0.64–0.68 (PPV ~15–20% at optimal threshold)', fontweight='bold', fontsize=11)
for i,(_,r) in enumerate(opt.iterrows()):
    ax.text(i-w, r['Apparent AUC']+0.01, f"{r['Apparent AUC']:.2f}", ha='center', fontsize=8)
    ax.text(i+w, r['10-fold OOF AUC']+0.01, f"{r['10-fold OOF AUC']:.2f}", ha='center', fontsize=8)
plt.tight_layout(); plt.savefig(FIG / 'Fig_Recon_7_predictive_ceiling.png'); plt.close()

print("\nSaved figures:")
import glob, os
for f in sorted(glob.glob(FIG / 'Fig_Recon_*.png')): print("  ", os.path.basename(f))
print("Saved tables: Recon_subgroup_codes.csv, Recon_readmission_logit.csv, Recon_los_predictors.csv, Recon_restraint_predictors.csv")
