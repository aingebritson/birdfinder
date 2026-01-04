/**
 * Hotspot Detail Page - Shows individual hotspot information
 */

let currentHotspot = null;
let hotspotsData = [];

/**
 * Get hotspot location ID from URL
 */
function getLocIdFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get('locId');
}

/**
 * Load hotspots data from JSON file
 */
async function loadHotspotsData() {
    try {
        const response = await fetch('data/washtenaw_hotspots_enriched.json');
        hotspotsData = await response.json();
        return true;
    } catch (error) {
        console.error('Error loading hotspots data:', error);
        return false;
    }
}

/**
 * Initialize the page
 */
async function init() {
    const success = await loadHotspotsData();

    if (!success) {
        showError();
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
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('hotspot-content').classList.remove('hidden');

    // Render hotspot details
    renderHotspotDetails();
    renderVisitorInfo();
    renderHowToBird();
    renderHabitats();
    renderTips();
    renderLinks();
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
    document.getElementById('hotspot-name').textContent = currentHotspot.name;
    document.getElementById('species-count').textContent = currentHotspot.numSpecies;

    // Update eBird link
    const ebirdLink = document.getElementById('ebird-link');
    ebirdLink.href = `https://ebird.org/hotspot/${currentHotspot.locId}`;

    // Update page title
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
        const parkingType = parkingTypes[currentHotspot.parking.type] || 'Parking available';
        const parkingNotes = currentHotspot.parking.notes;

        infoItems.push(`
            <div class="flex items-start gap-3">
                <svg class="w-5 h-5 mt-0.5 flex-shrink-0" style="color: #334155;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
        infoItems.push(`
            <div class="flex items-start gap-3">
                <svg class="w-5 h-5 mt-0.5 flex-shrink-0" style="color: #334155;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <div>
                    <div class="font-medium">Hours</div>
                    <div class="text-sm text-gray-600 mt-1">${currentHotspot.hours}</div>
                </div>
            </div>
        `);
    }

    // Fee
    if (currentHotspot.fee !== null && currentHotspot.fee !== undefined) {
        infoItems.push(`
            <div class="flex items-start gap-3">
                <svg class="w-5 h-5 mt-0.5 flex-shrink-0" style="color: #334155;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linnejoin="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <div>
                    <div class="font-medium">${currentHotspot.fee || 'Free'}</div>
                </div>
            </div>
        `);
    } else {
        infoItems.push(`
            <div class="flex items-start gap-3">
                <svg class="w-5 h-5 mt-0.5 flex-shrink-0" style="color: #334155;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
            .map(f => featureLabels[f] || f)
            .join(', ');

        infoItems.push(`
            <div class="flex items-start gap-3">
                <svg class="w-5 h-5 mt-0.5 flex-shrink-0" style="color: #334155;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
 * Render "How to Bird Here" content
 */
function renderHowToBird() {
    const section = document.getElementById('how-to-bird-section');
    const container = document.getElementById('how-to-bird');

    if (currentHotspot.howToBird) {
        section.classList.remove('hidden');
        // Convert markdown to HTML (basic implementation)
        const htmlContent = markdownToHtml(currentHotspot.howToBird);
        container.innerHTML = htmlContent;
    }
}

/**
 * Basic markdown to HTML converter
 */
function markdownToHtml(markdown) {
    let html = markdown;

    // Headers
    html = html.replace(/^### (.*$)/gim, '<h3 class="text-lg font-semibold mt-4 mb-2">$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2 class="text-xl font-bold mt-6 mb-3">$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold mt-6 mb-4">$1</h1>');

    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Italic
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Paragraphs (double line breaks)
    html = html.split('\n\n').map(para => {
        if (para.trim().startsWith('<h')) return para;
        return `<p class="mb-3 text-gray-700 leading-relaxed">${para.trim()}</p>`;
    }).join('\n');

    return html;
}

/**
 * Render habitats
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
            const label = habitatLabels[habitat] || habitat;
            return `<span class="px-3 py-1.5 text-sm font-medium rounded-lg bg-green-100 text-green-800">${label}</span>`;
        }).join('');

        container.innerHTML = habitatBadges;
    }
}

/**
 * Render birding tips
 */
function renderTips() {
    const section = document.getElementById('tips-section');
    const container = document.getElementById('tips');

    if (currentHotspot.tips && currentHotspot.tips.length > 0) {
        section.classList.remove('hidden');

        const tipsList = currentHotspot.tips.map(tip => {
            return `
                <li class="flex items-start gap-3">
                    <svg class="w-5 h-5 mt-0.5 flex-shrink-0" style="color: #CA8A04;" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                    </svg>
                    <span class="text-gray-700">${tip}</span>
                </li>
            `;
        }).join('');

        container.innerHTML = tipsList;
    }
}

/**
 * Render external links
 */
function renderLinks() {
    const section = document.getElementById('links-section');
    const container = document.getElementById('links');

    if (currentHotspot.links && currentHotspot.links.length > 0) {
        section.classList.remove('hidden');

        const linksList = currentHotspot.links.map(link => {
            return `
                <a href="${link.url}" target="_blank" rel="noopener noreferrer"
                   class="flex items-center gap-2 text-blue-600 hover:text-blue-800 hover:underline">
                    <span>${link.label}</span>
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                    </svg>
                </a>
            `;
        }).join('');

        container.innerHTML = linksList;
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
