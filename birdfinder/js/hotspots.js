/**
 * Hotspots page - Display and search eBird hotspots
 */

let hotspotsData = [];
let filteredHotspots = [];
let currentSort = { field: 'name', ascending: true };

/**
 * Load hotspots data from JSON file
 */
async function loadHotspots() {
    try {
        const response = await fetch('data/washtenaw_hotspots.json');
        hotspotsData = await response.json();

        console.log(`Loaded ${hotspotsData.length} hotspots`);
        filteredHotspots = hotspotsData;
        sortHotspots();
        renderHotspots();
        updateResultsCount();
    } catch (error) {
        console.error('Error loading hotspots data:', error);
        document.getElementById('hotspots-list').innerHTML =
            '<div class="text-center py-8 text-red-600">Error loading hotspots data</div>';
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
    const arrow = currentSort.ascending ? '↑' : '↓';
    buttons.name.textContent = currentSort.field === 'name' ? `Name ${arrow}` : 'Name';
    buttons.species.textContent = currentSort.field === 'species' ? `# Species ${arrow}` : '# Species';
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
        <a href="https://ebird.org/hotspot/${hotspot.locId}"
           target="_blank"
           rel="noopener noreferrer"
           class="species-card block">
            <div class="flex justify-between items-start mb-2">
                <h3 class="font-semibold text-lg">${hotspot.name}</h3>
                <svg class="w-4 h-4 text-gray-400 flex-shrink-0 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                </svg>
            </div>

            <div class="space-y-1 text-sm" style="color: #6B7280;">
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

    // Set up search
    const searchInput = document.getElementById('search');
    searchInput.addEventListener('input', (e) => {
        searchHotspots(e.target.value);
    });

    // Set up sort buttons
    document.getElementById('sort-name').addEventListener('click', () => setSort('name'));
    document.getElementById('sort-species').addEventListener('click', () => setSort('species'));

    // Initialize button states
    updateSortButtons();
});
