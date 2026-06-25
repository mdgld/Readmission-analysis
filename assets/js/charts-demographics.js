import { loadData } from './data.js';
import { pTwoSided, stars, sigLevel, colorByDirection, COHORT_RATE } from './format.js';

const REDUCED = window.__reducedMotion || matchMedia('(prefers-reduced-motion: reduce)').matches;

if (typeof Chart !== 'undefined') {
  Chart.defaults.color = '#cbd5e1';
  Chart.defaults.borderColor = 'rgba(255,255,255,.09)';
  Chart.defaults.font.family = "'Geist Mono', ui-monospace, monospace";
  Chart.defaults.font.size = 11;
}

document.addEventListener('portfolio:ready', renderDemographics);

async function renderDemographics() {
  let data;
  try { data = await loadData(); } catch { return; }
  const container = document.querySelector('[data-charts-demographics]');
  if (!container) return;

  const groups = data.findings.groups;
  const groupStats = data.findings.groupStats;
  const demoMax = data.findings.demo_max || 15;

  const panels = [
    { key: 'age', title: 'By age band', cls: 'demo-card demo-card--wide', showR: false, footnote: '\u2020 Unit age cap is 12; 12-year-olds aging out of eligibility cannot be readmitted to this site, which is a plausible explanation of the observed rate depression.' },
    { key: 'gender', title: 'By gender identity', cls: 'demo-card', showR: true, stats: groupStats.gender },
    { key: 'cssrs', title: 'By C-SSRS flag', cls: 'demo-card', showR: true, stats: groupStats.cssrs },
    { key: 'insurance', title: 'By insurance', cls: 'demo-card', showR: true, stats: groupStats.insurance, note: data.findings.groups.insurance_note },
    { key: 'restraint', title: 'By physical restraint', cls: 'demo-card', showR: true, stats: groupStats.restraint },
  ];

  container.innerHTML = '';
  for (const p of panels) {
    const items = groups[p.key];
    if (!items) continue;
    const card = document.createElement('div');
    card.className = p.cls;

    const h3 = document.createElement('h3');
    h3.className = 'demo-card-title';
    h3.textContent = p.title;
    if (p.note) {
      const note = document.createElement('span');
      note.style.cssText = 'font-family:var(--mono);font-size:.6rem;color:var(--faint);margin-left:.6rem;font-weight:400';
      note.textContent = p.note;
      h3.appendChild(note);
    }
    card.appendChild(h3);

    const canvas = document.createElement('canvas');
    canvas.setAttribute('role', 'img');
    const ariaParts = items.map(d => `${d.label} ${d.rate.toFixed(1)}% (n=${d.n})`);
    canvas.setAttribute('aria-label', `Readmission rate by ${p.title.toLowerCase()}: ${ariaParts.join(', ')}. Cohort baseline ${COHORT_RATE}%.`);
    canvas.style.maxHeight = p.key === 'age' ? '260px' : '160px';
    card.appendChild(canvas);

    if (p.stats) {
      const foot = document.createElement('div');
      foot.className = 'demo-foot';
      foot.innerHTML = `<span>OR <span>${p.stats.or}</span></span><span>95% CI <span>${p.stats.ci}</span></span><span>p <span>${p.stats.p}</span></span>`;
      card.appendChild(foot);
    }

    if (p.footnote) {
      const fn = document.createElement('p');
      fn.style.cssText = 'margin:1.2rem 0 0;padding-top:.9rem;border-top:1px solid var(--line-2);font-family:var(--mono);font-size:.64rem;line-height:1.5;color:var(--faint)';
      fn.innerHTML = `<span style="color:var(--accent)">\u2020</span> ${p.footnote}`;
      card.appendChild(fn);
    }

    container.appendChild(card);

    const labels = items.map(d => d.label);
    const rates = items.map(d => d.rate);
    const p0 = COHORT_RATE / 100;
    const colors = items.map(d => {
      const p = pTwoSided(d.readmitted / d.n, p0, d.n);
      const lvl = sigLevel(p);
      if (lvl === 0) return 'rgba(255,255,255,.22)';
      return d.rate >= COHORT_RATE ? '#e8927c' : '#7cc0a6';
    });

    new Chart(canvas, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          data: rates,
          backgroundColor: colors,
          borderRadius: 3,
          barPercentage: 0.7,
        }]
      },
      options: {
        indexAxis: p.key === 'age' ? 'y' : 'x',
        responsive: true,
        maintainAspectRatio: false,
        animation: REDUCED ? false : { duration: 600, easing: 'easeOutQuart' },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const d = items[ctx.dataIndex];
                const p = pTwoSided(d.readmitted / d.n, p0, d.n);
                const s = stars(p);
                return [`Rate: ${d.rate.toFixed(1)}%`, `n=${d.n}, readmit=${d.readmitted}`, s ? `p=${p.toFixed(4)} ${s}` : 'n.s.'];
              }
            }
          },
          annotation: {}
        },
        scales: {
          x: {
            max: demoMax,
            beginAtZero: true,
            grid: { color: 'rgba(255,255,255,.05)' },
            ticks: { callback: (v) => v + '%' }
          },
          y: {
            grid: { display: false },
            ticks: { font: { size: 10 } }
          }
        }
      },
      plugins: [baselineLinePlugin(COHORT_RATE, demoMax)]
    });
  }
}

function baselineLinePlugin(baseline, maxVal) {
  return {
    id: 'baselineLine',
    afterDraw(chart) {
      const { ctx, chartArea, scales } = chart;
      const xScale = scales.x;
      if (!xScale) return;
      const x = xScale.getPixelForValue(baseline);
      ctx.save();
      ctx.strokeStyle = '#6fb2f0';
      ctx.lineWidth = 1;
      ctx.globalAlpha = 0.6;
      ctx.beginPath();
      ctx.moveTo(x, chartArea.top);
      ctx.lineTo(x, chartArea.bottom);
      ctx.stroke();
      ctx.restore();
    }
  };
}
