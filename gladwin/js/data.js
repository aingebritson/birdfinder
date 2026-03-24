/**
 * Data loader - Loads species data from JSON with error recovery
 */

let speciesData = [];
let loadError = null;
let isLoading = false;

/**
 * Load species data from JSON file with retry logic
 *
 * @param {Object} options - Loading options
 * @param {Function} options.onProgress - Progress callback (message) => void
 * @param {Function} options.onError - Error callback (error) => void
 * @returns {Promise<Array>} Species data array (empty if failed)
 */
async function loadSpeciesData(options = {}) {
    const { onProgress = null, onError = null } = options;

    // Return cached data if already loaded
    if (speciesData.length > 0) {
        console.log(`Using cached species data (${speciesData.length} species)`);
        return speciesData;
    }

    // Prevent concurrent loads
    if (isLoading) {
        console.log('Load already in progress, waiting...');
        // Wait for the ongoing load to complete
        while (isLoading) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        return speciesData;
    }

    isLoading = true;
    loadError = null;

    try {
        const data = await fetchWithRetry('data/species_data.json', {
            autoRetry: true,
            timeoutMs: 10000,
            onProgress: (message) => {
                console.log(`Species data: ${message}`);
                if (onProgress) onProgress(message);
            },
            onRetry: (attempt, maxAttempts) => {
                console.warn(`Retrying species data load (${attempt}/${maxAttempts})...`);
            }
        });

        // Validate data structure
        if (!Array.isArray(data)) {
            throw new Error('Species data is not an array');
        }

        if (data.length === 0) {
            console.warn('Species data is empty');
        }

        speciesData = data;
        console.log(`✓ Loaded ${speciesData.length} species`);
        return speciesData;

    } catch (error) {
        loadError = error;
        console.error('Failed to load species data:', error);

        if (onError) {
            onError(error);
        }

        // Return empty array for graceful degradation
        return [];

    } finally {
        isLoading = false;
    }
}

/**
 * Get the last load error (if any)
 *
 * @returns {DataLoadError|null} The error or null if no error
 */
function getLoadError() {
    return loadError;
}

/**
 * Clear cached data and force reload on next call
 */
function clearCache() {
    speciesData = [];
    loadError = null;
}

/**
 * Get species by code
 */
function getSpeciesByCode(code) {
    return speciesData.find(s => s.code === code);
}

/**
 * Search species by name
 */
function searchSpecies(query) {
    const lowerQuery = query.toLowerCase();
    return speciesData.filter(s =>
        s.name.toLowerCase().includes(lowerQuery)
    );
}

/**
 * Filter species by category
 */
function filterByCategory(category) {
    if (!category || category === 'all') {
        return speciesData;
    }
    return speciesData.filter(s => s.category === category);
}

/**
 * Get category display name
 */
function getCategoryDisplay(category) {
    const categoryMap = {
        'resident': 'Year-round Resident',
        'single-season': 'Single Season',
        'two-passage-migrant': 'Two-passage Migrant',
        'vagrant': 'Vagrant'
    };
    return categoryMap[category] || category;
}

/**
 * Get category badge class
 */
function getCategoryBadgeClass(category) {
    const badgeMap = {
        'resident': 'badge-resident',
        'single-season': 'badge-single-season',
        'two-passage-migrant': 'badge-two-passage',
        'vagrant': 'badge-vagrant'
    };
    return badgeMap[category] || 'badge-vagrant';
}

/**
 * Format frequency as percentage
 */
function formatFrequency(frequency) {
    return `${(frequency * 100).toFixed(1)}%`;
}
