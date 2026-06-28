import { loadData } from './data.js';
import { fmt, pct, fmtCI, fmtP, COHORT_RATE } from './format.js';

document.addEventListener('portfolio:ready', renderContent);

async function renderContent() {
  let data;
  try { data = await loadData(); } catch { return; }

  renderMetrics(data);
  renderMethods(data);
  renderAbstract(data);
  renderSrOnlySummary(data);
}

function renderSrOnlySummary(data) {
  const existing = document.getElementById('sr-data-summary');
  if (existing) existing.remove();
  const div = document.createElement('div');
  div.id = 'sr-data-summary';
  div.className = 'sr-only';
  div.setAttribute('aria-hidden', 'true');

  const parts = [];

  parts.push(`Cohort: ${fmt(data.summary.n)} patients, ${data.summary.readmission_rate}% readmission rate, ${data.summary.readmitted} events, ${data.summary.age_mean} mean age, ${data.summary.unique_icd_codes} ICD codes, ${data.summary.diagnosis_records} diagnosis records, ${data.summary.dsm5_categories} DSM-5 categories, ${data.summary.best_oof_auc} best OOF AUC.`);

  for (const [key, label] of [['age','Age band'],['gender','Gender identity'],['cssrs','C-SSRS flag'],['insurance','Insurance'],['restraint','Restraint']]) {
    const items = data.findings.groups[key];
    if (!items) continue;
    parts.push(`${label}: ${items.map(d => `${d.label} ${d.rate.toFixed(1)}% (n=${fmt(d.n)}, readmit=${d.readmitted})`).join('; ')}.`);
  }

  const gs = data.findings.groupStats;
  parts.push(`Group odds ratios: gender OR ${gs.gender.or} CI ${gs.gender.ci} p ${gs.gender.p}; C-SSRS OR ${gs.cssrs.or} CI ${gs.cssrs.ci} p ${gs.cssrs.p}; insurance OR ${gs.insurance.or} CI ${gs.insurance.ci} p ${gs.insurance.p}; restraint OR ${gs.restraint.or} CI ${gs.restraint.ci} p ${gs.restraint.p}.`);

  parts.push(`DSM-5 spectrum: ${data.spectrum.items.map(d => `${d.label} ${d.rate.toFixed(1)}% (n=${fmt(d.n)}, readmit=${d.readmitted})`).join('; ')}.`);

  parts.push(`Forest plot: ${data.models.forest.map(f => `${f.label} OR ${f.or.toFixed(2)} CI ${f.lo.toFixed(2)}\u2013${f.hi.toFixed(2)} p ${f.p < 0.001 ? '<0.001' : f.p.toFixed(3)} ${f.stars}`).join('; ')}.`);

  parts.push(`Model AUC: ${data.models.auc.map(m => `${m.name} apparent ${m.apparent.toFixed(3)} corrected ${m.corrected.toFixed(3)} OOF ${m.oof.toFixed(3)}`).join('; ')}.`);
  parts.push(`Optimism deltas: Logistic ${data.models.optimism_delta.Logistic}, Random Forest ${data.models.optimism_delta['Random Forest']}, CatBoost ${data.models.optimism_delta.CatBoost}.`);

  parts.push(`Fairness: ${data.equity.fairness.map(f => `${f.label} gap ${f.gap.toFixed(1)}% AUC gap ${f.auc_gap.toFixed(1)}pt`).join('; ')}.`);

  parts.push(`Subgroups: ${data.equity.subgroups.map(s => `${s.label} n=${s.n} rate=${s.readmit_rate} CatBoost=${s.auc_catboost.toFixed(3)} RF=${s.auc_rf.toFixed(3)} LR=${s.auc_lr.toFixed(3)}`).join('; ')}.`);

  parts.push(`Abstract results: ${data.abstract.results.map(r => r.text).join(' ')}`);

  div.textContent = parts.join(' ');
  document.body.appendChild(div);
}

