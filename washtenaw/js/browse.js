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
    const speciesListContainer = document.getElementById('species-list');
    const emptyState = document.getElementById('empty-state');

    // Show loading state
    showLoadingUI(speciesListContainer, 'Loading species data...');
    emptyState.classList.add('hidden');

    // Load data with error handling
    await loadSpeciesData({
        onProgress: (message) => {
            showLoadingUI(speciesListContainer, message);
        },
        onError: (error) => {
            showErrorUI(speciesListContainer, error, () => {
                // Retry: clear cache and reload
                clearCache();
                init();
            });
        }
    });

    // Check if data loaded successfully
    if (speciesData.length === 0) {
        const error = getLoadError();
        if (error) {
            // Error UI already shown by onError callback
            return;
        } else {
            // Empty data but no error
            speciesListContainer.innerHTML = '';
            emptyState.classList.remove('hidden');
            return;
        }
    }

    console.log(`Loaded ${speciesData.length} species for browse`);

    // Set up event listeners
    const searchInput = document.getElementById('search');
    const categoryFilter = document.getElementById('category-filter');

    // Debounce search to avoid excessive filtering on every keystroke
    const debouncedSearch = debounce((value) => {
        currentSearchQuery = value.toLowerCase();
        updateResults();
    }, SEARCH_DEBOUNCE_MS);

    searchInput.addEventListener('input', (e) => {
        debouncedSearch(e.target.value);
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
 * Get the border color for a category (Field Journal palette)
 */
function getCategoryBorderColor(category) {
    const colors = {
        'resident': '#2D3E36',       // forest
        'single-season': '#C9A55C',  // ochre
        'two-passage-migrant': '#4A6D5C', // moss
        'vagrant': '#C17F59'         // terracotta
    };
    return colors[category] || '#2D3E36';
}

/**
 * Create HTML for a species card
 */
function createSpeciesCard(species) {
    const categoryBadge = getCategoryBadgeClass(species.category);
    const categoryName = getCategoryDisplay(species.category);
    const borderColor = getCategoryBorderColor(species.category);

    // Get timing summary
    const timingSummary = getTimingSummary(species);

    return `
        <a href="species.html?code=${species.code}" class="species-card" style="--card-accent: ${borderColor};">
            <div class="flex items-start justify-between">
                <div class="flex-1">
                    <h4>${species.name}</h4>
                    <div class="mt-2 flex flex-wrap items-center gap-2">
                        <span class="badge ${categoryBadge}">${categoryName}</span>
                        ${timingSummary ? `<span class="text-sm" style="color: var(--color-ink-muted);">${timingSummary}</span>` : ''}
                    </div>
                </div>
                <div class="ml-4" style="color: var(--color-ink-faint);">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
