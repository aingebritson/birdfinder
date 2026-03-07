/**
 * Hotspots page - Display and search eBird hotspots
 */

let hotspotsData = [];
let filteredHotspots = [];
let currentSort = { field: 'name', ascending: true };

/**
 * Load hotspots data from JSON file with error recovery
 */
async function loadHotspots() {
    const container = document.getElementById('hotspots-list');

    // Show loading state
    showLoadingUI(container, 'Loading hotspots data...');

    try {
        const data = await fetchWithRetry('data/washtenaw_hotspots.json', {
            autoRetry: true,
            timeoutMs: 10000,
            onProgress: (message) => {
                showLoadingUI(container, message);
            },
            onRetry: (attempt, maxAttempts) => {
                console.warn(`Retrying hotspots data load (${attempt}/${maxAttempts})...`);
            }
        });

        // Validate data structure
        if (!Array.isArray(data)) {
            throw new Error('Hotspots data is not an array');
        }

        hotspotsData = data;
        console.log(`✓ Loaded ${hotspotsData.length} hotspots`);

        filteredHotspots = hotspotsData;
        sortHotspots();
        renderHotspots();
        updateResultsCount();

    } catch (error) {
        console.error('Failed to load hotspots data:', error);

        // Show error with retry button
        showErrorUI(container, error, () => {
            // Retry
            loadHotspots();
        });
    }
}

/**
 * Search hotspots by name
 */
function searchHotspots(query) {
    const lowerQuery = query.toLowerCase();
    filteredHotspots = hotspotsData.filter(h =>
        h.name.toLowerCase().includes(lowerQuery)
    );
    sortHotspots();
    renderHotspots();
    updateResultsCount();
}

/**
 * Sort hotspots based on current sort settings
 */
function sortHotspots() {
    filteredHotspots.sort((a, b) => {
        let compareValue = 0;

        switch (currentSort.field) {
            case 'name':
                compareValue = a.name.localeCompare(b.name);
                break;
            case 'species':
                compareValue = a.numSpecies - b.numSpecies;
                break;
        }

        return currentSort.ascending ? compareValue : -compareValue;
    });
}

/**
 * Set sort field and direction
 */
function setSort(field) {
    // If clicking the same field, toggle direction
    if (currentSort.field === field) {
        currentSort.ascending = !currentSort.ascending;
    } else {
        // New field - set to descending for species/date, ascending for name
        currentSort.field = field;
        currentSort.ascending = field === 'name';
    }

    sortHotspots();
    renderHotspots();
    updateSortButtons();
}

/**
 * Update sort button visual states
 */
function updateSortButtons() {
    const buttons = {
        name: document.getElementById('sort-name'),
        species: document.getElementById('sort-species')
    };

    // Update active states
    Object.entries(buttons).forEach(([field, btn]) => {
        if (currentSort.field === field) {
            btn.classList.add('sort-btn-active');
        } else {
            btn.classList.remove('sort-btn-active');
        }
    });

    // Update button text with arrows
    const arrowIcon = currentSort.ascending ? Icons.sortAsc(12) : Icons.sortDesc(12);
    buttons.name.innerHTML = currentSort.field === 'name'
        ? `Name <span class="sort-arrow">${arrowIcon}</span>`
        : 'Name';
    buttons.species.innerHTML = currentSort.field === 'species'
        ? `# Species <span class="sort-arrow">${arrowIcon}</span>`
        : '# Species';
}

/**
 * Update the results count display
 */
function updateResultsCount() {
    document.getElementById('results-count').textContent = filteredHotspots.length;
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    if (!dateString) return 'No recent observations';

    // eBird dates come as "YYYY-MM-DD HH:MM" format
    const date = new Date(dateString.replace(' ', 'T'));
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
    return `${Math.floor(diffDays / 365)} years ago`;
}

/**
 * Render hotspots list
 */
function renderHotspots() {
    const container = document.getElementById('hotspots-list');
    const emptyState = document.getElementById('empty-state');

    if (filteredHotspots.length === 0) {
        container.classList.add('hidden');
        emptyState.classList.remove('hidden');
        return;
    }

    container.classList.remove('hidden');
    emptyState.classList.add('hidden');

    container.innerHTML = filteredHotspots.map(hotspot => `
        <a href="hotspot-detail.html?locId=${hotspot.locId}"
           class="species-card block bg-white rounded-lg shadow-sm hover:shadow-md p-4 border border-gray-200">
            <div class="flex justify-between items-start mb-2">
                <h3 class="font-semibold text-lg">${hotspot.name}</h3>
                <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
            </div>

            <div class="space-y-1 text-sm" style="color: var(--color-ink-muted);">
                <div class="flex items-center gap-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                    </svg>
                    <span><strong>${hotspot.numSpecies}</strong> species recorded</span>
                </div>
            </div>
        </a>
    `).join('');
}

/**
 * Initialize page
 */
document.addEventListener('DOMContentLoaded', async () => {
    await loadHotspots();

    // Set up search with debouncing to avoid excessive filtering on every keystroke
    const searchInput = document.getElementById('search');
    const debouncedSearch = debounce((value) => {
        searchHotspots(value);
    }, SEARCH_DEBOUNCE_MS);

    searchInput.addEventListener('input', (e) => {
        debouncedSearch(e.target.value);
    });

    // Set up sort buttons
    document.getElementById('sort-name').addEventListener('click', () => setSort('name'));
    document.getElementById('sort-species').addEventListener('click', () => setSort('species'));

    // Initialize button states
    updateSortButtons();
});
