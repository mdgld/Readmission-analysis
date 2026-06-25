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
  if (rate > baseline + 0.4) return getComputedStyle(document.documentElement).getPropertyValue('--risk').trim() || '#e8927c';
  if (rate < baseline - 0.4) return getComputedStyle(document.documentElement).getPropertyValue('--protect').trim() || '#7cc0a6';
  return 'rgba(255,255,255,.22)';
}

export const COHORT_RATE = 9.3;
export const COHORT_N = 2652;

if (typeof window !== 'undefined') {
  window.__fmt = { fmt, pct, fmtCI, fmtP, stars, logScale, pTwoSided, sigLevel, colorByDirection };
}
