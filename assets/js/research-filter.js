document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('research-filter');
  if (!input) return;

  const items = Array.from(document.querySelectorAll('.research-item'));
  const searchById = new Map();

  items.forEach((item) => {
    const paperId = item.getAttribute('data-paper-id') || '';
    const fallback = item.getAttribute('data-search') || '';
    if (paperId) {
      searchById.set(paperId, fallback);
    }
  });

  const indexUrl = input.dataset.indexUrl;
  if (indexUrl) {
    fetch(indexUrl)
      .then((response) => (response.ok ? response.json() : []))
      .then((rows) => {
        if (!Array.isArray(rows)) return;
        rows.forEach((row) => {
          if (!row || typeof row !== 'object') return;
          const id = String(row.id || '');
          const text = String(row.searchable_text || '');
          if (id && text) {
            searchById.set(id, text);
          }
        });
      })
      .catch(() => {
        // Keep fallback behavior if search index is unavailable.
      });
  }

  input.addEventListener('input', () => {
    const query = input.value.trim().toLowerCase();
    items.forEach((item) => {
      const paperId = item.getAttribute('data-paper-id') || '';
      const fallback = item.getAttribute('data-search') || '';
      const text = String(searchById.get(paperId) || fallback).toLowerCase();
      item.style.display = text.includes(query) ? '' : 'none';
    });
  });
});
