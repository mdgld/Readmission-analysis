const fmt = new Intl.NumberFormat('en-US');

function num(value, digits = 1) {
  const n = Number(value);
  if (!Number.isFinite(n)) return '—';
  return n.toFixed(digits);
}

function metric(label, value) {
  return `<div><dt>${label}</dt><dd>${value}</dd></div>`;
}

function renderBars(el, items, valueKey = 'rate', suffix = '%') {
  const max = Math.max(...items.map(d => Number(d[valueKey]) || 0), 1);
  const cells = items.map(d => {
    const value = Number(d[valueKey]) || 0;
    const width = Math.max(2, (value / max) * 100);
    const n = d.n ? ` <span class="muted">(n=${fmt.format(d.n)})</span>` : '';
    return `
      <div class="bar-label">${d.label}${n}</div>
      <div class="bar-track"><div class="bar-fill" style="width:${width}%"></div></div>
      <div class="bar-value">${num(value)}${suffix}</div>`;
  }).join('');
  el.innerHTML = `<div class="bar-list">${cells}</div>`;
}

function table(headers, rows) {
  return `
    <table>
      <thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead>
      <tbody>${rows.map(row => `<tr>${row.map(cell => `<td>${cell}</td>`).join('')}</tr>`).join('')}</tbody>
    </table>`;
}


function renderGallery(el, figures) {
  el.innerHTML = figures.map(fig => `
    <article class="figure-card">
      <a href="${fig.src}" target="_blank" rel="noopener">
        <img src="${fig.src}" alt="${fig.title}" loading="lazy" />
        <span>${fig.title}</span>
      </a>
    </article>
  `).join('');
}

async function main() {
  const res = await fetch('data.json');
  const data = await res.json();
  const s = data.summary;

  document.getElementById('snapshot').innerHTML = [
    metric('Patients', fmt.format(s.n)),
    metric('90-day readmission', `${s.readmission_rate}%`),
    metric('ICD-10-CM codes mapped', fmt.format(s.unique_icd_codes)),
    metric('Diagnosis records', fmt.format(s.diagnosis_records)),
    metric('Best out-of-fold AUC', num(s.best_oof_auc, 3)),
    metric('DSM-5 categories', fmt.format(s.dsm5_categories))
  ].join('');

  renderBars(document.getElementById('ageChart'), data.groups.age);
  renderBars(document.getElementById('genderChart'), data.groups.gender);
  renderBars(
    document.getElementById('fairnessChart'),
    data.fairness.map(d => ({
      label: d.Pairing,
      rate: Number(d['Equalized-odds gap (max|dTPR|,|dFPR|)']) * 100
    })),
    'rate',
    '% gap'
  );

  renderGallery(document.getElementById('figureGallery'), data.figures);
}

main().catch(err => {
  document.body.insertAdjacentHTML('afterbegin', `<pre style="padding:1rem;color:#fecaca">${err.stack || err}</pre>`);
});
