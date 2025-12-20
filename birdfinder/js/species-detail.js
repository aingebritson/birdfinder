/**
 * Species Detail Page - Shows individual species information
 */

let currentSpecies = null;

/**
 * Get species code from URL
 */
function getSpeciesCodeFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get('code');
}

/**
 * Initialize the page
 */
async function init() {
    await loadSpeciesData();

    const speciesCode = getSpeciesCodeFromURL();

    if (!speciesCode) {
        showError();
        return;
    }

    // Find species by code
    currentSpecies = speciesData.find(s => s.code === speciesCode);

    if (!currentSpecies) {
        showError();
        return;
    }

    // Hide loading, show content
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('species-content').classList.remove('hidden');

    // Render species details
    renderSpeciesDetails();
    renderTimingInfo();
    renderFrequencyChart();
}

/**
 * Show error state
 */
function showError() {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('error').classList.remove('hidden');
}

/**
 * Render species details
 */
function renderSpeciesDetails() {
    document.getElementById('species-name').textContent = currentSpecies.name;
    document.getElementById('species-code').textContent = currentSpecies.code;
    document.getElementById('species-category').textContent = getCategoryDisplay(currentSpecies.category);

    // Category badge
    const badge = document.getElementById('category-badge');
    badge.textContent = getCategoryDisplay(currentSpecies.category);
    badge.className = `badge ${getCategoryBadgeClass(currentSpecies.category)}`;

    // Update page title
    document.title = `${currentSpecies.name} - BirdFinder`;
}

/**
 * Render timing information
 */
function renderTimingInfo() {
    const timing = currentSpecies.timing;
    const container = document.getElementById('timing-info');

    // Year-round resident
    if (timing.status === 'year-round') {
        container.innerHTML = `
            <div class="text-center py-8">
                <div class="text-4xl mb-2">🏠</div>
                <p class="text-lg font-medium text-gray-900">Year-round Resident</p>
                <p class="text-gray-600 text-sm mt-1">Present throughout the year</p>
            </div>
        `;
        return;
    }

    // Vagrant
    if (timing.status === 'irregular') {
        container.innerHTML = `
            <div class="text-center py-8">
                <div class="text-4xl mb-2">❓</div>
                <p class="text-lg font-medium text-gray-900">Irregular Visitor</p>
                <p class="text-gray-600 text-sm mt-1">Rare or unpredictable occurrence</p>
            </div>
        `;
        return;
    }

    // Check if winter resident
    const isWinterResident = currentSpecies.flags && currentSpecies.flags.includes('winter_resident');

    // Single-season (including winter residents)
    if (timing.arrival || timing.winter_arrival) {
        const arrival = timing.arrival || timing.winter_arrival;
        const peak = timing.peak || timing.winter_peak;
        const departure = timing.departure || timing.winter_departure;
        const label = isWinterResident ? 'Winter' : 'Season';

        container.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="text-center p-4 rounded-lg" style="background-color: #D4EDE9;">
                    <div class="text-sm font-medium mb-1" style="color: #1A5D54;">Arrival</div>
                    <div class="text-xl font-bold">${arrival}</div>
                </div>
                <div class="text-center p-4 rounded-lg" style="background-color: #FDF3D7;">
                    <div class="text-sm font-medium mb-1" style="color: #8B6F1B;">Peak</div>
                    <div class="text-xl font-bold">${peak}</div>
                </div>
                <div class="text-center p-4 rounded-lg" style="background-color: #F2E5DD;">
                    <div class="text-sm font-medium mb-1" style="color: #7A4F36;">Departure</div>
                    <div class="text-xl font-bold">${departure}</div>
                </div>
            </div>
        `;
        return;
    }

    // Two-passage migrant
    if (timing.spring_arrival && timing.fall_arrival) {
        container.innerHTML = `
            <div class="space-y-6">
                <!-- Spring -->
                <div>
                    <h3 class="text-lg font-semibold mb-3 flex items-center gap-2">
                        <span>🌱</span>
                        Spring Migration
                    </h3>
                    <div class="grid grid-cols-3 gap-3">
                        <div class="text-center p-3 rounded-lg" style="background-color: #D4EDE9;">
                            <div class="text-xs font-medium mb-1" style="color: #1A5D54;">Arrival</div>
                            <div class="text-base font-bold">${timing.spring_arrival}</div>
                        </div>
                        <div class="text-center p-3 rounded-lg" style="background-color: #FDF3D7;">
                            <div class="text-xs font-medium mb-1" style="color: #8B6F1B;">Peak</div>
                            <div class="text-base font-bold">${timing.spring_peak}</div>
                        </div>
                        <div class="text-center p-3 rounded-lg" style="background-color: #F2E5DD;">
                            <div class="text-xs font-medium mb-1" style="color: #7A4F36;">Departure</div>
                            <div class="text-base font-bold">${timing.spring_departure}</div>
                        </div>
                    </div>
                </div>

                <!-- Fall -->
                <div>
                    <h3 class="text-lg font-semibold mb-3 flex items-center gap-2">
                        <span>🍂</span>
                        Fall Migration
                    </h3>
                    <div class="grid grid-cols-3 gap-3">
                        <div class="text-center p-3 rounded-lg" style="background-color: #D4EDE9;">
                            <div class="text-xs font-medium mb-1" style="color: #1A5D54;">Arrival</div>
                            <div class="text-base font-bold">${timing.fall_arrival}</div>
                        </div>
                        <div class="text-center p-3 rounded-lg" style="background-color: #FDF3D7;">
                            <div class="text-xs font-medium mb-1" style="color: #8B6F1B;">Peak</div>
                            <div class="text-base font-bold">${timing.fall_peak}</div>
                        </div>
                        <div class="text-center p-3 rounded-lg" style="background-color: #F2E5DD;">
                            <div class="text-xs font-medium mb-1" style="color: #7A4F36;">Departure</div>
                            <div class="text-base font-bold">${timing.fall_departure}</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        return;
    }
}

