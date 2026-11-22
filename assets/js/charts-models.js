import { loadData } from './data.js';
import { applyChartDefaults, chartScales, CHART_COLORS } from './format.js';

const REDUCED = window.__reducedMotion || matchMedia('(prefers-reduced-motion: reduce)').matches;

applyChartDefaults();
document.addEventListener('portfolio:ready', renderModels);

async function renderModels() {
  let data;
  try { data = await loadData(); } catch { return; }

  const forestEl = document.querySelector('[data-charts-forest]');
  const modelsEl = document.querySelector('[data-charts-models]');
  const readEl = document.querySelector('[data-clinical-read]');
  if (!forestEl || !modelsEl) return;

  if (readEl) readEl.innerHTML = `<span class="clinical-read-label">Interpretation</span><p class="clinical-read-text">${data.models.clinical_read}</p>`;
  renderForest(forestEl, data.models);
  renderAUC(modelsEl, data.models);
}

function renderForest(container, models) {
  const forest = models.forest;
  container.innerHTML = `
    <div class="chart-shell">
      <header class="chart-header"><div><h3 class="chart-title">Adjusted odds of readmission</h3><p class="chart-kicker">2,652 children · logistic regression</p></div><span class="chart-measure">Odds ratio · 95% CI</span></header>
      <div class="chart-frame chart-frame--forest"><canvas role="img" aria-label="${forestAria(forest)}"></canvas></div>
      <p class="chart-axis-note">Odds ratio on a logarithmic scale. The dashed line marks OR 1.00.</p>
      <div class="chart-legend chart-legend--wrap">
        <span><i class="legend-swatch legend-swatch--risk"></i>Higher odds</span>
        <span><i class="legend-swatch legend-swatch--protect"></i>Lower odds</span>
        <span><i class="legend-swatch legend-swatch--neutral"></i>Not significant</span>
        <span>* p&lt;.05 · ** p&lt;.01 · *** p&lt;.001</span>
      </div>
      ${models.coding_note ? `<p class="chart-note">${models.coding_note}</p>` : ''}
    </div>
  `;
  const canvas = container.querySelector('canvas');
  const colors = { risk: CHART_COLORS.risk, protect: CHART_COLORS.protect, null: CHART_COLORS.neutral };

  new Chart(canvas, {
    type: 'bar',
    data: { labels: forest.map(item => item.kind === 'null' ? item.label : `${item.label} ${item.stars}`), datasets: [{ data: forest.map(item => item.or), backgroundColor: 'transparent', borderColor: 'transparent', barPercentage: .28 }] },
    options: {
      indexAxis: 'y', responsive: true, maintainAspectRatio: false,
      animation: REDUCED ? false : { duration: 350 },
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: context => {
        const item = forest[context.dataIndex];
        return [`OR ${item.or.toFixed(2)} (95% CI ${item.lo.toFixed(2)}–${item.hi.toFixed(2)})`, `p ${item.p < .001 ? '< .001' : '= ' + item.p.toFixed(3)} ${item.stars}`];
      } } } },
      scales: {
        x: { ...chartScales(), type: 'logarithmic', min: .25, max: Math.max(4, ...forest.map(item => item.hi)), afterBuildTicks: axis => { axis.ticks = [.25, .5, 1, 2, 4].map(value => ({ value })); }, ticks: { ...chartScales().ticks, callback: value => value } },
        y: { ...chartScales(), grid: { display: false }, ticks: { ...chartScales().ticks, autoSkip: false, callback: (_, index) => wrapLabel(forest[index]?.label || '', 25) } },
      },
    },
    plugins: [forestWhiskers(forest, colors), referenceLine()],
  });
}

function forestWhiskers(forest, colors) {
  return { id: 'forestWhiskers', afterDatasetsDraw(chart) {
    const { ctx, scales } = chart;
    ctx.save();
    forest.forEach((item, index) => {
      const y = scales.y.getPixelForTick(index);
      const color = colors[item.kind] || colors.null;
      const lo = scales.x.getPixelForValue(item.lo);
      const hi = scales.x.getPixelForValue(item.hi);
      const estimate = scales.x.getPixelForValue(item.or);
      ctx.strokeStyle = color; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(lo, y); ctx.lineTo(hi, y); ctx.moveTo(lo, y - 5); ctx.lineTo(lo, y + 5); ctx.moveTo(hi, y - 5); ctx.lineTo(hi, y + 5); ctx.stroke();
      ctx.fillStyle = CHART_COLORS.paper; ctx.fillRect(estimate - 4, y - 4, 8, 8); ctx.strokeRect(estimate - 4, y - 4, 8, 8);
    });
    ctx.restore();
  } };
}

