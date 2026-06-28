import { loadData } from './data.js';
import { pTwoSided, stars, sigLevel, COHORT_RATE } from './format.js';

const REDUCED = window.__reducedMotion || matchMedia('(prefers-reduced-motion: reduce)').matches;

document.addEventListener('portfolio:ready', renderSpectrum);

async function renderSpectrum() {
  let data;
  try { data = await loadData(); } catch { return; }
  const container = document.querySelector('[data-charts-spectrum]');
  if (!container) return;

  const spec = data.spectrum;
  const items = spec.items;
  const dxMax = spec.dx_max || 24;
  const p0 = COHORT_RATE / 100;

  const intro = document.querySelector('[data-spectrum-intro]');
  if (intro) intro.textContent = spec.prose_note;

  const controls = document.createElement('div');
  controls.style.cssText = 'display:flex;gap:.6rem;margin-bottom:1rem;flex-wrap:wrap;font-family:var(--mono);font-size:.72rem';
  controls.innerHTML = `
    <button class="spectrum-sort" data-sort="rate" style="padding:.4rem .7rem;border:1px solid var(--line);border-radius:6px;background:transparent;color:var(--text);cursor:pointer">Sort by rate</button>
    <button class="spectrum-sort" data-sort="n" style="padding:.4rem .7rem;border:1px solid var(--line);border-radius:6px;background:transparent;color:var(--muted);cursor:pointer">Sort by n</button>
    <button class="spectrum-filter" data-filter="sig" style="padding:.4rem .7rem;border:1px solid var(--line);border-radius:6px;background:transparent;color:var(--muted);cursor:pointer">Significant only</button>
    <button class="spectrum-filter" data-filter="all" style="padding:.4rem .7rem;border:1px solid var(--line);border-radius:6px;background:transparent;color:var(--text);cursor:pointer">All</button>
  `;
  container.innerHTML = '';
  container.appendChild(controls);

  const canvasWrap = document.createElement('div');
  const chartHeight = Math.max(560, items.length * 42);
  canvasWrap.style.cssText = `position:relative;height:${chartHeight}px`;
  const canvas = document.createElement('canvas');
  canvas.setAttribute('role', 'img');
  canvas.setAttribute('aria-label', `DSM-5 diagnostic spectrum: ${items.length} categories ranked by 90-day readmission rate, ranging from ${items[0].rate}% to ${items[items.length-1].rate}%. Cohort baseline ${COHORT_RATE}%.`);
  canvasWrap.appendChild(canvas);
  container.appendChild(canvasWrap);

  const legend = document.createElement('div');
  legend.style.cssText = 'display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:.7rem 1.3rem;margin-top:1.4rem;padding-top:1rem;border-top:1px solid var(--line-2);font-family:var(--mono);font-size:.7rem;color:var(--faint)';
  legend.innerHTML = `
    <span style="display:flex;align-items:center;gap:.45rem"><span style="width:1px;height:12px;background:var(--accent)"></span>cohort ${COHORT_RATE}%</span>
    <span style="display:flex;align-items:center;gap:.45rem"><span style="width:16px;height:8px;border-radius:2px;background:#e8927c"></span>significant</span>
    <span style="display:flex;align-items:center;gap:.45rem"><span style="width:16px;height:8px;border-radius:2px;background:rgba(152,163,186,.22)"></span>n.s.</span>
    <span style="color:var(--line)">·</span>
    <span>* p&lt;0.05 · ** p&lt;0.01 · *** p&lt;0.001</span>
    <span style="color:var(--line)">·</span>
    <span>vs cohort · two-proportion z-test</span>
  `;
  container.appendChild(legend);

  let currentItems = [...items];
  let sortBy = 'rate';
  let sigOnly = false;

  function getChartData() {
    let filtered = sigOnly
      ? items.filter(d => sigLevel(pTwoSided(d.readmitted / d.n, p0, d.n)) > 0)
      : [...items];
    filtered.sort((a, b) => sortBy === 'rate' ? b.rate - a.rate : b.n - a.n);
    return filtered;
  }

  function getStars(arr) {
    return arr.map(d => {
      const p = pTwoSided(d.readmitted / d.n, p0, d.n);
      return stars(p);
    });
  }

  function getColors(arr) {
    return arr.map(d => {
      const p = pTwoSided(d.readmitted / d.n, p0, d.n);
      const lvl = sigLevel(p);
      return lvl === 0 ? 'rgba(152,163,186,.22)' : ['#e8927c', '#e8927ccc', '#e8927c'][Math.min(lvl - 1, 2)] || '#e8927c';
    });
  }

  const chart = new Chart(canvas, {
    type: 'bar',
    data: {
      labels: getChartData().map((d, i) => `${d.label} ${getStars(getChartData())[i]}`.trim()),
      datasets: [{
        data: getChartData().map(d => d.rate),
        backgroundColor: getColors(getChartData()),
        borderRadius: 3,
        barPercentage: 0.75,
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      animation: REDUCED ? false : { duration: 600, easing: 'easeOutQuart' },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const d = getChartData()[ctx.dataIndex];
              const p = pTwoSided(d.readmitted / d.n, p0, d.n);
              const s = stars(p);
              return [`Rate: ${d.rate.toFixed(1)}%`, `n=${d.n}, readmit=${d.readmitted}`, s ? `p=${p.toFixed(4)} ${s}` : 'n.s.'];
            }
          }
        }
      },
      scales: {
        x: { max: dxMax, beginAtZero: true, grid: { color: 'rgba(255,255,255,.05)' }, ticks: { callback: v => v + '%' } },
        y: { grid: { display: false }, ticks: { font: { size: 10 }, autoSkip: false } }
      }
    },
    plugins: [{
      id: 'spectrumBaseline',
      afterDraw(chart) {
        const { ctx, chartArea, scales } = chart;
        const x = scales.x.getPixelForValue(COHORT_RATE);
        ctx.save();
        ctx.strokeStyle = '#6fb2f0';
        ctx.lineWidth = 1;
        ctx.globalAlpha = 0.55;
        ctx.beginPath();
        ctx.moveTo(x, chartArea.top);
        ctx.lineTo(x, chartArea.bottom);
        ctx.stroke();
        ctx.restore();
      }
    }]
  });

  function update() {
    const newData = getChartData();
    const newStars = getStars(newData);
    chart.data.labels = newData.map((d, i) => `${d.label} ${newStars[i]}`.trim());
    chart.data.datasets[0].data = newData.map(d => d.rate);
    chart.data.datasets[0].backgroundColor = getColors(newData);
    chart.update();
  }

  controls.querySelectorAll('.spectrum-sort').forEach(btn => {
    btn.addEventListener('click', () => {
      sortBy = btn.dataset.sort;
      controls.querySelectorAll('.spectrum-sort').forEach(b => { b.style.color = 'var(--muted)'; });
      btn.style.color = 'var(--text)';
      update();
    });
  });

  controls.querySelectorAll('.spectrum-filter').forEach(btn => {
    btn.addEventListener('click', () => {
      sigOnly = btn.dataset.filter === 'sig';
      controls.querySelectorAll('.spectrum-filter').forEach(b => { b.style.color = 'var(--muted)'; });
      btn.style.color = 'var(--text)';
      update();
    });
  });
}
