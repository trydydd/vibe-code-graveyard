// === VIBE CODE GRAVEYARD — Entry Renderer ===

const ENTRIES = [];
const DESCRIPTION_MAX = 220; // Character budget per card description

function escapeHtml(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// Reject non-http(s) URLs to prevent javascript: injection
function safeUrl(url) {
  if (!url) return null;
  try {
    const u = new URL(url);
    return (u.protocol === 'https:' || u.protocol === 'http:') ? url : null;
  } catch { return null; }
}

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
    : entries.filter(e => (e.tool || '').toLowerCase().includes(filter));

  // Update counter with filtered context
  if (counter) {
    if (filter === 'all') {
      counter.textContent = `${entries.length} startups in the ground and counting`;
    } else {
      counter.textContent = `${filtered.length} of ${entries.length} shown`;
    }
  }

  if (filtered.length === 0) {
    container.innerHTML = `
      <p class="no-results">No graves found for ${escapeHtml(filter)}. The graveyard is still digging.</p>`;
    return;
  }

  container.innerHTML = filtered.map((entry, i) => {
    const name = escapeHtml(entry.name || 'Unknown');
    const status = escapeHtml(entry.status || 'Active');
    const statusClass = escapeHtml((entry.status || 'active').toLowerCase());
    const tool = escapeHtml(entry.tool || 'AI');
    const toolAttr = escapeHtml(entry.tool || 'unknown');
    const description = escapeHtml(entry.description || '');
    const date = escapeHtml(entry.date || '');
    const sourceUrl = safeUrl(entry.source);
    return `
    <article class="entry-card" data-tool="${toolAttr}" style="animation-delay: ${i * 0.04}s">
      <div class="entry-header">
        <span class="entry-name">${name}</span>
        <span class="entry-status status-${statusClass}">${status}</span>
      </div>
      <span class="entry-tool">${tool}</span>
      ${description ? `<p class="entry-description">${description}</p>` : ''}
      <div class="entry-meta">
        <span class="entry-date">${date}</span>
        ${sourceUrl ? `<a href="${escapeHtml(sourceUrl)}" target="_blank" rel="noopener noreferrer" class="entry-link">Source ↗</a>` : ''}
      </div>
    </article>`;
  }).join('');
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
