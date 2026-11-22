import { loadData } from './data.js';

document.addEventListener('portfolio:ready', async () => {
  let data;
  try { data = await loadData(); } catch { return; }
  const gallery = document.querySelector('[data-gallery]');
  gallery.innerHTML = data.figures.map(figure => `
    <a class="gallery-card" href="${figure.file}" data-figure-id="${figure.id}" aria-label="Enlarge ${figure.title}">
      <span class="gallery-thumb"><img src="${figure.file}" alt="" loading="lazy"></span>
      <span class="gallery-body"><span class="gallery-title">${figure.title}</span><span class="gallery-arrow" aria-hidden="true">↗</span></span>
    </a>`).join('');

  gallery.addEventListener('click', event => {
    const link = event.target.closest('.gallery-card');
    if (!link || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    const title = link.querySelector('.gallery-title').textContent;
    const dialog = document.createElement('dialog');
    dialog.className = 'figure-dialog';
    dialog.setAttribute('aria-labelledby', 'active-figure');
    dialog.innerHTML = '<div class="figure-toolbar"><h3 id="active-figure"></h3><button type="button" autofocus>Close</button></div><img>';
    dialog.querySelector('h3').textContent = title;
    const img = dialog.querySelector('img');
    img.src = link.href;
    img.alt = title;
    const note = document.createElement('p');
    note.className = 'figure-caption';
    note.textContent = data.figures.find(figure => figure.id === link.dataset.figureId).caption;
    dialog.append(note);
    dialog.querySelector('button').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', click => {
      if (click.target !== dialog) return;
      const box = dialog.getBoundingClientRect();
      if (click.clientX < box.left || click.clientX > box.right || click.clientY < box.top || click.clientY > box.bottom) dialog.close();
    });
    dialog.addEventListener('close', () => {
      dialog.remove();
      link.focus({preventScroll: true});
    }, {once: true});
    document.body.append(dialog);
    dialog.showModal();
  });
});
