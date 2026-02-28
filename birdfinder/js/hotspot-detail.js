/**
 * Hotspot Detail Page - Shows individual hotspot information
 * XSS-SAFE VERSION with comprehensive input sanitization
 */

let currentHotspot = null;
let hotspotsData = [];
let notableSpeciesIndex = null; // Pre-filtered specialties by hotspot
let commonSpeciesIndex = null; // Top species by occurrence per hotspot

/**
 * Get hotspot location ID from URL
 */
function getLocIdFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get('locId');
}

/**
 * Load notable species index (pre-filtered specialties) with retry logic
 */
async function loadNotableSpeciesIndex() {
    try {
        notableSpeciesIndex = await fetchWithRetry('data/notable_species_by_hotspot.json', {
            autoRetry: true,
            timeoutMs: 10000
        });
        return true;
    } catch (error) {
        console.error('Error loading notable species index:', error);
        return false;
    }
}

/**
 * Load common species index (top 15 by occurrence per hotspot) with retry logic
 */
async function loadCommonSpeciesIndex() {
    try {
        commonSpeciesIndex = await fetchWithRetry('data/common_species_by_hotspot.json', {
            autoRetry: true,
            timeoutMs: 10000
        });
        return true;
    } catch (error) {
        console.error('Error loading common species index:', error);
        return false;
    }
}

/**
 * Initialize the page
 */
async function init() {
    const loadingEl = document.getElementById('loading');
    const errorEl = document.getElementById('error');

    let loadError = null;
    try {
        hotspotsData = await fetchWithRetry('data/washtenaw_hotspots_enriched.json', {
            autoRetry: true,
            timeoutMs: 10000,
            onProgress: (message) => {
                const loadingText = loadingEl.querySelector('div');
                if (loadingText) {
                    loadingText.textContent = message;
                }
            }
        });
    } catch (error) {
        loadError = error;
        console.error('Error loading hotspots data:', error);
    }

    // If data loading failed, show error with retry option
    if (loadError) {
        loadingEl.classList.add('hidden');
        errorEl.classList.remove('hidden');
        showErrorUI(errorEl, loadError, () => {
            // Retry: reset state and reload
            hotspotsData = [];
            errorEl.classList.add('hidden');
            loadingEl.classList.remove('hidden');
            init();
        });
        return;
    }

    const locId = getLocIdFromURL();

    if (!locId) {
        showError();
        return;
    }

    // Find hotspot by location ID
    currentHotspot = hotspotsData.find(h => h.locId === locId);

    if (!currentHotspot) {
        showError();
        return;
    }

    // Hide loading, show content
    loadingEl.classList.add('hidden');
    document.getElementById('hotspot-content').classList.remove('hidden');

    // Render hotspot details
    renderHotspotDetails();
    renderHowToBird();
    renderHabitats();
    renderTips();
    renderLinks();

    // Load and render species data (async, don't block the main content)
    loadNotableSpeciesIndex().then(loaded => {
        if (loaded) {
            renderSpecialties(locId);
        }
    }).catch(error => {
        console.error('Error loading species data:', error);
    });
}

/**
 * Show error state
 */
function showError() {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('error').classList.remove('hidden');
}

/**
 * Render hotspot details
 */
function renderHotspotDetails() {
    // Use textContent for safe text insertion
    setTextContentSafe(document.getElementById('hotspot-name'), currentHotspot.name);
    setTextContentSafe(document.getElementById('species-count'), currentHotspot.numSpecies);

    // Update eBird link with URL sanitization
    const ebirdLink = document.getElementById('ebird-link');
    const safeUrl = sanitizeUrl(`https://ebird.org/hotspot/${escapeHtml(currentHotspot.locId)}`);
    if (safeUrl) {
        ebirdLink.href = safeUrl;
    }

    // Update page title (safe - browser handles escaping)
    document.title = `${currentHotspot.name} - BirdFinder`;
}

/**
 * Render visitor information
 */
