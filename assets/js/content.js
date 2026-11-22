import { loadData } from './data.js';
import { fmt } from './format.js';

document.addEventListener('portfolio:ready', async () => {
  let data;
  try { data = await loadData(); } catch { return; }

  const study = data.summary;
  document.querySelector('[data-cohort-rate]').innerHTML = `${study.readmission_rate}<span>%</span>`;
  document.querySelector('[data-cohort-count]').textContent = `${fmt(study.readmitted)} of ${fmt(study.n)} children`;
  drawCohort(document.querySelector('[data-cohort-plot]'), study);

  const facts = [
    ['Mean age', `${study.age_mean.toFixed(1)} years`],
    ['Diagnosis records', fmt(study.diagnosis_records)],
    ['Distinct ICD-10-CM codes', fmt(study.unique_icd_codes)],
    ['Diagnostic categories', fmt(study.dsm5_categories)]
  ];
  document.querySelector('[data-metrics-body]').innerHTML = facts.map(([label, value]) =>
    `<div><dt>${label}</dt><dd>${value}</dd></div>`
  ).join('');
  document.querySelector('[data-pipeline]').innerHTML = `<h3>From records to estimates</h3>
    <ol>${data.pipeline.map(step => `<li>${step.t}</li>`).join('')}</ol>`;
  document.querySelector('[data-abstract]').innerHTML = data.abstract.sections.map(section =>
    `<div class="abstract-section"><h3>${section.h}</h3><p>${section.body}</p></div>`
  ).join('');
  const objectives = document.querySelector('[data-objectives]');
  const list = document.createElement('ol');
  for (const item of data.abstract.objectives) {
    const row = document.createElement('li');
    row.textContent = item.t;
    list.append(row);
  }
  objectives.append(list);
});

function drawCohort(canvas, study) {
  const columns = 78;
  const rows = Math.ceil(study.n / columns);
  canvas.setAttribute('aria-label', `Each dot represents one child. ${fmt(study.readmitted)} of ${fmt(study.n)} children were readmitted within 90 days.`);
  function draw() {
    const width = canvas.clientWidth;
    if (!width) return;
    const step = width / columns;
    const height = canvas.clientHeight;
    const scale = window.devicePixelRatio || 1;
    canvas.width = Math.round(width * scale);
    canvas.height = Math.round(height * scale);
    const ctx = canvas.getContext('2d');
    ctx.scale(scale, scale);
    for (let i = 0; i < study.n; i++) {
      ctx.fillStyle = i < study.readmitted ? '#efbb77' : '#81a49a';
      ctx.beginPath();
      ctx.arc((Math.floor(i / rows) + .5) * step, ((i % rows) + .5) * height / rows, step * .31, 0, Math.PI * 2);
      ctx.fill();
    }
  }
  new ResizeObserver(draw).observe(canvas);
  draw();
}
