const button = document.querySelector('.nav-toggle');
const nav = document.querySelector('[data-nav]');
const links = Array.from(nav.querySelectorAll('a'));
const chapters = links.map(link => document.querySelector(link.hash));

function closeMenu() {
  button.setAttribute('aria-expanded', 'false');
}

button.addEventListener('click', () => {
  button.setAttribute('aria-expanded', String(button.getAttribute('aria-expanded') !== 'true'));
});
nav.addEventListener('click', closeMenu);
document.addEventListener('click', event => {
  if (!event.target.closest('.masthead')) closeMenu();
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && button.getAttribute('aria-expanded') === 'true') {
    closeMenu();
    button.focus();
  }
});

function markChapter() {
  const top = document.querySelector('.site-header').getBoundingClientRect().height + 60;
  const current = chapters.filter(section => section.getBoundingClientRect().top <= top).pop();
  for (const link of links) {
    if (current && link.hash === '#' + current.id) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  }
}
const observer = new IntersectionObserver(markChapter, { rootMargin: '-10% 0px -80% 0px' });
for (const chapter of chapters) observer.observe(chapter);