function renderMetrics(data) {
  const body = document.querySelector('[data-metrics-body]');
  if (!body) return;
  const s = data.summary;
  const metrics = [
    { k: 'Patients', v: fmt(s.n) },
    { k: '90-day readmission rate', v: `${s.readmission_rate}%`, sub: `${s.readmitted} events` },
    { k: 'ICD-10-CM codes mapped', v: fmt(s.unique_icd_codes) },
    { k: 'Diagnosis records', v: fmt(s.diagnosis_records) },
    { k: 'DSM-5 categories', v: fmt(s.dsm5_categories) },
    { k: 'Best OOF AUC', v: s.best_oof_auc.toFixed(3), sub: 'honest ceiling' },
    { k: 'Mean age', v: s.age_mean.toFixed(1), sub: `range ${s.age_range[0]}\u2013${s.age_range[1]} yrs` },
    { k: 'Study period', v: '2017\u20132024', sub: 'single AZ unit' },
  ];
  body.innerHTML = metrics.map(m =>
    `<div class="metric-row"><div><div class="metric-k">${m.k}</div></div><div><div class="metric-v">${m.v}</div>${m.sub ? `<div class="metric-sub">${m.sub}</div>` : ''}</div></div>`
  ).join('');
}

function renderMethods(data) {
  const prose = document.querySelector('[data-methods-prose]');
  if (prose) {
    prose.innerHTML = `
      <h2 class="section-h2">Readmission is clinically important, but individual prediction is hard</h2>
      <p style="color:var(--muted);line-height:1.75;margin:0 0 1rem">Can routine clinical, demographic, and diagnosis data identify children at higher risk for psychiatric rehospitalization? Several interpretable factors are associated with readmission — yet discrimination stays modest after out-of-fold and optimism-corrected evaluation.</p>
      <p style="color:var(--muted);line-height:1.75;margin:0 0 1rem">The work catalogued here treats inference and prediction as complementary: machine learning is used to surface risk factors that standard regression missed, while honest out-of-fold and bootstrap-corrected metrics keep the deployment claim modest.</p>
      <p style="color:var(--faint);line-height:1.75;margin:0;font-size:.92rem">This website implements only aggregate statistics and generated figures. Patient-level rows, identifiers, and source CSVs are never exposed.</p>
    `;
  }

  const pipeline = document.querySelector('[data-pipeline]');
  if (pipeline) {
    pipeline.innerHTML = `
      <div class="pipeline-head">Analysis pipeline</div>
      ${data.pipeline.map(step =>
        `<div class="pipeline-row"><span class="pipeline-num">${step.n}</span><span class="pipeline-text">${step.t}</span></div>`
      ).join('')}
    `;
  }
}

function renderAbstract(data) {
  const abstract = document.querySelector('[data-abstract]');
  if (abstract) {
    abstract.innerHTML = data.abstract.sections.map(sec =>
      `<div class="abstract-section"><h3 class="abstract-section-h">${sec.h}</h3><p class="abstract-section-body">${sec.body}</p></div>`
    ).join('');
  }

  const results = document.querySelector('[data-results]');
  if (results) {
    results.innerHTML = `
      <h3 class="abstract-section-h">Results</h3>
      <div style="display:grid;gap:.55rem">
        ${data.abstract.results.map(r =>
          `<div class="result-chip ${r.kind}"><span class="result-tag ${r.kind}">${r.tag}</span><span class="result-text ${r.kind}">${r.text}</span></div>`
        ).join('')}
      </div>
    `;
  }

  const objectives = document.querySelector('[data-objectives]');
  if (objectives) {
    objectives.innerHTML = `
      <h3 class="abstract-section-h">Learning objectives</h3>
      <div class="objective-grid">
        ${data.abstract.objectives.map(o =>
          `<div class="objective-row"><span class="objective-num">${o.n}</span><span class="objective-text">${o.t}</span></div>`
        ).join('')}
      </div>
    `;
  }
}
