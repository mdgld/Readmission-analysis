"""Check the full-cohort gallery inputs independently against the study records."""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import fisher_exact
from statsmodels.stats.multitest import multipletests


def check_spectrum(folder, df, site):
    dx = pd.read_csv(folder / 'data/diagnoses_long_form_complete.csv')
    outcomes = df.set_index('MRN').Readmissions.gt(0)
    assert dx.MRN.isin(outcomes.index).all()
    assert dx.Readmissions.gt(0).equals(dx.MRN.map(outcomes))
    # Use the long-form code table rather than the website's per-child category strings.
    coded = dx.groupby('dsm5_category').icd_code.agg(set)
    assert coded['Other Mental Disorder'] == {'R45.850'}
    assert coded['Non-Suicidal Self-Injury Behavior'] == {'R45.851', 'X78.9XXA', 'X78.9XXS'}
    unique = dx.drop_duplicates(['MRN', 'dsm5_category'])
    groups = unique.groupby('dsm5_category').Readmissions.agg(n='size', events=lambda x: x.gt(0).sum())
    groups = groups.loc[groups.n >= 15].copy()
    events, total = outcomes.sum(), len(outcomes)
    groups['p'] = [fisher_exact([[k, n-k], [events-k, total-n-events+k]]).pvalue
                   for n, k in groups.itertuples(index=False)]
    groups['q'] = multipletests(groups.p, method='fdr_bh')[1]
    groups.rename(index={'Non-Suicidal Self-Injury Behavior': 'Suicidal ideation / self-harm code group',
                         'Other Mental Disorder': 'Homicidal ideation (R45.850)'}, inplace=True)
    rows = pd.DataFrame(site['spectrum']['items']).set_index('label')
    assert set(rows.index) == set(groups.index)
    groups = groups.loc[rows.index]
    np.testing.assert_array_equal(groups.n, rows.n)
    np.testing.assert_array_equal(groups.events, rows.readmitted)
    np.testing.assert_allclose((100 * groups.events / groups.n).round(1), rows.rate)
    np.testing.assert_allclose(groups[['p', 'q']], rows[['p', 'q']], rtol=1e-10, atol=1e-14)
    assert rows.rate.is_monotonic_decreasing
    print(f'Diagnosis: {len(rows)} categories, {(groups.q < .05).sum()} adjusted q-values below .05.')


def check_regression(folder, df, los, site):
    from refresh_portfolio_data import NSSI_LABEL, tokens
    diagnoses = df[['VisitDiags', 'ChronicDiags', 'NonSuicidialDiags']].apply(tokens, axis=1, delimiter=',')
    categories = df[['VisitDiags_DSM5Categories', 'ChronicDiags_DSM5Categories']].apply(tokens, axis=1, delimiter=';')
    x = pd.DataFrame({
        'age': df.Pt_Age_Visit, 'gender_male': df.GenderCode.eq('Male'),
        'insurance_public': df.Insurance.str.contains('AHCCCS', case=False, na=False),
        'had_restraints': df.restraints.fillna(0).gt(0), 'csrss_red': df['Red flags (C-SSRS)'].notna(),
        'los_days': los, 'n_dsm5_categories': categories.map(len),
        'has_suicidal_ideation': diagnoses.map(lambda v: 'R45.851' in v),
        'has_z_code': diagnoses.map(lambda v: any(c.startswith('Z') for c in v)),
        'has_medical_comorbidity': df.ChronicDiags.fillna('').map(
            lambda v: any(c.strip()[:1] in set('CDEGHIJKLMNQ') for c in v.split(',')))
    })
    for term, label in {'depression': 'Depressive Disorders', 'trauma': 'Trauma and Stressor-Related Disorders',
                        'adhd': 'ADHD', 'nssi': NSSI_LABEL, 'psychotic': 'Psychotic Disorders',
                        'bipolar': 'Bipolar and Related Disorders', 'conduct': 'Conduct Disorder'}.items():
        x['has_' + term] = categories.map(lambda values, category=label: category in values)
    saved = pd.read_csv(folder / 'figures/Mv_logit_readmission.csv', index_col=0)
    assert set(saved.index) == set(x)
    # Fit the same binomial model via IRLS, independently of the notebook's logit optimizer.
    fit = sm.GLM(df.Readmissions.gt(0).astype(int), sm.add_constant(x.astype(float)),
                 family=sm.families.Binomial()).fit(tol=1e-12)
    assert fit.converged and fit.nobs == len(df)
    ci = np.exp(fit.conf_int())
    refit = pd.DataFrame({'OR': np.exp(fit.params), 'lo': ci[0], 'hi': ci[1], 'p': fit.pvalues})
    np.testing.assert_allclose(refit.loc[saved.index], saved, rtol=2e-6, atol=1e-12)
    terms = ['has_suicidal_ideation', 'has_depression', 'had_restraints', 'n_dsm5_categories',
             'age', 'has_nssi', 'csrss_red', 'gender_male']
    np.testing.assert_allclose(refit.loc[terms], pd.DataFrame(site['models']['forest'])[['or','lo','hi','p']],
                               rtol=2e-6, atol=1e-12)
    for term, mark in zip(terms, site['models']['forest']):
        row = refit.loc[term]
        expected = 'null' if row.p >= .05 else 'risk' if row.OR > 1 else 'protect'
        assert mark['kind'] == expected
    print(f'Regression: all {len(saved)} fitted terms agree, including the eight displayed estimates and intervals.')


