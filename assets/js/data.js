let _cache = null;

export async function loadData() {
  if (_cache) return _cache;
  try {
    const res = await fetch('data.json');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    _cache = await res.json();
    return _cache;
  } catch (err) {
    showDataError(err);
    throw err;
  }
}

function showDataError(err) {
  const banner = document.createElement('div');
  banner.setAttribute('data-error', '');
  banner.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:9999;padding:1rem;background:#e8927c;color:#08111c;font-family:monospace;font-size:.85rem;text-align:center';
  banner.textContent = `Failed to load data.json: ${err.message}. The page cannot render charts without data.`;
  document.body.prepend(banner);
}

if (typeof window !== 'undefined') {
  window.loadData = loadData;
}
