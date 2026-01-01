/**
 * Browse Page - Search and filter all species
 */

let filteredSpecies = [];
let currentSearchQuery = '';
let currentCategoryFilter = 'all';

/**
 * Initialize the page
 */
async function init() {
    await loadSpeciesData();

    console.log(`Loaded ${speciesData.length} species for browse`);

    // Set up event listeners
    const searchInput = document.getElementById('search');
    const categoryFilter = document.getElementById('category-filter');

    searchInput.addEventListener('input', (e) => {
        currentSearchQuery = e.target.value.toLowerCase();
        updateResults();
    });

    categoryFilter.addEventListener('change', (e) => {
        currentCategoryFilter = e.target.value;
        updateResults();
    });

    // Initial render
    updateResults();
}

/**
 * Update filtered results based on search and category
 */
function updateResults() {
    // Start with all species
    filteredSpecies = speciesData;

    // Apply search filter
    if (currentSearchQuery) {
        filteredSpecies = filteredSpecies.filter(species =>
            species.name.toLowerCase().includes(currentSearchQuery)
        );
    }

    // Apply category filter
    if (currentCategoryFilter !== 'all') {
        filteredSpecies = filteredSpecies.filter(species =>
            species.category === currentCategoryFilter
        );
    }

    // Sort alphabetically by name
    filteredSpecies.sort((a, b) => a.name.localeCompare(b.name));

    // Update count
    document.getElementById('results-count').textContent = filteredSpecies.length;

    // Render results
    renderSpeciesList();
}

/**
 * Render the species list
 */
function renderSpeciesList() {
    const container = document.getElementById('species-list');
    const emptyState = document.getElementById('empty-state');

    if (filteredSpecies.length === 0) {
        container.classList.add('hidden');
        emptyState.classList.remove('hidden');
        return;
    }

    container.classList.remove('hidden');
    emptyState.classList.add('hidden');

    container.innerHTML = filteredSpecies.map(species => createSpeciesCard(species)).join('');
}

/**
 * Create HTML for a species card
 */
function createSpeciesCard(species) {
    const categoryBadge = getCategoryBadgeClass(species.category);
    const categoryName = getCategoryDisplay(species.category);

    // Get timing summary
    const timingSummary = getTimingSummary(species);

    return `
        <a href="species.html?code=${species.code}" class="species-card block bg-white rounded-lg shadow-sm hover:shadow-md p-4 border border-gray-200">
            <div class="flex items-start justify-between">
                <div class="flex-1">
                    <h3 class="font-semibold text-gray-900 text-lg">${species.name}</h3>
                    <div class="mt-2 flex flex-wrap items-center gap-2">
                        <span class="badge ${categoryBadge}">${categoryName}</span>
                        ${timingSummary ? `<span class="text-sm text-gray-600">${timingSummary}</span>` : ''}
                    </div>
                </div>
                <div class="ml-4 text-gray-400">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                    </svg>
                </div>
            </div>
        </a>
    `;
}

/**
 * Get timing summary for a species
 */
function getTimingSummary(species) {
    const timing = species.timing;

    if (timing.status === 'year-round') {
        return 'Year-round';
    }

    if (timing.status === 'irregular') {
        return 'Irregular';
    }

    // Check if winter resident
    const isWinterResident = species.flags && species.flags.includes('winter_resident');

    // Single-season
    if (timing.arrival || timing.winter_arrival) {
        const arrival = timing.arrival || timing.winter_arrival;
        const departure = timing.departure || timing.winter_departure;
        return `${arrival} - ${departure}`;
    }

    // Two-passage
    if (timing.spring_arrival && timing.fall_arrival) {
        return `Spring: ${timing.spring_arrival} - ${timing.spring_departure} • Fall: ${timing.fall_arrival} - ${timing.fall_departure}`;
    }

    return '';
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
