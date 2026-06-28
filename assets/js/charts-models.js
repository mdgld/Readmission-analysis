import { loadData } from './data.js';
import { logScale } from './format.js';

const REDUCED = window.__reducedMotion || matchMedia('(prefers-reduced-motion: reduce)').matches;

document.addEventListener('portfolio:ready', renderModels);

async function renderModels() {
  let data;
  try { data = await loadData(); } catch { return; }

  const forestEl = document.querySelector('[data-charts-forest]');
  const modelsEl = document.querySelector('[data-charts-models]');
  const readEl = document.querySelector('[data-clinical-read]');
  if (!forestEl || !modelsEl) return;

  if (readEl) {
    readEl.innerHTML = `<span class="clinical-read-label">CLINICAL READ</span><p class="clinical-read-text">${data.models.clinical_read}</p>`;
  }

  renderForest(forestEl, data.models.forest);
  renderAUC(modelsEl, data.models);
}

function renderForest(container, forest) {
  container.innerHTML = `
    <div style="display:flex;flex-direction:column;height:100%">
      <div style="display:flex;align-items:baseline;justify-content:space-between;gap:1rem;margin-bottom:1rem">
        <h3 style="font-size:1.02rem;font-weight:600;margin:0">Independent predictors of readmission</h3>
        <span style="font-family:var(--mono);font-size:.68rem;color:var(--faint)">multivariable logistic regression</span>
      </div>
      <div style="position:relative;flex:1 1 auto;min-height:280px"><canvas role="img" aria-label="Forest plot: ${forest.length} predictors with odds ratios and 95% confidence intervals on log scale, OR=1 reference line."></canvas></div>
      <div style="font-family:var(--mono);font-size:.66rem;color:var(--faint);text-align:center;margin-top:.4rem">odds ratio (log scale) · point estimate, line = 95% CI</div>
      <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:.4rem .9rem;margin-top:.4rem;padding-top:.6rem;border-top:1px solid var(--line-2);font-family:var(--mono);font-size:.66rem;color:var(--faint)">
        <span><span style="color:var(--risk);font-weight:600">*</span> p&lt;.05</span>
        <span><span style="color:var(--risk);font-weight:600">**</span> p&lt;.01</span>
        <span><span style="color:var(--risk);font-weight:600">***</span> p&lt;.001</span>
        <span><span style="color:var(--risk)">red</span> = risk ↑</span>
        <span><span style="color:var(--protect)">green</span> = protective ↓</span>
        <span><span style="color:rgba(255,255,255,.32)">grey</span> = not significant</span>
        <span>† patients &gt;12 cannot be readmitted to this unit; ceiling effect may inflate the protective association for older age</span>
      </div>
    </div>
  `;
  const canvas = container.querySelector('canvas');

  const fColor = { risk: '#e8927c', protect: '#7cc0a6', null: 'rgba(255,255,255,.32)' };

  new Chart(canvas, {
    type: 'bar',
    data: {
      labels: forest.map(f => f.kind === 'null' ? f.label : `${f.label} ${f.stars}`),
      datasets: [{
        data: forest.map(f => f.or),
        backgroundColor: forest.map(f => fColor[f.kind] || fColor.null),
        borderRadius: 3,
        barPercentage: 0.3,
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      animation: REDUCED ? false : { duration: 700 },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const f = forest[ctx.dataIndex];
              return [`${f.label}`, `OR ${f.or.toFixed(2)} [${f.lo.toFixed(2)}\u2013${f.hi.toFixed(2)}]`, `p=${f.p < 0.001 ? '<0.001' : f.p.toFixed(3)} ${f.stars}`];
            }
          }
        }
      },
      scales: {
        x: {
          type: 'logarithmic',
          min: 0.25,
          max: 3.0,
          grid: { color: 'rgba(255,255,255,.05)' },
          afterBuildTicks: (axis) => {
            axis.ticks = [0.25, 0.5, 1, 2, 3].map(v => ({ value: v }));
          },
          ticks: { callback: v => v }
        },
        y: { grid: { display: false }, ticks: { font: { size: 10 }, autoSkip: false } }
      }
    },
    plugins: [forestWhiskerPlugin(forest, fColor), orRefLinePlugin()]
  });
}

function forestWhiskerPlugin(forest, fColor) {
  return {
    id: 'forestWhiskers',
    afterDatasetsDraw(chart) {
      const { ctx, scales } = chart;
      const xScale = scales.x;
      const yScale = scales.y;
      ctx.save();
      forest.forEach((f, i) => {
        const y = yScale.getPixelForTick(i);
        const color = fColor[f.kind] || fColor.null;
        const loX = xScale.getPixelForValue(f.lo);
        const hiX = xScale.getPixelForValue(f.hi);
        const ptX = xScale.getPixelForValue(f.or);
        ctx.strokeStyle = color;
        ctx.fillStyle = color;
        // Two-pass tube: dark outline then colored line, so the whisker is visible against the bar AND the dark bg.
        ctx.globalAlpha = 1;
        ctx.strokeStyle = '#0b0d13';
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.moveTo(loX, y);
        ctx.lineTo(hiX, y);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(loX, y - 6);
        ctx.lineTo(loX, y + 6);
        ctx.moveTo(hiX, y - 6);
        ctx.lineTo(hiX, y + 6);
        ctx.stroke();

        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(loX, y);
        ctx.lineTo(hiX, y);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(loX, y - 5);
        ctx.lineTo(loX, y + 5);
        ctx.moveTo(hiX, y - 5);
        ctx.lineTo(hiX, y + 5);
        ctx.stroke();
        ctx.globalAlpha = 1;
        ctx.fillStyle = '#0b0d13';
        ctx.fillRect(ptX - 4.5, y - 4.5, 9, 9);
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.strokeRect(ptX - 4.5, y - 4.5, 9, 9);
      });
      ctx.restore();
    }
  };
}