/**
 * Render frequency chart
 */
function renderFrequencyChart() {
    const container = document.getElementById('frequency-chart');
    const frequencies = currentSpecies.weekly_frequency;

    // Calculate dimensions
    const width = container.clientWidth;
    const height = 200;
    const padding = { top: 20, right: 20, bottom: 40, left: 50 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;

    // Find max frequency for scaling
    const maxFreq = Math.max(...frequencies);
    const yScale = chartHeight / maxFreq;
    const xScale = chartWidth / (frequencies.length - 1); // Divide by 47 so last point lands at chartWidth

    // Month labels
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    // Create SVG
    let svg = `<svg width="${width}" height="${height}" class="w-full">`;

    // Grid lines (horizontal)
    const numYTicks = 5;
    for (let i = 0; i <= numYTicks; i++) {
        const y = padding.top + (chartHeight * i / numYTicks);
        const value = maxFreq * (1 - i / numYTicks);
        svg += `<line x1="${padding.left}" y1="${y}" x2="${width - padding.right}" y2="${y}" stroke="#e5e7eb" stroke-width="1"/>`;
        svg += `<text x="${padding.left - 10}" y="${y + 4}" text-anchor="end" font-size="12" fill="#6b7280">${(value * 100).toFixed(0)}%</text>`;
    }

    // Month labels (x-axis)
    for (let i = 0; i < 12; i++) {
        const weekIndex = i * 4 + 2; // Middle of each month (week 2, 6, 10, etc.)
        const x = padding.left + (weekIndex * xScale);
        svg += `<text x="${x}" y="${height - 10}" text-anchor="middle" font-size="12" fill="#6b7280">${months[i]}</text>`;
    }

    // Draw area under curve
    let pathData = `M ${padding.left} ${padding.top + chartHeight}`;
    for (let i = 0; i < frequencies.length; i++) {
        const x = padding.left + (i * xScale);
        const y = padding.top + chartHeight - (frequencies[i] * yScale);
        pathData += ` L ${x} ${y}`;
    }
    pathData += ` L ${padding.left + chartWidth} ${padding.top + chartHeight} Z`;
    svg += `<path d="${pathData}" fill="#4A6670" fill-opacity="0.1" stroke="none"/>`;

    // Draw line
    let lineData = '';
    for (let i = 0; i < frequencies.length; i++) {
        const x = padding.left + (i * xScale);
        const y = padding.top + chartHeight - (frequencies[i] * yScale);
        lineData += (i === 0 ? 'M' : ' L') + ` ${x} ${y}`;
    }
    svg += `<path d="${lineData}" fill="none" stroke="#4A6670" stroke-width="2"/>`;

    svg += '</svg>';

    container.innerHTML = svg;
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