function renderVisitorInfo() {
    const container = document.getElementById('visitor-info');
    const infoItems = [];

    // Parking
    if (currentHotspot.parking) {
        const parkingTypes = {
            'lot': 'Parking lot',
            'street': 'Street parking',
            'roadside': 'Roadside parking',
            'none': 'No parking available'
        };
        const parkingType = escapeHtml(parkingTypes[currentHotspot.parking.type] || 'Parking available');
        const parkingNotes = currentHotspot.parking.notes ? escapeHtml(currentHotspot.parking.notes) : '';

        infoItems.push(`
            <div class="flex items-start gap-3">
                <svg class="w-5 h-5 mt-0.5 flex-shrink-0" style="color: var(--color-forest);" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2"></path>
                </svg>
                <div>
                    <div class="font-medium">${parkingType}</div>
                    ${parkingNotes ? `<div class="text-sm text-gray-600 mt-1">${parkingNotes}</div>` : ''}
                </div>
            </div>
        `);
    }

    // Hours
    if (currentHotspot.hours) {
        const hoursText = escapeHtml(currentHotspot.hours);
        infoItems.push(`
            <div class="flex items-start gap-3">
                <svg class="w-5 h-5 mt-0.5 flex-shrink-0" style="color: var(--color-forest);" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <div>
                    <div class="font-medium">Hours</div>
                    <div class="text-sm text-gray-600 mt-1">${hoursText}</div>
                </div>
            </div>
        `);
    }

    // Fee
    if (currentHotspot.fee !== null && currentHotspot.fee !== undefined) {
        const feeText = escapeHtml(currentHotspot.fee || 'Free');
        infoItems.push(`
            <div class="flex items-start gap-3">
                <svg class="w-5 h-5 mt-0.5 flex-shrink-0" style="color: var(--color-forest);" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <div>
                    <div class="font-medium">${feeText}</div>
                </div>
            </div>
        `);
    } else {
        infoItems.push(`
            <div class="flex items-start gap-3">
                <svg class="w-5 h-5 mt-0.5 flex-shrink-0" style="color: var(--color-forest);" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <div>
                    <div class="font-medium">Free</div>
                </div>
            </div>
        `);
    }

    // Features
    if (currentHotspot.features && currentHotspot.features.length > 0) {
        const featureLabels = {
            'restrooms': 'Restrooms available',
            'accessible-full': 'Fully accessible',
            'accessible-partial': 'Partially accessible',
            'dogs-leashed': 'Dogs allowed (leashed)',
            'dogs-prohibited': 'No dogs allowed',
            'no-facilities': 'No facilities'
        };

        const featuresList = currentHotspot.features
            .map(f => escapeHtml(featureLabels[f] || f))
            .join(', ');

        infoItems.push(`
            <div class="flex items-start gap-3">
                <svg class="w-5 h-5 mt-0.5 flex-shrink-0" style="color: var(--color-forest);" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <div>
                    <div class="font-medium">Features</div>
                    <div class="text-sm text-gray-600 mt-1">${featuresList}</div>
                </div>
            </div>
        `);
    }

    container.innerHTML = infoItems.join('');
}

/**
 * Render "How to Bird Here" content with XSS protection
 */
function renderHowToBird() {
    const section = document.getElementById('how-to-bird-section');
    const container = document.getElementById('how-to-bird');

    if (currentHotspot.howToBird) {
        section.classList.remove('hidden');
        // Use safe markdown converter that escapes all HTML
        const safeHtml = markdownToHtmlSafe(currentHotspot.howToBird);
        container.innerHTML = safeHtml;
    }
}

/**
 * Render habitats with XSS protection
 */
function renderHabitats() {
    const section = document.getElementById('habitats-section');
    const container = document.getElementById('habitats');

    if (currentHotspot.habitats && currentHotspot.habitats.length > 0) {
        section.classList.remove('hidden');

        const habitatLabels = {
            'deciduous-forest': 'Deciduous Forest',
            'coniferous-forest': 'Coniferous Forest',
            'wetland': 'Wetland',
            'marsh': 'Marsh',
            'river': 'River',
            'lake': 'Lake',
            'pond': 'Pond',
            'prairie': 'Prairie',
            'grassland': 'Grassland',
            'agricultural': 'Agricultural'
        };

        const habitatBadges = currentHotspot.habitats.map(habitat => {
            const label = escapeHtml(habitatLabels[habitat] || habitat);
            return `<span class="px-3 py-1.5 text-sm font-medium rounded-lg bg-green-100 text-green-800">${label}</span>`;
        }).join('');

        container.innerHTML = habitatBadges;
    }
}

/**
 * Render birding tips with XSS protection
 */
