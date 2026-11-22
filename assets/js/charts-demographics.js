import { loadData } from './data.js';
import { applyChartDefaults, chartScales, CHART_COLORS, COHORT_RATE } from './format.js';

const REDUCED = window.__reducedMotion || matchMedia('(prefers-reduced-motion: reduce)').matches;

applyChartDefaults();
document.addEventListener('portfolio:ready', renderDemographics);

async function renderDemographics() {
  let data;
  try { data = await loadData(); } catch { return; }
  const container = document.querySelector('[data-charts-demographics]');
  if (!container) return;

  const groups = data.findings.groups;
  const stats = data.findings.groupStats;
  const panels = [
    { key: 'age', title: 'Age band', cls: 'demo-card demo-card--wide', footnote: 'Age at the index admission.' },
    { key: 'gender', title: 'Gender identity', cls: 'demo-card demo-card--wide', stats: stats.gender },
    { key: 'cssrs', title: 'C-SSRS flag', cls: 'demo-card', stats: stats.cssrs, note: groups.cssrs_note },
    { key: 'insurance', title: 'Insurance', cls: 'demo-card', stats: stats.insurance, note: groups.insurance_note },
    { key: 'restraint', title: 'Physical restraint', cls: 'demo-card', stats: stats.restraint },
  ];

  container.replaceChildren();
  for (const panel of panels) {
    const items = groups[panel.key];
    if (!items) continue;

    const card = document.createElement('article');
    card.className = panel.cls;
    card.innerHTML = `
      <header class="chart-header">
        <div><h3 class="chart-title">${panel.title}</h3></div>
        <span class="chart-measure">90-day readmission</span>
      </header>
      <div class="chart-frame ${panel.key === 'age' ? 'chart-frame--age' : 'chart-frame--compact'}"><canvas role="img"></canvas></div>
      ${panel.stats ? statisticFooter(panel.stats) : ''}
      ${(panel.note || panel.footnote) ? `<p class="chart-note">${panel.note || panel.footnote}</p>` : ''}
    `;
    const canvas = card.querySelector('canvas');
    canvas.setAttribute('aria-label', `Readmission rate by ${panel.title.toLowerCase()}. ${items.map(item => `${item.label}: ${item.rate.toFixed(1)}%, ${item.readmitted} of ${item.n}`).join('. ')}. Cohort rate: ${COHORT_RATE}%.`);
    container.appendChild(card);
    renderChart(canvas, items, panel.key === 'age', Math.max(20, data.findings.demo_max || 0));
  }
}

function statisticFooter(stats) {
  return `<dl class="chart-stats" aria-label="Unadjusted pairwise comparison"><div><dt>Unadjusted OR</dt><dd>${stats.or}</dd></div><div><dt>95% CI</dt><dd>${stats.ci}</dd></div><div><dt>Fisher p</dt><dd>${stats.p}</dd></div></dl>`;
}

function renderChart(canvas, items, horizontal, max) {
  const colors = items.map(item => item.rate > COHORT_RATE ? CHART_COLORS.risk : item.rate < COHORT_RATE ? CHART_COLORS.protect : CHART_COLORS.neutral);

  new Chart(canvas, {
    type: 'bar',
    data: { labels: items.map(item => item.mark ? `${item.label} ${item.mark}` : item.label), datasets: [{ data: items.map(item => item.rate), backgroundColor: colors, borderRadius: 2, borderSkipped: false, barPercentage: .68, maxBarThickness: 34 }] },
    options: {
      indexAxis: horizontal ? 'y' : 'x', responsive: true, maintainAspectRatio: false,
      animation: REDUCED ? false : { duration: 350 }, layout: { padding: horizontal ? { right: 28 } : { top: 20 } },
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: ctx => {
        const item = items[ctx.dataIndex];
        return [`${item.rate.toFixed(1)}% readmitted`, `${item.readmitted} of ${item.n} patients`];
      } } } },
      scales: horizontal ? horizontalScales(max) : verticalScales(max),
    },
    plugins: [baselineLine(COHORT_RATE, horizontal), valueLabels(items, horizontal)],
  });
}

function valueLabels(items, horizontal) {
  return { id: `demographicValues-${horizontal}`, afterDatasetsDraw(chart) {
    const { ctx, scales } = chart;
    ctx.save(); ctx.font = '600 10px Inter, ui-sans-serif, system-ui, sans-serif'; ctx.fillStyle = CHART_COLORS.text;
    items.forEach((item, index) => {
      if (horizontal) {
        ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
        ctx.fillText(`${item.rate.toFixed(1)}%`, scales.x.getPixelForValue(item.rate) + 5, scales.y.getPixelForTick(index));
      } else {
        ctx.textAlign = 'center'; ctx.textBaseline = 'bottom';
        ctx.fillText(`${item.rate.toFixed(1)}%`, scales.x.getPixelForTick(index), scales.y.getPixelForValue(item.rate) - 5);
      }
    });
    ctx.restore();
  } };
}

function horizontalScales(max) {
  const base = chartScales();
  return { x: { ...base, max: max + 1, beginAtZero: true, ticks: { ...base.ticks, callback: value => `${value}%`, maxTicksLimit: 6 } }, y: { ...base, grid: { display: false }, ticks: { ...base.ticks, autoSkip: false } } };
}

function verticalScales(max) {
  const base = chartScales();
  return { x: { ...base, grid: { display: false }, ticks: { ...base.ticks, maxRotation: 0, minRotation: 0 } }, y: { ...base, max: max + 1, beginAtZero: true, ticks: { ...base.ticks, callback: value => `${value}%`, maxTicksLimit: 6 } } };
}

function baselineLine(value, horizontal) {
  return { id: `cohortBaseline-${horizontal}`, afterDraw(chart) {
    const { ctx, chartArea, scales } = chart;
    ctx.save(); ctx.strokeStyle = CHART_COLORS.teal; ctx.lineWidth = 1.25; ctx.setLineDash([4, 3]); ctx.beginPath();
    if (horizontal) { const x = scales.x.getPixelForValue(value); ctx.moveTo(x, chartArea.top); ctx.lineTo(x, chartArea.bottom); }
    else { const y = scales.y.getPixelForValue(value); ctx.moveTo(chartArea.left, y); ctx.lineTo(chartArea.right, y); }
    ctx.stroke(); ctx.restore();
  } };
}