function referenceLine() {
  return { id: 'oddsRatioReference', afterDraw(chart) {
    const { ctx, chartArea, scales } = chart;
    const x = scales.x.getPixelForValue(1);
    ctx.save(); ctx.strokeStyle = CHART_COLORS.muted; ctx.lineWidth = 1; ctx.setLineDash([4, 3]); ctx.beginPath(); ctx.moveTo(x, chartArea.top); ctx.lineTo(x, chartArea.bottom); ctx.stroke(); ctx.restore();
  } };
}

function renderAUC(container, models) {
  const auc = models.auc;
  container.innerHTML = `
    <div class="chart-shell">
      <header class="chart-header"><div><h3 class="chart-title">Validation AUC</h3><p class="chart-kicker">1,569 children · 10-fold cross-validation</p></div><span class="chart-measure">AUROC</span></header>
      <div class="chart-frame chart-frame--auc"><canvas role="img" aria-label="${aucAria(auc)}"></canvas></div>
      <div class="chart-toolbar auc-toolbar"><button class="chart-control" type="button" id="auc-toggle">Show training AUC</button><span class="chart-toolbar-status" id="auc-status" role="status">Held-out AUC</span></div>
      <table class="auc-table"><caption>Area under the ROC curve</caption><thead><tr><th scope="col">Model</th><th scope="col">Training</th><th scope="col">Bootstrap corrected</th><th scope="col">Held out</th></tr></thead>
        <tbody>${auc.map(item => `<tr><th scope="row">${item.name}</th><td>${item.apparent.toFixed(3)}</td><td>${item.corrected.toFixed(3)}</td><td>${item.oof.toFixed(3)}</td></tr>`).join('')}</tbody>
      </table>
      <p class="chart-note">Bootstrap correction estimates how much training scores are inflated by refitting models on repeated samples from the cohort. The bootstrap and held-out analyses used different model settings.</p>
    </div>
  `;

  const canvas = container.querySelector('canvas');
  const toggle = container.querySelector('#auc-toggle');
  const status = container.querySelector('#auc-status');
  let heldOut = true;
  const chart = new Chart(canvas, {
    type: 'bar',
    data: { labels: auc.map(item => item.name), datasets: [{ data: auc.map(item => item.oof), backgroundColor: [CHART_COLORS.teal, CHART_COLORS.tealSoft, CHART_COLORS.neutral], borderRadius: 2, borderSkipped: false, maxBarThickness: 72 }] },
    options: {
      responsive: true, maintainAspectRatio: false, animation: REDUCED ? false : { duration: 350 },
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: context => {
        const item = auc[context.dataIndex];
        return [`Apparent: ${item.apparent.toFixed(3)}`, `Corrected: ${item.corrected.toFixed(3)}`, `Out-of-fold: ${item.oof.toFixed(3)}`];
      } } } },
      scales: { y: { ...chartScales(), min: .5, max: 1, afterBuildTicks: axis => { axis.ticks = [.5, .6, .7, .8, .9, 1].map(value => ({ value })); }, ticks: { ...chartScales().ticks, callback: value => value.toFixed(2) } }, x: { ...chartScales(), grid: { display: false } } },
    },
  });

  toggle.addEventListener('click', () => {
    heldOut = !heldOut;
    chart.data.datasets[0].data = auc.map(item => heldOut ? item.oof : item.apparent);
    chart.data.datasets[0].backgroundColor = heldOut ? [CHART_COLORS.teal, CHART_COLORS.tealSoft, CHART_COLORS.neutral] : [CHART_COLORS.neutral, CHART_COLORS.risk, CHART_COLORS.risk];
    toggle.textContent = heldOut ? 'Show training AUC' : 'Show held-out AUC';
    status.textContent = heldOut ? 'Showing held-out predictions' : 'Showing in-sample estimates';
    chart.update();
  });
}

function forestAria(forest) {
  return `Forest plot. ${forest.map(item => `${item.label}: OR ${item.or.toFixed(2)}, 95% CI ${item.lo.toFixed(2)} to ${item.hi.toFixed(2)}, p ${item.p < .001 ? 'less than .001' : item.p.toFixed(3)}`).join('. ')}.`;
}

function aucAria(auc) {
  return `Model AUC comparison. ${auc.map(item => `${item.name}: apparent ${item.apparent.toFixed(3)}, corrected ${item.corrected.toFixed(3)}, out-of-fold ${item.oof.toFixed(3)}`).join('. ')}.`;
}

function wrapLabel(label, width) {
  const lines = []; let line = '';
  label.split(' ').forEach(word => { if (`${line} ${word}`.trim().length > width && line) { lines.push(line); line = word; } else line = `${line} ${word}`.trim(); });
  if (line) lines.push(line);
  return lines;
}