function renderTips() {
    const section = document.getElementById('tips-section');
    const container = document.getElementById('tips');

    if (currentHotspot.tips && currentHotspot.tips.length > 0) {
        section.classList.remove('hidden');

        const tipsList = currentHotspot.tips.map(tip => {
            const safeTip = escapeHtml(tip);
            return `
                <li class="flex items-start gap-3">
                    <svg class="w-5 h-5 mt-0.5 flex-shrink-0" style="color: var(--color-ochre);" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                    </svg>
                    <span class="text-gray-700">${safeTip}</span>
                </li>
            `;
        }).join('');

        container.innerHTML = tipsList;
    }
}

/**
 * Render external links with URL and XSS protection
 */
function renderLinks() {
    const section = document.getElementById('links-section');
    const container = document.getElementById('links');

    if (currentHotspot.links && currentHotspot.links.length > 0) {
        section.classList.remove('hidden');

        const linksList = currentHotspot.links.map(link => {
            const safeUrl = sanitizeUrl(link.url);
            const safeLabel = escapeHtml(link.label);

            // Skip links with invalid URLs
            if (!safeUrl) {
                console.warn('Skipped link with invalid URL:', link);
                return '';
            }

            return `
                <a href="${escapeHtml(safeUrl)}" target="_blank" rel="noopener noreferrer"
                   class="flex items-center gap-2 text-blue-600 hover:text-blue-800 hover:underline">
                    <span>${safeLabel}</span>
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                    </svg>
                </a>
            `;
        }).filter(html => html).join(''); // Filter out empty strings

        container.innerHTML = linksList;
    }
}

/**
 * Render specialties section - species where this hotspot is unusually good
 * Uses pre-filtered notable_species_by_hotspot.json (lift > 2.0, detection_count > 5)
 * Sort by lift descending, show top 10
 */
function renderSpecialties(locId) {
    const section = document.getElementById('specialties-section');
    const container = document.getElementById('specialties-list');

    // Get specialties from pre-filtered index
    const hotspotData = notableSpeciesIndex?.hotspots?.[locId];
    const specialties = hotspotData?.notable_species || [];

    if (specialties.length === 0) {
        section.classList.remove('hidden');
        container.innerHTML = `
            <div class="text-sm" style="color: var(--color-ink-muted); padding: 1rem 0;">
                No unusual specialties — this hotspot has a typical species mix for the county.
            </div>
        `;
        return;
    }

    section.classList.remove('hidden');

    // Already sorted by lift in the index, just take top 10
    const topSpecialties = specialties.slice(0, 10);

    const speciesList = topSpecialties.map(species => {
        const safeName = escapeHtml(species.common_name);
        const safeCode = escapeHtml(species.code);
        const liftDisplay = species.lift.toFixed(1);
        const detectionCount = species.detection_count || 0;

        return `
            <a href="species.html?code=${safeCode}" class="species-item species-item-specialty">
                <div class="species-item-name">${safeName}</div>
                <div class="species-item-stats">
                    <span class="specialty-lift">${liftDisplay}× county average</span>
                    <span class="species-item-separator">•</span>
                    <span class="species-item-detections">${detectionCount} observation${detectionCount !== 1 ? 's' : ''}</span>
                </div>
            </a>
        `;
    }).join('');

    container.innerHTML = speciesList;
}

/**
 * Render common species section - species most likely to encounter
 * Uses pre-computed common_species_by_hotspot.json (top 15 by occurrence)
 */
function renderCommonSpecies(locId) {
    const section = document.getElementById('common-section');
    const container = document.getElementById('common-list');

    // Get common species from pre-computed index
    const hotspotData = commonSpeciesIndex?.hotspots?.[locId];
    const commonSpecies = hotspotData?.common_species || [];

    if (commonSpecies.length === 0) {
        return;
    }

    section.classList.remove('hidden');

    const speciesList = commonSpecies.map(species => {
        const safeName = escapeHtml(species.common_name);
        const safeCode = escapeHtml(species.code);
        const occurrenceDisplay = (species.occurrence_rate * 100).toFixed(1);
        const detectionCount = species.detection_count || 0;

        return `
            <a href="species.html?code=${safeCode}" class="species-item">
                <div class="species-item-name">${safeName}</div>
                <div class="species-item-stats">
                    <span class="species-item-occurrence">${occurrenceDisplay}% of checklists</span>
                    <span class="species-item-separator">•</span>
                    <span class="species-item-detections">${detectionCount} observation${detectionCount !== 1 ? 's' : ''}</span>
                </div>
            </a>
        `;
    }).join('');

    container.innerHTML = speciesList;
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
