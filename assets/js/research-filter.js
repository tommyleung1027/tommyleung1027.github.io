document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('research-filter');
  if (!input) return;

  const items = Array.from(document.querySelectorAll('.research-item'));
  input.addEventListener('input', () => {
    const q = input.value.trim().toLowerCase();
    items.forEach((item) => {
      const text = (item.getAttribute('data-search') || '').toLowerCase();
      item.style.display = text.includes(q) ? '' : 'none';
    });
  });
});
