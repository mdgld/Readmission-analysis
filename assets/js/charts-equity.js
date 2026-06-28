import { loadData } from './data.js';

const REDUCED = window.__reducedMotion || matchMedia('(prefers-reduced-motion: reduce)').matches;

document.addEventListener('portfolio:ready', renderEquity);

async function renderEquity() {
  let data;
  try { data = await loadData(); } catch { return; }

  const equityEl = document.querySelector('[data-charts-equity]');
  const explorerEl = document.querySelector('[data-subgroup-explorer]');
  const proseEl = document.querySelector('[data-equity-prose]');
  if (!equityEl) return;

  if (proseEl) {
    proseEl.innerHTML = `
      <h2 style="font-size:clamp(1.4rem,2.2vw,1.9rem);letter-spacing:-.02em;font-weight:600;margin:0 0 1rem">Surface subgroup disparities before deployment</h2>
      <p style="color:var(--muted);line-height:1.7;margin:0 0 1rem">Equalized-odds gaps quantify how unevenly errors fall across subgroups. Age and ACE strata show the widest gaps — equity-aware validation should be a precondition to implementation.</p>
      <p style="color:var(--muted);line-height:1.7;margin:0 0 1rem">A model with respectable aggregate AUC can still systematically over- or under-flag a subgroup. Reporting the worst-case gap alongside the headline metric frames bias mitigation as the crucial calibration step that it is.</p>
      <p style="color:var(--faint);line-height:1.7;margin:0;font-size:.9rem;font-family:var(--mono)">${data.equity.metric_note}</p>
    `;
  }

  renderFairness(equityEl, data.equity.fairness);
  if (explorerEl) renderExplorer(explorerEl, data.equity.subgroups);
}

function renderFairness(container, fairness) {
  const fairMax = 30;
  container.innerHTML = `
    <div style="display:grid;gap:1.5rem">
      ${fairness.map(b => `
        <div style="display:grid;gap:.45rem">
          <div style="display:flex;align-items:baseline;justify-content:space-between;gap:1rem">
            <span style="font-size:.88rem;color:var(--text)">${b.label}</span>
            <span style="font-family:var(--mono);font-size:.82rem;color:var(--warn);font-variant-numeric:tabular-nums">${b.gap.toFixed(1)}%</span>
          </div>
          <div style="position:relative;height:.55rem;background:rgba(255,255,255,.05);border-radius:3px">
            <div style="position:absolute;inset:0 auto 0 0;width:${Math.max(3, b.gap / fairMax * 100)}%;background:var(--warn);border-radius:3px;opacity:.85"></div>
          </div>
          <span style="font-family:var(--mono);font-size:.66rem;color:var(--faint)">AUC gap ${b.auc_gap.toFixed(1)} pt</span>
        </div>
      `).join('')}
    </div>
  `;
}

function renderExplorer(container, subgroups) {
  container.innerHTML = `
    <div style="display:flex;align-items:baseline;justify-content:space-between;gap:1rem;margin-bottom:1rem">
      <h3 style="font-family:var(--mono);font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;color:var(--faint);margin:0">Subgroup explorer</h3>
      <span style="font-family:var(--mono);font-size:.64rem;color:var(--faint)">${subgroups.length} subgroups · 3 models</span>
    </div>
    <div style="display:flex;gap:.6rem;flex-wrap:wrap;margin-bottom:1rem">
      <select id="subgroup-select" style="padding:.4rem .7rem;border:1px solid var(--line);border-radius:6px;background:var(--bg-2);color:var(--text);font-family:var(--mono);font-size:.78rem;cursor:pointer">
        ${subgroups.map((s, i) => `<option value="${i}">${s.label} (n=${s.n})</option>`).join('')}
      </select>
    </div>
    <div id="subgroup-readout" style="display:grid;gap:.8rem"></div>
    <div style="position:relative;margin-top:1rem"><canvas role="img" aria-label="Subgroup AUC comparison chart" style="max-height:200px"></canvas></div>
  `;

  const select = container.querySelector('#subgroup-select');
  const readout = container.querySelector('#subgroup-readout');
  const canvas = container.querySelector('canvas');

  const chart = new Chart(canvas, {
    type: 'bar',
    data: { labels: ['CatBoost', 'Random Forest', 'Logistic'], datasets: [{ data: [0, 0, 0], backgroundColor: ['#6fb2f0', '#7cc0a6', '#e8927c'], borderRadius: 3 }] },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: REDUCED ? false : { duration: 400 },
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: (ctx) => `AUC ${ctx.parsed.y.toFixed(3)}` } } },
      scales: { y: { min: 0.5, max: 0.75, grid: { color: 'rgba(255,255,255,.05)' }, ticks: { callback: v => v.toFixed(2) } }, x: { grid: { display: false } } }
    }
  });

  function update() {
    const s = subgroups[parseInt(select.value)];
    const fmtAuc = (v, color) => v == null
      ? `<div style="color:var(--faint);font-size:1rem">\u2014</div>`
      : `<div style="color:${color};font-size:1rem">${v.toFixed(3)}</div>`;
    readout.innerHTML = `
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:.6rem;font-family:var(--mono);font-size:.82rem">
        <div style="padding:.6rem .8rem;border:1px solid var(--line);border-radius:8px"><div style="font-size:.62rem;color:var(--faint);text-transform:uppercase">N</div><div style="color:var(--text);font-size:1rem">${s.n}</div></div>
        <div style="padding:.6rem .8rem;border:1px solid var(--line);border-radius:8px"><div style="font-size:.62rem;color:var(--faint);text-transform:uppercase">Readmit rate</div><div style="color:var(--text);font-size:1rem">${s.readmit_rate}</div></div>
        <div style="padding:.6rem .8rem;border:1px solid var(--line);border-radius:8px"><div style="font-size:.62rem;color:var(--faint);text-transform:uppercase">CatBoost AUC</div>${fmtAuc(s.auc_catboost, 'var(--accent)')}</div>
        <div style="padding:.6rem .8rem;border:1px solid var(--line);border-radius:8px"><div style="font-size:.62rem;color:var(--faint);text-transform:uppercase">RF AUC</div>${fmtAuc(s.auc_rf, 'var(--protect)')}</div>
        <div style="padding:.6rem .8rem;border:1px solid var(--line);border-radius:8px"><div style="font-size:.62rem;color:var(--faint);text-transform:uppercase">LR AUC</div>${fmtAuc(s.auc_lr, 'var(--risk)')}</div>
      </div>
    `;
    chart.data.datasets[0].data = [s.auc_catboost ?? null, s.auc_rf ?? null, s.auc_lr ?? null];
    chart.update();
  }

  select.addEventListener('change', update);
  update();
}
