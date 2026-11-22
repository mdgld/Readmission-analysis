import { loadData } from './data.js';
import { applyChartDefaults, chartScales, CHART_COLORS, COHORT_RATE, fmt, stars } from './format.js';

const REDUCED = window.__reducedMotion || matchMedia('(prefers-reduced-motion: reduce)').matches;

applyChartDefaults();
document.addEventListener('portfolio:ready', renderSpectrum);

async function renderSpectrum() {
  let data;
  try { data = await loadData(); } catch { return; }
  const container = document.querySelector('[data-charts-spectrum]');
  if (!container) return;

  const spec = data.spectrum;
  const intro = document.querySelector('[data-spectrum-intro]');
  if (intro) intro.textContent = spec.prose_note;

  container.innerHTML = `
    <div class="chart-toolbar" role="group" aria-label="Diagnostic spectrum controls">
      <span class="chart-toolbar-label">Order</span>
      <button class="chart-control is-active" type="button" data-sort="rate" aria-pressed="true">Rate</button>
      <button class="chart-control" type="button" data-sort="n" aria-pressed="false">Sample size</button>
      <span class="chart-toolbar-divider" aria-hidden="true"></span>
      <button class="chart-control" type="button" data-filter="sig" aria-pressed="false">BH q &lt; .05</button>
      <button class="chart-control is-active" type="button" data-filter="all" aria-pressed="true">All categories</button>
      <span class="chart-toolbar-status" role="status" aria-live="polite"></span>
    </div>
    <div class="chart-frame chart-frame--spectrum"><canvas role="img"></canvas></div>
    <div class="chart-legend" aria-label="Chart legend">
      <span><i class="legend-line"></i>Cohort ${COHORT_RATE}%</span>
      <span><i class="legend-swatch legend-swatch--risk"></i>BH q &lt; .05</span>
      <span><i class="legend-swatch legend-swatch--neutral"></i>BH q ≥ .05</span>
      <span>Multiple comparisons controlled with Benjamini–Hochberg q-values</span>
    </div>
    <p class="chart-note">The chart includes diagnoses recorded for at least 15 children. Each statistical test compares children with and without that diagnosis.</p>
  `;

  const canvas = container.querySelector('canvas');
  const frame = container.querySelector('.chart-frame');
  const status = container.querySelector('.chart-toolbar-status');
  let sortBy = 'rate';
  let significantOnly = false;
  let rows = selectRows();

  updateRowSummary();

  const chart = new Chart(canvas, {
    type: 'bar',
    data: dataset(rows),
    options: {
      indexAxis: 'y', responsive: true, maintainAspectRatio: false,
      animation: REDUCED ? false : { duration: 350 },
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: tooltipLines } } },
      scales: {
        x: { ...chartScales(), max: Math.max(spec.dx_max || 0, ...spec.items.map(item => item.rate)) + 4, beginAtZero: true, ticks: { ...chartScales().ticks, callback: value => `${value}%`, maxTicksLimit: 7 } },
        y: { ...chartScales(), grid: { display: false }, ticks: { ...chartScales().ticks, autoSkip: false, callback: rowLabel } },
      },
    },
    plugins: [cohortLine(), spectrumValues(() => rows)],
  });

  container.querySelectorAll('[data-sort]').forEach(button => button.addEventListener('click', () => {
    sortBy = button.dataset.sort;
    setActive(container.querySelectorAll('[data-sort]'), button);
    update();
  }));
  container.querySelectorAll('[data-filter]').forEach(button => button.addEventListener('click', () => {
    significantOnly = button.dataset.filter === 'sig';
    setActive(container.querySelectorAll('[data-filter]'), button);
    update();
  }));

  function selectRows() {
    const filtered = significantOnly ? spec.items.filter(item => qValue(item) < .05) : [...spec.items];
    return filtered.sort((a, b) => sortBy === 'rate' ? b.rate - a.rate : b.n - a.n);
  }

  function rowLabel(index) {
    const row = rows[index];
    const ctx = this.chart.ctx;
    const maxWidth = Math.min(165, this.maxWidth - 18);
    ctx.save();
    ctx.font = Chart.helpers.toFont(this.options.ticks.font).string;
    const label = wrapLabel(row.label, ctx, maxWidth);
    ctx.restore();
    if (sortBy === 'n') label.push(`n = ${fmt(row.n)}`);
    return label;
  }

  function dataset(items) {
    return { labels: items.map(item => item.label), datasets: [{ data: items.map(item => item.rate), backgroundColor: items.map(colorFor), borderRadius: 2, borderSkipped: false, barPercentage: .72, maxBarThickness: 25 }] };
  }

  function tooltipLines(context) {
    const item = rows[context.dataIndex];
    const comparison = comparisonValue(item);
    const eventLine = Number.isFinite(item.readmitted) ? `${item.readmitted} children readmitted out of ${item.n}` : `n=${item.n}`;
    const comparisonLine = Number.isFinite(comparison) ? `${Number.isFinite(item.q) ? 'q' : 'p'} ${comparison < .001 ? '< .001' : '= ' + comparison.toFixed(3)} ${stars(comparison)}` : 'No source comparison p/q reported';
    return [`${item.rate.toFixed(1)}% readmission rate`, eventLine, comparisonLine];
  }

  function updateRowSummary() {
    frame.style.setProperty('--chart-rows', Math.max(rows.length, 1));
    frame.classList.toggle('chart-frame--sample-sizes', sortBy === 'n');
    const order = sortBy === 'n' ? 'largest sample first' : 'highest rate first';
    const summary = rows.length ? `${rows.length} categories · ${order}` : 'No categories have a BH q-value below .05';
    status.textContent = summary;
    canvas.setAttribute('aria-label', `${summary}. ${spectrumAria(rows)}`);
  }

  function update() {
    rows = selectRows();
    const next = dataset(rows);
    chart.data.labels = next.labels;
    chart.data.datasets[0].data = next.datasets[0].data;
    chart.data.datasets[0].backgroundColor = next.datasets[0].backgroundColor;
    updateRowSummary();
    chart.resize();
    chart.update('none');
  }
}

