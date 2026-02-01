/**
 * Species Detail Page - Shows individual species information
 */

let currentSpecies = null;
let hotspotData = null;

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
    const loadingEl = document.getElementById('loading');
    const errorEl = document.getElementById('error');
    const contentEl = document.getElementById('species-content');

    // Load data with error handling
    await loadSpeciesData({
        onProgress: (message) => {
            // Update loading message
            const loadingText = loadingEl.querySelector('p');
            if (loadingText) {
                loadingText.textContent = message;
            }
        },
        onError: (error) => {
            loadingEl.classList.add('hidden');
            errorEl.classList.remove('hidden');

            // Show detailed error with retry button
            const errorContent = errorEl.querySelector('.error-content') || errorEl;
            showErrorUI(errorContent, error, () => {
                // Retry: clear cache and reload
                clearCache();
                errorEl.classList.add('hidden');
                loadingEl.classList.remove('hidden');
                init();
            });
        }
    });

    const speciesCode = getSpeciesCodeFromURL();

    if (!speciesCode) {
        showError();
        return;
    }

    // Check if data loaded
    if (speciesData.length === 0) {
        const error = getLoadError();
        if (error) {
            // Error already handled above
            return;
        } else {
            showError();
            return;
        }
    }

    // Find species by code
    currentSpecies = speciesData.find(s => s.code === speciesCode);

    if (!currentSpecies) {
        showError();
        return;
    }

    // Hide loading, show content
    loadingEl.classList.add('hidden');
    contentEl.classList.remove('hidden');

    // Render species details
    renderSpeciesDetails();
    renderTimingInfo();
    renderFrequencyChart();

    // Load and render hotspot data
    await loadHotspotData();
    renderHotspots();
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
    if (currentSpecies.category === 'resident') {
        container.innerHTML = `
            <div class="text-center py-8">
                <div class="text-4xl mb-2">🏠</div>
                <p class="text-lg font-medium text-gray-900">Year-round Resident</p>
                <p class="text-gray-600 text-sm mt-1">Present throughout the year</p>
            </div>
        `;
        return;
    }

    // Irregular visitor (vagrant or irregular presence)
    if (currentSpecies.category === 'vagrant' || timing.first_appears) {
        const firstAppears = timing.first_appears || '';
        const peak = timing.peak || '';
        const lastAppears = timing.last_appears || '';

        container.innerHTML = `
            <div class="text-center py-8">
                <div class="text-4xl mb-2">❓</div>
                <p class="text-lg font-medium text-gray-900">Irregular Visitor</p>
                <p class="text-gray-600 text-sm mt-1">Rare or unpredictable occurrence</p>
                ${firstAppears ? `
                    <div class="mt-4 grid grid-cols-3 gap-3 max-w-xl mx-auto">
                        <div class="text-center">
                            <div class="text-xs" style="color: #475569;">First appears</div>
                            <div class="text-sm font-medium mt-1">${firstAppears}</div>
                        </div>
                        <div class="text-center">
                            <div class="text-xs" style="color: #475569;">Peak</div>
                            <div class="text-sm font-medium mt-1">${peak}</div>
                        </div>
                        <div class="text-center">
                            <div class="text-xs" style="color: #475569;">Last appears</div>
                            <div class="text-sm font-medium mt-1">${lastAppears}</div>
                        </div>
                    </div>
                ` : ''}
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
                        <div class="text-center p-3 rounded-lg" style="background-color: #CCFBF1;">
                            <div class="text-xs font-medium mb-1" style="color: #0D9488;">Arrival</div>
                            <div class="text-base font-bold">${timing.spring_arrival}</div>
                        </div>
                        <div class="text-center p-3 rounded-lg" style="background-color: #FEF3C7;">
                            <div class="text-xs font-medium mb-1" style="color: #CA8A04;">Peak</div>
                            <div class="text-base font-bold">${timing.spring_peak}</div>
                        </div>
                        <div class="text-center p-3 rounded-lg" style="background-color: #F5E6DC;">
                            <div class="text-xs font-medium mb-1" style="color: #C17F59;">Departure</div>
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
                        <div class="text-center p-3 rounded-lg" style="background-color: #CCFBF1;">
                            <div class="text-xs font-medium mb-1" style="color: #0D9488;">Arrival</div>
                            <div class="text-base font-bold">${timing.fall_arrival}</div>
                        </div>
                        <div class="text-center p-3 rounded-lg" style="background-color: #FEF3C7;">
                            <div class="text-xs font-medium mb-1" style="color: #CA8A04;">Peak</div>
                            <div class="text-base font-bold">${timing.fall_peak}</div>
                        </div>
                        <div class="text-center p-3 rounded-lg" style="background-color: #F5E6DC;">
                            <div class="text-xs font-medium mb-1" style="color: #C17F59;">Departure</div>
                            <div class="text-base font-bold">${timing.fall_departure}</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        return;
    }

    // Single-season winter (overwintering)
    if (timing.winter_arrival) {
        container.innerHTML = `
            <div class="space-y-4">
                <div class="text-center">
                    <div class="text-4xl mb-2">❄️</div>
                    <p class="text-lg font-medium text-gray-900">Winter Resident</p>
                    <p class="text-gray-600 text-sm mt-1">Present during winter months</p>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="text-center p-4 rounded-lg" style="background-color: #CCFBF1;">
                        <div class="text-sm font-medium mb-1" style="color: #0D9488;">Arrival</div>
                        <div class="text-xl font-bold">${timing.winter_arrival}</div>
                    </div>
                    <div class="text-center p-4 rounded-lg" style="background-color: #FEF3C7;">
                        <div class="text-sm font-medium mb-1" style="color: #CA8A04;">Peak</div>
                        <div class="text-xl font-bold">${timing.winter_peak}</div>
                    </div>
                    <div class="text-center p-4 rounded-lg" style="background-color: #F5E6DC;">
                        <div class="text-sm font-medium mb-1" style="color: #C17F59;">Departure</div>
                        <div class="text-xl font-bold">${timing.winter_departure}</div>
                    </div>
                </div>
            </div>
        `;
        return;
    }

    // Single-season summer
    if (timing.arrival) {
        container.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="text-center p-4 rounded-lg" style="background-color: #CCFBF1;">
                    <div class="text-sm font-medium mb-1" style="color: #0D9488;">Arrival</div>
                    <div class="text-xl font-bold">${timing.arrival}</div>
                </div>
                <div class="text-center p-4 rounded-lg" style="background-color: #FEF3C7;">
                    <div class="text-sm font-medium mb-1" style="color: #CA8A04;">Peak</div>
                    <div class="text-xl font-bold">${timing.peak}</div>
                </div>
                <div class="text-center p-4 rounded-lg" style="background-color: #F5E6DC;">
                    <div class="text-sm font-medium mb-1" style="color: #C17F59;">Departure</div>
                    <div class="text-xl font-bold">${timing.departure}</div>
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

    // Calculate dimensions - use offsetWidth for more accurate width
    const width = container.offsetWidth || container.clientWidth;
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

    // Get current week for indicator
    const currentWeek = WeekCalculator.getCurrentWeek();

    // Create container with SVG and tooltip
    container.innerHTML = `
        <div style="position: relative; width: 100%;">
            <svg id="freq-svg" width="100%" height="${height}" viewBox="0 0 ${width} ${height}" preserveAspectRatio="xMidYMid meet" style="cursor: crosshair; display: block;"></svg>
            <div id="freq-tooltip" style="
                position: absolute;
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 6px 10px;
                border-radius: 4px;
                font-size: 12px;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.15s;
                white-space: nowrap;
            "></div>
            <div id="freq-indicator" style="
                position: absolute;
                top: ${padding.top}px;
                width: 1px;
                height: ${chartHeight}px;
                background: #CA8A04;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.15s;
            "></div>
        </div>
    `;

    const svg = document.getElementById('freq-svg');
    const tooltip = document.getElementById('freq-tooltip');
    const indicator = document.getElementById('freq-indicator');

    // Build SVG content
    let svgContent = '';

    // Grid lines (horizontal)
    const numYTicks = 5;

    // First, calculate all tick values to determine if we need decimal places
    const tickValues = [];
    for (let i = 0; i <= numYTicks; i++) {
        const value = maxFreq * (1 - i / numYTicks);
        tickValues.push(value * 100);
    }

    // Check if any values round to the same integer
    const roundedValues = tickValues.map(v => Math.round(v));
    const hasDuplicates = roundedValues.length !== new Set(roundedValues).size;
    const decimalPlaces = hasDuplicates ? 1 : 0;

    // Draw grid lines and labels
    for (let i = 0; i <= numYTicks; i++) {
        const y = padding.top + (chartHeight * i / numYTicks);
        const value = tickValues[i];
        svgContent += `<line x1="${padding.left}" y1="${y}" x2="${width - padding.right}" y2="${y}" stroke="#E5E7EB" stroke-width="1"/>`;
        svgContent += `<text x="${padding.left - 10}" y="${y + 4}" text-anchor="end" font-size="12" fill="#475569">${value.toFixed(decimalPlaces)}%</text>`;
    }

    // Month labels (x-axis)
    for (let i = 0; i < 12; i++) {
        const weekIndex = i * 4 + 2; // Middle of each month (week 2, 6, 10, etc.)
        const x = padding.left + (weekIndex * xScale);
        svgContent += `<text x="${x}" y="${height - 10}" text-anchor="middle" font-size="12" fill="#475569">${months[i]}</text>`;
    }

    // Draw area under curve
    let pathData = `M ${padding.left} ${padding.top + chartHeight}`;
    for (let i = 0; i < frequencies.length; i++) {
        const x = padding.left + (i * xScale);
        const y = padding.top + chartHeight - (frequencies[i] * yScale);
        pathData += ` L ${x} ${y}`;
    }
    pathData += ` L ${padding.left + chartWidth} ${padding.top + chartHeight} Z`;
    svgContent += `<path d="${pathData}" fill="#BFDBFE" fill-opacity="0.6" stroke="none"/>`;

    // Draw line
    let lineData = '';
    for (let i = 0; i < frequencies.length; i++) {
        const x = padding.left + (i * xScale);
        const y = padding.top + chartHeight - (frequencies[i] * yScale);
        lineData += (i === 0 ? 'M' : ' L') + ` ${x} ${y}`;
    }
    svgContent += `<path d="${lineData}" fill="none" stroke="#334155" stroke-width="2"/>`;

    // Draw current week indicator line
    const currentWeekX = padding.left + (currentWeek * xScale);
    svgContent += `<line x1="${currentWeekX}" y1="${padding.top}" x2="${currentWeekX}" y2="${padding.top + chartHeight}" stroke="#CA8A04" stroke-width="2" stroke-dasharray="4,3" opacity="0.7"/>`;
    svgContent += `<text x="${currentWeekX}" y="${padding.top - 5}" text-anchor="middle" font-size="11" fill="#CA8A04" font-weight="600">Now</text>`;

    svg.innerHTML = svgContent;

    // Add interactivity
    svg.addEventListener('mousemove', (e) => {
        const rect = svg.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        // Get SVG point from screen coordinates
        const pt = svg.createSVGPoint();
        pt.x = e.clientX;
        pt.y = e.clientY;
        const svgP = pt.matrixTransform(svg.getScreenCTM().inverse());

        // Only show tooltip if mouse is within chart area
        if (svgP.x < padding.left || svgP.x > width - padding.right) {
            tooltip.style.opacity = '0';
            indicator.style.opacity = '0';
            return;
        }

        // Find closest week using SVG coordinates
        const relativeX = svgP.x - padding.left;
        const weekIndex = Math.round(relativeX / xScale);

        if (weekIndex >= 0 && weekIndex < frequencies.length) {
            const freq = frequencies[weekIndex];
            const weekInfo = WeekCalculator.getWeekInfo(weekIndex);

            // Position indicator in screen coordinates
            const indicatorSvgX = padding.left + (weekIndex * xScale);
            const indicatorPt = svg.createSVGPoint();
            indicatorPt.x = indicatorSvgX;
            indicatorPt.y = 0;
            const indicatorScreen = indicatorPt.matrixTransform(svg.getScreenCTM());
            indicator.style.left = `${indicatorScreen.x - rect.left}px`;
            indicator.style.opacity = '0.5';

            // Update and position tooltip
            tooltip.innerHTML = `
                <div style="font-weight: 600; margin-bottom: 2px;">${weekInfo.dateRange}</div>
                <div>${(freq * 100).toFixed(1)}% frequency</div>
            `;
            tooltip.style.opacity = '1';

            // Position tooltip above mouse, centered
            const tooltipX = mouseX - (tooltip.offsetWidth / 2);
            const tooltipY = mouseY - tooltip.offsetHeight - 10;
            tooltip.style.left = `${Math.max(0, Math.min(tooltipX, rect.width - tooltip.offsetWidth))}px`;
            tooltip.style.top = `${tooltipY}px`;
        }
    });

    svg.addEventListener('mouseleave', () => {
        tooltip.style.opacity = '0';
        indicator.style.opacity = '0';
    });
}

/**
 * Load hotspot data from JSON file
 */
async function loadHotspotData() {
    const url = '../regions/washtenaw/hotspot_guide_output/index/top_hotspots_by_species.json';
    console.log('Fetching hotspot data from:', url);
    try {
        const data = await fetchWithRetry(url, {
            autoRetry: true,
            timeoutMs: 10000
        });
        hotspotData = data;
        console.log('✓ Loaded hotspot data, species count:', Object.keys(data.species || {}).length);
    } catch (error) {
        console.warn('Could not load hotspot data:', error.message, error);
        hotspotData = null;
    }
}

/**
 * Render hotspot cards for current species
 */
function renderHotspots() {
    const container = document.getElementById('hotspots-container');
    if (!container) return;

    console.log('renderHotspots: hotspotData =', hotspotData);
    console.log('renderHotspots: currentSpecies.code =', currentSpecies?.code);

    // Check if we have hotspot data
    if (!hotspotData || !hotspotData.species) {
        console.log('renderHotspots: No hotspot data or species object');
        container.innerHTML = `
            <div class="text-center py-6" style="color: #6B7280;">
                <p>No hotspot data available - this species is rarely recorded in the county</p>
            </div>
        `;
        return;
    }

    // Find hotspots for current species by code
    const speciesHotspots = hotspotData.species[currentSpecies.code];
    console.log('renderHotspots: speciesHotspots =', speciesHotspots);

    if (!speciesHotspots || !speciesHotspots.top_hotspots || speciesHotspots.top_hotspots.length === 0) {
        container.innerHTML = `
            <div class="text-center py-6" style="color: #6B7280;">
                <p>No hotspot data available - this species is rarely recorded in the county</p>
            </div>
        `;
        return;
    }

    // Render hotspot cards
    const hotspotsHtml = speciesHotspots.top_hotspots.map(hotspot => {
        const occurrencePercent = (hotspot.occurrence_rate * 100).toFixed(1);
        const liftText = hotspot.lift ? `${hotspot.lift.toFixed(1)}× county average` : '';
        const ebirdUrl = `https://ebird.org/hotspot/${hotspot.locality_id}`;

        return `
            <a href="${ebirdUrl}" target="_blank" rel="noopener noreferrer" class="hotspot-card block">
                <div class="hotspot-name">${hotspot.name}</div>
                <div class="hotspot-stats">
                    <span class="hotspot-occurrence">${occurrencePercent}% of checklists</span>
                    ${liftText ? `<span class="hotspot-separator">•</span><span class="hotspot-lift">${liftText}</span>` : ''}
                </div>
                <div class="hotspot-detections">${hotspot.detection_count.toLocaleString()} detections</div>
            </a>
        `;
    }).join('');

    container.innerHTML = `
        <div class="hotspots-grid">
            ${hotspotsHtml}
        </div>
    `;
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
