import { loadData } from './data.js';
import { applyChartDefaults, chartScales, CHART_COLORS } from './format.js';

const REDUCED = window.__reducedMotion || matchMedia('(prefers-reduced-motion: reduce)').matches;

applyChartDefaults();
document.addEventListener('portfolio:ready', renderEquity);

async function renderEquity() {
  let data;
  try { data = await loadData(); } catch { return; }

  const equityEl = document.querySelector('[data-charts-equity]');
  const explorerEl = document.querySelector('[data-subgroup-explorer]');
  const proseEl = document.querySelector('[data-equity-prose]');
  if (!equityEl) return;

  if (proseEl) renderProse(proseEl, data.equity);
  renderFairness(equityEl, data.equity.fairness);
  if (explorerEl) renderExplorer(explorerEl, data.equity.subgroups);
}

function renderProse(container, equity) {
  const ranked = [...equity.fairness].sort((a, b) => b.gap - a.gap);
  const largest = ranked[0];
  const next = ranked[1];
  container.innerHTML = `
    <h2 class="section-h2 equity-title">Error rates varied across patient groups</h2>
    <p class="equity-copy">The equalized-odds summary compares gaps in sensitivity and false-positive rates. The largest observed gap was ${largest.label.toLowerCase()} (${largest.gap.toFixed(1)} percentage points)${next ? `, followed by ${next.label.toLowerCase()} (${next.gap.toFixed(1)} points)` : ''}.</p>
    <dl class="definition-list">
      <div><dt>ΔTPR</dt><dd>Difference in sensitivity between subgroups among patients who were readmitted.</dd></div>
      <div><dt>ΔFPR</dt><dd>Difference in false-positive rates between subgroups among patients who were not readmitted.</dd></div>
      <div><dt>Equalized-odds gap</dt><dd>The larger absolute value of ΔTPR and ΔFPR.</dd></div>
    </dl>
    <p class="chart-note">${equity.metric_note}</p>
  `;
}

function renderFairness(container, fairness) {
  const max = Math.max(30, ...fairness.map(item => item.gap));
  container.innerHTML = `
    <div class="chart-shell">
      <header class="chart-header"><div><h3 class="chart-title">Equalized-odds gap</h3><p class="chart-kicker">Held-out logistic predictions · n=1,569 · threshold 0.078 (Youden J)</p></div><span class="chart-measure">Percentage points</span></header>
      <div class="fairness-list">
        ${fairness.map(item => `
          <div class="fairness-row">
            <div class="fairness-label"><span>${item.label}</span><strong>${item.gap.toFixed(1)}</strong></div>
            <div class="fairness-track" role="img" aria-label="${item.label}: equalized-odds gap ${item.gap.toFixed(1)} percentage points; AUC gap ${item.auc_gap.toFixed(1)} points"><span class="fairness-bar" data-gap="${item.gap}"></span></div>
            <span class="fairness-detail">AUC gap ${item.auc_gap.toFixed(1)} points</span>
          </div>
        `).join('')}
      </div>
    </div>
  `;
  container.querySelectorAll('[data-gap]').forEach(bar => bar.style.setProperty('--bar-width', `${Number(bar.dataset.gap) / max * 100}%`));
}

function renderExplorer(container, subgroups) {
  container.innerHTML = `
    <div class="chart-shell">
      <header class="chart-header"><div><h3 class="chart-title">Subgroup model performance</h3><p class="chart-kicker">Separate 10-fold model run · broader cohort (n=2,652)</p></div><span class="chart-measure">${subgroups.length} subgroups · 3 models</span></header>
      <div class="chart-toolbar"><label class="chart-select-label" for="subgroup-select">Patient group</label><select class="chart-select" id="subgroup-select">${subgroups.map((item, index) => `<option value="${index}">${item.label} (n=${item.n})</option>`).join('')}</select></div>
      <div class="subgroup-readout" id="subgroup-readout" aria-live="polite"></div>
      <div class="chart-frame chart-frame--subgroup"><canvas role="img" aria-label="Subgroup AUC comparison for CatBoost, random forest, and logistic regression"></canvas></div>
    </div>
  `;

  const select = container.querySelector('#subgroup-select');
  const readout = container.querySelector('#subgroup-readout');
  const canvas = container.querySelector('canvas');
  const chart = new Chart(canvas, {
    type: 'bar',
    data: { labels: ['CatBoost', 'Random forest', 'Logistic'], datasets: [{ data: [0, 0, 0], backgroundColor: [CHART_COLORS.neutral, CHART_COLORS.tealSoft, CHART_COLORS.teal], borderRadius: 2, borderSkipped: false, maxBarThickness: 74 }] },
    options: {
      responsive: true, maintainAspectRatio: false, animation: REDUCED ? false : { duration: 300 },
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: context => context.parsed.y == null ? 'AUC unavailable' : `AUC ${context.parsed.y.toFixed(3)}` } } },
      scales: { y: { ...chartScales(), min: .5, max: .75, ticks: { ...chartScales().ticks, callback: value => value.toFixed(2) } }, x: { ...chartScales(), grid: { display: false } } },
    },
  });

  function update() {
    const subgroup = subgroups[Number.parseInt(select.value, 10)];
    const metrics = [
      ['N', subgroup.n],
      ['Readmission rate', subgroup.readmit_rate],
      ['CatBoost AUC', formatAuc(subgroup.auc_catboost)],
      ['Random forest AUC', formatAuc(subgroup.auc_rf)],
      ['Logistic AUC', formatAuc(subgroup.auc_lr)],
    ];
    readout.innerHTML = `<dl class="subgroup-metrics">${metrics.map(([label, value]) => `<div><dt>${label}</dt><dd>${value}</dd></div>`).join('')}</dl>`;
    chart.data.datasets[0].data = [subgroup.auc_catboost ?? null, subgroup.auc_rf ?? null, subgroup.auc_lr ?? null];
    canvas.setAttribute('aria-label', `${subgroup.label}. CatBoost AUC ${formatAuc(subgroup.auc_catboost)}, random forest AUC ${formatAuc(subgroup.auc_rf)}, logistic AUC ${formatAuc(subgroup.auc_lr)}.`);
    chart.update();
  }

  select.addEventListener('change', update);
  update();
}

function formatAuc(value) {
  return Number.isFinite(value) ? value.toFixed(3) : '—';
}