function orRefLinePlugin() {
  return {
    id: 'orRefLine',
    afterDraw(chart) {
      const { ctx, chartArea, scales } = chart;
      const x = scales.x.getPixelForValue(1);
      ctx.save();
      ctx.strokeStyle = 'rgba(255,255,255,.32)';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([5, 4]);
      ctx.beginPath();
      ctx.moveTo(x, chartArea.top);
      ctx.lineTo(x, chartArea.bottom);
      ctx.stroke();
      ctx.restore();
    }
  };
}

function renderAUC(container, models) {
  const aucData = models.auc;
  const delta = models.optimism_delta;

  container.innerHTML = `
    <div style="display:flex;flex-direction:column;height:100%">
      <div style="display:flex;align-items:baseline;justify-content:space-between;gap:1rem;margin-bottom:1.2rem">
        <h3 style="font-size:1.02rem;font-weight:600;margin:0">Apparent vs. honest AUC</h3>
      </div>
      <div style="display:flex;gap:1rem;margin-bottom:1rem;font-family:var(--mono);font-size:.72rem">
        <button id="auc-toggle" style="padding:.4rem .8rem;border:1px solid var(--accent);border-radius:6px;background:rgba(111,178,240,.1);color:var(--accent);cursor:pointer;font-family:inherit">Showing: Apparent</button>
      </div>
      <div style="position:relative;flex:1 1 auto;min-height:280px"><canvas role="img" aria-label="Model AUC comparison: Logistic, Random Forest, CatBoost. Toggle between apparent and out-of-fold (honest) AUC."></canvas></div>
      <div style="font-family:var(--mono);font-size:.66rem;color:var(--faint);text-align:center;margin-top:.6rem">AUROC · 5-fold CV · bootstrap optimism correction (1,000 iterations)</div>
      <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:.5rem 1.2rem;margin-top:.6rem;padding-top:.8rem;border-top:1px solid var(--line-2);font-family:var(--mono);font-size:.66rem;color:var(--faint)">
        <span>Logistic <span style="color:var(--text)">\u0394=${delta.Logistic.toFixed(3)}</span></span>
        <span>Random Forest <span style="color:var(--text)">\u0394=${delta['Random Forest'].toFixed(3)}</span></span>
        <span>CatBoost <span style="color:var(--risk);font-weight:600">\u0394=${delta.CatBoost.toFixed(3)}</span></span>
        <span style="color:var(--line)">·</span>
        <span>\u0394 = apparent \u2212 out-of-fold (optimism)</span>
      </div>
    </div>
  `;

  const canvas = container.querySelector('canvas');
  const toggle = container.querySelector('#auc-toggle');
  let showingApparent = true;

  const apparentColors = ['rgba(255,255,255,.16)', '#6fb2f0', '#6fb2f0'];
  const honestColors   = ['rgba(255,255,255,.16)', '#d8b06a', '#d8b06a'];

  const chart = new Chart(canvas, {
    type: 'bar',
    data: {
      labels: aucData.map(m => m.name),
      datasets: [{
        data: aucData.map(m => m.apparent),
        backgroundColor: apparentColors,
        borderRadius: 3,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: REDUCED ? false : { duration: 500 },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const m = aucData[ctx.dataIndex];
              return [`${m.name}`, `Apparent: ${m.apparent.toFixed(3)}`, `Corrected: ${m.corrected.toFixed(3)}`, `OOF: ${m.oof.toFixed(3)}`];
            }
          }
        }
      },
      scales: {
        y: {
          min: 0.5,
          max: 0.95,
          grid: { color: 'rgba(255,255,255,.05)' },
          afterBuildTicks: (axis) => {
            axis.ticks = [0.5, 0.6, 0.7, 0.8, 0.9].map(v => ({ value: v }));
          },
          ticks: { callback: v => v.toFixed(2) }
        },
        x: { grid: { display: false } }
      }
    }
  });

  function updateChart() {
    const values = showingApparent
      ? aucData.map(m => m.apparent)
      : aucData.map(m => m.oof);
    chart.data.datasets[0].data = values;
    chart.data.datasets[0].backgroundColor = showingApparent ? apparentColors : honestColors;
    toggle.textContent = showingApparent ? 'Showing: Apparent' : 'Showing: Honest (OOF)';
    toggle.style.background = showingApparent ? 'rgba(111,178,240,.1)' : 'rgba(216,176,106,.1)';
    toggle.style.borderColor = showingApparent ? 'var(--accent)' : 'var(--warn)';
    toggle.style.color = showingApparent ? 'var(--accent)' : 'var(--warn)';
    chart.update();
  }

  toggle.addEventListener('click', () => {
    showingApparent = !showingApparent;
    updateChart();
  });
  toggle.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle.click(); }
  });
}
