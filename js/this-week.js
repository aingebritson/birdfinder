/**
 * This Week View - Main page showing arriving, peak, and departing species
 */

let currentWeekIndex = WeekCalculator.getCurrentWeek();

/**
 * Initialize the page
 */
async function init() {
    // Load data with error handling
    await loadSpeciesData({
        onError: (error) => {
            // Show error in all three list containers
            const containers = ['arriving-list', 'peak-list', 'departing-list'];
            containers.forEach((containerId) => {
                const container = document.getElementById(containerId);
                if (container) {
                    showErrorUI(container, error, () => {
                        // Retry: clear cache and reload
                        clearCache();
                        init();
                    });
                }
            });
        }
    });

    // Check if data loaded
    if (speciesData.length === 0) {
        const error = getLoadError();
        if (error) {
            // Error already shown above
            return;
        }
    }

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
function createSpeciesCard(species, frequency) {
    const categoryBadge = getCategoryBadgeClass(species.category);
    const categoryName = getCategoryDisplay(species.category);
    const borderColor = getCategoryBorderColor(species.category);
    const freqPercent = (frequency * 100).toFixed(1);
    const barWidth = Math.min(frequency * 100, 100);

    return `
        <a href="species.html?code=${species.code}" class="species-card" style="--card-accent: ${borderColor};">
            <div class="flex items-start justify-between mb-3">
                <div class="flex-1">
                    <h4>${species.name}</h4>
                    <span class="badge ${categoryBadge} mt-2">${categoryName}</span>
                </div>
                <div class="text-right ml-4">
                    <div class="frequency-percent">${freqPercent}%</div>
                    <div class="text-xs" style="color: var(--color-ink-muted);">frequency</div>
                </div>
            </div>
            <div class="frequency-bar" style="width: ${barWidth}%;"></div>
        </a>
    `;
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
