import './data.js';
import './format.js';
import './content.js';
import './charts-demographics.js';
import './charts-spectrum.js';
import './charts-models.js';
import './charts-equity.js';
import './gallery.js';
import './motion.js';

window.__reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

function init() {
  console.log('[portfolio] shell loaded');
  document.dispatchEvent(new CustomEvent('portfolio:ready'));
}
