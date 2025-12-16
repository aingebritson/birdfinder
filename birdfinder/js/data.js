/**
 * Data loader - Loads species data from JSON
 */

let speciesData = [];

/**
 * Load species data from JSON file
 */
async function loadSpeciesData() {
    try {
        const response = await fetch('birdfinder/data/species_data.json');
        speciesData = await response.json();
        console.log(`Loaded ${speciesData.length} species`);
        return speciesData;
    } catch (error) {
        console.error('Error loading species data:', error);
        return [];
    }
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