function comparisonValue(item) {
  const value = item.q ?? item.p;
  return Number.isFinite(value) ? Number(value) : Number.NaN;
}

function qValue(item) {
  return Number.isFinite(item.q) ? Number(item.q) : Number.NaN;
}

function colorFor(item) {
  const comparison = comparisonValue(item);
  if (!Number.isFinite(comparison)) return CHART_COLORS.neutralSoft;
  if (!Number.isFinite(qValue(item)) || qValue(item) >= .05) return CHART_COLORS.neutral;
  return item.rate >= COHORT_RATE ? CHART_COLORS.risk : CHART_COLORS.protect;
}

function setActive(buttons, activeButton) {
  buttons.forEach(button => {
    const active = button === activeButton;
    button.classList.toggle('is-active', active);
    button.setAttribute('aria-pressed', String(active));
  });
}

function spectrumAria(items) {
  return `Diagnostic spectrum. ${items.map(item => `${item.label}: ${item.rate.toFixed(1)}%, n=${item.n}`).join('. ')}. Cohort rate: ${COHORT_RATE}%.`;
}

function wrapLabel(label, ctx, maxWidth) {
  const segments = label.match(/[^ -]+-?|[ -]+/g) ?? [];
  const lines = [];
  let line = '';
  for (const segment of segments) {
    const next = (line + segment).trimStart();
    if (line && ctx.measureText(next.trimEnd()).width > maxWidth) {
      lines.push(line.trimEnd());
      line = segment.trimStart();
    } else {
      line = next;
    }
  }
  if (line) lines.push(line.trimEnd());
  return lines;
}

function cohortLine() {
  return { id: 'spectrumCohortLine', afterDraw(chart) {
    const { ctx, chartArea, scales } = chart;
    const x = scales.x.getPixelForValue(COHORT_RATE);
    ctx.save(); ctx.strokeStyle = CHART_COLORS.teal; ctx.lineWidth = 1.25; ctx.setLineDash([4, 3]); ctx.beginPath(); ctx.moveTo(x, chartArea.top); ctx.lineTo(x, chartArea.bottom); ctx.stroke(); ctx.restore();
  } };
}

function spectrumValues(getRows) {
  return { id: 'spectrumValues', afterDatasetsDraw(chart) {
    const rows = getRows();
    const { ctx, scales } = chart;
    ctx.save(); ctx.font = '600 10px Inter, ui-sans-serif, system-ui, sans-serif'; ctx.fillStyle = CHART_COLORS.text; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
    rows.forEach((item, index) => ctx.fillText(`${item.rate.toFixed(1)}%`, scales.x.getPixelForValue(item.rate) + 5, scales.y.getPixelForTick(index)));
    ctx.restore();
  } };
}
