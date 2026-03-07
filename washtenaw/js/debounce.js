/**
 * Debounce utility - delays function execution until after wait period
 *
 * Prevents excessive function calls during rapid events like typing.
 * The function only executes after the specified wait time has passed
 * since the last call.
 *
 * @param {Function} func - The function to debounce
 * @param {number} wait - Milliseconds to wait before executing
 * @returns {Function} Debounced function
 *
 * @example
 * const debouncedSearch = debounce(searchFunction, 300);
 * input.addEventListener('input', debouncedSearch);
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// Default debounce delay for search inputs (milliseconds)
const SEARCH_DEBOUNCE_MS = 300;
