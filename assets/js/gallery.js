import { loadData } from './data.js';

document.addEventListener('portfolio:ready', renderGallery);

async function renderGallery() {
  let data;
  try { data = await loadData(); } catch { return; }
  const container = document.querySelector('[data-gallery]');
  if (!container) return;

  container.innerHTML = data.figures.map(fig => `
    <a class="gallery-card" href="${fig.file}" data-figure-id="${fig.id}" target="_blank" rel="noopener" aria-label="${fig.title} — open full size">
      <div class="gallery-thumb">
        <img src="${fig.file}" alt="${fig.title}" loading="lazy">
        <span class="gallery-tag">${fig.id}</span>
      </div>
      <div class="gallery-body">
        <div>
          <div class="gallery-title">${fig.title}</div>
          <div class="gallery-sub">${fig.tag}</div>
        </div>
        <span class="gallery-arrow" aria-hidden="true">\u2197</span>
      </div>
    </a>
  `).join('');

  container.querySelectorAll('.gallery-card').forEach(card => {
    card.addEventListener('click', (e) => {
      e.preventDefault();
      openLightbox(card.href, card.querySelector('.gallery-title').textContent, card.querySelector('img').alt);
    });
  });
}

function openLightbox(src, title, alt) {
  const overlay = document.createElement('div');
  overlay.className = 'lightbox-overlay';
  overlay.style.cssText = 'position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.92);display:flex;align-items:center;justify-content:center;flex-direction:column;padding:2rem';
  overlay.setAttribute('role', 'dialog');
  overlay.setAttribute('aria-modal', 'true');
  overlay.setAttribute('aria-label', `Figure: ${title}`);

  const img = document.createElement('img');
  img.src = src;
  img.alt = alt || title;
  img.style.cssText = 'max-width:90vw;max-height:80vh;object-fit:contain;background:#fff;border-radius:8px';

  const caption = document.createElement('div');
  caption.style.cssText = 'color:var(--muted);font-family:var(--mono);font-size:.82rem;margin-top:1rem;text-align:center';
  caption.textContent = title;

  const close = document.createElement('button');
  close.textContent = '\u2715 Close';
  close.style.cssText = 'position:absolute;top:1rem;right:1rem;padding:.5rem 1rem;background:var(--panel-2);color:var(--text);border:1px solid var(--line);border-radius:8px;cursor:pointer;font-family:var(--mono);font-size:.78rem';
  close.setAttribute('aria-label', 'Close figure viewer');

  overlay.appendChild(close);
  overlay.appendChild(img);
  overlay.appendChild(caption);
  document.body.appendChild(overlay);
  document.body.style.overflow = 'hidden';

  let lastFocused = document.activeElement;
  close.focus();

  function closeLightbox() {
    overlay.remove();
    document.body.style.overflow = '';
    if (lastFocused) lastFocused.focus();
  }

  close.addEventListener('click', closeLightbox);
  overlay.addEventListener('click', (e) => { if (e.target === overlay) closeLightbox(); });

  const trapHandler = (e) => {
    if (e.key === 'Escape') { e.preventDefault(); closeLightbox(); document.removeEventListener('keydown', trapHandler); }
  };
  document.addEventListener('keydown', trapHandler);

  const focusables = [close];
  const trapTab = (e) => {
    if (e.key !== 'Tab') return;
    const idx = focusables.indexOf(document.activeElement);
    if (e.shiftKey && idx === 0) { e.preventDefault(); focusables[focusables.length - 1].focus(); }
    else if (!e.shiftKey && idx === focusables.length - 1) { e.preventDefault(); focusables[0].focus(); }
  };
  overlay.addEventListener('keydown', trapTab);
}
