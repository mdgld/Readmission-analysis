"""Refresh the website from a local analysis checkout. Only aggregate values leave this process.

Run with the analysis project's Python, passing the directory that contains data/ and figures/.
The July regression and validation notebooks produce the CSV tables used here.
"""
import argparse
import json
from pathlib import Path

import pandas as pd
from scipy.stats import fisher_exact
from statsmodels.stats.contingency_tables import Table2x2
from statsmodels.stats.multitest import multipletests

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ['VisitDiags', 'ChronicDiags', 'NonSuicidialDiags']
NSSI_LABEL = 'Non-Suicidal Self-Injury Behavior'


def group(label, mask, outcome):
    n, events = int(mask.sum()), int(outcome[mask].sum())
    return dict(label=label, n=n, readmitted=events, rate=round(events * 100 / n, 1))


def comparison(rows):
    table = [[r['readmitted'], r['n'] - r['readmitted']] for r in rows]
    odds, p = fisher_exact(table)
    low, high = Table2x2(table).oddsratio_confint()
    return {'or': f'{odds:.2f}', 'ci': f'{low:.2f}–{high:.2f}',
            'p': '<0.001' if p < .001 else f'{p:.3f}'}


def tokens(series, delimiter):
    return {word.strip() for value in series.dropna() for word in value.split(delimiter) if word.strip()}


def describe(source, site):
    df = pd.read_csv(source / 'data/annotated_psychiatric_data_complete.csv', low_memory=False)
    if df.MRN.isna().any() or not df.MRN.is_unique:
        raise ValueError('The cohort must have exactly one row per child.')
    outcome = pd.to_numeric(df.Readmissions).fillna(0) > 0
    age = df.Pt_Age_Visit
    n, events = len(df), int(outcome.sum())
    diagnosis_count = len(pd.read_csv(source / 'data/diagnoses_long_form_complete.csv', usecols=['diagnosis_type']))
    cat_rows = df[[f'{field}_DSM5Categories' for field in FIELDS]].apply(tokens, axis=1, delimiter=';')
    code_rows = df[FIELDS].apply(tokens, axis=1, delimiter=',')
    categories = sorted(set.union(*cat_rows))
    codes = set.union(*code_rows)
    site['summary'] = {'n': n, 'readmitted': events, 'readmission_rate': round(100 * events / n, 1),
                       'age_mean': round(float(age.mean()), 2), 'age_range': [int(age.min()), int(age.max())],
                       'diagnosis_records': diagnosis_count, 'unique_icd_codes': len(codes),
                       'dsm5_categories': len(categories)}
    male = df.GenderCode.str.strip().str.lower() == 'male'
    red = df['Red flags (C-SSRS)'].notna()
    unflagged = df[['Red flags (C-SSRS)', 'Orange flags (C-SSRS)', 'Yellow flags (C-SRSS)']].isna().all(axis=1)
    insured = df.Insurance.notna()
    ahcccs = df.Insurance.str.contains('AHCCCS', case=False, na=False)
    restraint = pd.to_numeric(df.restraints).fillna(0) > 0
    pairs = {
        'gender': [('Male', male), ('Female', df.GenderCode.str.strip().str.lower() == 'female')],
        'cssrs': [('Red flag', red), ('No flag', unflagged)],
        'insurance': [('AHCCCS', ahcccs), ('Other recorded', insured & ~ahcccs)],
        'restraint': [('Restraint used', restraint), ('No restraint', ~restraint)],
    }
    groups = {key: [group(label, mask, outcome) for label, mask in pair] for key, pair in pairs.items()}
    stats = {key: comparison(rows) for key, rows in groups.items()}
    groups['age'] = [group(f'{int(value)} years', age == value, outcome) for value in sorted(age.unique())]
    groups['insurance_note'] = f'{int((~insured).sum())} children with missing insurance were excluded.'
    groups['cssrs_note'] = f'{int((~red & ~unflagged).sum())} children with only a yellow or orange flag were excluded.'
    site['findings'] = {'cohort_rate': site['summary']['readmission_rate'], 'demo_max': 20, 'groups': groups, 'groupStats': stats}

    ref = pd.read_csv(source / 'data/ICD10_to_DSM5_Complete_Reference.csv')
    ideation = code_rows.map(lambda values: 'R45.851' in values)
    model_flag = df[[f'{field}_DSM5Categories' for field in FIELDS[:2]]].apply(tokens, axis=1, delimiter=';').map(lambda values: NSSI_LABEL in values)
    site['models']['coding_note'] = (
        f'The study mapping includes suicidal ideation (R45.851) in the self-injury code group. '
        f'Of {int(model_flag.sum()):,} children with that visit or chronic diagnosis flag, '
        f'{int((model_flag & ideation).sum()):,} also had R45.851. The two coefficients cannot distinguish '
        'the effects of suicidal ideation and non-suicidal self-injury.'
    )
    rows = []
    for category in categories:
        mask = cat_rows.map(lambda values: category in values)
        if mask.sum() < 15:
            continue
        label = category
        if category == NSSI_LABEL:
            label = 'Suicidal ideation / self-harm code group'
        elif category == 'Other Mental Disorder':
            mapped = set(ref.loc[ref.DSM5_Category == category, 'ICD_Code'])
            if mapped == {'R45.850'} and mask.equals(code_rows.map(lambda values: 'R45.850' in values)):
                label = 'Homicidal ideation (R45.850)'
        row = group(label, mask, outcome)
        a, total = row['readmitted'], row['n']
        b, c = total - a, events - a
        row['p'] = float(fisher_exact([[a, b], [c, n - total - c]]).pvalue)
        rows.append(row)
    for row, q in zip(rows, multipletests([r['p'] for r in rows], method='fdr_bh')[1]):
        row['q'] = float(q)
    site['spectrum'].update({'dx_max': 25, 'cohort_rate': site['summary']['readmission_rate'],
                             'items': sorted(rows, key=lambda row: (-row['rate'], row['label']))})


