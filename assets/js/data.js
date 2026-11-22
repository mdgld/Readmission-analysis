let dataset;

export function loadData() {
  if (!dataset) {
    dataset = fetch('data.json').then(response => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    }).catch(error => {
      const notice = document.createElement('p');
      notice.className = 'data-error';
      notice.setAttribute('role', 'alert');
      notice.textContent = 'The study data could not be loaded. Reload the page to try again.';
      document.querySelector('main').prepend(notice);
      throw error;
    });
  }
  return dataset;
}
