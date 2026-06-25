// === VIBE CODE GRAVEYARD — Entry Renderer ===

// Load entries from graveyard/*.md files (fetched at build time or via JS)
const ENTRIES = []; // Populated dynamically below

// --- Fetch all .md files from /graveyard/ ---
async function loadEntries() {
  try {
    // We use a simple approach: fetch an index file or scan graveyard/ directory
    // For GitHub Pages static hosting, we generate an entries.json at build time
    const response = await fetch('graveyard/_entries.json');
    if (!response.ok) return [];
    return await response.json();
  } catch {
    return [];
  }
}

// --- Render entries to the grid ---
function renderEntries(entries, filter = 'all') {
  const container = document.getElementById('entries');
  const counter = document.getElementById('grave-count');

  if (!container) return;

  // Update counter (total, not filtered)
  counter.textContent = ENTRIES.length;

  // Filter
  const filtered = filter === 'all'
    ? entries
    : entries.filter(e => (e.tool || '').toLowerCase() === filter);

  if (filtered.length === 0) {
    container.innerHTML = `
      <p style="color: var(--text-dim); font-family: var(--mono); font-size: 0.85rem; grid-column: 1/-1; text-align: center; padding: 3rem 0;">
        No graves found${filter !== 'all' ? ` for ${filter}` : ''}. The graveyard is still digging.
      </p>`;
    return;
  }

  container.innerHTML = filtered.map(entry => `
    <article class="entry-card" data-tool="${entry.tool || 'unknown'}">
      <div class="entry-header">
        <span class="entry-name">${entry.name || 'Unknown'}</span>
        <span class="entry-status status-${(entry.status || 'active').toLowerCase()}">${entry.status || 'Active'}</span>
      </div>
      <span class="entry-tool">${entry.tool || 'AI'}</span>
      <p class="entry-description">${entry.description || ''}</p>
      <div class="entry-meta">
        <span class="entry-date">${entry.date || ''}</span>
        ${entry.source ? `<a href="${entry.source}" target="_blank" rel="noopener" class="entry-link">Source ↗</a>` : ''}
      </div>
    </article>
  `).join('');
}

// --- Filter buttons ---
function initFilters() {
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderEntries(ENTRIES, btn.dataset.filter);
    });
  });
}

// --- Init ---
document.addEventListener('DOMContentLoaded', async () => {
  ENTRIES.push(...await loadEntries());
  renderEntries(ENTRIES);
  initFilters();
});
