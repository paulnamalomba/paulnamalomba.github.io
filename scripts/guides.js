const search = document.querySelector('[data-guide-search]');
const filters = [...document.querySelectorAll('[data-guide-filter]')];
const cards = [...document.querySelectorAll('[data-guide-card]')];
const count = document.querySelector('[data-result-count]');
const empty = document.querySelector('[data-empty-state]');
let activeCategory = 'all';

const applyFilters = () => {
  const query = (search?.value || '').trim().toLowerCase();
  let visible = 0;
  cards.forEach((card) => {
    const matchesCategory = activeCategory === 'all' || card.dataset.category === activeCategory;
    const matchesQuery = !query || card.textContent.toLowerCase().includes(query);
    card.hidden = !(matchesCategory && matchesQuery);
    if (!card.hidden) visible += 1;
  });
  if (count) count.textContent = `${visible} guide${visible === 1 ? '' : 's'}`;
  empty?.classList.toggle('visible', visible === 0);
};

search?.addEventListener('input', applyFilters);
filters.forEach((button) => button.addEventListener('click', () => {
  activeCategory = button.dataset.guideFilter;
  filters.forEach((item) => item.classList.toggle('active', item === button));
  applyFilters();
}));
applyFilters();
