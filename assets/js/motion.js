const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
window.__reducedMotion = REDUCED;

if (!REDUCED) {
  initScrollReveal();
  initCounters();
  initScrollspy();
} else {
  document.documentElement.classList.add('reduced-motion');
}

function initScrollReveal() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

  document.querySelectorAll('.section, .demo-card, .panel, .gallery-card, .metric-row, .pipeline-row').forEach(el => {
    el.classList.add('reveal');
    observer.observe(el);
  });
}

function initCounters() {
  const counters = document.querySelectorAll('.metric-v');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const el = entry.target;
      const text = el.textContent;
      const numMatch = text.match(/^([\d,]+(?:\.\d+)?)$/);
      if (!numMatch) { observer.unobserve(el); return; }
      const target = parseFloat(numMatch[1].replace(/,/g, ''));
      if (isNaN(target)) { observer.unobserve(el); return; }
      const hasComma = numMatch[1].includes(',');
      const hasDecimal = numMatch[1].includes('.');
      const decimals = hasDecimal ? numMatch[1].split('.')[1].length : 0;
      const duration = 1200;
      const start = performance.now();
      function tick(now) {
        const t = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - t, 3);
        const val = target * eased;
        el.textContent = hasComma ? Math.round(val).toLocaleString('en-US') : val.toFixed(decimals);
        if (t < 1) requestAnimationFrame(tick);
        else el.textContent = hasComma ? Math.round(target).toLocaleString('en-US') : target.toFixed(decimals);
      }
      requestAnimationFrame(tick);
      observer.unobserve(el);
    });
  }, { threshold: 0.5 });

  counters.forEach(c => observer.observe(c));
}

function initScrollspy() {
  const nav = document.querySelector('[data-nav]');
  if (!nav) return;
  nav.style.display = 'flex';

  const links = nav.querySelectorAll('a');
  const sections = ['findings', 'spectrum', 'models', 'equity', 'abstract']
    .map(id => document.getElementById(id))
    .filter(Boolean);

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.id;
        links.forEach(link => {
          link.classList.toggle('active', link.getAttribute('href') === `#${id}`);
        });
      }
    });
  }, { rootMargin: '-30% 0px -60% 0px' });

  sections.forEach(s => observer.observe(s));
}
