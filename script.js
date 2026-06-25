// === VIBE CODE GRAVEYARD — Entry Renderer ===

const ENTRIES = [];
const DESCRIPTION_MAX = 220; // Character budget per card description

// --- Fetch entries ---
async function loadEntries() {
  try {
    const response = await fetch('graveyard/_entries.json');
    if (!response.ok) return [];
    const raw = await response.json();
    // Truncate descriptions at word boundary + ellipsis
    return raw.map(entry => ({
      ...entry,
      description: truncateAtWord(entry.description, DESCRIPTION_MAX),
    }));
  } catch {
    return [];
  }
}

function truncateAtWord(text, maxLen) {
  if (!text || text.length <= maxLen) return text || '';
  const sliced = text.slice(0, maxLen);
  const lastSpace = sliced.lastIndexOf(' ');
  const cut = lastSpace > maxLen * 0.7 ? lastSpace : maxLen;
  return sliced.slice(0, cut) + '…';
}

// --- Read URL filter on load ---
function getInitialFilter() {
  const params = new URLSearchParams(window.location.search);
  const tool = params.get('tool');
  if (tool && document.querySelector(`.filter-btn[data-filter="${tool}"]`)) {
    return tool;
  }
  return 'all';
}

// --- Update URL when filter changes ---
function setFilterURL(filter) {
  const params = new URLSearchParams(window.location.search);
  if (filter === 'all') {
    params.delete('tool');
  } else {
    params.set('tool', filter);
  }
  const newURL = params.toString()
    ? `${window.location.pathname}?${params.toString()}`
    : window.location.pathname;
  window.history.replaceState({}, '', newURL);
}

// --- Render entries ---
function renderEntries(entries, filter = 'all') {
  const container = document.getElementById('entries');
  const counter = document.getElementById('grave-count');

  if (!container) return;

  const filtered = filter === 'all'
    ? entries
    : entries.filter(e => (e.tool || '').toLowerCase() === filter);

  // Update counter with filtered context
  if (filter === 'all') {
    counter.textContent = `${entries.length} startups in the ground and counting`;
  } else {
    counter.textContent = `${filtered.length} of ${entries.length} shown`;
  }

  if (filtered.length === 0) {
    container.innerHTML = `
      <p style="color: var(--text-dim); font-family: var(--mono); font-size: 0.85rem; grid-column: 1/-1; text-align: center; padding: 3rem 0;">
        No graves found for ${filter}. The graveyard is still digging.
      </p>`;
    return;
  }

  container.innerHTML = filtered.map((entry, i) => `
    <article class="entry-card" data-tool="${entry.tool || 'unknown'}" style="animation-delay: ${i * 0.04}s">
      <div class="entry-header">
        <span class="entry-name">${entry.name || 'Unknown'}</span>
        <span class="entry-status status-${(entry.status || 'active').toLowerCase()}">${entry.status || 'Active'}</span>
      </div>
      <span class="entry-tool">${entry.tool || 'AI'}</span>
      ${entry.description
        ? `<p class="entry-description">${entry.description}</p>`
        : ''}
      <div class="entry-meta">
        <span class="entry-date">${entry.date || ''}</span>
        ${entry.source ? `<a href="${entry.source}" target="_blank" rel="noopener" class="entry-link">Source ↗</a>` : ''}
      </div>
    </article>
  `).join('');
}

// --- Filter buttons ---
function initFilters() {
  const initialFilter = getInitialFilter();

  // Set active state from URL
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.filter === initialFilter);
  });

  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-pressed', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-pressed', 'true');
      const filter = btn.dataset.filter;
      setFilterURL(filter);
      renderEntries(ENTRIES, filter);
    });
  });
}

// --- Init ---
document.addEventListener('DOMContentLoaded', async () => {
  ENTRIES.push(...await loadEntries());
  const initialFilter = getInitialFilter();
  renderEntries(ENTRIES, initialFilter);
  initFilters();
});