def checked_cohort(folder, site):
    df = pd.read_csv(folder / 'data/annotated_psychiatric_data_complete.csv')
    assert df.MRN.is_unique and df.MRN.notna().all() and df.Readmissions.notna().all()
    original = folder / 'data/With Ages GD1854RVSD_Psychiatric Rehospitalization In School-Aged Children.csv'
    export = pd.read_csv(original, skiprows=2).set_index('MRN').sort_index()
    annotated = df.set_index('MRN').loc[:, export.columns].sort_index()
    if not annotated.equals(export):
        raise ValueError('Annotated records differ from the original cohort export.')
    los = (pd.to_datetime(df.DischDate, format='mixed') - pd.to_datetime(df.VisitDate, format='mixed')).dt.days
    assert los.notna().all() and los.ge(0).all()
    assert len(df) == site['summary']['n'] and df.Readmissions.gt(0).sum() == site['summary']['readmitted']
    cohort_rate = round(100 * df.Readmissions.gt(0).mean(), 1)
    assert site['spectrum']['cohort_rate'] == site['summary']['readmission_rate'] == cohort_rate
    check_spectrum(folder, df, site)
    check_regression(folder, df, los, site)
    return df, los


def draw_cohort(df, los, output):
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator

    readmissions = df.Readmissions.astype(int)
    ace = df.ACEscore.dropna()
    fig, axes = plt.subplots(2, 2, figsize=(10.8, 7.3), layout='constrained')
    fig.suptitle(f'Cohort characteristics · {len(df):,} children', fontsize=17)
    for ax, values, title, xlabel in [
        (axes[0, 0], readmissions, 'Readmissions per child',
         f'Recorded readmissions · mean {readmissions.mean():.2f} (SD {readmissions.std():.2f})'),
        (axes[0, 1], ace, f'Adverse childhood experiences · {len(ace):,} recorded ({len(ace)/len(df):.1%})',
         f'ACE score · median {ace.median():.0f}, mean {ace.mean():.1f} (SD {ace.std():.1f})')
    ]:
        counts = values.astype(int).value_counts().sort_index()
        bars = ax.bar(counts.index, counts, color='#12655e')
        ax.bar_label(bars, fmt='{:,.0f}', padding=3, fontsize=8)
        ax.set(xticks=counts.index, xlabel=xlabel, ylabel='Children', ylim=(0, counts.max()*1.14))
        ax.set_title(title, loc='left', fontsize=12)
    ax = axes[1, 0]
    ax.hist(los, bins=30, color='#12655e')
    ax.set(xlabel=f'Days from admission to discharge · mean {los.mean():.1f} (SD {los.std():.1f})', ylabel='Children')
    ax.set_title(f'Length of stay · median {los.median():.0f} days (range {los.min()}–{los.max()})',
                 loc='left', fontsize=12)
    ax = axes[1, 1]
    returned = int(readmissions.gt(0).sum())
    rates = np.array([len(df)-returned, returned]) / len(df) * 100
    bars = ax.barh(['No recorded readmission', 'Readmitted'], rates, color=['#9ba7a1', '#985037'])
    ax.bar_label(bars, labels=[f'{r:.1f}%' for r in rates], padding=3)
    ax.set(xlim=(0, 105), xlabel='Percentage of children')
    ax.set_title('Readmission within 90 days', loc='left', fontsize=12)
    for ax in axes.flat:
        ax.spines[['top', 'right']].set_visible(False)
    for ax in [axes[0,0], axes[0,1], axes[1,0]]:
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    fig.savefig(output / 'Cohort_Descriptive_Overview.png')
    plt.close(fig)


def draw_demographics(df, output):
    import matplotlib.pyplot as plt
    from scipy.stats import chi2_contingency

    outcome = df.Readmissions.gt(0)
    flags = df[['Yellow flags (C-SRSS)', 'Orange flags (C-SSRS)', 'Red flags (C-SSRS)']]
    groups = [
        ('Recorded gender identity', df.GenderCode.eq('Male'), ['Female', 'Male']),
        ('Insurance', df.Insurance.str.contains('AHCCCS', case=False, na=False), ['Other or missing', 'AHCCCS']),
        ('C-SSRS screening', flags.notna().any(axis=1), ['No flag', 'Any flag']),
        ('Physical restraint', df.restraints.fillna(0).gt(0), ['No restraint', 'Restraint used'])
    ]
    fig, axes = plt.subplots(2, 2, figsize=(10.2, 7.8), sharey=True, layout='constrained')
    fig.suptitle('Observed readmission within 90 days', fontsize=17)
    for ax, (title, flag, labels) in zip(axes.flat, groups):
        counts = pd.crosstab(flag, outcome).reindex(index=[False, True], columns=[False, True], fill_value=0)
        n, events = counts.sum(axis=1), counts[True]
        proportion = events / n
        # Match the descriptive notebook's normal-approximation intervals and Yates-corrected test.
        error = 100 * 1.96 * np.sqrt(proportion * (1-proportion) / n)
        p = chi2_contingency(counts).pvalue
        bars = ax.bar(labels, 100 * proportion, yerr=error, capsize=4, width=.54, color=['#9ba7a1', '#12655e'])
        for bar, rate, err, k, size in zip(bars, proportion, error, events, n):
            ax.text(bar.get_x()+bar.get_width()/2, 100*rate+err+.5, f'{rate:.1%}\n{k:,} of {size:,}',
                    ha='center', va='bottom', fontsize=9)
        p_label = 'p < .001' if p < .001 else f'p = {p:.3f}'
        ax.set_title(f'{title} · {p_label}', fontsize=12, loc='left')
        ax.set(ylabel='Readmitted (%)', ylim=(0, 23))
        ax.spines[['top', 'right']].set_visible(False)
        print(f'{title}: {list(zip(events, n))}, p={p:.6g}')
    fig.savefig(output / 'Fig2_demographics_panel.png')
    plt.close(fig)
