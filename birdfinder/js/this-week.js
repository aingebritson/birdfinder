/**
 * This Week View - Main page showing arriving, peak, and departing species
 */

let currentWeekIndex = WeekCalculator.getCurrentWeek();

/**
 * Initialize the page
 */
async function init() {
    await loadSpeciesData();

    console.log(`Loaded ${speciesData.length} species`);
    console.log('Sample species:', speciesData[0]);

    // Set up event listeners
    document.getElementById('prev-week').addEventListener('click', () => {
        currentWeekIndex = (currentWeekIndex - 1 + 48) % 48;
        updateView();
    });

    document.getElementById('next-week').addEventListener('click', () => {
        currentWeekIndex = (currentWeekIndex + 1) % 48;
        updateView();
    });

    document.getElementById('current-week').addEventListener('click', () => {
        currentWeekIndex = WeekCalculator.getCurrentWeek();
        updateView();
    });

    // Initial render
    updateView();
}

/**
 * Update the view for the current week
 */
function updateView() {
    updateWeekHeader();
    updateSpeciesLists();
}

/**
 * Update the week header
 */
function updateWeekHeader() {
    const weekInfo = WeekCalculator.getWeekInfo(currentWeekIndex);

    document.getElementById('week-title').textContent = weekInfo.title;
    document.getElementById('week-dates').textContent = weekInfo.dateRange;
}

/**
 * Update all three species lists
 */
function updateSpeciesLists() {
    const arriving = [];
    const atPeak = [];
    const departing = [];

    // Categorize each species
    for (const species of speciesData) {
        // Skip vagrants and year-round residents
        if (species.category === 'vagrant') continue;
        if (species.timing.status === 'year-round') continue;

        const frequency = species.weekly_frequency[currentWeekIndex];

        // Check each category (species can be in multiple)
        if (WeekCalculator.isArriving(species, currentWeekIndex)) {
            arriving.push({ species, frequency });
        }

        if (WeekCalculator.isAtPeak(species, currentWeekIndex)) {
            atPeak.push({ species, frequency });
        }

        if (WeekCalculator.isDeparting(species, currentWeekIndex)) {
            departing.push({ species, frequency });
        }
    }

    // Sort by frequency (highest first)
    arriving.sort((a, b) => b.frequency - a.frequency);
    atPeak.sort((a, b) => b.frequency - a.frequency);
    departing.sort((a, b) => b.frequency - a.frequency);

    console.log(`Week ${currentWeekIndex}: ${arriving.length} arriving, ${atPeak.length} at peak, ${departing.length} departing`);

    // Render each list
    renderSpeciesList('arriving-list', arriving);
    renderSpeciesList('peak-list', atPeak);
    renderSpeciesList('departing-list', departing);
}

/**
 * Render a species list
 */
function renderSpeciesList(elementId, speciesList) {
    const container = document.getElementById(elementId);

    if (speciesList.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🔍</div>
                <p>No species found for this week</p>
            </div>
        `;
        return;
    }

    container.innerHTML = speciesList.map(({ species, frequency }) =>
        createSpeciesCard(species, frequency)
    ).join('');
}

/**
 * Create HTML for a species card
 */
function createSpeciesCard(species, frequency) {
    const categoryBadge = getCategoryBadgeClass(species.category);
    const categoryName = getCategoryDisplay(species.category);
    const freqPercent = (frequency * 100).toFixed(1);
    const barWidth = Math.min(frequency * 100, 100);

    return `
        <a href="species.html?code=${species.code}" class="species-card block bg-white rounded-lg shadow-sm hover:shadow-md p-4 border border-gray-200">
            <div class="flex items-start justify-between mb-2">
                <div class="flex-1">
                    <h4 class="font-semibold text-gray-900 text-lg">${species.name}</h4>
                    <span class="badge ${categoryBadge} mt-1">${categoryName}</span>
                </div>
                <div class="text-right ml-4">
                    <div class="text-2xl font-bold text-gray-900">${freqPercent}%</div>
                    <div class="text-xs text-gray-500">frequency</div>
                </div>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-1 mt-3">
                <div class="bg-blue-600 h-1 rounded-full transition-all" style="width: ${barWidth}%"></div>
            </div>
        </a>
    `;
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