def model_results(figures, site):
    forest = pd.read_csv(figures / 'Mv_logit_readmission.csv', index_col=0)
    terms = {
        'has_suicidal_ideation': 'Suicidal ideation (R45.851)',
        'has_depression': 'Depressive disorders',
        'had_restraints': 'Physical restraint use',
        'n_dsm5_categories': 'Each additional diagnostic category',
        'age': 'Age (per year)',
        'has_nssi': 'Self-injury code group (visit or chronic)',
        'csrss_red': 'C-SSRS red flag',
        'gender_male': 'Male gender identity',
    }
    rows = []
    for key, label in terms.items():
        r = forest.loc[key]
        stars = '***' if r.p < .001 else '**' if r.p < .01 else '*' if r.p < .05 else 'n.s.'
        rows.append(dict(label=label, **{'or': r.OR}, lo=r.lo, hi=r.hi, p=r.p, stars=stars,
                         kind='null' if r.p >= .05 else 'risk' if r.OR > 1 else 'protect'))
    auc = pd.read_csv(figures / 'AdvStats_optimism_validation.csv')
    site['models']['forest'] = rows
    site['models']['auc'] = [
        {'name': r['Model'], 'apparent': r['Apparent AUC'], 'corrected': r['Bootstrap-corrected AUC'],
         'oof': r['10-fold OOF AUC']} for _, r in auc.iterrows()]
    site['models']['optimism_delta'] = {
        row['name']: round(row['apparent'] - row['oof'], 3) for row in site['models']['auc']}
    subgroup = pd.read_csv(figures / 'Subgroup_AUC.csv')
    labels = {'Public Insurance': 'AHCCCS recorded', 'Private Insurance': 'No AHCCCS recorded',
              'With Trauma': 'Trauma diagnosis', 'Without Trauma': 'No trauma diagnosis',
              'With Restraints': 'Restraint used', 'Without Restraints': 'No restraint'}
    site['equity']['subgroups'] = [
        dict(label=labels.get(r['Subgroup'], r['Subgroup']), n=int(r.N), readmit_rate=r['Readmission rate'],
             auc_catboost=r['AUC (CatBoost)'], auc_rf=r['AUC (Random Forest)'],
             auc_lr=r['AUC (Logistic Regression)']) for _, r in subgroup.iterrows()]
    disparities = pd.read_csv(figures / 'AdvStats_fairness_disparities.csv')
    names = {'Age (<=9 vs >=10)': 'Age (5–9 vs 10–12)', 'Sex (M vs F)': 'Recorded gender (male vs female)',
             'Insurance (Public vs Private)': 'Insurance (AHCCCS vs other or missing)',
             'ACE category (high vs not high)': 'ACE category (high vs lower)'}
    gaps = [dict(label=names[r.Pairing], gap=100*r['Equalized-odds gap (max|dTPR|,|dFPR|)'],
                 auc_gap=100*r['AUC gap']) for _, r in disparities.iterrows()]
    site['equity']['fairness'] = sorted(gaps, key=lambda row: -row['gap'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('analysis_dir', type=Path)
    args = parser.parse_args()
    path = ROOT / 'data.json'
    data = json.loads(path.read_text())
    describe(args.analysis_dir, data)
    model_results(args.analysis_dir / 'figures', data)
    path.write_text(json.dumps(data, ensure_ascii=False, allow_nan=False, indent=2) + '\n')
