/**
 * Week Calculator - Handles date/week conversions for eBird data
 * eBird uses 48 weeks: 4 weeks per month, indexed 0-47
 */

const WeekCalculator = {
    monthNames: [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ],

    /**
     * Get the current week index (0-47)
     */
    getCurrentWeek() {
        const now = new Date();
        const month = now.getMonth(); // 0-11
        const day = now.getDate(); // 1-31

        // Calculate which week of the month (0-3)
        const weekOfMonth = Math.min(Math.floor((day - 1) / 7), 3);

        // Calculate overall week index
        return (month * 4) + weekOfMonth;
    },

    /**
     * Convert week index to readable date range
     * @param {number} weekIndex - Week index (0-47)
     * @returns {string} - e.g., "May 8-14"
     */
    weekToDateRange(weekIndex) {
        const monthIndex = Math.floor(weekIndex / 4);
        const weekOfMonth = weekIndex % 4;

        // Days in each month (non-leap year)
        const daysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

        const dayStarts = [1, 8, 15, 22];

        const month = this.monthNames[monthIndex];
        const startDay = dayStarts[weekOfMonth];

        // End day: weeks 1-3 end on day 7, 14, 21
        // Week 4 ends on the last day of the month
        let endDay;
        if (weekOfMonth === 3) {
            endDay = daysInMonth[monthIndex];
        } else {
            endDay = dayStarts[weekOfMonth] + 6;
        }

        return `${month} ${startDay}-${endDay}`;
    },

    /**
     * Convert week index to short form
     * @param {number} weekIndex - Week index (0-47)
     * @returns {string} - e.g., "early May", "mid May", "late May"
     */
    weekToShortForm(weekIndex) {
        const monthIndex = Math.floor(weekIndex / 4);
        const weekOfMonth = weekIndex % 4;

        const weekLabels = ['early', 'mid', 'late', 'late'];
        const month = this.monthNames[monthIndex];

        return `${weekLabels[weekOfMonth]} ${month}`;
    },

    /**
     * Get week info for display
     * @param {number} weekIndex - Week index (0-47)
     * @returns {object} - {title, dateRange, isCurrentWeek}
     */
    getWeekInfo(weekIndex) {
        const currentWeek = this.getCurrentWeek();
        const isCurrentWeek = weekIndex === currentWeek;

        return {
            title: isCurrentWeek ? 'This Week' : this.weekToDateRange(weekIndex),
            dateRange: this.weekToDateRange(weekIndex),
            shortForm: this.weekToShortForm(weekIndex),
            isCurrentWeek
        };
    },

    /**
     * Parse timing string to week index
     * e.g., "early May" -> week index
     */
    parseTimingToWeek(timingStr) {
        if (!timingStr) return null;

        const parts = timingStr.toLowerCase().split(' ');
        if (parts.length < 2) return null;

        const modifier = parts[0]; // early, mid, late
        const monthName = parts[1].charAt(0).toUpperCase() + parts[1].slice(1);

        const monthIndex = this.monthNames.indexOf(monthName);
        if (monthIndex === -1) return null;

        const weekOfMonth = modifier === 'early' ? 0 :
                           modifier === 'mid' ? 1 : 2;

        return (monthIndex * 4) + weekOfMonth;
    },

    /**
     * Check if a species is arriving this week
     * Exact match only
     */
    isArriving(species, weekIndex) {
        if (species.timing.status === 'year-round' || species.timing.status === 'irregular') {
            return false;
        }

        // Check spring arrival for single-season and two-passage
        if (species.timing.arrival) {
            const arrivalWeek = this.parseTimingToWeek(species.timing.arrival);
            if (arrivalWeek === weekIndex) return true;
        }
        if (species.timing.spring_arrival) {
            const arrivalWeek = this.parseTimingToWeek(species.timing.spring_arrival);
            if (arrivalWeek === weekIndex) return true;
        }

        // Check fall arrival for two-passage
        if (species.timing.fall_arrival) {
            const arrivalWeek = this.parseTimingToWeek(species.timing.fall_arrival);
            if (arrivalWeek === weekIndex) return true;
        }

        // Check winter arrival for winter residents
        if (species.timing.winter_arrival) {
            const arrivalWeek = this.parseTimingToWeek(species.timing.winter_arrival);
            if (arrivalWeek === weekIndex) return true;
        }

        return false;
    },

    /**
     * Check if a species is at peak this week
     * Exact match only
     */
    isAtPeak(species, weekIndex) {
        if (species.timing.status === 'year-round' || species.timing.status === 'irregular') {
            return false;
        }

        // Check peak for single-season
        if (species.timing.peak) {
            const peakWeek = this.parseTimingToWeek(species.timing.peak);
            if (peakWeek === weekIndex) return true;
        }

        // Check spring peak for two-passage
        if (species.timing.spring_peak) {
            const peakWeek = this.parseTimingToWeek(species.timing.spring_peak);
            if (peakWeek === weekIndex) return true;
        }

        // Check fall peak for two-passage
        if (species.timing.fall_peak) {
            const peakWeek = this.parseTimingToWeek(species.timing.fall_peak);
            if (peakWeek === weekIndex) return true;
        }

        // Check winter peak for winter residents
        if (species.timing.winter_peak) {
            const peakWeek = this.parseTimingToWeek(species.timing.winter_peak);
            if (peakWeek === weekIndex) return true;
        }

        return false;
    },

    /**
     * Check if a species is departing this week
     * Exact match only
     */
    isDeparting(species, weekIndex) {
        if (species.timing.status === 'year-round' || species.timing.status === 'irregular') {
            return false;
        }

        // Check departure for single-season
        if (species.timing.departure) {
            const departureWeek = this.parseTimingToWeek(species.timing.departure);
            if (departureWeek === weekIndex) return true;
        }

        // Check spring departure for two-passage
        if (species.timing.spring_departure) {
            const departureWeek = this.parseTimingToWeek(species.timing.spring_departure);
            if (departureWeek === weekIndex) return true;
        }

        // Check fall departure for two-passage
        if (species.timing.fall_departure) {
            const departureWeek = this.parseTimingToWeek(species.timing.fall_departure);
            if (departureWeek === weekIndex) return true;
        }

        // Check winter departure for winter residents
        if (species.timing.winter_departure) {
            const departureWeek = this.parseTimingToWeek(species.timing.winter_departure);
            if (departureWeek === weekIndex) return true;
        }

        return false;
    }
};
