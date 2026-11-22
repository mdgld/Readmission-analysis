const _intfmt = new Intl.NumberFormat('en-US');

export function fmt(n) {
  return _intfmt.format(Number(n));
}

export function pct(n, digits = 1) {
  return `${Number(n).toFixed(digits)}%`;
}

export function fmtCI(lo, hi) {
  return `${Number(lo).toFixed(2)}\u2013${Number(hi).toFixed(2)}`;
}

export function fmtP(p) {
  if (p < 0.001) return '<0.001';
  return Number(p).toFixed(3);
}

export function stars(p) {
  if (p < 0.001) return '***';
  if (p < 0.01) return '**';
  if (p < 0.05) return '*';
  return '';
}

export function logScale(or, lo = 0.6, hi = 3.0) {
  return ((Math.log(or) - Math.log(lo)) / (Math.log(hi) - Math.log(lo))) * 100;
}

export function pTwoSided(phat, p0, n) {
  const se = Math.sqrt((p0 * (1 - p0)) / n);
  const z = Math.abs((phat - p0) / se);
  const t = 1 / (1 + 0.2316419 * z);
  const d = 0.3989423 * Math.exp((-z * z) / 2);
  const upper = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));
  return 2 * upper;
}

export function sigLevel(p) {
  if (p < 0.001) return 3;
  if (p < 0.01) return 2;
  if (p < 0.05) return 1;
  return 0;
}

export function colorByDirection(rate, baseline = 9.3) {
  if (rate > baseline + 0.4) return CHART_COLORS.risk;
  if (rate < baseline - 0.4) return CHART_COLORS.protect;
  return CHART_COLORS.neutral;
}

export const COHORT_RATE = 9.3;
export const COHORT_N = 2652;

export const CHART_COLORS = Object.freeze({
  text: '#182e2c',
  muted: '#536661',
  line: '#d5ddd6',
  grid: 'rgba(83, 102, 97, .16)',
  paper: '#fbfcf8',
  teal: '#12655e',
  tealSoft: '#8fb9b1',
  risk: '#985037',
  protect: '#12655e',
  neutral: '#a8b3ae',
  neutralSoft: '#dfe5df',
  caution: '#9a6a2f',
});

export function chartScales() {
  return {
    grid: { color: CHART_COLORS.grid, drawBorder: false },
    border: { color: CHART_COLORS.line },
    ticks: {
      color: CHART_COLORS.muted,
      font: { family: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif", size: 11 },
    },
  };
}

export function applyChartDefaults() {
  if (typeof Chart === 'undefined') return;
  Chart.defaults.color = CHART_COLORS.muted;
  Chart.defaults.borderColor = CHART_COLORS.line;
  Chart.defaults.font.family = "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
  Chart.defaults.font.size = 11;
  Chart.defaults.plugins.tooltip.backgroundColor = CHART_COLORS.text;
  Chart.defaults.plugins.tooltip.titleColor = '#fff';
  Chart.defaults.plugins.tooltip.bodyColor = '#fff';
  Chart.defaults.plugins.tooltip.cornerRadius = 3;
  Chart.defaults.plugins.tooltip.padding = 10;
}

if (typeof window !== 'undefined') {
  window.__fmt = { fmt, pct, fmtCI, fmtP, stars, logScale, pTwoSided, sigLevel, colorByDirection };
}
